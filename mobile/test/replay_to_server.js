// Integration harness: the app's CameraSession + EdgeClient, with a mock native
// camera that replays precomputed detections in real time, against a real
// `bt serve`. Used by tests/test_edge.py (run_live_demo(edge_client="node")).
//
//   node --experimental-websocket mobile/test/replay_to_server.js \
//        --url ws://127.0.0.1:8090/ws/edge --name cam-a --dets dets.json [--offset 12.5]
//
// dets.json: {width, height, fps, frames: [[t_clip, [[u, v, r, score], ...]], ...],
//             previews: [[t_clip, "<jpeg base64>"], ...]}
// Prints "START <wall clock s of clip t=0>" and finally "DONE <json stats>".

import { readFileSync } from 'node:fs';

import { CameraSession } from '../src/core/session.js';
import { MockNative } from './mocks.js';

const args = Object.fromEntries(process.argv.slice(2).reduce((acc, a, i, all) => {
  if (a.startsWith('--')) acc.push([a.slice(2), all[i + 1]]);
  return acc;
}, []));
const data = JSON.parse(readFileSync(args.dets, 'utf8'));
const offset = Number(args.offset || 0);
const sleep = (ms) => new Promise((r) => setTimeout(r, Math.max(0, ms)));

class ReplayNative extends MockNative {
  constructor() {
    super({ clockOffset: offset, startResult: { width: data.width, height: data.height, fps: data.fps, format: 'replay' } });
  }
}

const native = new ReplayNative();
let connectedAt = null;
const session = new CameraSession({
  native,
  settings: { url: args.url, name: args.name, width: data.width, height: data.height, fps: data.fps,
    device: 'node-replay', platform: 'node', appVersion: 'test' },
  onState: (s) => {
    if (s.connection === 'connected' && connectedAt === null) connectedAt = performance.now();
  },
});

await session.start();
for (let i = 0; i < 100 && connectedAt === null; i++) await sleep(50);
if (connectedAt === null) {
  console.log('DONE ' + JSON.stringify({ error: 'could not connect' }));
  process.exit(2);
}
await sleep(1500); // let the server's clock sync settle (as the real app does by just running)
const configsBefore = native.detectorConfigs.length;

const batchMs = 50;
const startPerf = performance.now() + 200;
console.log(`START ${(performance.timeOrigin + startPerf) / 1000}`);
const t0Native = native.now() + 0.2;
let pending = [];
let nextSend = startPerf + batchMs;
let pi = 0;
let seq = 0;
for (const [tClip, cands] of data.frames) {
  const due = startPerf + tClip * 1000;
  if (due >= nextSend && pending.length) {
    await sleep(nextSend - performance.now());
    native.emit('onDetections', { width: data.width, height: data.height, frames: pending });
    pending = [];
    while (nextSend <= due) nextSend += batchMs;
  }
  pending.push({ seq: seq++, t: t0Native + tClip, c: cands.flat() });
  while (data.previews && pi < data.previews.length && data.previews[pi][0] <= tClip) {
    native.emit('onPreview', { seq, t: t0Native + data.previews[pi][0], width: data.width, height: data.height,
      jpegBase64: data.previews[pi][1] });
    pi++;
  }
  if (seq % 30 === 0) {
    native.emit('onStats', { fpsCapture: data.fps, fpsProcessed: data.fps, detectMs: 2.0, dropped: 0, thermal: 'nominal' });
  }
}
if (pending.length) {
  await sleep(nextSend - performance.now());
  native.emit('onDetections', { width: data.width, height: data.height, frames: pending });
}
await sleep(800);
const stats = { ...session.client.stats, connection: session.state.connection, calibrated: session.state.calibrated,
  configs: native.detectorConfigs.length, configBeforeStart: configsBefore > 0,
  configFps: native.detectorConfigs.at(-1)?.fps ?? null, lastCall: session.state.lastCall };
await session.stop();
console.log('DONE ' + JSON.stringify(stats));
process.exit(0);
