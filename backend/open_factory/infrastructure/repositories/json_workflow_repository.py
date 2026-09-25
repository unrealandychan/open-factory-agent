"""JSON-backed workflow repository with thread-safe atomic writes and backups."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from open_factory.domain.entities import Step, StepField, StepOutput, StepType, Workflow
from open_factory.domain.repositories import IWorkflowRepository


class JsonWorkflowRepository(IWorkflowRepository):
    """Stores workflows in a local JSON file with atomic write semantics."""

    def __init__(self, file_path: Path, max_backups: int = 5) -> None:
        self.file_path = Path(file_path).resolve()
        self.max_backups = max_backups
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
                if isinstance(data, dict) and "workflows" in data:
                    return data["workflows"]
                if isinstance(data, list):
                    return data
                return []
            except (json.JSONDecodeError, OSError):
                return []

    def _write_raw(self, workflows: list[dict]) -> None:
        temp_dir = self.file_path.parent
        temp_dir.mkdir(parents=True, exist_ok=True)

        payload = {
            "version": "1.0",
            "workflows": workflows,
        }

        # Backup current file if it exists and has content
        if self.file_path.exists() and self.file_path.stat().st_size > 0:
            for i in range(self.max_backups - 1, 0, -1):
                backup_i = self.file_path.with_suffix(f".bak.{i}")
                backup_prev = self.file_path.with_suffix(f".bak.{i-1}" if i > 1 else ".bak")
                if backup_prev.exists():
                    shutil.copy2(backup_prev, backup_i)
            shutil.copy2(self.file_path, self.file_path.with_suffix(".bak"))

        with tempfile.NamedTemporaryFile("w", dir=temp_dir, delete=False, encoding="utf-8") as tf:
            json.dump(payload, tf, indent=2, ensure_ascii=False)
            temp_name = tf.name

        os.replace(temp_name, self.file_path)

    def list_all(self) -> Sequence[Workflow]:
        raw_items = self._read_raw()
        return [self._to_entity(item) for item in raw_items]

    def get_by_id(self, workflow_id: str) -> Workflow | None:
        for wf in self.list_all():
            if wf.id == workflow_id:
                return wf
        return None

    def save(self, workflow: Workflow) -> None:
        with self._lock:
            raw_items = self._read_raw()
            updated = False
            for i, item in enumerate(raw_items):
                if item.get("id") == workflow.id:
                    raw_items[i] = workflow.to_dict()
                    updated = True
                    break
            if not updated:
                raw_items.append(workflow.to_dict())
            self._write_raw(raw_items)

    def delete(self, workflow_id: str) -> bool:
        with self._lock:
            raw_items = self._read_raw()
            filtered = [item for item in raw_items if item.get("id") != workflow_id]
            if len(filtered) == len(raw_items):
                return False
            self._write_raw(filtered)
            return True

    @staticmethod
    def _to_entity(raw: dict) -> Workflow:
        steps: list[Step] = []
        for s in raw.get("steps", []):
            try:
                st = StepType(s.get("type", "script"))
            except ValueError:
                st = StepType.SCRIPT

            fields = [
                StepField(
                    id=f.get("id", ""),
                    label=f.get("label", ""),
                    field_type=f.get("field_type", "text"),
                    placeholder=f.get("placeholder", ""),
                    default_value=f.get("default_value", ""),
                    required=f.get("required", False),
                )
                for f in s.get("fields", [])
            ]
            outputs = [
                StepOutput(
                    label=o.get("label", ""),
                    filename=o.get("filename", ""),
                    file_type=o.get("type", o.get("file_type", "JSON")),
                    path=o.get("path", ""),
                )
                for o in s.get("outputs", [])
            ]

            steps.append(
                Step(
                    id=s.get("id", ""),
                    title=s.get("title", ""),
                    step_type=st,
                    description=s.get("desc", s.get("description", "")),
                    order=s.get("order", 1),
                    depends_on=s.get("dependsOn", s.get("depends_on", [])),
                    script_content=s.get("script", s.get("script_content", "")),
                    command=s.get("command", ""),
                    http_url=s.get("http_url", ""),
                    http_method=s.get("http_method", "GET"),
                    http_headers=s.get("http_headers", {}),
                    prompt_template=s.get("prompt_template", ""),
                    fields=fields,
                    outputs=outputs,
                    output_path=s.get("outputPath", s.get("output_path", "")),
                )
            )

        def parse_date(value: str | None) -> datetime:
            if not value:
                return datetime.now(timezone.utc)
            try:
                return datetime.fromisoformat(value)
            except Exception:
                return datetime.now(timezone.utc)

        return Workflow(
            id=raw.get("id", ""),
            name=raw.get("name", "Untitled Workflow"),
            description=raw.get("description", raw.get("desc", "")),
            steps=steps,
            created_at=parse_date(raw.get("created_at")),
            updated_at=parse_date(raw.get("updated_at")),
        )
