"""Subprocess script and command runner with live output streaming."""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path
from typing import Any

from open_factory.domain.entities import Step, StepType
from open_factory.infrastructure.runners.base import ExecutionContext, IStepRunner, StepResult


class ScriptRunner(IStepRunner):
    """Executes Python scripts, Bash scripts, or shell commands as isolated subprocesses."""

    def run(self, step: Step, context: ExecutionContext) -> StepResult:
        if context.is_cancelled():
            context.log("WARN", f"Step '{step.title}' skipped due to run cancellation.")
            return StepResult(exit_code=130, error_message="Execution cancelled before start.")

        context.output_dir.mkdir(parents=True, exist_ok=True)
        context.log("INFO", f"Starting step [{step.title}] (ID: {step.id})")
        context.log("INFO", f"Output directory: {context.output_dir}")

        command_args, temp_script_path = self._prepare_command(step, context)

        try:
            env = self._build_environment(context)
            process = subprocess.Popen(
                command_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                cwd=str(context.output_dir),
                bufsize=1,
            )

            # Stream stdout and stderr concurrently
            def read_stream(stream, log_level: str) -> None:
                for line in iter(stream.readline, ""):
                    clean_line = line.rstrip("\r\n")
                    if clean_line:
                        context.log(log_level, clean_line)
                stream.close()

            stdout_thread = threading.Thread(target=read_stream, args=(process.stdout, "INFO"))
            stderr_thread = threading.Thread(target=read_stream, args=(process.stderr, "ERROR"))
            stdout_thread.start()
            stderr_thread.start()

            # Poll for completion or cancellation
            while process.poll() is None:
                if context.is_cancelled():
                    context.log("WARN", f"Terminating process {process.pid} on cancellation...")
                    process.terminate()
                    try:
                        process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        process.kill()
                    return StepResult(exit_code=130, error_message="Process killed after cancellation.")
                time.sleep(0.1)

            stdout_thread.join()
            stderr_thread.join()

            exit_code = process.returncode
            if exit_code == 0:
                context.log("INFO", f"Step [{step.title}] completed successfully (exit code 0).")
                output_files = [str(p) for p in context.output_dir.glob("*") if p.is_file()]
                return StepResult(exit_code=0, output_files=output_files)

            error_msg = f"Step [{step.title}] exited with code {exit_code}."
            context.log("ERROR", error_msg)
            return StepResult(exit_code=exit_code, error_message=error_msg)

        except Exception as exc:
            context.log("ERROR", f"Step execution failed with exception: {exc}")
            return StepResult(exit_code=1, error_message=str(exc))
        finally:
            if temp_script_path and os.path.exists(temp_script_path):
                try:
                    os.unlink(temp_script_path)
                except OSError:
                    pass

    def _prepare_command(self, step: Step, context: ExecutionContext) -> tuple[list[str], str | None]:
        """Prepare executable command and write temporary script file if needed."""
        script = step.script_content or ""
        command_str = step.command or ""

        # Interpolate variables: ${OUT} and {{param}}
        interpolated_script = self._interpolate(script, context)
        interpolated_command = self._interpolate(command_str, context)

        if step.step_type == StepType.COMMAND and interpolated_command:
            return ["/bin/bash", "-c", interpolated_command], None

        if interpolated_script:
            # Create a temporary file
            suffix = ".py" if "python" in (interpolated_script[:50] or "") or step.step_type == StepType.SCRIPT else ".sh"
            with tempfile.NamedTemporaryFile("w", suffix=suffix, delete=False, encoding="utf-8") as temp_file:
                temp_file.write(interpolated_script)
                temp_path = temp_file.name

            os.chmod(temp_path, 0o755)

            if suffix == ".py":
                return [sys.executable, temp_path], temp_path
            return ["/bin/bash", temp_path], temp_path

        if interpolated_command:
            return ["/bin/bash", "-c", interpolated_command], None

        # Fallback dummy echo
        return ["echo", f"Step '{step.title}' has no script or command configured."], None

    def _interpolate(self, text: str, context: ExecutionContext) -> str:
        """Replace ${OUT} and {{param}} placeholders."""
        if not text:
            return text

        result = text.replace("${OUT}", str(context.output_dir))
        for key, value in context.parameters.items():
            result = result.replace(f"{{{{{key}}}}}", str(value))
        return result

    def _build_environment(self, context: ExecutionContext) -> dict[str, str]:
        """Assemble environment variables including output path and PATH."""
        env = os.environ.copy()
        env["OUT"] = str(context.output_dir)
        for key, value in context.parameters.items():
            env[f"FLOW_PARAM_{key.upper()}"] = str(value)
        return env
