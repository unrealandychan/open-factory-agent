"""Test configuration and shared fixtures for Open Factory Agent."""

import shutil
import tempfile
from pathlib import Path
import pytest

from open_factory.domain.entities import Step, StepField, StepOutput, StepType, Workflow
from open_factory.infrastructure.repositories.json_schedule_repository import JsonScheduleRepository
from open_factory.infrastructure.repositories.json_workflow_repository import JsonWorkflowRepository
from open_factory.infrastructure.repositories.memory_run_repository import MemoryRunRepository


@pytest.fixture
def temp_dir():
    d = tempfile.mkdtemp()
    yield Path(d)
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def sample_workflow():
    step1 = Step(
        id="step-1",
        title="Step One",
        step_type=StepType.SCRIPT,
        order=1,
        script_content="print('Hello from Step 1')",
        output_path="step1_out",
    )
    step2 = Step(
        id="step-2",
        title="Step Two",
        step_type=StepType.SCRIPT,
        order=2,
        depends_on=["step-1"],
        script_content="print('Hello from Step 2')",
        output_path="step2_out",
    )
    return Workflow(
        id="wf-test-1",
        name="Test Workflow",
        description="A test workflow",
        steps=[step1, step2],
    )


@pytest.fixture
def workflow_repo(temp_dir):
    return JsonWorkflowRepository(temp_dir / "workflows.json")


@pytest.fixture
def schedule_repo(temp_dir):
    return JsonScheduleRepository(temp_dir / "schedules.json")


@pytest.fixture
def run_repo():
    return MemoryRunRepository()
