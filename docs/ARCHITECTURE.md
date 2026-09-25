# Open Factory Agent (OFA) Architecture Specification

## 1. Executive Summary & Vision

**Open Factory Agent** is an open-source, modular, local-first workflow automation platform designed to execute multi-step workflows, AI agents, and local automation tasks with complete transparency and zero vendor lock-in.

Key Design Tenets:
- **Zero DRM / Open Source**: Fully open-source under the MIT License. No paywalls, license keys, or obfuscated telemetry.
- **Clean Code & Domain-Driven Design (DDD)**: Strict separation of concerns across Domain, Application, Infrastructure, and Presentation layers.
- **High Observability & Testability**: Every workflow run emits structured domain events and real-time execution streams.
- **Agentic & Human-in-the-Loop Ready**: Seamlessly orchestrates scripts, AI prompt invocations, HTTP endpoints, and shell tasks.

---

## 2. Bounded Contexts & DDD Layering

```
+-------------------------------------------------------------+
|                     Presentation Layer                      |
|   FastAPI REST API & SSE Endpoints  |  Vite/React Dashboard |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                     Application Layer                       |
|   WorkflowService   |   ExecutionService   | ScheduleService|
|   (Use cases, DTOs, Event dispatching, Flow orchestration)  |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                       Domain Layer                          |
|   Entities: Workflow, Step, Run, Schedule, LogEntry         |
|   Value Objects: StepType, RunStatus, CronExpression        |
|   Domain Events & Repository Interfaces                     |
+-------------------------------------------------------------+
                              ^
                              | (implements interfaces)
+-------------------------------------------------------------+
|                    Infrastructure Layer                     |
|   JsonWorkflowRepository  |  LocalScriptRunner              |
|   MemoryRunRepository     |  BackgroundScheduler            |
+-------------------------------------------------------------+
```

### 2.1 Domain Layer (`open_factory.domain`)
The domain layer encapsulates enterprise business rules and entities without any external framework dependencies.

- **Workflow Aggregate**:
  - `id: str`: Unique workflow identifier.
  - `name: str`: Human-readable name.
  - `description: str`: Purpose and description.
  - `steps: list[Step]`: Ordered sequence of execution steps.
  - Invariants: Step IDs within a workflow must be unique; dependencies (`depends_on`) must not form cycles.

- **Step Entity**:
  - `id: str`: Step ID.
  - `title: str`: Step title.
  - `type: StepType`: `SCRIPT`, `PROMPT`, `HTTP`, `COMMAND`.
  - `config: dict`: Script content, prompt parameters, environment variables, or HTTP configuration.
  - `depends_on: list[str]`: List of prerequisite step IDs.
  - `output_path: str`: Directory or file path for step artifacts.

- **Run Aggregate**:
  - `id: str`: Execution run UUID.
  - `workflow_id: str`: Target workflow ID.
  - `status: RunStatus`: `PENDING`, `RUNNING`, `SUCCESS`, `FAILED`, `CANCELLED`.
  - `step_runs: list[StepRun]`: Progress, status, and exit codes of individual steps.
  - `logs: list[LogEntry]`: Real-time structured log entries (timestamp, level, message, step_id).
  - `started_at / finished_at`: Timestamps.

- **Schedule Entity**:
  - `id: str`: Schedule UUID.
  - `workflow_id: str`: Workflow to trigger.
  - `cron_expression: str`: Cron schedule string (e.g. `0 9 * * *`).
  - `enabled: bool`: Active toggle.

- **Repository Interfaces**:
  - `WorkflowRepository`: Abstract interface for `get`, `list`, `save`, `delete`.
  - `RunRepository`: Abstract interface for `get`, `list`, `save`, `append_log`.

### 2.2 Application Layer (`open_factory.application`)
Orchestrates domain models to perform user actions.

- **WorkflowService**: Workflow validation, persistence, cloning, and schema conversion.
- **ExecutionService**:
  - Manages asynchronous workflow and individual step runs.
  - Resolves dependency graphs and parallel/sequential execution order.
  - Dispatches execution events to listeners (e.g., SSE/WebSocket subscribers).
- **ScheduleService**: Evaluates cron triggers and triggers executions.

### 2.3 Infrastructure Layer (`open_factory.infrastructure`)
Concrete implementations of storage, execution runners, and system interfaces.

- **JsonWorkflowRepository**: Thread-safe atomic JSON file persistence with automatic backup rotation.
- **Runners**:
  - `ScriptRunner`: Subprocess execution runner with real-time stdout/stderr capture and cancellation support.
  - `HttpRunner`: Asynchronous HTTP request executor.
- **SchedulerEngine**: Background thread timer evaluating active cron schedules.

### 2.4 Presentation Layer (`open_factory.api` & `frontend`)
- **Backend API (FastAPI)**:
  - Clean REST endpoints (`/api/v1/...`).
  - Server-Sent Events (SSE) `/api/v1/runs/{run_id}/stream` for real-time live log output.
- **Frontend (Vite + React + Tailwind)**:
  - Dashboard: Grid/list of workflows, quick status badges, trigger buttons.
  - Execution Monitor: Step cards, live logs, artifact previews.
  - Workflow Editor: Step visualizer and configuration panel.

---

## 3. Workflow Schema Specification

Workflows are serialized in a clean JSON format:

```json
{
  "version": "1.0",
  "workflows": [
    {
      "id": "workflow-news-digest",
      "name": "News Collector & Digest Agent",
      "description": "Fetches RSS feeds and generates markdown summaries",
      "steps": [
        {
          "id": "step-fetch-rss",
          "title": "Fetch RSS Feed",
          "type": "script",
          "order": 1,
          "depends_on": [],
          "script": "#!/usr/bin/env python3\n...",
          "output_path": "outputs/news/fetch_result.json"
        },
        {
          "id": "step-generate-markdown",
          "title": "Generate Markdown Digest",
          "type": "script",
          "order": 2,
          "depends_on": ["step-fetch-rss"],
          "script": "#!/usr/bin/env python3\n...",
          "output_path": "outputs/news/digest.md"
        }
      ]
    }
  ]
}
```

---

## 4. Execution Engine Lifecycle

1. **Trigger**: User triggers run via REST API or Scheduler triggers run.
2. **Run Initialization**: `ExecutionService` creates `Run` entity with status `RUNNING`.
3. **Step Resolution**: Topologically sorts steps based on `depends_on`.
4. **Execution**:
   - Spawns subprocess or handler for the step.
   - Captures stdout/stderr in real time and streams to SSE subscribers.
   - Interpolates `${OUT}` and environment variables into the step execution context.
   - Verifies step outputs and logs completion status.
5. **Finalization**: `Run` status updated to `SUCCESS` or `FAILED`.
