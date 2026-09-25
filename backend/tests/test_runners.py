"""Tests for ScriptRunner and HttpRunner."""

import threading
import time
from pathlib import Path
import pytest

from open_factory.domain.entities import Step, StepType
from open_factory.infrastructure.runners.base import ExecutionContext
from open_factory.infrastructure.runners.script_runner import ScriptRunner


def test_script_runner_python_execution(temp_dir):
    runner = ScriptRunner()
    logs = []

    def log_cb(lvl, msg):
        logs.append((lvl, msg))

    context = ExecutionContext(
        run_id="run-test",
        step_id="step-py",
        output_dir=temp_dir / "out",
        parameters={"name": "World"},
        log_callback=log_cb,
    )

    script_content = """
import os
print("Hello {{name}}!")
with open("${OUT}/result.txt", "w") as f:
    f.write("done")
"""
    step = Step(
        id="step-py",
        title="Python Script Step",
        step_type=StepType.SCRIPT,
        script_content=script_content,
    )

    result = runner.run(step, context)

    assert result.exit_code == 0
    assert result.error_message is None
    assert (temp_dir / "out" / "result.txt").exists()
    assert (temp_dir / "out" / "result.txt").read_text() == "done"
    assert any("Hello World!" in msg for lvl, msg in logs)


def test_script_runner_command_execution(temp_dir):
    runner = ScriptRunner()
    logs = []

    context = ExecutionContext(
        run_id="run-cmd",
        step_id="step-cmd",
        output_dir=temp_dir / "cmd_out",
        parameters={},
        log_callback=lambda lvl, msg: logs.append(msg),
    )

    step = Step(
        id="step-cmd",
        title="Bash Command Step",
        step_type=StepType.COMMAND,
        command="echo 'Testing command runner' > ${OUT}/cmd.txt",
    )

    result = runner.run(step, context)
    assert result.exit_code == 0
    assert (temp_dir / "cmd_out" / "cmd.txt").exists()
    assert "Testing command runner" in (temp_dir / "cmd_out" / "cmd.txt").read_text()


def test_script_runner_failure(temp_dir):
    runner = ScriptRunner()
    context = ExecutionContext(
        run_id="run-fail",
        step_id="step-fail",
        output_dir=temp_dir / "fail_out",
    )

    step = Step(
        id="step-fail",
        title="Failing Step",
        step_type=StepType.COMMAND,
        command="exit 42",
    )

    result = runner.run(step, context)
    assert result.exit_code == 42
    assert "exited with code 42" in (result.error_message or "")


def test_script_runner_cancellation(temp_dir):
    runner = ScriptRunner()
    cancel_event = threading.Event()

    context = ExecutionContext(
        run_id="run-cancel",
        step_id="step-cancel",
        output_dir=temp_dir / "cancel_out",
        cancel_event=cancel_event,
    )

    step = Step(
        id="step-cancel",
        title="Sleep Step",
        step_type=StepType.COMMAND,
        command="sleep 5",
    )

    # Cancel after 200ms
    def trigger_cancel():
        time.sleep(0.2)
        cancel_event.set()

    t = threading.Thread(target=trigger_cancel)
    t.start()

    result = runner.run(step, context)
    t.join()

    assert result.exit_code == 130
    assert "cancel" in (result.error_message or "").lower()
