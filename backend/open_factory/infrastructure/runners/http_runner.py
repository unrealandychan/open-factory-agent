"""HTTP step runner for API requests and webhook triggers."""

from __future__ import annotations

import json
from typing import Any
import httpx

from open_factory.domain.entities import Step
from open_factory.infrastructure.runners.base import ExecutionContext, IStepRunner, StepResult


class HttpRunner(IStepRunner):
    """Executes HTTP requests and writes response payloads to the output directory."""

    def run(self, step: Step, context: ExecutionContext) -> StepResult:
        if context.is_cancelled():
            context.log("WARN", f"Step '{step.title}' skipped due to run cancellation.")
            return StepResult(exit_code=130, error_message="Execution cancelled before start.")

        url = self._interpolate(step.http_url, context)
        method = (step.http_method or "GET").upper()
        context.output_dir.mkdir(parents=True, exist_ok=True)
        context.log("INFO", f"Sending {method} request to {url}")

        if not url:
            context.log("ERROR", "No HTTP URL provided for step.")
            return StepResult(exit_code=1, error_message="Missing HTTP URL.")

        try:
            with httpx.Client(timeout=60.0) as client:
                headers = dict(step.http_headers)
                response = client.request(method=method, url=url, headers=headers)
                context.log("INFO", f"HTTP Response status: {response.status_code}")

                # Save response payload
                response_file = context.output_dir / "response.json"
                try:
                    payload = response.json()
                    response_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
                except Exception:
                    response_file = context.output_dir / "response.txt"
                    response_file.write_text(response.text, encoding="utf-8")

                if 200 <= response.status_code < 300:
                    context.log("INFO", f"HTTP Step '{step.title}' succeeded.")
                    return StepResult(exit_code=0, output_files=[str(response_file)])

                error_msg = f"HTTP request failed with status code {response.status_code}"
                context.log("ERROR", error_msg)
                return StepResult(exit_code=1, error_message=error_msg, output_files=[str(response_file)])

        except Exception as exc:
            context.log("ERROR", f"HTTP request exception: {exc}")
            return StepResult(exit_code=1, error_message=str(exc))

    def _interpolate(self, text: str, context: ExecutionContext) -> str:
        if not text:
            return ""
        result = text.replace("${OUT}", str(context.output_dir))
        for key, value in context.parameters.items():
            result = result.replace(f"{{{{{key}}}}}", str(value))
        return result
