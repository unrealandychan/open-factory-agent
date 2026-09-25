"""Data Transfer Objects (DTOs) for Application layer."""

from typing import Any
from pydantic import BaseModel, Field


class StepFieldDto(BaseModel):
    id: str
    label: str
    field_type: str = "text"
    placeholder: str = ""
    default_value: str = ""
    required: bool = False


class StepOutputDto(BaseModel):
    label: str
    filename: str
    file_type: str = "JSON"
    path: str = ""


class StepDto(BaseModel):
    id: str
    title: str
    step_type: str = Field(default="script", alias="type")
    description: str = ""
    order: int = 1
    depends_on: list[str] = Field(default_factory=list, alias="dependsOn")
    script_content: str = Field(default="", alias="script")
    command: str = ""
    http_url: str = Field(default="", alias="httpUrl")
    http_method: str = Field(default="GET", alias="httpMethod")
    http_headers: dict[str, str] = Field(default_factory=dict, alias="httpHeaders")
    prompt_template: str = Field(default="", alias="promptTemplate")
    fields: list[StepFieldDto] = Field(default_factory=list)
    outputs: list[StepOutputDto] = Field(default_factory=list)
    output_path: str = Field(default="", alias="outputPath")

    model_config = {
        "populate_by_name": True,
    }


class WorkflowCreateDto(BaseModel):
    id: str | None = None
    name: str
    description: str = ""
    steps: list[StepDto] = Field(default_factory=list)


class WorkflowUpdateDto(BaseModel):
    name: str | None = None
    description: str | None = None
    steps: list[StepDto] | None = None


class TriggerRunDto(BaseModel):
    workflow_id: str
    target_step_id: str | None = None
    parameters: dict[str, Any] = Field(default_factory=dict)


class ScheduleCreateDto(BaseModel):
    workflow_id: str
    cron_expression: str
    name: str = ""
    enabled: bool = True
    parameters: dict[str, Any] = Field(default_factory=dict)
