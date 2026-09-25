"""Dependency injection container for FastAPI routes."""

from open_factory.application.execution_service import ExecutionService
from open_factory.application.schedule_service import ScheduleService
from open_factory.application.workflow_service import WorkflowService
from open_factory.infrastructure.config import OUTPUTS_DIR, SCHEDULES_PATH, WORKFLOWS_PATH
from open_factory.infrastructure.repositories.json_schedule_repository import JsonScheduleRepository
from open_factory.infrastructure.repositories.json_workflow_repository import JsonWorkflowRepository
from open_factory.infrastructure.repositories.memory_run_repository import MemoryRunRepository
from open_factory.infrastructure.runners.http_runner import HttpRunner
from open_factory.infrastructure.runners.script_runner import ScriptRunner
from open_factory.infrastructure.scheduler.cron_engine import CronEngine

# Repositories
workflow_repo = JsonWorkflowRepository(WORKFLOWS_PATH)
run_repo = MemoryRunRepository()
schedule_repo = JsonScheduleRepository(SCHEDULES_PATH)

# Runners
script_runner = ScriptRunner()
http_runner = HttpRunner()

# Application Services
workflow_service = WorkflowService(workflow_repo)
execution_service = ExecutionService(
    workflow_repo=workflow_repo,
    run_repo=run_repo,
    base_output_dir=OUTPUTS_DIR,
    script_runner=script_runner,
    http_runner=http_runner,
)
schedule_service = ScheduleService(schedule_repo=schedule_repo, workflow_repo=workflow_repo)

# Scheduler Engine
cron_engine = CronEngine(
    schedule_repo=schedule_repo,
    trigger_callback=execution_service.trigger_run,
    check_interval_seconds=5.0,
)


def get_workflow_service() -> WorkflowService:
    return workflow_service


def get_execution_service() -> ExecutionService:
    return execution_service


def get_schedule_service() -> ScheduleService:
    return schedule_service
