# Sample data

Small, real recordings that ship with the repository so the tests and tools run on any
clone. Full sessions stay in `data/live/sessions/` (not committed: ~1 GB per hour).

| Folder | What |
|---|---|
| `fieldtest2_60s/` | 60 s (session time 1190-1250 s) of field test 2 (2026-11-19, full-size indoor court, 2 app phones: iPhone 17 at 120 fps, Samsung at ~40-55 fps). Per-frame on-phone detections (`dets.jsonl`), events, the calibrations used live (net-top points included: ~9 px RMS). No camera images (they show people). |

Make more with `python scripts/slice_session.py <session> <out> --from <s> --to <s> --previews 0`;
`bt replay <folder>` re-runs any of them with the current code.
