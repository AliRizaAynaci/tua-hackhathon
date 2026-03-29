from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException

from backend.schemas import (
    GlobalPlanRequest,
    GlobalPlanResponse,
    HealthResponse,
    LocalRrtRequest,
    LocalRrtResponse,
    SessionPathResponse,
    UpdateObstaclesRequest,
    UpdateObstaclesResponse,
    PointXY,
)
from backend.service import PlanningService
from backend.state import MapRegistry, SessionStore


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MAP_PATH = ROOT / "output" / "cost_test_data" / "cost_map.npy"


app = FastAPI(title="Lunar Rover Planning API", version="1.0.0")


@app.on_event("startup")
def startup_event():
    if not DEFAULT_MAP_PATH.exists():
        raise RuntimeError(f"Default map not found: {DEFAULT_MAP_PATH}")

    maps = MapRegistry({"baseline": str(DEFAULT_MAP_PATH)})
    store = SessionStore()
    app.state.service = PlanningService(maps, store)


def get_service() -> PlanningService:
    return app.state.service


@app.get("/health", response_model=HealthResponse)
def health(service: PlanningService = Depends(get_service)):
    return HealthResponse(status="ok", maps_loaded=service.maps.ids())


@app.post("/plan/global", response_model=GlobalPlanResponse)
def plan_global(req: GlobalPlanRequest, service: PlanningService = Depends(get_service)):
    try:
        state = service.plan_global(
            map_id=req.map_id,
            start=req.start,
            goal=req.goal,
            mode=req.mode,
            session_id=req.session_id,
        )
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    path = [PointXY(x=x, y=y) for x, y in state.path_xy]
    return GlobalPlanResponse(
        session_id=state.session_id,
        map_id=state.map_id,
        mode=state.mode,
        path=path,
        total_cost=service.session_cost(state),
    )


@app.post("/map/update-obstacles", response_model=UpdateObstaclesResponse)
def update_obstacles(req: UpdateObstaclesRequest, service: PlanningService = Depends(get_service)):
    try:
        state = service.sessions.get(req.session_id)
        count = service.apply_obstacle_deltas(state, req.deltas)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return UpdateObstaclesResponse(session_id=req.session_id, updated_cells=count)


@app.post("/plan/local-rrt", response_model=LocalRrtResponse)
def plan_local_rrt(req: LocalRrtRequest, service: PlanningService = Depends(get_service)):
    try:
        state = service.sessions.get(req.session_id)
        local_path, splice_start, splice_end = service.plan_local_rrt(
            state=state,
            robot_pose=req.robot_pose,
            current_path_index=req.current_path_index,
            lookahead=req.lookahead,
        )
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return LocalRrtResponse(
        session_id=req.session_id,
        local_path=[PointXY(x=x, y=y) for x, y in local_path],
        splice_start_index=splice_start,
        splice_end_index=splice_end,
        updated_path_length=len(state.path_xy),
    )


@app.get("/session/{session_id}/path", response_model=SessionPathResponse)
def get_session_path(session_id: str, service: PlanningService = Depends(get_service)):
    try:
        state = service.sessions.get(session_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return SessionPathResponse(
        session_id=state.session_id,
        map_id=state.map_id,
        mode=state.mode,
        path=[PointXY(x=x, y=y) for x, y in state.path_xy],
    )


@app.delete("/session/{session_id}")
def delete_session(session_id: str, service: PlanningService = Depends(get_service)):
    deleted = service.sessions.delete(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Unknown session_id")
    return {"deleted": True, "session_id": session_id}
