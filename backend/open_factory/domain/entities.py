"""Domain entities and value objects for Open Factory Agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import uuid
from typing import Any

from open_factory.domain.exceptions import WorkflowValidationError


def current_utc_time() -> datetime:
    """Return timezone-aware current UTC datetime."""
    return datetime.now(timezone.utc)


class StepType(str, Enum):
    """Supported step execution types."""

    SCRIPT = "script"
    PROMPT = "prompt"
    HTTP = "http"
    COMMAND = "command"


class RunStatus(str, Enum):
    """Lifecycle status of workflow and step executions."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class StepField:
    """Configurable user input field for a step."""

    id: str
    label: str
    field_type: str = "text"
    placeholder: str = ""
    default_value: str = ""
    required: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "field_type": self.field_type,
            "placeholder": self.placeholder,
            "default_value": self.default_value,
            "required": self.required,
        }


@dataclass(frozen=True)
class StepOutput:
    """Declaration of an artifact produced by a step."""

    label: str
    filename: str
    file_type: str = "JSON"
    path: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "filename": self.filename,
            "file_type": self.file_type,
            "path": self.path,
        }


@dataclass
class Step:
    """A discrete executable unit within a workflow."""

    id: str
    title: str
    step_type: StepType
    description: str = ""
    order: int = 1
    depends_on: list[str] = field(default_factory=list)
    script_content: str = ""
    command: str = ""
    http_url: str = ""
    http_method: str = "GET"
    http_headers: dict[str, str] = field(default_factory=dict)
    prompt_template: str = ""
    fields: list[StepField] = field(default_factory=list)
    outputs: list[StepOutput] = field(default_factory=list)
    output_path: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "type": self.step_type.value,
            "description": self.description,
            "order": self.order,
            "depends_on": self.depends_on,
            "script_content": self.script_content,
            "command": self.command,
            "http_url": self.http_url,
            "http_method": self.http_method,
            "http_headers": self.http_headers,
            "prompt_template": self.prompt_template,
            "fields": [f.to_dict() for f in self.fields],
            "outputs": [o.to_dict() for o in self.outputs],
            "output_path": self.output_path,
        }


@dataclass
class Workflow:
    """Aggregate root representing an automated process."""

    id: str
    name: str
    description: str = ""
    steps: list[Step] = field(default_factory=list)
    created_at: datetime = field(default_factory=current_utc_time)
    updated_at: datetime = field(default_factory=current_utc_time)

    def validate(self) -> None:
        """Validate step identifiers and cycle-free dependency graph."""
        step_ids = {step.id for step in self.steps}
        if len(step_ids) != len(self.steps):
            raise WorkflowValidationError(f"Workflow '{self.id}' contains duplicate step IDs.")

        for step in self.steps:
            for dependency in step.depends_on:
                if dependency not in step_ids:
                    raise WorkflowValidationError(
                        f"Step '{step.id}' depends on non-existent step '{dependency}'."
                    )
                if dependency == step.id:
                    raise WorkflowValidationError(
                        f"Step '{step.id}' cannot depend on itself."
                    )

        # Cycle detection using depth-first search
        visited: dict[str, int] = {}  # 0: visiting, 1: visited

        def has_cycle(current_id: str) -> bool:
            visited[current_id] = 0
            current_step = next(s for s in self.steps if s.id == current_id)
            for dependency in current_step.depends_on:
                state = visited.get(dependency)
                if state == 0:
                    return True
                if state is None and has_cycle(dependency):
                    return True
            visited[current_id] = 1
            return False

        for step in self.steps:
            if step.id not in visited:
                if has_cycle(step.id):
                    raise WorkflowValidationError(f"Workflow '{self.id}' contains circular dependencies.")

    def get_step(self, step_id: str) -> Step | None:
        """Return step matching identifier or None."""
        return next((step for step in self.steps if step.id == step_id), None)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "steps": [step.to_dict() for step in self.steps],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass(frozen=True)
class LogEntry:
    """An immutable log record captured during execution."""

    timestamp: datetime
    level: str
    message: str
    step_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level,
            "message": self.message,
            "step_id": self.step_id,
        }


@dataclass
class StepRun:
    """Execution status and result of a single step."""

    step_id: str
    title: str
    status: RunStatus = RunStatus.PENDING
    started_at: datetime | None = None
    finished_at: datetime | None = None
    exit_code: int | None = None
    error_message: str | None = None
    output_files: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_id": self.step_id,
            "title": self.title,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "exit_code": self.exit_code,
            "error_message": self.error_message,
            "output_files": self.output_files,
        }


@dataclass
class Run:
    """Aggregate root tracking a workflow or single-step execution."""

    id: str
    workflow_id: str
    status: RunStatus = RunStatus.PENDING
    target_step_id: str | None = None
    parameters: dict[str, Any] = field(default_factory=dict)
    step_runs: list[StepRun] = field(default_factory=list)
    logs: list[LogEntry] = field(default_factory=list)
    started_at: datetime = field(default_factory=current_utc_time)
    finished_at: datetime | None = None
    error_message: str | None = None

    def append_log(self, level: str, message: str, step_id: str | None = None) -> LogEntry:
        """Append a new log entry to the run."""
        entry = LogEntry(
            timestamp=current_utc_time(),
            level=level,
            message=message,
            step_id=step_id,
        )
        self.logs.append(entry)
        return entry

    def mark_success(self) -> None:
        """Mark run as successfully completed."""
        self.status = RunStatus.SUCCESS
        self.finished_at = current_utc_time()

    def mark_failed(self, error: str) -> None:
        """Mark run as failed with an error message."""
        self.status = RunStatus.FAILED
        self.error_message = error
        self.finished_at = current_utc_time()

    def mark_cancelled(self) -> None:
        """Mark run as cancelled."""
        self.status = RunStatus.CANCELLED
        self.finished_at = current_utc_time()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "workflow_id": self.workflow_id,
            "status": self.status.value,
            "target_step_id": self.target_step_id,
            "parameters": self.parameters,
            "step_runs": [s.to_dict() for s in self.step_runs],
            "logs": [entry.to_dict() for entry in self.logs],
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "error_message": self.error_message,
        }


@dataclass
class Schedule:
    """Cron-based automatic execution trigger."""

    id: str
    workflow_id: str
    cron_expression: str
    name: str = ""
    enabled: bool = True
    parameters: dict[str, Any] = field(default_factory=dict)
    last_run_at: datetime | None = None
    created_at: datetime = field(default_factory=current_utc_time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "workflow_id": self.workflow_id,
            "cron_expression": self.cron_expression,
            "name": self.name,
            "enabled": self.enabled,
            "parameters": self.parameters,
            "last_run_at": self.last_run_at.isoformat() if self.last_run_at else None,
            "created_at": self.created_at.isoformat(),
        }
