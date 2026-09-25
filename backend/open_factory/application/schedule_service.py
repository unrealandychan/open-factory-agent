"""Application service managing workflow schedules."""

from __future__ import annotations

import uuid
from typing import Sequence
from croniter import croniter

from open_factory.application.dto import ScheduleCreateDto
from open_factory.domain.entities import Schedule, current_utc_time
from open_factory.domain.exceptions import DomainError, ScheduleNotFoundError, WorkflowNotFoundError
from open_factory.domain.repositories import IScheduleRepository, IWorkflowRepository


class InvalidCronError(DomainError):
    """Raised when an invalid cron expression is supplied."""


class ScheduleService:
    """Use case service for scheduling workflows."""

    def __init__(self, schedule_repo: IScheduleRepository, workflow_repo: IWorkflowRepository) -> None:
        self._schedule_repo = schedule_repo
        self._workflow_repo = workflow_repo

    def list_schedules(self) -> Sequence[Schedule]:
        return self._schedule_repo.list_all()

    def get_schedule(self, schedule_id: str) -> Schedule:
        schedule = self._schedule_repo.get_by_id(schedule_id)
        if not schedule:
            raise ScheduleNotFoundError(schedule_id)
        return schedule

    def create_schedule(self, dto: ScheduleCreateDto) -> Schedule:
        if not self._workflow_repo.get_by_id(dto.workflow_id):
            raise WorkflowNotFoundError(dto.workflow_id)

        if not croniter.is_valid(dto.cron_expression):
            raise InvalidCronError(f"Invalid cron expression: '{dto.cron_expression}'")

        schedule = Schedule(
            id=f"sched-{uuid.uuid4().hex[:8]}",
            workflow_id=dto.workflow_id,
            cron_expression=dto.cron_expression,
            name=dto.name or f"Schedule for {dto.workflow_id}",
            enabled=dto.enabled,
            parameters=dict(dto.parameters),
            created_at=current_utc_time(),
        )
        self._schedule_repo.save(schedule)
        return schedule

    def toggle_schedule(self, schedule_id: str, enabled: bool) -> Schedule:
        schedule = self.get_schedule(schedule_id)
        schedule.enabled = enabled
        self._schedule_repo.save(schedule)
        return schedule

    def delete_schedule(self, schedule_id: str) -> None:
        if not self._schedule_repo.delete(schedule_id):
            raise ScheduleNotFoundError(schedule_id)
