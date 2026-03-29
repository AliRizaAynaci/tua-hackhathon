from typing import List, Literal, Optional

from pydantic import BaseModel, Field


PlannerMode = Literal["safe", "balanced", "aggressive"]


class PointXY(BaseModel):
    x: int
    y: int


class ObstacleDelta(BaseModel):
    kind: Literal["cells", "circle", "rect"]
    cells: List[PointXY] = Field(default_factory=list)
    center: Optional[PointXY] = None
    radius: Optional[int] = None
    top_left: Optional[PointXY] = None
    width: Optional[int] = None
    height: Optional[int] = None


class GlobalPlanRequest(BaseModel):
    map_id: str = "baseline"
    start: PointXY
    goal: PointXY
    mode: PlannerMode = "safe"
    session_id: Optional[str] = None


class GlobalPlanResponse(BaseModel):
    session_id: str
    map_id: str
    mode: PlannerMode
    path: List[PointXY]
    total_cost: float


class UpdateObstaclesRequest(BaseModel):
    session_id: str
    deltas: List[ObstacleDelta] = Field(default_factory=list)


class UpdateObstaclesResponse(BaseModel):
    session_id: str
    updated_cells: int


class LocalRrtRequest(BaseModel):
    session_id: str
    robot_pose: PointXY
    current_path_index: int = 0
    lookahead: int = 40


class LocalRrtResponse(BaseModel):
    session_id: str
    local_path: List[PointXY]
    splice_start_index: int
    splice_end_index: int
    updated_path_length: int


class SessionPathResponse(BaseModel):
    session_id: str
    map_id: str
    mode: PlannerMode
    path: List[PointXY]


class HealthResponse(BaseModel):
    status: str
    maps_loaded: List[str]
