from dataclasses import dataclass, field
from datetime import datetime
from threading import RLock
from typing import Dict, List, Optional, Tuple
import uuid

import numpy as np


@dataclass
class SessionState:
    session_id: str
    map_id: str
    mode: str
    baseline_map: np.ndarray
    dynamic_map: np.ndarray
    path_xy: List[Tuple[int, int]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


class MapRegistry:
    def __init__(self, map_sources: Dict[str, str]):
        self._maps: Dict[str, np.ndarray] = {}
        for map_id, path in map_sources.items():
            self._maps[map_id] = np.load(path).astype(np.float32)

    def get(self, map_id: str) -> np.ndarray:
        if map_id not in self._maps:
            raise KeyError(f"Unknown map_id: {map_id}")
        return self._maps[map_id]

    def ids(self) -> List[str]:
        return list(self._maps.keys())


class SessionStore:
    def __init__(self):
        self._lock = RLock()
        self._sessions: Dict[str, SessionState] = {}

    def create_or_replace(
        self,
        map_id: str,
        mode: str,
        baseline_map: np.ndarray,
        session_id: Optional[str] = None,
    ) -> SessionState:
        with self._lock:
            sid = session_id or str(uuid.uuid4())
            state = SessionState(
                session_id=sid,
                map_id=map_id,
                mode=mode,
                baseline_map=baseline_map,
                dynamic_map=baseline_map.copy(),
            )
            self._sessions[sid] = state
            return state

    def get(self, session_id: str) -> SessionState:
        with self._lock:
            if session_id not in self._sessions:
                raise KeyError(f"Unknown session_id: {session_id}")
            return self._sessions[session_id]

    def delete(self, session_id: str) -> bool:
        with self._lock:
            return self._sessions.pop(session_id, None) is not None
