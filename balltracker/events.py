"""Universal event model (schema v1).

Three tiers, each referencing the tier below so every decision is traceable:

1. ``BallObservation``     - what a detector saw in one frame of one camera.
2. ``BounceEvent``         - a reconstructed physical event (sport-agnostic).
3. ``LineCallEvent``       - what the bounce means under a sport's rules.

Conventions
-----------
* Time: seconds on the *session clock*. For a single recorded file this is the
  presentation timestamp of the frame from the start of the file. With several
  cameras every camera's clock is mapped onto one session clock (see
  ARCHITECTURE.md, "Time base").
* Space: the court frame defined in ``balltracker.geometry.court`` (metres,
  origin at net centre on the surface, z up).
* Pixels: (u, v) with origin at the top-left of the full-resolution frame.
* Observations are immutable. Derived events record the algorithm/model version
  and parameters so they can be regenerated when algorithms improve.
"""

from __future__ import annotations

import uuid
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

SCHEMA_VERSION = "1.0"


def new_id() -> str:
    return uuid.uuid4().hex[:16]


class Provenance(BaseModel):
    algorithm: str
    version: str
    params: dict = Field(default_factory=dict)


class BallObservation(BaseModel):
    schema_version: Literal["1.0"] = SCHEMA_VERSION
    kind: Literal["ball_observation"] = "ball_observation"
    id: str = Field(default_factory=new_id)
    camera_id: str
    frame_index: int
    t: float  # session clock, seconds
    u: float  # pixel x of ball centre
    v: float  # pixel y of ball centre
    radius_px: float | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    provenance: Provenance


class Point3(BaseModel):
    x: float
    y: float
    z: float = 0.0
    frame: Literal["court"] = "court"
    units: Literal["m"] = "m"


class BounceEvent(BaseModel):
    """A ball-surface contact, reconstructed from observations."""

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    kind: Literal["bounce"] = "bounce"
    id: str = Field(default_factory=new_id)
    t: float  # estimated contact time (sub-frame), session clock
    t_std: float  # 1-sigma uncertainty of t (s)
    position: Point3  # estimated contact point on the surface
    cov_xy: list[list[float]]  # 2x2 covariance of (x, y), m^2
    pixel: tuple[float, float]  # estimated ball-centre pixel at contact
    camera_ids: list[str]
    confidence: float = Field(ge=0.0, le=1.0)  # that this really was a bounce
    supporting_observations: list[str]  # BallObservation ids
    provenance: Provenance


class CallResult(str, Enum):
    IN = "IN"
    OUT = "OUT"
    UNCERTAIN = "UNCERTAIN"


class ShotContext(str, Enum):
    RALLY = "rally"  # any shot after the serve
    SERVE = "serve"


class LineCallEvent(BaseModel):
    """Interpretation of a bounce under the sport's rules.

    ``announce`` is True only when the system would speak: it stays silent for
    IN and UNCERTAIN.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    kind: Literal["line_call"] = "line_call"
    id: str = Field(default_factory=new_id)
    sport: str = "pickleball"
    bounce_id: str
    t: float
    context: ShotContext
    target_region: str
    result: CallResult
    p_out: float = Field(ge=0.0, le=1.0)
    nearest_line: str
    signed_distance_m: float  # contact edge to region boundary; >0 = outside
    announce: bool
    call_text: str | None = None  # e.g. "OUT", "FAULT"
    provenance: Provenance


class AnalysisResult(BaseModel):
    """Everything produced from one analysed video."""

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    source: str
    camera_id: str
    court: dict
    fps: float
    frame_count: int
    observations: list[BallObservation]
    bounces: list[BounceEvent]
    calls: list[LineCallEvent]
    timings: dict = Field(default_factory=dict)
