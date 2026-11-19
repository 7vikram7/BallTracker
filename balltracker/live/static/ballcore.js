// Loader for ballcore.wasm: the app's C++ ball detector, compiled for browsers.
// Works in a classic Web Worker (importScripts), in a page, and in Node (tests).
//
//   const det = await BallCore.load('/static/ballcore.wasm');   // or ArrayBuffer/Uint8Array of the file
//   det.configure({fps: 60, hsv_low: [25, 100, 90], ...});      // EdgeDetectorConfig fields (server "config" message)
//   const c = det.detect(rgbaPixels, width, height);           // [u, v, r, score, u, v, r, score, ...]
(function (root) {
  'use strict';

  const FMT_RGBA = 1;
  const DEFAULTS = {
    bin: 2, hsv_low: [25, 100, 90], hsv_high: [55, 255, 255], max_candidates: 12, flicker_compensation: true,
    var_threshold: 24, var_init: 15, var_min: 4, var_max: 75, bg_history_s: 2, bg_update_hz: 60, fps: 60,
    min_radius_px: 1.5, max_radius_px: 80, max_elongation: 6, flicker_alpha: 0.02,
  };

  function flatten(cfg) {
    const c = Object.assign({}, DEFAULTS, cfg || {});
    return [c.bin, c.hsv_low[0], c.hsv_low[1], c.hsv_low[2], c.hsv_high[0], c.hsv_high[1], c.hsv_high[2],
      c.max_candidates, c.flicker_compensation ? 1 : 0, c.var_threshold, c.var_init, c.var_min, c.var_max,
      c.bg_history_s, c.bg_update_hz, c.fps, c.min_radius_px, c.max_radius_px, c.max_elongation, c.flicker_alpha];
  }

  class Detector {
    constructor(ex) {
      this.ex = ex;
      this.h = ex.bcw_create();
      this.cfgPtr = ex.bcw_alloc(20 * 8);
      this.outPtr = ex.bcw_alloc(64 * 4 * 4);
      this.pxPtr = 0;
      this.pxSize = 0;
    }
    get memory() { return this.ex.memory.buffer; } // re-read after every call: memory can grow
    configure(cfg) {
      const v = flatten(cfg);
      new Float64Array(this.memory, this.cfgPtr, 20).set(v);
      return this.ex.bcw_configure(this.h, this.cfgPtr, 20) === 1;
    }
    reset() { this.ex.bcw_reset(this.h); }
    /** pixels: RGBA bytes (ImageData.data), rows packed (stride = width * 4). */
    detect(pixels, width, height, fmt) {
      const n = width * height * 4;
      if (n > this.pxSize) {
        if (this.pxPtr) this.ex.bcw_free(this.pxPtr);
        this.pxPtr = this.ex.bcw_alloc(n);
        this.pxSize = n;
      }
      new Uint8Array(this.memory, this.pxPtr, n).set(pixels.subarray ? pixels.subarray(0, n) : pixels);
      const k = this.ex.bcw_detect(this.h, this.pxPtr, width, height, width * 4, fmt == null ? FMT_RGBA : fmt, this.outPtr, 64);
      return k > 0 ? Array.from(new Float32Array(this.memory, this.outPtr, k * 4)) : [];
    }
    lastMicros() { return this.ex.bcw_last_us(this.h); }
  }

  async function load(src) {
    let memory = null;
    const dv = () => new DataView(memory.buffer);
    const now = () => (typeof performance !== 'undefined' ? performance.now() : Date.now());
    const wasi = {
      clock_time_get(_id, _precision, outPtr) {
        dv().setBigUint64(outPtr, BigInt(Math.round(now() * 1e6)), true);
        return 0;
      },
      fd_write(_fd, iovs, iovsLen, nwrittenPtr) { // stdio (only used for abort messages): discard
        let total = 0;
        for (let i = 0; i < iovsLen; i++) total += dv().getUint32(iovs + 8 * i + 4, true);
        dv().setUint32(nwrittenPtr, total, true);
        return 0;
      },
      fd_close() { return 0; },
      fd_seek() { return 0; },
    };
    let bytes = src;
    if (typeof src === 'string') bytes = await (await fetch(src)).arrayBuffer();
    const { instance } = await WebAssembly.instantiate(bytes, { wasi_snapshot_preview1: wasi });
    memory = instance.exports.memory;
    instance.exports._initialize();
    return new Detector(instance.exports);
  }

  const api = { load, flatten, DEFAULTS, FMT_RGBA };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.BallCore = api;
})(typeof self !== 'undefined' ? self : this);
