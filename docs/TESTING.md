# Tests: what protects what

Run everything: `.venv/bin/python -m pytest -q` (about 8 min; includes the app's Node tests).
The slow end-to-end tests run in real time (simulated phones streaming to a live server): run them
on a quiet Mac. A big background job (e.g. a Homebrew source build) makes them fail on latency and drops.

Quick loop while editing: `.venv/bin/python -m pytest -q -m "not slow"` (under 1 min).

| Layer | Where | Catches |
|---|---|---|
| Unit | `tests/test_*.py`, `mobile/test/core.test.js` | geometry, tracking, bounce physics, fusion, judge rules, clock sync, wire format, app client/session logic |
| **Golden** | `tests/test_golden.py` + `tests/golden/` | **any** change in what the system decides from fixed inputs: a frozen app-phone rally (2 cameras, 8 bounces) must give the same calls, positions (±1 mm), p(out) (±0.01); the phone detector must give the same candidates (Python and C++); detection messages must have the same bytes (Python and JS) |
| Parity | `tests/test_edge.py` | C++ detector == Python reference (BGR, BGRA, RGBA), ROI; the WebAssembly build (browser) == reference |
| Browser | `tests/test_browser_edge.py` (slow, needs Chrome) | real phone page in headless Chrome with a fake camera playing a synthetic rally: WebAssembly detection in a Web Worker -> server -> calls |
| End to end | `test_live.py`, `test_edge.py`, `test_session_tools.py` (slow) | real server + simulated phones (browser, app in Python, app's own JS): accuracy, latency, clock sync, no wrong OUT, logging, replay, report |

| Lob / play state | `tests/test_playstate.py` | dead ball vs moonball, lob off a volley, toss-back not announced, rally window for lobs, cameras combined by covariance |
| Calibration | `tests/test_autocal.py`, `tests/test_crosscal.py` | "Snap to lines" from bad taps, nonsense taps refused; re-snap of a drifted calibration; shared-bounce refinement (bumped camera, few noisy clicks), no proposal when cameras agree |
| Practice court | `tests/test_court_scale.py` | `--court-scale`: lines scale, ball does not; play thresholds scale; separate calibration folder |

## Studies (not run by pytest)

* `scripts/lob_study.py`: lobs (and drives) through the whole pipeline on mock data: four corner
  cameras, gravity + drag + bounce physics, detections projected with noise and frame edges,
  real replay, and again after the phone-side reducer. About 5 min. Results: docs/LOB_STUDY.md.
* `scripts/reduce_dets.mjs in.jsonl out.jsonl`: run the app's reducer over a recorded `dets.jsonl`
  (what the phone would have sent); replay the result to see what reduction costs.

## Auto-commit

A full passing run (`pytest` with no file / `-k` / `-m` selection) leaves `.bt_tests_ok`, a
fingerprint of the tested working tree. At the end of each Claude Code response the Stop hook
(`scripts/hooks/autocommit.py`) commits and pushes if the tree is still exactly that one. Off:
`BT_AUTOCOMMIT=0`.

## When a golden test fails

It means decisions changed. If that was **not** intended, it's a regression: fix it.
If it **was** intended (a tuned threshold, a better fit):

```bash
.venv/bin/python tests/golden/make_golden.py --only expected   # re-judge the frozen rally with the new code
git diff tests/golden/edge_rally/expected.json                 # read what changed, call by call
```

The accuracy test against synthetic truth (`test_frozen_rally_accuracy_against_truth`) must
still pass. Commit the new fixture together with the code change, saying why the calls moved.
The full `make_golden.py` (no `--only`) re-records the rally too; only do that if the inputs
themselves should change (e.g. a new protocol field).

## Real sessions as regression tests

Every recorded field session can be re-run with new code: `bt replay <session>` lists
calls that changed, moved, appeared or disappeared, and saves the comparison in
`<session>/replays/`. A good field session (with its marks sheet) can be promoted to a golden
fixture by copying its `dets.jsonl`, `calibration/` and `court.json` like `tests/golden/edge_rally`.

## Rebuilding the browser detector

`balltracker/live/static/ballcore.wasm` is built from the shared C++ (`mobile/modules/ball-camera/cpp/`)
and committed, so the server works without a compiler. After changing the C++:

```bash
scripts/build_wasm.sh        # needs wasi-sdk in ~/.local/toolchains (or set WASI_SDK)
.venv/bin/python -m pytest -q tests/test_edge.py -k wasm
```

## Added after field test 2 (2026-11-19)

| Test | What it guards |
|---|---|
| `tests/test_playstate.py` | Play state: rallies called, second bounces / dead balls / slow tosses silent, feeding drills still called. |
| `tests/test_samples.py` (slow) | Replays 60 s of real field data (`data/samples/fieldtest2_60s`): every judged bounce has a play label; no announced OUT from a lone imprecise camera or a dead ball. |
| `tests/test_autocal.py` | Experimental auto-calibration on synthetic courts (snap from 4 rough clicks < 4 px; full auto up to the A/B ambiguity). |
| `mobile/test/reducer.test.js` | Phone-side reduction: full rate around a bounce, base rate elsewhere, still clutter dropped, pass-through when off. |
| `tests/test_edge.py::test_browser_reducer_is_the_app_reducer` | The browser copy of the reducer equals the app's. |
| `tests/test_edge.py::test_app_javascript_core_against_live_server` (slow) | The app's JS (now with the reducer) against the real server: every bounce called, < 2 cm median. |
