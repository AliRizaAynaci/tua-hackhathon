from __future__ import annotations

from datetime import datetime
from typing import List, Tuple

import numpy as np

from src.planners import AStarPlanner, RRTPlanner
from backend.schemas import ObstacleDelta, PlannerMode, PointXY
from backend.state import MapRegistry, SessionState, SessionStore


def planner_params(mode: PlannerMode) -> Tuple[float, float]:
    if mode == "safe":
        return 50.0, 0.80
    if mode == "aggressive":
        return 0.5, 0.95
    return 20.0, 0.85


class PlanningService:
    def __init__(self, map_registry: MapRegistry, store: SessionStore):
        self.maps = map_registry
        self.sessions = store

    def _validate_point(self, arr: np.ndarray, p: PointXY, max_danger: float):
        if p.y < 0 or p.y >= arr.shape[0] or p.x < 0 or p.x >= arr.shape[1]:
            raise ValueError("Point is out of bounds")
        if np.isnan(arr[p.y, p.x]) or arr[p.y, p.x] >= max_danger:
            raise ValueError("Point is blocked for current mode")

    def _path_cost(self, arr: np.ndarray, path_xy: List[Tuple[int, int]]) -> float:
        if not path_xy:
            return float("inf")
        total = 0.0
        for x, y in path_xy:
            if 0 <= y < arr.shape[0] and 0 <= x < arr.shape[1] and not np.isnan(arr[y, x]):
                total += float(arr[y, x])
        return total

    def plan_global(
        self,
        map_id: str,
        start: PointXY,
        goal: PointXY,
        mode: PlannerMode,
        session_id: str | None,
    ) -> SessionState:
        baseline = self.maps.get(map_id)
        safety_weight, max_danger = planner_params(mode)

        self._validate_point(baseline, start, max_danger)
        self._validate_point(baseline, goal, max_danger)

        state = self.sessions.create_or_replace(
            map_id=map_id,
            mode=mode,
            baseline_map=baseline,
            session_id=session_id,
        )

        planner = AStarPlanner(state.dynamic_map, obstacle_threshold=max_danger)
        path = planner.plan((start.x, start.y), (goal.x, goal.y), safety_weight=safety_weight, max_danger=max_danger)
        if not path:
            raise ValueError("A* could not find a global path")

        state.path_xy = [(int(x), int(y)) for x, y in path]
        state.updated_at = datetime.utcnow()
        return state

    def apply_obstacle_deltas(self, state: SessionState, deltas: List[ObstacleDelta]) -> int:
        updated = 0
        arr = state.dynamic_map
        h, w = arr.shape

        for d in deltas:
            if d.kind == "cells":
                for p in d.cells:
                    if 0 <= p.x < w and 0 <= p.y < h:
                        if arr[p.y, p.x] < 1.0:
                            arr[p.y, p.x] = 1.0
                            updated += 1

            elif d.kind == "circle" and d.center is not None and d.radius is not None:
                cx, cy, r = d.center.x, d.center.y, d.radius
                x0, x1 = max(0, cx - r), min(w - 1, cx + r)
                y0, y1 = max(0, cy - r), min(h - 1, cy + r)
                for y in range(y0, y1 + 1):
                    for x in range(x0, x1 + 1):
                        if (x - cx) * (x - cx) + (y - cy) * (y - cy) <= r * r:
                            if arr[y, x] < 1.0:
                                arr[y, x] = 1.0
                                updated += 1

            elif d.kind == "rect" and d.top_left is not None and d.width is not None and d.height is not None:
                x0 = max(0, d.top_left.x)
                y0 = max(0, d.top_left.y)
                x1 = min(w, x0 + d.width)
                y1 = min(h, y0 + d.height)
                patch = arr[y0:y1, x0:x1]
                updated += int(np.sum(patch < 1.0))
                arr[y0:y1, x0:x1] = 1.0

        state.updated_at = datetime.utcnow()
        return updated

    def plan_local_rrt(
        self,
        state: SessionState,
        robot_pose: PointXY,
        current_path_index: int,
        lookahead: int,
    ):
        mode = state.mode
        _, max_danger = planner_params(mode)

        if not state.path_xy:
            raise ValueError("Session has no active global path")

        if current_path_index < 0:
            current_path_index = 0
        if current_path_index >= len(state.path_xy):
            current_path_index = len(state.path_xy) - 1

        # pick local goal ahead on the active path
        local_goal_index = min(current_path_index + lookahead, len(state.path_xy) - 1)

        # make sure local goal is on traversable cell; scan forward if needed
        for i in range(local_goal_index, len(state.path_xy)):
            gx, gy = state.path_xy[i]
            if 0 <= gy < state.dynamic_map.shape[0] and 0 <= gx < state.dynamic_map.shape[1]:
                if not np.isnan(state.dynamic_map[gy, gx]) and state.dynamic_map[gy, gx] < max_danger:
                    local_goal_index = i
                    break

        lgx, lgy = state.path_xy[local_goal_index]

        rrt = RRTPlanner(state.dynamic_map, obstacle_threshold=max_danger, step_size=6.0, max_iter=5000)
        local_path = rrt.plan((robot_pose.x, robot_pose.y), (lgx, lgy))

        if not local_path:
            # fallback A*
            safety_weight, _ = planner_params("aggressive")
            a = AStarPlanner(state.dynamic_map, obstacle_threshold=max_danger)
            local_path = a.plan((robot_pose.x, robot_pose.y), (lgx, lgy), safety_weight=safety_weight, max_danger=max_danger)
            if not local_path:
                raise ValueError("Local replanning failed (RRT + A* fallback)")

        local_path_xy = [(int(round(x)), int(round(y))) for x, y in local_path]
        splice_start = current_path_index
        splice_end = local_goal_index

        state.path_xy = state.path_xy[:splice_start] + local_path_xy + state.path_xy[splice_end:]
        state.updated_at = datetime.utcnow()

        return local_path_xy, splice_start, splice_end

    def session_cost(self, state: SessionState) -> float:
        return self._path_cost(state.dynamic_map, state.path_xy)
