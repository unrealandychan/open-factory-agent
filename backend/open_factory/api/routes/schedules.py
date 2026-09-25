"""REST API endpoints for Schedule management."""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from open_factory.api.dependencies import get_schedule_service
from open_factory.application.dto import ScheduleCreateDto
from open_factory.application.schedule_service import InvalidCronError, ScheduleService
from open_factory.domain.exceptions import ScheduleNotFoundError, WorkflowNotFoundError

router = APIRouter(prefix="/schedules", tags=["Schedules"])


@router.get("", status_code=status.HTTP_200_OK)
def list_schedules(service: ScheduleService = Depends(get_schedule_service)):
    """List all workflow schedules."""
    schedules = service.list_schedules()
    return {"schedules": [s.to_dict() for s in schedules]}


@router.post("", status_code=status.HTTP_201_CREATED)
def create_schedule(dto: ScheduleCreateDto, service: ScheduleService = Depends(get_schedule_service)):
    """Create a new schedule."""
    try:
        schedule = service.create_schedule(dto)
        return schedule.to_dict()
    except WorkflowNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except InvalidCronError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)


@router.patch("/{schedule_id}/toggle", status_code=status.HTTP_200_OK)
def toggle_schedule(
    schedule_id: str,
    enabled: bool = Query(...),
    service: ScheduleService = Depends(get_schedule_service),
):
    """Enable or disable a schedule."""
    try:
        updated = service.toggle_schedule(schedule_id, enabled)
        return updated.to_dict()
    except ScheduleNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_schedule(schedule_id: str, service: ScheduleService = Depends(get_schedule_service)):
    """Delete a schedule."""
    try:
        service.delete_schedule(schedule_id)
    except ScheduleNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
