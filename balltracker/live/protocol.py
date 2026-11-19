"""Wire format between phone (or fake phone) and server.

WebSocket text messages are JSON objects with a ``type``:

  phone -> server   {"type": "hello", "name": "baseline-left", "device": "...",
                     "width": 1280, "height": 720, "fps": 60, "ts_source": "...", "proto": 1}
  server -> phone   {"type": "welcome", "name": ..., "calibrated": bool}
  server -> phone   {"type": "ping", "id": 7, "ts": <server clock>}
  phone -> server   {"type": "pong", "id": 7, "tp": <phone clock, seconds>}
  phone -> server   {"type": "stats", ...}            (optional, informational)
  server -> phone   {"type": "status", ...}           (processing fps, calibrated, ...)
  server -> phone   {"type": "call", "text": "OUT"}   (so the phone can flash it)

WebSocket binary messages are frames: a 20-byte little-endian header followed
by one JPEG image.

  offset  size  field
  0       4     magic b"BTF1"
  4       4     uint32 frame sequence number
  8       8     float64 capture time on the phone clock (seconds)
  16      2     uint16 width
  18      2     uint16 height
  20      ...   JPEG bytes

Protocol 2 adds the native app ("edge" camera), which processes frames on the
phone. Its hello carries ``"mode": "edge"`` and ``"proto": 2``; the server
answers with ``{"type": "config", "detector": {...}}`` (EdgeDetectorConfig
fields) and, when the camera is calibrated, ``{"type": "calibration", ...}``.
Edge phones send two more binary messages:

Detections ("BTD1"), batched (the app sends one about every 50 ms)::

  header   10 bytes  magic b"BTD1", uint16 width, uint16 height, uint16 n_frames
  frame    14 bytes  uint32 seq, float64 t_phone, uint8 n_cands, uint8 flags (0)
  cand     16 bytes  float32 u, v, radius_px, score         (n_cands of them)

A frame with no candidates is still sent (n_cands = 0): it tells the server the
camera was watching at that moment.

Preview ("BTP1"): same 20-byte header as a frame, then a JPEG. The server
shows it on the dashboard and uses it for calibration, but doesn't run the
detector on it. It must be full detection resolution.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass

PROTO_VERSION = 2
FRAME_MAGIC = b"BTF1"
PREVIEW_MAGIC = b"BTP1"
DETS_MAGIC = b"BTD1"
_HDR = struct.Struct("<4sIdHH")
HEADER_SIZE = _HDR.size  # 20


@dataclass(frozen=True)
class FrameMsg:
    seq: int
    t_phone: float
    width: int
    height: int
    jpeg: bytes


def pack_frame(seq: int, t_phone: float, width: int, height: int, jpeg: bytes) -> bytes:
    return _HDR.pack(FRAME_MAGIC, seq & 0xFFFFFFFF, t_phone, width, height) + jpeg


def unpack_frame(buf: bytes, magic_expected: bytes = FRAME_MAGIC) -> FrameMsg:
    if len(buf) < HEADER_SIZE:
        raise ValueError("frame message too short")
    magic, seq, t, w, h = _HDR.unpack_from(buf, 0)
    if magic != magic_expected:
        raise ValueError(f"bad frame magic {magic!r}")
    return FrameMsg(seq, t, w, h, bytes(buf[HEADER_SIZE:]))


def pack_preview(seq: int, t_phone: float, width: int, height: int, jpeg: bytes) -> bytes:
    return _HDR.pack(PREVIEW_MAGIC, seq & 0xFFFFFFFF, t_phone, width, height) + jpeg


# --- detections (protocol 2) -------------------------------------------------
_DHDR = struct.Struct("<4sHHH")
_DFRM = struct.Struct("<IdBB")
_DCND = struct.Struct("<ffff")


@dataclass(frozen=True)
class DetFrame:
    seq: int
    t_phone: float
    cands: list[tuple[float, float, float, float]]  # (u, v, radius_px, score)


@dataclass(frozen=True)
class DetBatch:
    width: int
    height: int
    frames: list[DetFrame]


def pack_detections(width: int, height: int, frames: list[DetFrame]) -> bytes:
    parts = [_DHDR.pack(DETS_MAGIC, width, height, len(frames))]
    for f in frames:
        cands = f.cands[:255]
        parts.append(_DFRM.pack(f.seq & 0xFFFFFFFF, f.t_phone, len(cands), 0))
        parts += [_DCND.pack(*c) for c in cands]
    return b"".join(parts)


def unpack_detections(buf: bytes) -> DetBatch:
    if len(buf) < _DHDR.size:
        raise ValueError("detections message too short")
    magic, w, h, n = _DHDR.unpack_from(buf, 0)
    if magic != DETS_MAGIC:
        raise ValueError(f"bad detections magic {magic!r}")
    off, frames = _DHDR.size, []
    for _ in range(n):
        if off + _DFRM.size > len(buf):
            raise ValueError("truncated detections message")
        seq, t, nc, _flags = _DFRM.unpack_from(buf, off)
        off += _DFRM.size
        if off + nc * _DCND.size > len(buf):
            raise ValueError("truncated detections message")
        cands = [_DCND.unpack_from(buf, off + i * _DCND.size) for i in range(nc)]
        off += nc * _DCND.size
        frames.append(DetFrame(seq, t, cands))
    return DetBatch(w, h, frames)


def magic_of(buf: bytes) -> bytes:
    return bytes(buf[:4])
