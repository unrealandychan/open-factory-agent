"""Domain-specific exceptions for Open Factory Agent."""


class DomainError(Exception):
    """Base domain exception."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class WorkflowNotFoundError(DomainError):
    """Raised when a requested workflow does not exist."""

    def __init__(self, workflow_id: str) -> None:
        super().__init__(f"Workflow with ID '{workflow_id}' was not found.")
        self.workflow_id = workflow_id


class StepNotFoundError(DomainError):
    """Raised when a referenced step is missing."""

    def __init__(self, step_id: str, workflow_id: str) -> None:
        super().__init__(f"Step '{step_id}' not found in workflow '{workflow_id}'.")
        self.step_id = step_id
        self.workflow_id = workflow_id


class RunNotFoundError(DomainError):
    """Raised when an execution run record is missing."""

    def __init__(self, run_id: str) -> None:
        super().__init__(f"Run with ID '{run_id}' was not found.")
        self.run_id = run_id


class ScheduleNotFoundError(DomainError):
    """Raised when a schedule definition is missing."""

    def __init__(self, schedule_id: str) -> None:
        super().__init__(f"Schedule with ID '{schedule_id}' was not found.")
        self.schedule_id = schedule_id


class WorkflowValidationError(DomainError):
    """Raised when workflow schema or dependencies violate domain constraints."""


class StepExecutionError(DomainError):
    """Raised when a step runner fails during execution."""
