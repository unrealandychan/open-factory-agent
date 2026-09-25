"""Tests for ScheduleService and CronEngine."""

from datetime import datetime, timezone, timedelta
import pytest

from open_factory.application.dto import ScheduleCreateDto
from open_factory.application.schedule_service import InvalidCronError, ScheduleService
from open_factory.domain.entities import Schedule
from open_factory.infrastructure.scheduler.cron_engine import CronEngine


def test_schedule_service_crud(workflow_repo, schedule_repo, sample_workflow):
    workflow_repo.save(sample_workflow)
    service = ScheduleService(schedule_repo=schedule_repo, workflow_repo=workflow_repo)

    dto = ScheduleCreateDto(
        workflow_id=sample_workflow.id,
        cron_expression="*/5 * * * *",
        name="Every 5 mins",
    )
    created = service.create_schedule(dto)
    assert created.id.startswith("sched-")
    assert created.enabled is True

    schedules = service.list_schedules()
    assert len(schedules) == 1

    toggled = service.toggle_schedule(created.id, enabled=False)
    assert toggled.enabled is False

    service.delete_schedule(created.id)
    assert len(service.list_schedules()) == 0


def test_schedule_service_invalid_cron(workflow_repo, schedule_repo, sample_workflow):
    workflow_repo.save(sample_workflow)
    service = ScheduleService(schedule_repo=schedule_repo, workflow_repo=workflow_repo)

    dto = ScheduleCreateDto(
        workflow_id=sample_workflow.id,
        cron_expression="invalid-cron-string",
    )
    with pytest.raises(InvalidCronError):
        service.create_schedule(dto)


def test_cron_engine_due_evaluation(schedule_repo, sample_workflow):
    now = datetime.now(timezone.utc)
    ten_mins_ago = now - timedelta(minutes=10)

    # Schedule set to run every 5 minutes, last run 10 minutes ago -> due!
    schedule = Schedule(
        id="s-due",
        workflow_id=sample_workflow.id,
        cron_expression="*/5 * * * *",
        enabled=True,
        last_run_at=ten_mins_ago,
    )
    schedule_repo.save(schedule)

    triggered = []
    engine = CronEngine(
        schedule_repo=schedule_repo,
        trigger_callback=lambda dto: triggered.append(dto.workflow_id),
    )

    due_ids = engine.check_and_trigger_due_schedules(now=now)
    assert "s-due" in due_ids
    assert sample_workflow.id in triggered
