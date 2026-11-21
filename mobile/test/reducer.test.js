// Phone-side data reduction: still clutter dropped, full rate around direction changes,
// base rate elsewhere, nothing lost when disabled.
import test from 'node:test';
import assert from 'node:assert/strict';
import { Reducer } from '../src/core/reducer.js';

const FPS = 120;

/** A ball thrown across the image, bouncing at t=1.0 s (image v goes down then up), plus a still blob. */
function scene(seconds = 2.0, withClutter = true) {
  const frames = [];
  for (let i = 0; i < seconds * FPS; i++) {
    const t = i / FPS;
    const c = [];
    // Ball: u moves steadily; v follows a parabola that reverses at the bounce (image y grows downward).
    const u = 100 + 400 * t;
    const v = t < 1.0 ? 200 + 300 * t + 250 * t * t : 750 - 260 * (t - 1.0) + 250 * (t - 1.0) ** 2;
    if (t > 0.2 && t < 1.8) c.push(u, v, 4, 0.9);
    if (withClutter) c.push(900 + (i % 2) * 0.5, 300, 6, 0.85);  // still object, sub-pixel jitter
    frames.push({ seq: i, t, c });
  }
  return frames;
}

function runAll(red, frames, batch = 6) {
  const out = [];
  for (let i = 0; i < frames.length; i += batch) out.push(...red.push(frames.slice(i, i + batch)));
  out.push(...red.flush());
  return out;
}

test('reducer: full rate around the bounce, ~base rate elsewhere', () => {
  const red = new Reducer({ baseHz: 30 });
  const out = runAll(red, scene());
  const sent = new Set(out.map((f) => f.seq));
  // Every frame within +-60 ms of the bounce is sent (the server's sub-frame fit needs them).
  for (let i = Math.round(0.94 * FPS); i <= Math.round(1.06 * FPS); i++) assert.ok(sent.has(i), `frame ${i} near the bounce`);
  // Far from any change (0.4-0.7 s) only ~30 fps go out.
  const quiet = out.filter((f) => f.t > 0.4 && f.t < 0.7).length;
  assert.ok(quiet >= 8 && quiet <= 11, `quiet stretch sent ${quiet} frames`);
  assert.ok(out.length < 0.45 * scene().length, `sent ${out.length} of ${scene().length}`);
  // Output stays in capture order, without duplicates.
  for (let i = 1; i < out.length; i++) assert.ok(out[i].seq > out[i - 1].seq);
  assert.ok(red.stats.changes >= 1);
});

test('reducer: a still object is dropped after it has been there a while, the ball never', () => {
  const red = new Reducer();
  const out = runAll(red, scene(6.0));
  const late = out.filter((f) => f.t > 2.5);
  assert.ok(late.length > 0);
  for (const f of late) assert.equal(f.c.length, 0, `still blob still sent at t=${f.t}`);
  const early = out.filter((f) => f.t > 0.3 && f.t < 1.5);
  for (const f of early) assert.ok(f.c.some((_, i) => i % 4 === 0 && Math.abs(f.c[i] - (100 + 400 * f.t)) < 1), `ball missing at t=${f.t}`);
});

test('reducer: disabled passes everything through unchanged', () => {
  const frames = scene(1.0);
  const red = new Reducer({ enabled: false });
  const out = runAll(red, frames);
  assert.equal(out.length, frames.length);
  assert.deepEqual(out[10], frames[10]);
});

test('reducer: a busy scene does not starve the ball of a track (full rate at its bounce)', () => {
  // 20 slow-moving blobs (players, shirts) take every track slot before the ball appears at 0.2 s.
  // Review of defed68 (TODO-27): new candidates then got no track, so the bounce went out at 30 fps.
  const frames = scene(2.0, false).map((f) => {
    const c = [...f.c];
    for (let k = 0; k < 20; k++) {
      c.push(60 + 45 * k + 25 * Math.sin(2 * Math.PI * 0.3 * f.t + k), 620 + 10 * Math.cos(f.t + k), 9, 0.95);
    }
    return { seq: f.seq, t: f.t, c };
  });
  const red = new Reducer({ baseHz: 30 });
  const sent = new Set(runAll(red, frames).map((f) => f.seq));
  for (let i = Math.round(0.96 * FPS); i <= Math.round(1.04 * FPS); i++) assert.ok(sent.has(i), `frame ${i} near the bounce`);
});
