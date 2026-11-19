# Lobs: what happens at every stage (mock-data study, 2026-11-19)

How a lob travels through the whole pipeline, what went wrong, and what was changed. All
numbers come from `scripts/lob_study.py` (re-run it to reproduce: about 5 min).

## Setup

* Full-size court, **four corner cameras** on 2.4 m tripods, 1.5 m outside the sidelines and 3 m
  behind the baselines, 1920x1080, aimed so the whole court fits (that needed an 80° lens: the
  main 1x lens could not fit the court from there). Two cameras at 120 fps, two at 60 fps.
  Each camera calibrated from noisy clicks (1.5 px), like the dashboard.
* Ball flight with gravity, air drag (an outdoor ball's drag is ~half of gravity at lob
  landing speeds) and bounce physics (restitution 0.62, friction 0.82).
* Detections: the ball projected into each camera with 0.4 px noise, 2 % dropouts, and **not
  detected outside the frame** (lobs leave the top of every frame).
* Shots from side A landing near baseline B at 6 offsets (-30, -10, -3, +3, +10, +30 cm) and near
  a sideline:

  | shot | flight | apex | landing angle | horizontal speed at landing |
  |---|---|---|---|---|
  | drive | 0.9 s | ~1.5 m | 14-22° | 11-14 m/s |
  | offensive lob | 1.55 s | ~3 m | ~53° | ~5 m/s |
  | defensive lob | 2.2 s | ~6 m | ~67° | ~3.7 m/s |
  | moonball | 2.7 s | ~9 m | ~75° | ~2.6 m/s |

* Each shot played two ways: **rally** (the incoming ball bounced on side A 0.35 s before the
  lob) and **volley** (no bounce for many seconds before: hit out of the air after a volley
  exchange). The ball is not returned, so it bounces again (2nd, 3rd...).
* The real pipeline: `bt replay` path (tracking → bounce detection + physics check → fusion →
  play state → line call), then again after the phone-side reducer (`scripts/reduce_dets.mjs`).

## Stage by stage

**1. In the frame.** From a 2.4 m tripod the top of the frame is only ~1 m above the court at
mid-distance, so every lob is out of view for most of its flight and comes back steeply 0.2-1 s
before landing. That is enough: bounce detection uses ±0.06 s around the contact and the physics
check ±0.15 s. *Not simulated:* a ball against a bright sky or roof lights, which the colour
detector may lose; the real check is a mini-court or court session (toss it high).

**2. Tracking.** The ball re-enters at the top falling fast (up to ~25 px per frame at 60 fps);
tracks start reliably. No change needed.

**3. Phone-side reducer.** It keeps ~30-40 % of frames at 120 fps (55 % at 60 fps). The steep
descent and bounce are a clear direction change, so the frames around the contact are kept in
full. Lob calls with the reducer were the same as without it, within one borderline case.

**4. Bounce detection + physics check: this was broken for lobs.**
One camera measures the ball's velocity across its view very precisely (2-8 cm/s) but along its
line of sight badly (median error 1.3-2.3 m/s, 10 % worse than 5-11 m/s). The physics checks
("did the direction turn more than 60°?", "did the horizontal speed change too much?") used
those numbers as if exact. Lobs land slowly horizontally, so an error of 2 m/s turned their
direction randomly, and **cameras rejected true lob bounces** ("direction changed too much",
"implausible horizontal speed change": 200+ rejected reports in the full study). The bounce was
usually still found by another camera, but with 2 cameras instead of 4 that becomes missed bounces
and single-camera (silent) calls.
*Fix:* the physics fit now returns the velocity's covariance; turn and speed change reject only
when out of range by more than 2 standard deviations of that camera's measurement. The
restitution check (rise speed / fall speed) stays strict: every true bounce had 0.19-0.80 from
every camera, while paddle hits had 1.5-12, and relaxing it let paddle hits through as
"bounces" in a first attempt.

**5. Position accuracy.** Lobs land steeply and slowly, so timing errors barely move the contact
point: median error 0.8-1.1 cm, the same as drives. Not a problem.

**6. Fusion.** Unchanged; 2+ cameras agreed on every lob bounce.

**7. Play state: this was the main reason OUT lobs were silent.**
* *Speed came from one camera.* The "dead ball" (< 2 m/s) and "shot" (≥ 5 m/s) rules used the
  horizontal speed of the best-fitting camera: off by up to 12 m/s. A moonball (2.6 m/s) was
  sometimes a "dead ball", an offensive lob (5 m/s) a "not clearly a shot". *Fix:* all cameras
  are combined by their covariances; the combined speed matched the truth within ~0.1 m/s.
* *Lobs are slow but fall fast.* A moonball lands at 2.6 m/s horizontally but falls at 10+ m/s;
  a ball dropped by hand falls at < 7 m/s. *Fix:* "dead ball" also needs a slow fall (< 7 m/s); a
  ball falling ≥ 8 m/s (apex above ~4 m) counts as a shot at the start of play.
* *Rally window.* Bounces on alternating halves within 4 s made a rally; a lob after a volley
  exchange can take longer. *Fix:* the window grows with the incoming ball's flight time
  (estimated from its fall speed), up to 7 s.
* *Second bounce.* Prediction from the outgoing velocity works for lobs; all detected second and
  later bounces were suppressed.

**8. Line call.** Lobs OUT by 3 cm come out UNCERTAIN (silent): with 1-2 cm of measurement error,
p(out) does not reach the 95 % bar. That is the intended caution and is the same for drives.

## Results (full study, 54 scenarios, 4 cameras, all frames sent)

Before = the code at commit a7f2cc5 (this morning); after = now. Same scenarios, same noise.

| | before | after |
|---|---|---|
| lob first bounces found | 42/42 | 42/42 |
| median position error (lobs) | 0.8-1.1 cm | 0.8-1.1 cm |
| **OUT lobs announced** | **11/21** | **19/21** (the 2 silent ones are 3 cm out: UNCERTAIN by design) |
| OUT drives announced | 4/6 | 4/6 (same: the 3 cm cases) |
| wrong OUT calls | 0 | 0 |
| horizontal speed used by the play state (moonball, true 2.6 m/s) | 2.2-2.4 m/s, single camera, errors up to 12 m/s elsewhere | 2.7 m/s |
| lob labelled "dead ball" or "not clearly a shot" | 16 of 42 | 1 of 42 (an offensive lob off a volley, 5.0 m/s, at the shot threshold) |
| second / later bounces found, all suppressed | 22 / not counted | 38 / 10 |
| false decisions (none announced in either) | 3 | 0 |

With the phone-side reducer (30-60 % of frames sent) the results were the same within one case
(one more OUT drive and one more OUT moonball announced).

## Remaining risks and what to check on court

* **Bright background.** A ball against the sky/roof lights may not be detected: toss lobs on the
  mini court and at the next session and check the tracks on the dashboard.
* **Toss-backs.** A ball tossed back to the server with an apex above ~4 m, landing outside a
  line at the start of a point, would now be announced. Rare, but if it happens, raise
  `PlayConfig.lob_vz_mps`.
* **Two cameras only.** With fewer cameras, each camera's own physics check matters more; the
  covariance-aware checks are the reason true lob bounces survive.
* **Camera placement.** From a tripod behind the baseline, a lob landing near that baseline can
  leave the bottom of the frame right after the bounce. Keep 1-2 m of court-surround visible
  behind each baseline.
