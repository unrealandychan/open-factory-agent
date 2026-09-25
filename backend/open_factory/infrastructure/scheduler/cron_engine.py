"""Background cron scheduler engine that triggers workflow runs when schedules are due."""

from __future__ import annotations

import logging
import threading
import time
from datetime import datetime, timezone
from typing import Callable
from croniter import croniter

from open_factory.application.dto import TriggerRunDto
from open_factory.domain.entities import Schedule, current_utc_time
from open_factory.domain.repositories import IScheduleRepository

logger = logging.getLogger("open_factory.scheduler")


class CronEngine:
    """Evaluates active cron schedules periodically and triggers workflow runs."""

    def __init__(
        self,
        schedule_repo: IScheduleRepository,
        trigger_callback: Callable[[TriggerRunDto], Any],
        check_interval_seconds: float = 5.0,
    ) -> None:
        self._schedule_repo = schedule_repo
        self._trigger_callback = trigger_callback
        self._check_interval = check_interval_seconds
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        """Start the background scheduler thread."""
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True, name="CronEngineThread")
        self._thread.start()
        logger.info("Cron scheduler engine started.")

    def stop(self) -> None:
        """Stop the background scheduler thread."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=3.0)
            self._thread = None
        logger.info("Cron scheduler engine stopped.")

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                self.check_and_trigger_due_schedules()
            except Exception as exc:
                logger.error(f"Error checking schedules: {exc}")
            self._stop_event.wait(self._check_interval)

    def check_and_trigger_due_schedules(self, now: datetime | None = None) -> list[str]:
        """Check all enabled schedules and trigger any that are due."""
        current_time = now or current_utc_time()
        triggered_schedule_ids = []

        schedules = self._schedule_repo.list_all()
        for schedule in schedules:
            if not schedule.enabled:
                continue

            if self._is_schedule_due(schedule, current_time):
                logger.info(f"Triggering scheduled run for workflow {schedule.workflow_id} (schedule {schedule.id})")
                try:
                    dto = TriggerRunDto(
                        workflow_id=schedule.workflow_id,
                        parameters=schedule.parameters,
                    )
                    self._trigger_callback(dto)
                    schedule.last_run_at = current_time
                    self._schedule_repo.save(schedule)
                    triggered_schedule_ids.append(schedule.id)
                except Exception as exc:
                    logger.error(f"Failed to trigger schedule {schedule.id}: {exc}")

        return triggered_schedule_ids

    @staticmethod
    def _is_schedule_due(schedule: Schedule, now: datetime) -> bool:
        """Determine if a schedule has elapsed its cron interval."""
        if not croniter.is_valid(schedule.cron_expression):
            return False

        if schedule.last_run_at is None:
            # First time: mark it and wait for next interval
            schedule.last_run_at = now
            return False

        iter_cron = croniter(schedule.cron_expression, schedule.last_run_at)
        next_due = iter_cron.get_next(datetime)
        if next_due.tzinfo is None:
            next_due = next_due.replace(tzinfo=timezone.utc)

        return now >= next_due
