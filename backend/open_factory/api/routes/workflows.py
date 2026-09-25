"""REST API endpoints for Workflow aggregate management."""

from fastapi import APIRouter, Depends, HTTPException, status
from open_factory.api.dependencies import get_workflow_service
from open_factory.application.dto import WorkflowCreateDto, WorkflowUpdateDto
from open_factory.application.workflow_service import WorkflowService
from open_factory.domain.exceptions import WorkflowNotFoundError, WorkflowValidationError

router = APIRouter(prefix="/workflows", tags=["Workflows"])


@router.get("", status_code=status.HTTP_200_OK)
def list_workflows(service: WorkflowService = Depends(get_workflow_service)):
    """List all workflows."""
    workflows = service.list_workflows()
    return {"workflows": [w.to_dict() for w in workflows]}


@router.get("/{workflow_id}", status_code=status.HTTP_200_OK)
def get_workflow(workflow_id: str, service: WorkflowService = Depends(get_workflow_service)):
    """Retrieve a workflow by ID."""
    try:
        wf = service.get_workflow(workflow_id)
        return wf.to_dict()
    except WorkflowNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_workflow(dto: WorkflowCreateDto, service: WorkflowService = Depends(get_workflow_service)):
    """Create a new workflow."""
    try:
        created = service.create_workflow(dto)
        return created.to_dict()
    except WorkflowValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.message)


@router.put("/{workflow_id}", status_code=status.HTTP_200_OK)
def update_workflow(
    workflow_id: str,
    dto: WorkflowUpdateDto,
    service: WorkflowService = Depends(get_workflow_service),
):
    """Update an existing workflow."""
    try:
        updated = service.update_workflow(workflow_id, dto)
        return updated.to_dict()
    except WorkflowNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except WorkflowValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.message)


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workflow(workflow_id: str, service: WorkflowService = Depends(get_workflow_service)):
    """Delete a workflow."""
    try:
        service.delete_workflow(workflow_id)
    except WorkflowNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


@router.post("/{workflow_id}/duplicate", status_code=status.HTTP_201_CREATED)
def duplicate_workflow(
    workflow_id: str,
    service: WorkflowService = Depends(get_workflow_service),
):
    """Clone an existing workflow."""
    try:
        cloned = service.duplicate_workflow(workflow_id)
        return cloned.to_dict()
    except WorkflowNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
