"""Application service orchestrating workflow and step runs with real-time log event streaming."""

from __future__ import annotations

import queue
import threading
import uuid
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Callable, Generator

from open_factory.application.dto import TriggerRunDto
from open_factory.domain.entities import (
    LogEntry,
    Run,
    RunStatus,
    Step,
    StepRun,
    StepType,
    Workflow,
    current_utc_time,
)
from open_factory.domain.exceptions import RunNotFoundError, StepNotFoundError, WorkflowNotFoundError
from open_factory.domain.repositories import IRunRepository, IWorkflowRepository
from open_factory.infrastructure.runners.base import ExecutionContext, IStepRunner, StepResult
from open_factory.infrastructure.runners.http_runner import HttpRunner
from open_factory.infrastructure.runners.script_runner import ScriptRunner


class ExecutionService:
    """Manages asynchronous workflow executions, step dependency resolution, and real-time log feeds."""

    def __init__(
        self,
        workflow_repo: IWorkflowRepository,
        run_repo: IRunRepository,
        base_output_dir: Path,
        script_runner: IStepRunner | None = None,
        http_runner: IStepRunner | None = None,
    ) -> None:
        self._workflow_repo = workflow_repo
        self._run_repo = run_repo
        self._base_output_dir = Path(base_output_dir).resolve()
        self._script_runner = script_runner or ScriptRunner()
        self._http_runner = http_runner or HttpRunner()

        # Active executions and cancellation events
        self._active_runs: dict[str, threading.Thread] = {}
        self._cancel_events: dict[str, threading.Event] = {}
        # Subscriber queues for Server-Sent Events: run_id -> list[queue.Queue]
        self._subscribers: dict[str, list[queue.Queue]] = defaultdict(list)
        self._lock = threading.Lock()

    def get_run(self, run_id: str) -> Run:
        """Fetch run by ID or raise RunNotFoundError."""
        run = self._run_repo.get_by_id(run_id)
        if not run:
            raise RunNotFoundError(run_id)
        return run

    def list_recent_runs(self, limit: int = 50) -> list[Run]:
        """List recent runs."""
        return list(self._run_repo.list_recent(limit=limit))

    def trigger_run(self, dto: TriggerRunDto) -> Run:
        """Initialize and launch an asynchronous run."""
        workflow = self._workflow_repo.get_by_id(dto.workflow_id)
        if not workflow:
            raise WorkflowNotFoundError(dto.workflow_id)

        target_step: Step | None = None
        if dto.target_step_id:
            target_step = workflow.get_step(dto.target_step_id)
            if not target_step:
                raise StepNotFoundError(dto.target_step_id, dto.workflow_id)

        run_id = f"run-{uuid.uuid4().hex[:12]}"
        run = Run(
            id=run_id,
            workflow_id=dto.workflow_id,
            status=RunStatus.RUNNING,
            target_step_id=dto.target_step_id,
            parameters=dict(dto.parameters),
            step_runs=[],
            logs=[],
            started_at=current_utc_time(),
        )

        steps_to_run = [target_step] if target_step else self._resolve_execution_order(workflow)
        for s in steps_to_run:
            run.step_runs.append(StepRun(step_id=s.id, title=s.title, status=RunStatus.PENDING))

        self._run_repo.save(run)

        cancel_event = threading.Event()
        with self._lock:
            self._cancel_events[run_id] = cancel_event

        thread = threading.Thread(
            target=self._execute_run_thread,
            args=(run_id, workflow, steps_to_run, cancel_event),
            daemon=True,
        )
        with self._lock:
            self._active_runs[run_id] = thread
        thread.start()

        return run

    def cancel_run(self, run_id: str) -> Run:
        """Cancel an in-flight run."""
        run = self.get_run(run_id)
        if run.status != RunStatus.RUNNING:
            return run

        with self._lock:
            event = self._cancel_events.get(run_id)
            if event:
                event.set()

        run.mark_cancelled()
        self._run_repo.save(run)
        self._broadcast(run_id, {"type": "status", "status": run.status.value})
        return run

    def stream_logs(self, run_id: str) -> Generator[dict[str, Any], None, None]:
        """Generator yielding SSE event dictionaries for live logs and status changes."""
        run = self.get_run(run_id)
        q: queue.Queue = queue.Queue()

        # Send historic logs first
        for log in run.logs:
            yield {"event": "log", "data": log.to_dict()}

        if run.status != RunStatus.RUNNING:
            yield {"event": "status", "data": run.to_dict()}
            return

        with self._lock:
            self._subscribers[run_id].append(q)

        try:
            while True:
                try:
                    event = q.get(timeout=1.0)
                    yield event
                    if event.get("event") == "status":
                        status = event.get("data", {}).get("status")
                        if status in (RunStatus.SUCCESS.value, RunStatus.FAILED.value, RunStatus.CANCELLED.value):
                            break
                except queue.Empty:
                    # Heartbeat ping
                    yield {"event": "ping", "data": {}}
                    current = self.get_run(run_id)
                    if current.status != RunStatus.RUNNING:
                        yield {"event": "status", "data": current.to_dict()}
                        break
        finally:
            with self._lock:
                if q in self._subscribers[run_id]:
                    self._subscribers[run_id].remove(q)

    def _execute_run_thread(
        self,
        run_id: str,
        workflow: Workflow,
        steps: list[Step],
        cancel_event: threading.Event,
    ) -> None:
        """Worker thread executing the steps of a run."""
        run = self.get_run(run_id)

        def log_handler(level: str, message: str, step_id: str | None = None) -> None:
            entry = run.append_log(level, message, step_id)
            self._run_repo.save(run)
            self._broadcast(run_id, {"event": "log", "data": entry.to_dict()})

        log_handler("INFO", f"Run {run_id} started for workflow '{workflow.name}'")

        overall_success = True
        for step in steps:
            if cancel_event.is_set():
                log_handler("WARN", f"Run cancelled before step '{step.title}'.", step.id)
                overall_success = False
                break

            step_run = next(sr for sr in run.step_runs if sr.step_id == step.id)
            step_run.status = RunStatus.RUNNING
            step_run.started_at = current_utc_time()
            self._run_repo.save(run)
            self._broadcast(run_id, {"event": "step_status", "data": step_run.to_dict()})

            output_dir = self._base_output_dir / workflow.id / step.id
            context = ExecutionContext(
                run_id=run_id,
                step_id=step.id,
                output_dir=output_dir,
                parameters=run.parameters,
                cancel_event=cancel_event,
                log_callback=lambda lvl, msg, sid=step.id: log_handler(lvl, msg, sid),
            )

            runner = self._select_runner(step)
            result: StepResult = runner.run(step, context)

            step_run.finished_at = current_utc_time()
            step_run.exit_code = result.exit_code
            step_run.error_message = result.error_message
            step_run.output_files = result.output_files

            if result.exit_code == 0:
                step_run.status = RunStatus.SUCCESS
            else:
                step_run.status = RunStatus.FAILED
                overall_success = False

            self._run_repo.save(run)
            self._broadcast(run_id, {"event": "step_status", "data": step_run.to_dict()})

            if result.exit_code != 0:
                log_handler("ERROR", f"Step '{step.title}' failed. Stopping execution.", step.id)
                break

        if cancel_event.is_set():
            run.mark_cancelled()
        elif overall_success:
            run.mark_success()
            log_handler("INFO", f"Workflow execution finished successfully.")
        else:
            run.mark_failed("One or more steps failed during execution.")

        self._run_repo.save(run)
        self._broadcast(run_id, {"event": "status", "data": run.to_dict()})

        with self._lock:
            self._active_runs.pop(run_id, None)
            self._cancel_events.pop(run_id, None)

    def _select_runner(self, step: Step) -> IStepRunner:
        if step.step_type == StepType.HTTP:
            return self._http_runner
        return self._script_runner

    def _broadcast(self, run_id: str, event_payload: dict[str, Any]) -> None:
        with self._lock:
            for q in list(self._subscribers.get(run_id, [])):
                try:
                    q.put_nowait(event_payload)
                except queue.Full:
                    pass

    @staticmethod
    def _resolve_execution_order(workflow: Workflow) -> list[Step]:
        """Topological sort respecting dependencies, with fallback to order field."""
        step_map = {s.id: s for s in workflow.steps}
        indegree = {s.id: 0 for s in workflow.steps}
        dependents = defaultdict(list)

        for s in workflow.steps:
            for dep in s.depends_on:
                if dep in step_map:
                    indegree[s.id] += 1
                    dependents[dep].append(s.id)

        queue_steps = deque([sid for sid, deg in indegree.items() if deg == 0])
        # Sort initial queue by step order
        queue_steps = deque(sorted(queue_steps, key=lambda sid: step_map[sid].order))

        ordered: list[Step] = []
        while queue_steps:
            current_id = queue_steps.popleft()
            ordered.append(step_map[current_id])
            for dep in dependents[current_id]:
                indegree[dep] -= 1
                if indegree[dep] == 0:
                    queue_steps.append(dep)

        if len(ordered) != len(workflow.steps):
            # Fallback if any cycles remain
            return sorted(workflow.steps, key=lambda s: s.order)

        return ordered
