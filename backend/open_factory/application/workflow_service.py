"""Application service orchestrating Workflow domain logic and persistence."""

from __future__ import annotations

import uuid
from typing import Sequence

from open_factory.application.dto import StepDto, WorkflowCreateDto, WorkflowUpdateDto
from open_factory.domain.entities import Step, StepField, StepOutput, StepType, Workflow, current_utc_time
from open_factory.domain.exceptions import WorkflowNotFoundError
from open_factory.domain.repositories import IWorkflowRepository


class WorkflowService:
    """Use case service for Workflow management."""

    def __init__(self, repository: IWorkflowRepository) -> None:
        self._repository = repository

    def list_workflows(self) -> Sequence[Workflow]:
        """List all registered workflows."""
        return self._repository.list_all()

    def get_workflow(self, workflow_id: str) -> Workflow:
        """Retrieve a workflow by ID or raise WorkflowNotFoundError."""
        workflow = self._repository.get_by_id(workflow_id)
        if workflow is None:
            raise WorkflowNotFoundError(workflow_id)
        return workflow

    def create_workflow(self, dto: WorkflowCreateDto) -> Workflow:
        """Create, validate, and persist a new workflow."""
        workflow_id = dto.id or f"wf-{uuid.uuid4().hex[:8]}"
        steps = [self._map_step_dto_to_domain(step_dto) for step_dto in dto.steps]
        now = current_utc_time()

        workflow = Workflow(
            id=workflow_id,
            name=dto.name,
            description=dto.description,
            steps=steps,
            created_at=now,
            updated_at=now,
        )
        workflow.validate()
        self._repository.save(workflow)
        return workflow

    def update_workflow(self, workflow_id: str, dto: WorkflowUpdateDto) -> Workflow:
        """Update an existing workflow."""
        existing = self.get_workflow(workflow_id)

        if dto.name is not None:
            existing.name = dto.name
        if dto.description is not None:
            existing.description = dto.description
        if dto.steps is not None:
            existing.steps = [self._map_step_dto_to_domain(s) for s in dto.steps]

        existing.updated_at = current_utc_time()
        existing.validate()
        self._repository.save(existing)
        return existing

    def delete_workflow(self, workflow_id: str) -> None:
        """Delete a workflow by ID."""
        success = self._repository.delete(workflow_id)
        if not success:
            raise WorkflowNotFoundError(workflow_id)

    def duplicate_workflow(self, workflow_id: str, new_name: str | None = None) -> Workflow:
        """Clone an existing workflow under a new ID."""
        source = self.get_workflow(workflow_id)
        new_id = f"wf-{uuid.uuid4().hex[:8]}"
        cloned_steps = [
            Step(
                id=f"{step.id}-copy",
                title=step.title,
                step_type=step.step_type,
                description=step.description,
                order=step.order,
                depends_on=[f"{dep}-copy" for dep in step.depends_on],
                script_content=step.script_content,
                command=step.command,
                http_url=step.http_url,
                http_method=step.http_method,
                http_headers=dict(step.http_headers),
                prompt_template=step.prompt_template,
                fields=list(step.fields),
                outputs=list(step.outputs),
                output_path=step.output_path,
            )
            for step in source.steps
        ]

        now = current_utc_time()
        cloned = Workflow(
            id=new_id,
            name=new_name or f"{source.name} (Copy)",
            description=source.description,
            steps=cloned_steps,
            created_at=now,
            updated_at=now,
        )
        cloned.validate()
        self._repository.save(cloned)
        return cloned

    @staticmethod
    def _map_step_dto_to_domain(dto: StepDto) -> Step:
        """Convert a StepDto into a domain Step entity."""
        try:
            step_type = StepType(dto.step_type.lower())
        except ValueError:
            step_type = StepType.SCRIPT

        fields = [
            StepField(
                id=f.id,
                label=f.label,
                field_type=f.field_type,
                placeholder=f.placeholder,
                default_value=f.default_value,
                required=f.required,
            )
            for f in dto.fields
        ]

        outputs = [
            StepOutput(
                label=o.label,
                filename=o.filename,
                file_type=o.file_type,
                path=o.path,
            )
            for o in dto.outputs
        ]

        return Step(
            id=dto.id,
            title=dto.title,
            step_type=step_type,
            description=dto.description,
            order=dto.order,
            depends_on=dto.depends_on,
            script_content=dto.script_content,
            command=dto.command,
            http_url=dto.http_url,
            http_method=dto.http_method,
            http_headers=dto.http_headers,
            prompt_template=dto.prompt_template,
            fields=fields,
            outputs=outputs,
            output_path=dto.output_path,
        )
