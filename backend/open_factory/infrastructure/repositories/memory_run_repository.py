"""In-memory thread-safe execution run repository."""

from __future__ import annotations

import threading
from typing import Sequence

from open_factory.domain.entities import Run
from open_factory.domain.repositories import IRunRepository


class MemoryRunRepository(IRunRepository):
    """Stores execution runs in memory with thread safety."""

    def __init__(self, max_runs: int = 500) -> None:
        self._runs: dict[str, Run] = {}
        self._max_runs = max_runs
        self._lock = threading.Lock()

    def list_recent(self, limit: int = 50) -> Sequence[Run]:
        with self._lock:
            # Sort by started_at descending
            all_runs = list(self._runs.values())
            all_runs.sort(key=lambda r: r.started_at, reverse=True)
            return all_runs[:limit]

    def get_by_id(self, run_id: str) -> Run | None:
        with self._lock:
            return self._runs.get(run_id)

    def save(self, run: Run) -> None:
        with self._lock:
            self._runs[run.id] = run
            # Evict oldest runs if beyond max_runs
            if len(self._runs) > self._max_runs:
                sorted_keys = sorted(self._runs.keys(), key=lambda k: self._runs[k].started_at)
                for k in sorted_keys[: len(self._runs) - self._max_runs]:
                    del self._runs[k]
