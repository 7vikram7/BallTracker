"""Python binding (ctypes) for the app's C++ detector, for tests and benchmarks.

The C++ source lives with the app: mobile/modules/ball-camera/cpp/ballcore.{h,cpp}.
``load()`` compiles it with the system C++ compiler into a cache folder the
first time (no build system needed) and returns a ``NativeDetector`` factory.
"""

from __future__ import annotations

import ctypes as C
import hashlib
import shutil
import subprocess
from pathlib import Path

import numpy as np

from .detection import Candidate
from .edge_detection import EdgeDetectorConfig

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "mobile" / "modules" / "ball-camera" / "cpp"
FMT = {"BGRA": 0, "RGBA": 1, "BGR": 2, "RGB": 3}


class BcConfig(C.Structure):
    _fields_ = [
        ("bin", C.c_int), ("hsv_low", C.c_int * 3), ("hsv_high", C.c_int * 3),
        ("var_threshold", C.c_float), ("var_init", C.c_float), ("var_min", C.c_float), ("var_max", C.c_float),
        ("bg_history_s", C.c_double), ("bg_update_hz", C.c_double), ("fps", C.c_double),
        ("min_radius_px", C.c_double), ("max_radius_px", C.c_double), ("max_elongation", C.c_double),
        ("max_candidates", C.c_int), ("flicker_compensation", C.c_int), ("flicker_alpha", C.c_double),
    ]


class BcCandidate(C.Structure):
    _fields_ = [("u", C.c_float), ("v", C.c_float), ("radius_px", C.c_float), ("score", C.c_float),
                ("area_px", C.c_float), ("elongation", C.c_float)]


_lib = None


def build(out_dir: Path | None = None) -> Path:
    """Compile ballcore.cpp into a shared library (cached by source hash)."""
    cxx = shutil.which("clang++") or shutil.which("c++") or shutil.which("g++")
    if cxx is None:
        raise RuntimeError("no C++ compiler found")
    srcs = [SRC / "ballcore.cpp", SRC / "ballcore.h"]
    h = hashlib.sha1(b"".join(p.read_bytes() for p in srcs)).hexdigest()[:12]
    out_dir = out_dir or ROOT / "build" / "ballcore"
    out_dir.mkdir(parents=True, exist_ok=True)
    lib = out_dir / f"libballcore_{h}.so"
    if not lib.exists():
        cmd = [cxx, "-std=c++17", "-O2", "-ffp-contract=off", "-fPIC", "-shared", "-Wall", "-Wextra",
               "-o", str(lib), str(SRC / "ballcore.cpp")]
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    return lib


def load():
    global _lib
    if _lib is None:
        lib = C.CDLL(str(build()))
        lib.bc_create.restype = C.c_void_p
        lib.bc_create.argtypes = [C.POINTER(BcConfig)]
        lib.bc_destroy.argtypes = [C.c_void_p]
        lib.bc_reset.argtypes = [C.c_void_p]
        lib.bc_default_config.argtypes = [C.POINTER(BcConfig)]
        lib.bc_set_roi.argtypes = [C.c_void_p, C.c_void_p, C.c_int, C.c_int, C.c_int]
        lib.bc_detect.restype = C.c_int
        lib.bc_detect.argtypes = [C.c_void_p, C.c_void_p, C.c_int, C.c_int, C.c_int, C.c_int,
                                  C.POINTER(BcCandidate), C.c_int]
        lib.bc_last_detect_us.restype = C.c_double
        lib.bc_last_detect_us.argtypes = [C.c_void_p]
        _lib = lib
    return _lib


def to_bc_config(cfg: EdgeDetectorConfig) -> BcConfig:
    b = BcConfig()
    b.bin = cfg.bin
    b.hsv_low[:] = list(cfg.hsv_low)
    b.hsv_high[:] = list(cfg.hsv_high)
    b.var_threshold, b.var_init, b.var_min, b.var_max = cfg.var_threshold, cfg.var_init, cfg.var_min, cfg.var_max
    b.bg_history_s, b.bg_update_hz, b.fps = cfg.bg_history_s, cfg.bg_update_hz, cfg.fps
    b.min_radius_px, b.max_radius_px, b.max_elongation = cfg.min_radius_px, cfg.max_radius_px, cfg.max_elongation
    b.max_candidates = cfg.max_candidates
    b.flicker_compensation = int(cfg.flicker_compensation)
    b.flicker_alpha = cfg.flicker_alpha
    return b


class NativeDetector:
    """Same interface as EdgeBallDetector, backed by the C++ code."""

    name = "edge_color_motion(native)"

    def __init__(self, cfg: EdgeDetectorConfig | None = None, fmt: str = "BGR"):
        self.cfg = cfg or EdgeDetectorConfig()
        self.lib = load()
        self._bc = to_bc_config(self.cfg)
        self.h = self.lib.bc_create(C.byref(self._bc))
        self.fmt = FMT[fmt]
        self._out = (BcCandidate * 64)()
        if self.cfg.roi_mask is not None:
            m = np.ascontiguousarray(self.cfg.roi_mask, np.uint8)
            self.lib.bc_set_roi(self.h, m.ctypes.data, m.shape[1], m.shape[0], m.strides[0])

    def __del__(self):
        if getattr(self, "h", None):
            self.lib.bc_destroy(self.h)
            self.h = None

    @property
    def last_us(self) -> float:
        return self.lib.bc_last_detect_us(self.h)

    def detect(self, image: np.ndarray) -> list[Candidate]:
        img = np.ascontiguousarray(image)
        h, w = img.shape[:2]
        n = self.lib.bc_detect(self.h, img.ctypes.data, w, h, img.strides[0], self.fmt, self._out, 64)
        if n < 0:
            raise ValueError("bc_detect rejected the arguments")
        return [Candidate(u=o.u, v=o.v, radius_px=o.radius_px, score=o.score, area_px=o.area_px, elongation=o.elongation)
                for o in self._out[:n]]
