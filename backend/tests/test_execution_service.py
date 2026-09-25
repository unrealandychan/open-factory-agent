"""Tests for ExecutionService."""

import time
import pytest

from open_factory.application.dto import TriggerRunDto
from open_factory.application.execution_service import ExecutionService
from open_factory.domain.entities import RunStatus, Step, StepType, Workflow


def test_execution_service_full_workflow_run(sample_workflow, workflow_repo, run_repo, temp_dir):
    workflow_repo.save(sample_workflow)

    service = ExecutionService(
        workflow_repo=workflow_repo,
        run_repo=run_repo,
        base_output_dir=temp_dir / "outputs",
    )

    dto = TriggerRunDto(workflow_id=sample_workflow.id)
    run = service.trigger_run(dto)

    assert run.id is not None
    assert run.workflow_id == sample_workflow.id

    # Wait for execution thread to finish
    max_wait = 5.0
    start = time.time()
    while time.time() - start < max_wait:
        current_run = service.get_run(run.id)
        if current_run.status in (RunStatus.SUCCESS, RunStatus.FAILED):
            break
        time.sleep(0.1)

    completed_run = service.get_run(run.id)
    assert completed_run.status == RunStatus.SUCCESS
    assert len(completed_run.step_runs) == 2
    assert all(sr.status == RunStatus.SUCCESS for sr in completed_run.step_runs)
    assert len(completed_run.logs) > 0


def test_execution_service_single_step_run(sample_workflow, workflow_repo, run_repo, temp_dir):
    workflow_repo.save(sample_workflow)

    service = ExecutionService(
        workflow_repo=workflow_repo,
        run_repo=run_repo,
        base_output_dir=temp_dir / "outputs",
    )

    dto = TriggerRunDto(workflow_id=sample_workflow.id, target_step_id="step-1")
    run = service.trigger_run(dto)

    max_wait = 5.0
    start = time.time()
    while time.time() - start < max_wait:
        current_run = service.get_run(run.id)
        if current_run.status in (RunStatus.SUCCESS, RunStatus.FAILED):
            break
        time.sleep(0.1)

    completed_run = service.get_run(run.id)
    assert completed_run.status == RunStatus.SUCCESS
    assert len(completed_run.step_runs) == 1
    assert completed_run.step_runs[0].step_id == "step-1"


def test_execution_service_cancel_run(workflow_repo, run_repo, temp_dir):
    slow_step = Step(
        id="slow-step",
        title="Slow Step",
        step_type=StepType.COMMAND,
        command="sleep 10",
    )
    slow_wf = Workflow(id="wf-slow", name="Slow Workflow", steps=[slow_step])
    workflow_repo.save(slow_wf)

    service = ExecutionService(
        workflow_repo=workflow_repo,
        run_repo=run_repo,
        base_output_dir=temp_dir / "outputs",
    )

    dto = TriggerRunDto(workflow_id=slow_wf.id)
    run = service.trigger_run(dto)

    # Allow it to start
    time.sleep(0.2)
    service.cancel_run(run.id)

    time.sleep(0.5)
    cancelled_run = service.get_run(run.id)
    assert cancelled_run.status == RunStatus.CANCELLED
