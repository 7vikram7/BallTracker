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
