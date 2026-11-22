// Send the server only what it needs (the phone sees everything, the Mac gets the essentials).
//
// The phone runs the detector on every camera frame (60-240 fps). Sending every frame's
// candidates made the Mac's tracker and bounce search the bottleneck (field test 2:
// 120 fps x 3-7 candidates per frame overloaded one Mac core). Two reductions:
//
// 1. Still clutter: a spot of the image that has held a candidate for more than
//    `staticFrac` of the last `staticTauS` seconds (a plant, a sign, a sunlit patch, a ball
//    lying on the court) is not a ball in play. Its candidates are dropped.
// 2. Frame rate: a light tracker follows the remaining candidates. Where a track changes
//    direction or speed abruptly (bounce, paddle hit), the frames from `preS` before to
//    `postS` after go out at the full camera rate (the server's sub-frame bounce timing
//    needs them). Elsewhere one frame per 1/`baseHz` s is sent (enough to keep tracks alive
//    and still detect a bounce if a change was missed, at lower precision).
//
// Frames are held for `holdS` (plus the batching) so the full-rate window can include the
// frames before a change. When unsure the reducer sends more, never less.
// Pure JS (no React Native APIs): unit-tested with node, shared with the browser phone page
// (balltracker/live/static/reducer.js is a copy, checked by tests).

/** @typedef {{seq: number, t: number, c: number[], dense?: boolean}} DetFrame  c = [u, v, r, score, ...] */

export const DEFAULT_REDUCE = Object.freeze({
  enabled: true,
  baseHz: 30,        // frames per second sent outside full-rate windows
  preS: 0.08,        // full rate from this long before the start of the changing stretch
  postS: 0.15,       // ... until this long after its end
  holdS: 0.3,        // frames are held this long before release (so a window can reach back)
  cellPx: 24,        // still-clutter grid cell (pixels)
  staticTauS: 3.0,   // memory of the still-clutter map
  staticFrac: 0.5,   // a cell occupied more than this fraction of the time is still clutter
  minSpeedPxS: 60,   // slower tracks are ignored by the change detector
  minPathPx: 12,     // ... and so are tracks that moved less than this over the 7 points
  maxJitterPx: 1.5,  // each side of a change must be a smooth path (RMS off a straight line)
  turnDeg: 25,       // direction change that counts as a contact
  speedRatio: 1.5,   // speed change (either way) that counts as a contact
  maxTracks: 16,
});

/** RMS distance of points from the straight line through their first and last point. */
function jitter(/** @type {{u: number, v: number}[]} */ p) {
  const a = p[0], b = p[p.length - 1];
  const du = b.u - a.u, dv = b.v - a.v, L = Math.hypot(du, dv);
  if (L < 1e-6) return 0;
  let ss = 0;
  for (const q of p) { const d = ((q.u - a.u) * dv - (q.v - a.v) * du) / L; ss += d * d; }
  return Math.sqrt(ss / p.length);
}

export class Reducer {
  /** @param {Partial<typeof DEFAULT_REDUCE>} [cfg] */
  constructor(cfg) {
    this.cfg = { ...DEFAULT_REDUCE, ...(cfg || {}) };
    /** @type {DetFrame[]} */
    this.buf = [];
    /** @type {Map<number, {h: number, t: number}>} */
    this.heat = new Map();
    /** @type {number | null} */
    this.lastHeatT = null;
    this.lastPrune = -Infinity;
    /** @type {{pts: {t: number, u: number, v: number}[], miss: number}[]} */
    this.tracks = [];
    this.denseUntil = -Infinity;
    this.lastSentT = -Infinity;
    this.stats = { framesIn: 0, framesOut: 0, candsIn: 0, candsStatic: 0, changes: 0 };
  }

  /** @param {Partial<typeof DEFAULT_REDUCE>} cfg */
  configure(cfg) {
    this.cfg = { ...this.cfg, ...(cfg || {}) };
  }

  /**
   * Feed frames in capture order; returns the frames to send now (in order).
   * @param {DetFrame[]} frames
   * @returns {DetFrame[]}
   */
  push(frames) {
    if (!this.cfg.enabled) {
      this.stats.framesIn += frames.length;
      this.stats.framesOut += frames.length;
      return frames;
    }
    for (const f of frames) {
      this.stats.framesIn += 1;
      this.stats.candsIn += f.c.length / 4;
      const c = this._dropStatic(f);
      /** @type {DetFrame} */
      const g = { seq: f.seq, t: f.t, c };
      this.buf.push(g);
      this._track(g);
      if (g.t <= this.denseUntil) g.dense = true;
    }
    const last = this.buf.length ? this.buf[this.buf.length - 1].t : -Infinity;
    return this._release(last - this.cfg.holdS);
  }

  /** Release everything still buffered (stream stopping). */
  flush() {
    return this._release(Infinity);
  }

  /** @param {number} tUpTo */
  _release(tUpTo) {
    const out = [];
    const minGap = 1 / Math.max(this.cfg.baseHz, 0.1);
    while (this.buf.length && this.buf[0].t <= tUpTo) {
      const f = /** @type {DetFrame} */ (this.buf.shift());
      // 0.999: frame times jitter; don't skip a frame that is essentially on the base grid.
      if (f.dense || f.t - this.lastSentT >= 0.999 * minGap) {
        out.push({ seq: f.seq, t: f.t, c: f.c });
        this.lastSentT = f.t;
      }
    }
    this.stats.framesOut += out.length;
    return out;
  }

  /** @param {DetFrame} f */
  _dropStatic(f) {
    const cfg = this.cfg;
    const dt = this.lastHeatT === null ? 0 : Math.max(0, f.t - this.lastHeatT);
    this.lastHeatT = f.t;
    // Per cell: exponentially weighted seconds occupied within the last ~tau, decayed lazily.
    const heatAt = (/** @type {number} */ key) => {
      const e = this.heat.get(key);
      return e ? e.h * Math.exp(-(f.t - e.t) / cfg.staticTauS) : 0;
    };
    const keep = [];
    const seen = new Set();
    for (let i = 0; i + 3 < f.c.length; i += 4) {
      const key = Math.floor(f.c[i] / cfg.cellPx) * 100003 + Math.floor(f.c[i + 1] / cfg.cellPx);
      const h = heatAt(key);
      if (!seen.has(key)) {
        seen.add(key);
        this.heat.set(key, { h: h + dt, t: f.t });
      }
      if (h > cfg.staticFrac * cfg.staticTauS) {
        this.stats.candsStatic += 1;
        continue;
      }
      keep.push(f.c[i], f.c[i + 1], f.c[i + 2], f.c[i + 3]);
    }
    if (f.t - this.lastPrune > 2.0) {  // forget cells that went cold
      this.lastPrune = f.t;
      for (const k of [...this.heat.keys()]) if (heatAt(k) < 0.01) this.heat.delete(k);
    }
    return keep;
  }

  /** @param {DetFrame} f */
  _track(f) {
    const cfg = this.cfg;
    const used = new Set();
    // Greedy association: highest-score candidates first, nearest predicted track within the gate.
    const order = [];
    for (let i = 0; i + 3 < f.c.length; i += 4) order.push(i);
    order.sort((a, b) => f.c[b + 3] - f.c[a + 3]);
    for (const i of order) {
      const u = f.c[i], v = f.c[i + 1];
      let best = -1, bestD = Infinity;
      this.tracks.forEach((tr, k) => {
        if (used.has(k)) return;
        const p = tr.pts[tr.pts.length - 1];
        const dt = f.t - p.t;
        let pu = p.u, pv = p.v, speed = 0;
        if (tr.pts.length >= 2) {
          const q = tr.pts[tr.pts.length - 2];
          const dq = Math.max(p.t - q.t, 1e-4);
          pu += ((p.u - q.u) / dq) * dt;
          pv += ((p.v - q.v) / dq) * dt;
          speed = Math.hypot(p.u - q.u, p.v - q.v) / dq;
        }
        const gate = 40 + 2 * speed * dt;
        const d = Math.hypot(u - pu, v - pv);
        if (d < gate && d < bestD) { best = k; bestD = d; }
      });
      if (best >= 0) {
        used.add(best);
        const tr = this.tracks[best];
        tr.pts.push({ t: f.t, u, v });
        if (tr.pts.length > 12) tr.pts.shift();
        tr.miss = 0;
        this._checkChange(tr);
      } else if (this.tracks.length < cfg.maxTracks) {
        used.add(this.tracks.length);
        this.tracks.push({ pts: [{ t: f.t, u, v }], miss: 0 });
      } else {
        // All slots taken (a busy scene: players, shirts). A track slower than minSpeedPxS is
        // ignored by the change detector anyway: give its slot to the new candidate, which may
        // be the ball (review of defed68: the ball got no track and its bounce went out at base rate).
        const k = this._slowestTrack();
        if (k >= 0) {
          used.add(k);
          this.tracks[k] = { pts: [{ t: f.t, u, v }], miss: 0 };
        }
      }
    }
    this.tracks.forEach((tr, k) => { if (!used.has(k)) tr.miss += 1; });
    this.tracks = this.tracks.filter((tr) => tr.miss <= 6);
  }

  /**
   * Index of the slowest track, if it is too slow for the change detector (speed over its stored
   * points below minSpeedPxS); else -1. It may have been matched in this frame already (higher-
   * scoring clutter is matched first); dropping a slow track's point costs nothing. Fresh tracks
   * (one point) are kept: they have no speed yet.
   */
  _slowestTrack() {
    let best = -1;
    /** @type {number} */
    let bestS = this.cfg.minSpeedPxS;
    this.tracks.forEach((tr, k) => {
      if (tr.pts.length < 2) return;
      const a = tr.pts[0], b = tr.pts[tr.pts.length - 1];
      const s = Math.hypot(b.u - a.u, b.v - a.v) / Math.max(b.t - a.t, 1e-4);
      if (s < bestS) { best = k; bestS = s; }
    });
    return best;
  }

  /** @param {{pts: {t: number, u: number, v: number}[]}} tr */
  _checkChange(tr) {
    const cfg = this.cfg;
    const n = tr.pts.length;
    if (n < 7) return;
    const a = tr.pts[n - 7], m = tr.pts[n - 4], b = tr.pts[n - 1];
    const d1 = Math.max(m.t - a.t, 1e-4), d2 = Math.max(b.t - m.t, 1e-4);
    const v1u = (m.u - a.u) / d1, v1v = (m.v - a.v) / d1;
    const v2u = (b.u - m.u) / d2, v2v = (b.v - m.v) / d2;
    const s1 = Math.hypot(v1u, v1v), s2 = Math.hypot(v2u, v2v);
    if (Math.max(s1, s2) < cfg.minSpeedPxS) return;
    if (Math.hypot(b.u - a.u, b.v - a.v) + Math.hypot(m.u - a.u, m.v - a.v) < cfg.minPathPx) return;
    // Clutter and noise make jagged tracks; a ball in flight is smooth on each side of a contact.
    if (jitter(tr.pts.slice(n - 7, n - 3)) > cfg.maxJitterPx || jitter(tr.pts.slice(n - 4)) > cfg.maxJitterPx) return;
    const cos = (v1u * v2u + v1v * v2v) / Math.max(s1 * s2, 1e-9);
    const turned = s1 > 1e-6 && s2 > 1e-6 && cos < Math.cos((cfg.turnDeg * Math.PI) / 180);
    const ratio = Math.max(s1, s2) / Math.max(Math.min(s1, s2), 1e-6);
    if (turned || ratio > cfg.speedRatio) {
      // Full rate over the whole changing stretch [a, b], widened by preS / postS. Frames still
      // held get marked now; later frames up to denseUntil get marked as they arrive.
      const from = a.t - cfg.preS;
      for (const f of this.buf) if (f.t >= from) f.dense = true;
      this.denseUntil = Math.max(this.denseUntil, b.t + cfg.postS);
      this.stats.changes += 1;
    }
  }
}
