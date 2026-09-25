"""Abstract interfaces and execution context for step runners."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
import threading
from typing import Any, Callable


@dataclass
class ExecutionContext:
    """Runtime context provided to step runners."""

    run_id: str
    step_id: str
    output_dir: Path
    parameters: dict[str, Any] = field(default_factory=dict)
    cancel_event: threading.Event = field(default_factory=threading.Event)
    log_callback: Callable[[str, str], None] = field(default=lambda level, msg: None)

    def is_cancelled(self) -> bool:
        """Check if cancellation has been requested."""
        return self.cancel_event.is_set()

    def log(self, level: str, message: str) -> None:
        """Emit a structured log message."""
        self.log_callback(level, message)


@dataclass
class StepResult:
    """Outcome of a step execution."""

    exit_code: int
    error_message: str | None = None
    output_files: list[str] = field(default_factory=list)


class IStepRunner(ABC):
    """Abstract interface for step runners."""

    @abstractmethod
    def run(self, step: Any, context: ExecutionContext) -> StepResult:
        """Execute a step within the given context."""
