// Runs ballcore.wasm (browser build) on raw RGBA frames written by tests/test_edge.py; prints JSON.
//   node tests/js/wasm_detect.js frames.rgba width height n fps
const fs = require('fs');
const path = require('path');
const BallCore = require(path.join(__dirname, '../../balltracker/live/static/ballcore.js'));
(async () => {
  const [file, w, h, n, fps] = process.argv.slice(2);
  const W = +w, H = +h, N = +n;
  const det = await BallCore.load(fs.readFileSync(path.join(__dirname, '../../balltracker/live/static/ballcore.wasm')));
  det.configure({ fps: +fps });
  const all = fs.readFileSync(file);
  const out = [];
  let us = 0;
  for (let i = 0; i < N; i++) {
    out.push(det.detect(all.subarray(i * W * H * 4, (i + 1) * W * H * 4), W, H));
    us += det.lastMicros();
  }
  process.stdout.write(JSON.stringify({ frames: out, ms_per_frame: us / N / 1000 }));
})();
