// Test doubles: a native camera module and a WebSocket, both scriptable.

export class MockNative {
  constructor({ clockOffset = 0, startResult } = {}) {
    this.clockOffset = clockOffset;
    this.listeners = new Map();
    this.started = null;
    this.detectorConfigs = [];
    this.exposures = [];
    this.startResult = startResult || { width: 1920, height: 1080, fps: 120, format: 'mock' };
    this.stopped = 0;
    this.spoken = [];
  }
  speak(text) {
    this.spoken.push(text);
  }
  now() {
    return performance.now() / 1000 + this.clockOffset;
  }
  async start(opts) {
    this.started = opts;
    return this.startResult;
  }
  async stop() {
    this.stopped += 1;
  }
  setDetectorConfig(cfg) {
    this.detectorConfigs.push(cfg);
  }
  async setExposure(opts) {
    this.exposures.push(opts);
    return { mode: opts.mode, shutterS: opts.shutterS ?? null, iso: 400 };
  }
  addListener(event, fn) {
    if (!this.listeners.has(event)) this.listeners.set(event, new Set());
    this.listeners.get(event).add(fn);
    return { remove: () => this.listeners.get(event).delete(fn) };
  }
  emit(event, payload) {
    for (const fn of this.listeners.get(event) || []) fn(payload);
  }
  listenerCount() {
    let n = 0;
    for (const s of this.listeners.values()) n += s.size;
    return n;
  }
}

/** Minimal browser-style WebSocket double. Tests call open()/receive()/close(). */
export class FakeWebSocket {
  static instances = [];
  constructor(url) {
    this.url = url;
    this.readyState = 0;
    this.sent = [];
    this.bufferedAmount = 0;
    FakeWebSocket.instances.push(this);
  }
  send(data) {
    if (this.readyState !== 1) throw new Error('not open');
    this.sent.push(data);
  }
  close() {
    if (this.readyState === 3) return;
    this.readyState = 3;
    if (this.onclose) this.onclose({});
  }
  // --- test controls ---
  open() {
    this.readyState = 1;
    if (this.onopen) this.onopen({});
  }
  receive(obj) {
    if (this.onmessage) this.onmessage({ data: typeof obj === 'string' ? obj : JSON.stringify(obj) });
  }
  json() {
    return this.sent.filter((d) => typeof d === 'string').map((d) => JSON.parse(d));
  }
  binary() {
    return this.sent.filter((d) => typeof d !== 'string');
  }
  static last() {
    return FakeWebSocket.instances[FakeWebSocket.instances.length - 1];
  }
  static reset() {
    FakeWebSocket.instances = [];
  }
}
