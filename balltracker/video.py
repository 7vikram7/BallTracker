"""Video sources that yield frames with timestamps.

``FrameSource`` is the seam between video acquisition and everything else:
recorded files today; live phone streams and edge-metadata later.

Timestamps come from the container's presentation timestamps (PTS), not from
frame_index / fps, so variable-frame-rate phone recordings are timed correctly.

iPhone slo-mo note: share the clip as the *original* file (AirDrop with
"All Photos Data", or Image Capture). Re-exported slo-mo clips are often
re-timed to 30 fps playback, which destroys the real capture timing.

Rotation: phones store portrait video as landscape pixels plus a display
rotation. Frames are rotated upright by default (``autorotate``), so image
"down" is roughly gravity and matches what you see when you play the clip.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Protocol

import av
import numpy as np


@dataclass(frozen=True)
class Frame:
    index: int
    t: float  # seconds from start of source (session clock for single-camera)
    image: np.ndarray  # HxWx3 BGR uint8


@dataclass(frozen=True)
class SourceInfo:
    path: str
    width: int
    height: int
    fps: float  # nominal capture rate
    frame_count: int | None
    duration_s: float | None
    codec: str


class FrameSource(Protocol):
    info: SourceInfo

    def frames(self, start_s: float = 0.0, end_s: float | None = None) -> Iterator[Frame]: ...


class VideoFileSource:
    """Decode a video file with PyAV (FFmpeg)."""

    def __init__(self, path: str | Path, fps_override: float | None = None, autorotate: bool = True):
        self.path = str(path)
        if not Path(self.path).exists():
            raise FileNotFoundError(self.path)
        self.fps_override = fps_override
        with av.open(self.path) as c:
            s = c.streams.video[0]
            fps = float(s.average_rate) if s.average_rate else float(s.guessed_rate or 30)
            dur = float(s.duration * s.time_base) if s.duration else (c.duration / 1e6 if c.duration else None)
            rot = 0
            if autorotate:
                try:
                    rot = int(round(float(next(c.decode(s)).rotation or 0))) % 360
                except (StopIteration, AttributeError, TypeError, ValueError):
                    rot = 0
            # Display rotation is counter-clockwise degrees: np.rot90 k counts CCW quarter turns.
            self._rot_k = (rot // 90) % 4 if rot % 90 == 0 else 0
            w0, h0 = s.codec_context.width, s.codec_context.height
            if self._rot_k % 2:
                w0, h0 = h0, w0
            self.rotation_deg = self._rot_k * 90
            self.info = SourceInfo(
                path=self.path,
                width=w0,
                height=h0,
                fps=fps_override or fps,
                frame_count=s.frames or None,
                duration_s=dur,
                codec=s.codec_context.name,
            )

    def frames(self, start_s: float = 0.0, end_s: float | None = None) -> Iterator[Frame]:
        with av.open(self.path) as c:
            s = c.streams.video[0]
            s.thread_type = "AUTO"
            t0: float | None = None
            idx = 0
            for frame in c.decode(s):
                if self.fps_override:
                    t = idx / self.fps_override
                else:
                    if frame.pts is None:
                        t = idx / self.info.fps
                    else:
                        tt = float(frame.pts * s.time_base)
                        if t0 is None:
                            t0 = tt
                        t = tt - t0
                if t < start_s:
                    idx += 1
                    continue
                if end_s is not None and t > end_s:
                    break
                img = frame.to_ndarray(format="bgr24")
                if self._rot_k:
                    img = np.ascontiguousarray(np.rot90(img, self._rot_k))
                yield Frame(index=idx, t=t, image=img)
                idx += 1


def write_video(path: str | Path, frames: Iterator[np.ndarray], fps: float, size: tuple[int, int]) -> None:
    """Write BGR frames to an H.264 MP4 (falls back to MPEG-4 Part 2)."""
    w, h = size
    with av.open(str(path), mode="w") as c:
        try:
            s = c.add_stream("libx264", rate=round(fps))
            s.options = {"crf": "18", "preset": "veryfast"}
        except Exception:  # pragma: no cover - codec availability varies
            s = c.add_stream("mpeg4", rate=round(fps))
            s.bit_rate = 20_000_000
        s.width, s.height, s.pix_fmt = w, h, "yuv420p"
        for img in frames:
            vf = av.VideoFrame.from_ndarray(img, format="bgr24")
            for pkt in s.encode(vf):
                c.mux(pkt)
        for pkt in s.encode():
            c.mux(pkt)
