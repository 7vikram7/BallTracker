// Unit tests for the app core. Run: node --test mobile/test/   (Node 20+, no packages needed)

import assert from 'node:assert/strict';
import { test } from 'node:test';

import { EdgeClient } from '../src/core/edgeClient.js';
import { base64ToBytes, packDetections, packPreview, unpackDetections } from '../src/core/protocol.js';
import { displayHost, toEdgeUrl } from '../src/core/serverAddress.js';
import { CameraSession } from '../src/core/session.js';
import { FakeWebSocket, MockNative } from './mocks.js';

const tick = () => new Promise((r) => setTimeout(r, 0));

test('detections pack/unpack round trip with the documented layout', () => {
  const batch = { width: 1920, height: 1080, frames: [
    { seq: 41, t: 1234.567891, c: [10.5, 20.25, 3, 0.875, 100, 200, 5, 0.5] },
    { seq: 42, t: 1234.576, c: [] },
  ] };
  const buf = packDetections(batch);
  assert.equal(buf.byteLength, 10 + 14 + 32 + 14);
  const dv = new DataView(buf);
  assert.equal(String.fromCharCode(...new Uint8Array(buf, 0, 4)), 'BTD1');
  assert.equal(dv.getUint16(8, true), 2);
  const back = unpackDetections(buf);
  assert.equal(back.frames[0].seq, 41);
  assert.equal(back.frames[0].t, 1234.567891);
  assert.deepEqual(back.frames[0].c, [10.5, 20.25, 3, 0.875, 100, 200, 5, 0.5]);
  assert.deepEqual(back.frames[1].c, []);
});

test('preview header and base64 decoding', () => {
  const jpeg = new Uint8Array([0xff, 0xd8, 1, 2, 3, 0xff, 0xd9]);
  const buf = packPreview(7, 99.5, 1280, 720, jpeg);
  const dv = new DataView(buf);
  assert.equal(String.fromCharCode(...new Uint8Array(buf, 0, 4)), 'BTP1');
  assert.equal(dv.getUint32(4, true), 7);
  assert.equal(dv.getFloat64(8, true), 99.5);
  assert.equal(dv.getUint16(16, true), 1280);
  assert.deepEqual(new Uint8Array(buf, 20), jpeg);
  for (const n of [0, 1, 2, 3, 100, 1001]) {
    const bytes = Uint8Array.from({ length: n }, (_, i) => (i * 37 + 11) & 0xff);
    const b64 = Buffer.from(bytes).toString('base64');
    assert.deepEqual(base64ToBytes(b64), bytes);
    assert.deepEqual(base64ToBytes(b64.replace(/(.{76})/g, '$1\n')), bytes);
  }
});

test('server address parsing', () => {
  assert.equal(toEdgeUrl('192.168.0.247'), 'ws://192.168.0.247:8080/ws/edge');
  assert.equal(toEdgeUrl(' 192.168.0.247:9000 '), 'ws://192.168.0.247:9000/ws/edge');
  assert.equal(toEdgeUrl('https://192.168.0.247:8443/phone'), 'ws://192.168.0.247:8080/ws/edge');
  assert.equal(toEdgeUrl('http://mac.local:8080/dashboard'), 'ws://mac.local:8080/ws/edge');
  assert.equal(toEdgeUrl('ws://10.0.0.2:8090'), 'ws://10.0.0.2:8090/ws/edge');
  assert.equal(toEdgeUrl('ws://10.0.0.2:8090/ws/edge'), 'ws://10.0.0.2:8090/ws/edge');
  assert.equal(toEdgeUrl('balltracker://connect?ws=' + encodeURIComponent('ws://10.0.0.5:8080/ws/edge')),
    'ws://10.0.0.5:8080/ws/edge');
  assert.equal(toEdgeUrl(''), null);
  assert.equal(toEdgeUrl('not a host!'), null);
  assert.equal(displayHost('ws://10.0.0.5:8080/ws/edge'), '10.0.0.5:8080');
});

test('client: hello on open, pong with the native clock, reconnect after a drop', async () => {
  FakeWebSocket.reset();
  const states = [];
  const c = new EdgeClient({
    url: 'ws://x:8080/ws/edge', WebSocketImpl: FakeWebSocket, now: () => 4242.5,
    hello: () => ({ name: 'cam-a', width: 1920, height: 1080, fps: 240 }),
    onConnection: (s) => states.push(s),
  });
  // Not connected yet: detections are counted as offline (not a Wi-Fi drop), not thrown.
  assert.equal(c.sendDetections({ width: 1, height: 1, frames: [{ seq: 0, t: 0, c: [] }] }), false);
  c.start();
  const ws = FakeWebSocket.last();
  ws.open();
  const hello = ws.json()[0];
  assert.equal(hello.type, 'hello');
  assert.equal(hello.mode, 'edge');
  assert.equal(hello.proto, 2);
  assert.equal(hello.fps, 240);
  ws.receive({ type: 'ping', id: 9, ts: 1.0 });
  assert.deepEqual(ws.json()[1], { type: 'pong', id: 9, tp: 4242.5 });
  assert.equal(c.sendDetections({ width: 1920, height: 1080, frames: [{ seq: 1, t: 1, c: [1, 2, 3, 0.5] }] }), true);
  assert.equal(ws.binary().length, 1);
  // Backlog too large: drop instead of queueing forever.
  ws.bufferedAmount = 10_000_000;
  assert.equal(c.sendDetections({ width: 1920, height: 1080, frames: [{ seq: 2, t: 2, c: [] }] }), false);
  assert.equal(c.stats.droppedFrames, 1);
  assert.equal(c.stats.offlineFrames, 1);
  ws.close();
  assert.equal(states.at(-1), 'disconnected');
  await new Promise((r) => setTimeout(r, 600)); // first backoff 0.5 s
  assert.equal(FakeWebSocket.instances.length, 2);
  FakeWebSocket.last().open();
  assert.equal(states.at(-1), 'connected');
  c.stop();
  assert.equal(states.at(-1), 'stopped');
  await new Promise((r) => setTimeout(r, 600));
  assert.equal(FakeWebSocket.instances.length, 2); // no reconnect after stop
});

test('session: applies server config at the real fps, forwards detections and previews, shows calls', async () => {
  FakeWebSocket.reset();
  const native = new MockNative({ startResult: { width: 1920, height: 1080, fps: 240, format: 'mock' } });
  let wall = 0;
  const states = [];
  const s = new CameraSession({
    native, WebSocketImpl: FakeWebSocket, wallNow: () => wall, onState: (st) => states.push(st),
    // reduction off: this test checks the plumbing (reducer.test.js covers the reduction)
    settings: { url: 'ws://x/ws/edge', name: 'cam-b', width: 1920, height: 1080, fps: 240, reduce: { enabled: false } },
  });
  await s.start();
  assert.equal(native.started.fps, 240);
  assert.equal(s.state.phase, 'running');
  const ws = FakeWebSocket.last();
  ws.open();
  assert.equal(ws.json()[0].width, 1920);
  ws.receive({ type: 'welcome', name: 'cam-b', calibrated: false });
  ws.receive({ type: 'config', detector: { bin: 2, fps: 60, hsv_low: [25, 100, 90] } });
  assert.equal(native.detectorConfigs.length, 1);
  assert.equal(native.detectorConfigs[0].fps, 240); // camera's real rate, not the server's default
  native.emit('onDetections', { width: 1920, height: 1080, frames: [
    { seq: 1, t: 10.0, c: [5, 5, 3, 0.9] }, { seq: 2, t: 10.004, c: [] }] });
  native.emit('onPreview', { seq: 1, t: 10.0, width: 1920, height: 1080,
    jpegBase64: Buffer.from([0xff, 0xd8, 0xff, 0xd9]).toString('base64') });
  assert.equal(ws.binary().length, 2);
  wall = 1500;
  native.emit('onStats', { fpsCapture: 240, fpsProcessed: 238, detectMs: 2.1, dropped: 0, thermal: 'nominal' });
  const stats = ws.json().find((m) => m.type === 'stats');
  assert.equal(stats.fps_processed, 238);
  assert.equal(s.state.candidatesPerSec, 1 / 1.5);
  ws.receive({ type: 'calibration', camera: { focal_px: 1500 } });
  assert.equal(s.state.calibrated, true);
  ws.receive({ type: 'call', text: 'OUT' });
  assert.equal(s.state.lastCall.text, 'OUT');
  await s.stop();
  assert.equal(native.stopped, 1);
  assert.equal(native.listenerCount(), 0);
  assert.equal(s.state.phase, 'idle');
});

test('session: camera failure is reported, not thrown', async () => {
  const native = new MockNative();
  native.start = async () => { throw new Error('format 1920x1080@240 not supported'); };
  const s = new CameraSession({ native, WebSocketImpl: FakeWebSocket,
    settings: { url: 'ws://x/ws/edge', name: 'c', width: 1920, height: 1080, fps: 240 } });
  await s.start();
  await tick();
  assert.equal(s.state.phase, 'error');
  assert.match(s.state.error, /not supported/);
  assert.equal(native.listenerCount(), 0);
});

test('simulated camera drives a full session (what Expo Go uses before the native build)', async () => {
  const { SimCamera } = await import('../src/core/simCamera.js');
  FakeWebSocket.reset();
  const cam = new SimCamera();
  const s = new CameraSession({ native: cam, WebSocketImpl: FakeWebSocket,
    settings: { url: 'ws://x/ws/edge', name: 'sim', width: 1280, height: 720, fps: 60 } });
  await s.start();
  FakeWebSocket.last().open();
  await new Promise((r) => setTimeout(r, 1200));
  await s.stop();
  const ws = FakeWebSocket.last();
  const frames = ws.binary().reduce((n, b) => n + new DataView(b).getUint16(8, true), 0);
  // ~72 frames captured at 60 fps; the phone-side reducer sends ~30 per second outside bounces.
  assert.ok(frames > 20 && frames < 60, `frames sent: ${frames}`);
  assert.ok(ws.json().some((m) => m.type === 'stats'));
  assert.equal(cam.timer, null);
});

test('simulated session with phone-side reduction off sends every frame', async () => {
  const { SimCamera } = await import('../src/core/simCamera.js');
  FakeWebSocket.reset();
  const cam = new SimCamera();
  const s = new CameraSession({ native: cam, WebSocketImpl: FakeWebSocket,
    settings: { url: 'ws://x/ws/edge', name: 'sim', width: 1280, height: 720, fps: 60, reduce: { enabled: false } } });
  await s.start();
  FakeWebSocket.last().open();
  await new Promise((r) => setTimeout(r, 1200));
  await s.stop();
  const frames = FakeWebSocket.last().binary().reduce((n, b) => n + new DataView(b).getUint16(8, true), 0);
  assert.ok(frames > 50, `frames sent: ${frames}`);
});

test('wire format matches the frozen bytes shared with the Python server (tests/golden)', async () => {
  const { readFileSync } = await import('node:fs');
  const golden = new URL('../../tests/golden/', import.meta.url);
  const inp = JSON.parse(readFileSync(new URL('protocol_dets.json', golden), 'utf8'));
  const hex = readFileSync(new URL('protocol_dets.hex', golden), 'utf8').trim();
  const got = Buffer.from(packDetections(inp)).toString('hex');
  assert.equal(got, hex, 'protocol.js differs from balltracker/live/protocol.py');
});

test('base64 decoding rejects characters outside the alphabet', () => {
  // U+0100 used to index past the lookup table and add six zero bits silently (review of defed68)
  assert.throws(() => base64ToBytes('QUJDĀREVG'), /base64/);
  assert.throws(() => base64ToBytes('QUJD!REVG'), /base64/);
  assert.deepEqual(base64ToBytes('QUJD\r\n REVG\t'), new Uint8Array([65, 66, 67, 68, 69, 70]));  // whitespace is fine
});
