// Web Worker for the phone page: runs the C++ ball detector (ballcore.wasm) off the main thread.
// Messages in:  {type:'init', wasmUrl, config} | {type:'config', config} | {type:'frame', bitmap, seq, t}
// Messages out: {type:'ready'} | {type:'error', message} | {type:'det', seq, t, c, us, w, h}
'use strict';
importScripts('ballcore.js');

let det = null;
let canvas = null;
let ctx = null;

self.onmessage = async (e) => {
  const m = e.data;
  try {
    if (m.type === 'init') {
      det = await BallCore.load(m.wasmUrl);
      det.configure(m.config || {});
      self.postMessage({ type: 'ready' });
    } else if (m.type === 'config') {
      if (det) det.configure(m.config);
    } else if (m.type === 'frame') {
      const bmp = m.bitmap;
      if (!det) {
        bmp.close();
        self.postMessage({ type: 'det', seq: m.seq, t: m.t, c: [], us: 0, w: 0, h: 0, skipped: true });
        return;
      }
      if (!canvas || canvas.width !== bmp.width || canvas.height !== bmp.height) {
        canvas = new OffscreenCanvas(bmp.width, bmp.height);
        ctx = canvas.getContext('2d', { willReadFrequently: true, alpha: false });
      }
      ctx.drawImage(bmp, 0, 0);
      bmp.close();
      const img = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const c = det.detect(img.data, img.width, img.height);
      self.postMessage({ type: 'det', seq: m.seq, t: m.t, c, us: det.lastMicros(), w: img.width, h: img.height });
    }
  } catch (err) {
    self.postMessage({ type: 'error', message: String((err && err.message) || err) });
  }
};
