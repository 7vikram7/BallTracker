// A stand-in for the native camera module, used when the native code isn't
// built in (e.g. running in Expo Go) and in tests. It produces frames at the
// requested rate with a simulated ball moving across the image, so the
// connection, clock sync, dashboard and UI can be exercised without a camera.

export class SimCamera {
  constructor() {
    this.listeners = new Map();
    this.timer = null;
    this.detectorConfig = null;
    this.isSimulator = true;
  }

  now() {
    return performance.now() / 1000;
  }

  async getFormats() {
    return [{ width: 1280, height: 720, maxFps: 60, binned: false }, { width: 1920, height: 1080, maxFps: 60, binned: false }];
  }

  /** @param {string} event @param {(payload: any) => void} fn */
  addListener(event, fn) {
    if (!this.listeners.has(event)) this.listeners.set(event, new Set());
    this.listeners.get(event).add(fn);
    return { remove: () => this.listeners.get(event).delete(fn) };
  }

  /** @param {string} event @param {any} payload */
  _emit(event, payload) {
    for (const fn of this.listeners.get(event) || []) fn(payload);
  }

  /** @param {{width?: number, height?: number, fps?: number, batchMs?: number}} opts */
  async start(opts) {
    await this.stop();
    const width = opts.width || 1280, height = opts.height || 720, fps = Math.min(opts.fps || 60, 60);
    const batchMs = opts.batchMs || 50;
    /** @type {{seq: number, t: number, c: number[]}[]} */
    let frames = [];
    let seq = 0, tStats = this.now(), nStats = 0, tBatch = this.now();
    const t0 = this.now();
    const step = () => {
      const t = this.now();
      // A ball crossing the image every 2 s along a parabola (pixels).
      const ph = ((t - t0) % 2) / 2;
      const u = width * (0.1 + 0.8 * ph);
      const v = height * (0.25 + 1.6 * (ph - 0.5) ** 2);
      frames.push({ seq: seq++, t, c: [u, v, 6, 0.9] });
      nStats++;
      if ((t - tBatch) * 1000 >= batchMs) {
        this._emit('onDetections', { width, height, frames });
        frames = [];
        tBatch = t;
      }
      if (t - tStats >= 1) {
        this._emit('onStats', { fpsCapture: nStats / (t - tStats), fpsProcessed: nStats / (t - tStats), detectMs: 0,
          dropped: 0, thermal: 'nominal', battery: -1 });
        tStats = t;
        nStats = 0;
      }
    };
    this.timer = setInterval(step, 1000 / fps);
    return { width, height, fps, format: 'simulated' };
  }

  async stop() {
    if (this.timer) clearInterval(this.timer);
    this.timer = null;
  }

  /** @param {object} cfg */
  setDetectorConfig(cfg) {
    this.detectorConfig = cfg;
  }

  /** @param {{mode: string, shutterS?: number}} opts */
  async setExposure(opts) {
    return { mode: opts.mode, shutterS: opts.shutterS ?? null, iso: null, simulated: true };
  }

  /** The simulator has no voice: it keeps what it was asked to say (tests read it).
   * @param {string} text */
  speak(text) {
    this.spoken = [...(this.spoken || []), text];
  }
}
