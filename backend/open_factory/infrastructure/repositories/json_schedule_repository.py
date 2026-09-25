"""JSON file-backed schedule repository."""

from __future__ import annotations

import json
import os
import tempfile
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from open_factory.domain.entities import Schedule
from open_factory.domain.repositories import IScheduleRepository


class JsonScheduleRepository(IScheduleRepository):
    """File-backed persistence for workflow schedules."""

    def __init__(self, file_path: Path) -> None:
        self.file_path = Path(file_path).resolve()
        self._lock = threading.RLock()
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        if not self.file_path.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            self._write_raw([])

    def _read_raw(self) -> list[dict]:
        with self._lock:
            try:
                data = json.loads(self.file_path.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    return data
                if isinstance(data, dict) and "schedules" in data:
                    return data["schedules"]
                return []
            except (json.JSONDecodeError, OSError):
                return []

    def _write_raw(self, schedules: list[dict]) -> None:
        temp_dir = self.file_path.parent
        temp_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", dir=temp_dir, delete=False, encoding="utf-8") as tf:
            json.dump(schedules, tf, indent=2, ensure_ascii=False)
            temp_name = tf.name
        os.replace(temp_name, self.file_path)

    def list_all(self) -> Sequence[Schedule]:
        raw_items = self._read_raw()
        return [self._to_entity(item) for item in raw_items]

    def get_by_id(self, schedule_id: str) -> Schedule | None:
        for s in self.list_all():
            if s.id == schedule_id:
                return s
        return None

    def save(self, schedule: Schedule) -> None:
        with self._lock:
            raw_items = self._read_raw()
            updated = False
            for i, item in enumerate(raw_items):
                if item.get("id") == schedule.id:
                    raw_items[i] = schedule.to_dict()
                    updated = True
                    break
            if not updated:
                raw_items.append(schedule.to_dict())
            self._write_raw(raw_items)

    def delete(self, schedule_id: str) -> bool:
        with self._lock:
            raw_items = self._read_raw()
            filtered = [item for item in raw_items if item.get("id") != schedule_id]
            if len(filtered) == len(raw_items):
                return False
            self._write_raw(filtered)
            return True

    @staticmethod
    def _to_entity(raw: dict) -> Schedule:
        def parse_date(value: str | None) -> datetime | None:
            if not value:
                return None
            try:
                return datetime.fromisoformat(value)
            except Exception:
                return None

        return Schedule(
            id=raw.get("id", ""),
            workflow_id=raw.get("workflow_id", ""),
            cron_expression=raw.get("cron_expression", "* * * * *"),
            name=raw.get("name", ""),
            enabled=raw.get("enabled", True),
            parameters=raw.get("parameters", {}),
            last_run_at=parse_date(raw.get("last_run_at")),
            created_at=parse_date(raw.get("created_at")) or datetime.now(timezone.utc),
        )
