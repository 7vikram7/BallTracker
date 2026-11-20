"""Court model: dimensions, line geometry, named keypoints and regions.

Coordinate system (the "court frame"), used everywhere in the project:

* Origin: centre of the net, on the playing surface.
* +X: across the court, to the right when standing behind the side-A baseline
  looking at the net.
* +Y: along the court, from side A towards side B (side A is y < 0).
* +Z: up, away from the playing surface.
* Units: metres.

All dimensions follow the pickleball convention that court dimensions are
measured to the OUTSIDE edge of the boundary lines, and lines belong to the area
they bound (except the non-volley/kitchen line, which belongs to the kitchen,
which matters on a serve).

The model is sport-agnostic in shape (a rectangle with optional zones) but the
default values are pickleball. A scaled-down practice court is created with
``CourtSpec.scaled(factor)`` or by passing explicit dimensions, which lets the
same pipeline run on a taped indoor floor and a real hard court.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

import numpy as np
import yaml

FT = 0.3048
INCH = 0.0254


class Side(str, Enum):
    A = "A"  # y < 0
    B = "B"  # y > 0

    @property
    def other(self) -> "Side":
        return Side.B if self is Side.A else Side.A

    @property
    def sign(self) -> float:
        return -1.0 if self is Side.A else 1.0


class ServiceSide(str, Enum):
    """Which half of the court the server stands in, from the server's view."""

    RIGHT = "right"
    LEFT = "left"


@dataclass(frozen=True)
class Rect:
    """Axis-aligned rectangle in court coordinates (metres)."""

    x0: float
    x1: float
    y0: float
    y1: float

    def __post_init__(self) -> None:
        if self.x1 < self.x0 or self.y1 < self.y0:
            raise ValueError(f"Degenerate rect {self}")

    def contains(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        return (x >= self.x0) & (x <= self.x1) & (y >= self.y0) & (y <= self.y1)

    def distance_outside(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Euclidean distance from points to the rectangle (0 inside)."""
        dx = np.maximum(np.maximum(self.x0 - x, 0.0), x - self.x1)
        dy = np.maximum(np.maximum(self.y0 - y, 0.0), y - self.y1)
        return np.hypot(dx, dy)

    def signed_distance(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Positive outside, negative inside (distance to nearest edge)."""
        outside = self.distance_outside(x, y)
        inside = np.minimum.reduce(
            [np.asarray(x - self.x0), np.asarray(self.x1 - x), np.asarray(y - self.y0), np.asarray(self.y1 - y)]
        )
        return np.where(outside > 0, outside, -np.maximum(inside, 0.0))


@dataclass(frozen=True)
class LineSegment:
    name: str
    # Rectangle covering the painted/taped line, in court coordinates.
    rect: Rect


@dataclass(frozen=True)
class CourtSpec:
    """Physical description of a rectangular net court.

    Defaults are a regulation pickleball court.
    """

    name: str = "pickleball"
    width: float = 20 * FT  # sideline to sideline, outside edges
    length: float = 44 * FT  # baseline to baseline, outside edges
    kitchen_depth: float = 7 * FT  # net to OUTSIDE (far-from-net) edge of kitchen line
    line_width: float = 2 * INCH
    net_height_sideline: float = 36 * INCH
    net_height_center: float = 34 * INCH
    net_post_offset: float = 12 * INCH  # posts outside the sidelines
    ball_radius: float = 0.0371  # ~2.92 in diameter (USA Pickleball: 2.87-2.97 in)
    # Radius of the ball's contact patch at bounce. The ball is IN if any part of
    # the contact patch touches the line. This is an ASSUMPTION to be measured with
    # the chalk drill (see docs/RECORDING_GUIDE.md); 0 means "centre of contact".
    contact_patch_radius: float = 0.010
    scale: float = 1.0
    extra: dict = field(default_factory=dict, compare=False, hash=False)

    # ------------------------------------------------------------------ build
    @classmethod
    def pickleball(cls) -> "CourtSpec":
        return cls()

    def scaled(self, factor: float, *, scale_ball: bool = False, scale_lines: bool = False) -> "CourtSpec":
        """A geometrically scaled court, e.g. 0.5 for a half-size taped floor.

        By default the ball and line width are NOT scaled, because a practice
        court usually uses a real ball and ordinary tape.
        """
        if factor <= 0:
            raise ValueError("scale factor must be positive")
        return CourtSpec(
            name=f"{self.name}_x{factor:g}",
            width=self.width * factor,
            length=self.length * factor,
            kitchen_depth=self.kitchen_depth * factor,
            line_width=self.line_width * (factor if scale_lines else 1.0),
            net_height_sideline=self.net_height_sideline * factor,
            net_height_center=self.net_height_center * factor,
            net_post_offset=self.net_post_offset * factor,
            ball_radius=self.ball_radius * (factor if scale_ball else 1.0),
            contact_patch_radius=self.contact_patch_radius * (factor if scale_ball else 1.0),
            scale=self.scale * factor,
        )

    @classmethod
    def from_dict(cls, d: dict) -> "CourtSpec":
        d = dict(d)
        base_name = d.pop("base", "pickleball")
        if base_name != "pickleball":
            raise ValueError(f"Unknown court base '{base_name}'")
        factor = d.pop("scale", None)
        units = d.pop("units", "m")
        conv = {"m": 1.0, "cm": 0.01, "ft": FT, "in": INCH}[units]
        for k in list(d):
            if k not in ("name",) and isinstance(d[k], (int, float)):
                d[k] = float(d[k]) * conv
        spec = cls(**d) if d else cls()
        if factor is not None:
            if "width" in d or "length" in d:
                # Explicit dimensions are final (to_dict writes the scaled sizes plus the factor);
                # scaling them again shrank every saved mini court a second time on replay.
                spec = dataclasses.replace(spec, scale=float(factor))
            else:
                spec = spec.scaled(float(factor))
        return spec

    @classmethod
    def load(cls, path: str | Path) -> "CourtSpec":
        with open(path) as f:
            return cls.from_dict(yaml.safe_load(f) or {})

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "width": self.width,
            "length": self.length,
            "kitchen_depth": self.kitchen_depth,
            "line_width": self.line_width,
            "net_height_sideline": self.net_height_sideline,
            "net_height_center": self.net_height_center,
            "net_post_offset": self.net_post_offset,
            "ball_radius": self.ball_radius,
            "contact_patch_radius": self.contact_patch_radius,
            "scale": self.scale,
        }

    # -------------------------------------------------------------- geometry
    @property
    def half_w(self) -> float:
        return self.width / 2

    @property
    def half_l(self) -> float:
        return self.length / 2

    def court_rect(self) -> Rect:
        """Whole playing area including boundary lines."""
        return Rect(-self.half_w, self.half_w, -self.half_l, self.half_l)

    def half_rect(self, side: Side) -> Rect:
        """Half of the court on one side of the net (incl. lines)."""
        if side is Side.A:
            return Rect(-self.half_w, self.half_w, -self.half_l, 0.0)
        return Rect(-self.half_w, self.half_w, 0.0, self.half_l)

    def kitchen_rect(self, side: Side) -> Rect:
        """Non-volley zone on a side, INCLUDING the kitchen line."""
        k = self.kitchen_depth
        if side is Side.A:
            return Rect(-self.half_w, self.half_w, -k, 0.0)
        return Rect(-self.half_w, self.half_w, 0.0, k)

    def service_court_rect(self, receiving_side: Side, half: str) -> Rect:
        """Service court on the receiving side.

        ``half`` is "left"/"right" *as seen by the receiver* (standing on their
        baseline looking at the net). The centreline belongs to both service
        courts; the kitchen line does NOT belong to the service court.
        """
        k = self.kitchen_depth
        lw2 = self.line_width / 2
        if receiving_side is Side.B:
            y0, y1 = k, self.half_l
            # Receiver on B faces -Y; their right is -X.
            right = Rect(-self.half_w, lw2, y0, y1)
            left = Rect(-lw2, self.half_w, y0, y1)
        else:
            y0, y1 = -self.half_l, -k
            # Receiver on A faces +Y; their right is +X.
            right = Rect(-lw2, self.half_w, y0, y1)
            left = Rect(-self.half_w, lw2, y0, y1)
        return right if half == "right" else left

    def serve_target(self, server_side: Side, service_side: ServiceSide) -> Rect:
        """Diagonal service court a serve must land in.

        A server in their RIGHT court serves to the receiver's RIGHT court
        (diagonally opposite).
        """
        return self.service_court_rect(server_side.other, service_side.value)

    def lines(self) -> list[LineSegment]:
        """All painted lines as thin rectangles (for drawing and nearest-line)."""
        lw = self.line_width
        hw, hl, k = self.half_w, self.half_l, self.kitchen_depth
        segs = [
            LineSegment("baseline_A", Rect(-hw, hw, -hl, -hl + lw)),
            LineSegment("baseline_B", Rect(-hw, hw, hl - lw, hl)),
            LineSegment("sideline_left", Rect(-hw, -hw + lw, -hl, hl)),
            LineSegment("sideline_right", Rect(hw - lw, hw, -hl, hl)),
            LineSegment("kitchen_A", Rect(-hw, hw, -k, -k + lw)),
            LineSegment("kitchen_B", Rect(-hw, hw, k - lw, k)),
            LineSegment("centreline_A", Rect(-lw / 2, lw / 2, -hl, -k)),
            LineSegment("centreline_B", Rect(-lw / 2, lw / 2, k, hl)),
        ]
        return segs

    def keypoints(self) -> dict[str, tuple[float, float, float]]:
        """Named 3D points usable for camera calibration.

        Ground points are line-intersection *outer corners* (easy to click).
        Net-post tops are off the ground plane and greatly improve calibration
        when visible.
        """
        hw, hl, k = self.half_w, self.half_l, self.kitchen_depth
        p: dict[str, tuple[float, float, float]] = {
            # Outer corners of the court.
            "A_left_corner": (-hw, -hl, 0.0),
            "A_right_corner": (hw, -hl, 0.0),
            "B_left_corner": (-hw, hl, 0.0),
            "B_right_corner": (hw, hl, 0.0),
            # Kitchen line meets sideline (far-from-net edge of the kitchen line).
            "A_kitchen_left": (-hw, -k, 0.0),
            "A_kitchen_right": (hw, -k, 0.0),
            "B_kitchen_left": (-hw, k, 0.0),
            "B_kitchen_right": (hw, k, 0.0),
            # Centreline meets baseline / kitchen line (centre of the T).
            "A_centre_baseline": (0.0, -hl, 0.0),
            "B_centre_baseline": (0.0, hl, 0.0),
            "A_centre_kitchen": (0.0, -k, 0.0),
            "B_centre_kitchen": (0.0, k, 0.0),
            # Net line on the sidelines (ground).
            "net_left_ground": (-hw, 0.0, 0.0),
            "net_right_ground": (hw, 0.0, 0.0),
            # Top of the net at the sidelines (3D).
            "net_left_top": (-hw, 0.0, self.net_height_sideline),
            "net_right_top": (hw, 0.0, self.net_height_sideline),
            "net_centre_top": (0.0, 0.0, self.net_height_center),
        }
        return p

    def nearest_line(self, x: float, y: float) -> tuple[str, float]:
        """Name of nearest line and signed distance (m) from its outer edge.

        Signed distance is computed against the boundary lines only, positive
        when the point is outside the court rectangle.
        """
        best_name, best_d = "", float("inf")
        for seg in self.lines():
            d = float(seg.rect.distance_outside(np.array(x), np.array(y)))
            if d < best_d:
                best_name, best_d = seg.name, d
        return best_name, best_d
