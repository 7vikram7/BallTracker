# Counterfactual calibration history, field test 3

`calibrations.jsonl` holds 24 `calibrated` events: what the server's calibration upkeep would
have used during this session, in place of the calibrations actually made. The upkeep is the
auto line snap at each calibration, the re-snap of the other cameras, and drift tracking every
10 s. Each event has the camera model, the points and the source:
- 3 × clicks + lines (auto);
- 3 × lines (auto, after another camera);
- 18 × drift.

The cameras in the session as recorded had rough, drifting calibrations. The Samsung's was
6.9 px RMS and isn't used for calls. This file answers "what would the newer server have
called with the same detections?".

- **Produced by** `scripts/counterfactual_calibration.py` from the local session folder, which
  includes the preview snapshots. They show people and are not committed. It used the code of
  commit 22aef8d, whose drift tracking was a similarity transform; it has been a homography since
  ee648f1, so a fresh run gives a somewhat different history.
- **Names** are scrubbed to the export's camera names (`iphone17`, `nothing`, `samsung`).
- **Use:**

```bash
bt replay data/field/20261121-071625 --calibrations data/field/20261121-071625/counterfactual/calibrations.jsonl --workers 3
.venv/bin/python scripts/replay_counts.py data/field/20261121-071625 --calibrations data/field/20261121-071625/counterfactual/calibrations.jsonl
```

There is no ground truth for this session, so the counts measure change, not accuracy.
