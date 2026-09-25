"""Domain entities and business rule validation tests."""

import pytest
from open_factory.domain.entities import Step, StepField, StepOutput, StepType, Workflow, Run, RunStatus
from open_factory.domain.exceptions import WorkflowValidationError


def test_workflow_validation_success(sample_workflow):
    sample_workflow.validate()
    assert len(sample_workflow.steps) == 2
    assert sample_workflow.get_step("step-1") is not None
    assert sample_workflow.get_step("non-existent") is None


def test_workflow_validation_duplicate_steps():
    step1 = Step(id="dup-step", title="Step 1", step_type=StepType.SCRIPT)
    step2 = Step(id="dup-step", title="Step 2", step_type=StepType.SCRIPT)
    wf = Workflow(id="wf-dup", name="Duplicate Test", steps=[step1, step2])

    with pytest.raises(WorkflowValidationError, match="duplicate step IDs"):
        wf.validate()


def test_workflow_validation_missing_dependency():
    step1 = Step(id="s1", title="S1", step_type=StepType.SCRIPT, depends_on=["missing-step"])
    wf = Workflow(id="wf-missing", name="Missing Dep Test", steps=[step1])

    with pytest.raises(WorkflowValidationError, match="non-existent step"):
        wf.validate()


def test_workflow_validation_self_dependency():
    step1 = Step(id="s1", title="S1", step_type=StepType.SCRIPT, depends_on=["s1"])
    wf = Workflow(id="wf-self", name="Self Dep Test", steps=[step1])

    with pytest.raises(WorkflowValidationError, match="cannot depend on itself"):
        wf.validate()


def test_workflow_validation_circular_dependency():
    step1 = Step(id="s1", title="S1", step_type=StepType.SCRIPT, depends_on=["s2"])
    step2 = Step(id="s2", title="S2", step_type=StepType.SCRIPT, depends_on=["s1"])
    wf = Workflow(id="wf-circ", name="Circular Dep Test", steps=[step1, step2])

    with pytest.raises(WorkflowValidationError, match="circular dependencies"):
        wf.validate()


def test_run_aggregate_state_transitions():
    run = Run(id="run-1", workflow_id="wf-1")
    assert run.status == RunStatus.PENDING

    log = run.append_log("INFO", "Starting execution")
    assert len(run.logs) == 1
    assert log.message == "Starting execution"

    run.mark_success()
    assert run.status == RunStatus.SUCCESS
    assert run.finished_at is not None

    run.mark_failed("Test error")
    assert run.status == RunStatus.FAILED
    assert run.error_message == "Test error"

    run.mark_cancelled()
    assert run.status == RunStatus.CANCELLED
