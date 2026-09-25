"""Repository interfaces (ports) for domain entity persistence."""

from abc import ABC, abstractmethod
from typing import Sequence

from open_factory.domain.entities import Workflow, Run, Schedule


class IWorkflowRepository(ABC):
    """Persistence port for Workflow aggregate."""

    @abstractmethod
    def list_all(self) -> Sequence[Workflow]:
        """Retrieve all workflows."""

    @abstractmethod
    def get_by_id(self, workflow_id: str) -> Workflow | None:
        """Retrieve a single workflow by ID."""

    @abstractmethod
    def save(self, workflow: Workflow) -> None:
        """Create or update a workflow."""

    @abstractmethod
    def delete(self, workflow_id: str) -> bool:
        """Delete a workflow by ID."""


class IRunRepository(ABC):
    """Persistence port for Run aggregate."""

    @abstractmethod
    def list_recent(self, limit: int = 50) -> Sequence[Run]:
        """Retrieve recent execution runs."""

    @abstractmethod
    def get_by_id(self, run_id: str) -> Run | None:
        """Retrieve an execution run by ID."""

    @abstractmethod
    def save(self, run: Run) -> None:
        """Persist or update an execution run."""


class IScheduleRepository(ABC):
    """Persistence port for Schedule entity."""

    @abstractmethod
    def list_all(self) -> Sequence[Schedule]:
        """Retrieve all defined schedules."""

    @abstractmethod
    def get_by_id(self, schedule_id: str) -> Schedule | None:
        """Retrieve schedule by ID."""

    @abstractmethod
    def save(self, schedule: Schedule) -> None:
        """Create or update a schedule."""

    @abstractmethod
    def delete(self, schedule_id: str) -> bool:
        """Delete a schedule by ID."""
