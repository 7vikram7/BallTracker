#!/usr/bin/env python3
"""The headline numbers of a replay: decisions, spoken calls, reports per camera, through the
same path as ``bt replay`` (``live.replay.replay``). Decision log figures cite this command.

    .venv/bin/python scripts/replay_counts.py data/field/20261121-071625
    .venv/bin/python scripts/replay_counts.py data/field/20261121-071625 \\
        --calibrations data/field/20261121-071625/counterfactual/calibrations.jsonl
    add --calls out.json to save every spoken call (t, text, line, distance, cameras)

Works on older checkouts too (without ``--calibrations`` / ``--workers`` support it runs serially).
"""

from __future__ import annotations

import argparse
import collections
import inspect
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from balltracker.live.replay import replay  # noqa: E402


def environment() -> str:
    """The libraries a replay's numbers depend on: two environments have differed by one report
    in a 68-minute session (decision log 33), so every count is printed with this line."""
    import platform

    import cv2
    import numpy
    import scipy

    return (f"python {platform.python_version()} numpy {numpy.__version__} scipy {scipy.__version__} "
            f"opencv {cv2.__version__} {platform.machine()} {platform.system()} {platform.release()}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("session")
    ap.add_argument("--calibrations")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--calls", help="write the spoken calls here (JSON)")
    a = ap.parse_args()
    params = inspect.signature(replay).parameters
    kw = {}
    if a.calibrations:
        if "calibrations" not in params:
            raise SystemExit("this checkout's replay() has no calibrations option")
        kw["calibrations"] = a.calibrations
    if "workers" in params:
        kw["workers"] = a.workers
    t0 = time.time()
    res = replay(a.session, **kw)
    D = res["decisions"]
    spoken = [d for d in D if d.get("announce")]
    root = Path(__file__).resolve().parents[1]
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=root).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no", "--", "balltracker"],
                           capture_output=True, text=True, cwd=root).stdout.strip()
    commit += " + uncommitted changes in balltracker/" if dirty else ""
    print(f"code {commit}  session {a.session}  calibrations {a.calibrations or 'as recorded'}")
    print(f"environment {environment()}")
    print(f"decisions {len(D)}  spoken {len(spoken)} {dict(collections.Counter(d.get('text') for d in spoken))}  "
          f"reports {{{', '.join(f'{n}: {c.get('reports')}' for n, c in res['cameras'].items())}}}  "
          f"({(time.time() - t0) / 60:.0f} min)")
    if a.calls:
        Path(a.calls).write_text(json.dumps([{k: d.get(k) for k in ("t", "text", "line", "distance_cm", "cameras", "p_out")}
                                             for d in spoken], indent=1, default=str))


if __name__ == "__main__":
    main()
