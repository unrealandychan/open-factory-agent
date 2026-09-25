"""REST and SSE endpoints for execution runs and log streaming."""

import json
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from open_factory.api.dependencies import get_execution_service
from open_factory.application.dto import TriggerRunDto
from open_factory.application.execution_service import ExecutionService
from open_factory.domain.exceptions import RunNotFoundError, StepNotFoundError, WorkflowNotFoundError

router = APIRouter(prefix="/runs", tags=["Runs"])


@router.post("", status_code=status.HTTP_202_ACCEPTED)
def trigger_run(dto: TriggerRunDto, service: ExecutionService = Depends(get_execution_service)):
    """Trigger a workflow or specific step run."""
    try:
        run = service.trigger_run(dto)
        return run.to_dict()
    except WorkflowNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except StepNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


@router.get("", status_code=status.HTTP_200_OK)
def list_runs(limit: int = Query(50, ge=1, le=200), service: ExecutionService = Depends(get_execution_service)):
    """List recent execution runs."""
    runs = service.list_recent_runs(limit=limit)
    return {"runs": [r.to_dict() for r in runs]}


@router.get("/{run_id}", status_code=status.HTTP_200_OK)
def get_run(run_id: str, service: ExecutionService = Depends(get_execution_service)):
    """Get details and logs of a run."""
    try:
        run = service.get_run(run_id)
        return run.to_dict()
    except RunNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


@router.post("/{run_id}/cancel", status_code=status.HTTP_200_OK)
def cancel_run(run_id: str, service: ExecutionService = Depends(get_execution_service)):
    """Cancel an active execution run."""
    try:
        cancelled = service.cancel_run(run_id)
        return cancelled.to_dict()
    except RunNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


@router.get("/{run_id}/stream")
def stream_run_logs(run_id: str, service: ExecutionService = Depends(get_execution_service)):
    """Stream real-time execution events and logs via Server-Sent Events (SSE)."""
    try:
        service.get_run(run_id)
    except RunNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)

    def event_generator():
        for event in service.stream_logs(run_id):
            payload = json.dumps(event.get("data", {}))
            yield f"event: {event.get('event', 'message')}\ndata: {payload}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
