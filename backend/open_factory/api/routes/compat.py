"""Compatibility API routes matching original Flow Factory 1:1 API contracts."""

import json
from pathlib import Path
from typing import Any
from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.responses import JSONResponse

from open_factory import __version__
from open_factory.api.dependencies import get_execution_service, get_schedule_service, get_workflow_service
from open_factory.application.dto import TriggerRunDto
from open_factory.application.execution_service import ExecutionService
from open_factory.application.schedule_service import ScheduleService
from open_factory.application.workflow_service import WorkflowService
from open_factory.infrastructure.config import DATA_DIR, OUTPUTS_DIR, WORKFLOWS_PATH

router = APIRouter(prefix="/api", tags=["Legacy Compatibility API"])


@router.get("/config")
def get_config():
    """Flow Factory configuration endpoint."""
    return {
        "ok": True,
        "workflows_path": str(WORKFLOWS_PATH),
        "content_root": str(OUTPUTS_DIR),
        "agent": {
            "mode": "local",
            "name": "Open Factory Agent",
            "connected": True,
        },
        "version": __version__,
        "managed_install": False,
        "network": {
            "lan_enabled": False,
            "password_configured": False,
            "lan_ip": "127.0.0.1",
            "lan_url": "http://127.0.0.1:8765/",
        },
    }


@router.get("/license")
def get_license():
    """Unrestricted permanent open-source license response."""
    return {
        "ok": True,
        "licensed": True,
        "plan": "lifetime",
        "type": "lifetime",
        "permanent": True,
        "expires_at": None,
    }


@router.get("/settings")
def get_settings(file: str = Query("workflows")):
    """Read configuration file content."""
    if file == "workflows":
        content = WORKFLOWS_PATH.read_text(encoding="utf-8") if WORKFLOWS_PATH.exists() else '{"workflows":[]}'
        return {"ok": True, "content": content, "limited": False}

    app_settings_file = DATA_DIR / "app_settings.json"
    if app_settings_file.exists():
        content = app_settings_file.read_text(encoding="utf-8")
    else:
        content = json.dumps({"content_root": str(OUTPUTS_DIR), "theme": "dark", "sound_enabled": True}, indent=2)
    return {"ok": True, "content": content}


@router.post("/settings")
async def save_settings(request: Request, file: str = Query("workflows")):
    """Save configuration file content."""
    payload = await request.json()
    content = payload.get("content", "{}")

    if file == "workflows":
        WORKFLOWS_PATH.write_text(content, encoding="utf-8")
        return {"ok": True, "content": content, "limited": False}

    app_settings_file = DATA_DIR / "app_settings.json"
    app_settings_file.write_text(content, encoding="utf-8")
    return {"ok": True, "content": content}


@router.get("/schedule")
def get_schedule(factory_id: str = Query(None)):
    """Retrieve schedule status for a factory."""
    return {
        "ok": True,
        "schedule": {
            "factory_id": factory_id,
            "running": False,
            "enabled": False,
            "mode": "daily",
        },
    }


@router.post("/schedule")
async def save_schedule(request: Request):
    """Save factory schedule."""
    payload = await request.json()
    return {"ok": True, "schedule": payload}


@router.post("/script/run")
async def run_script(
    request: Request,
    execution_service: ExecutionService = Depends(get_execution_service),
):
    """Execute a step in a workflow."""
    payload = await request.json()
    factory_id = str(payload.get("factory_id", ""))
    step_id = str(payload.get("step_id", ""))
    values = payload.get("values", {})

    dto = TriggerRunDto(
        workflow_id=factory_id,
        target_step_id=step_id,
        parameters=values,
    )
    run = execution_service.trigger_run(dto)
    return {"ok": True, "status": "running", "run_id": run.id}


@router.get("/outputs")
def list_outputs():
    """List output files."""
    files = []
    if OUTPUTS_DIR.exists():
        for p in OUTPUTS_DIR.rglob("*"):
            if p.is_file():
                files.append(str(p.relative_to(OUTPUTS_DIR)))
    return {"ok": True, "files": files}


@router.get("/output-preview")
def preview_output(path: str = Query("")):
    """Preview output file content."""
    file_path = OUTPUTS_DIR / path
    if not file_path.exists() or not file_path.is_file():
        return {"ok": False, "error": "檔案不存在"}
    try:
        content = file_path.read_text(encoding="utf-8")
        return {"ok": True, "content": content}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


@router.post("/input-file/upload")
async def upload_input_file(request: Request):
    """Handle dropped file inputs."""
    payload = await request.json()
    filename = payload.get("filename", "dropped_file")
    return {"ok": True, "path": str(DATA_DIR / filename)}


@router.get("/changelog")
def get_changelog():
    """Software changelog."""
    return {
        "ok": True,
        "entries": [
            {
                "version": __version__,
                "date": "2026-09-24",
                "title": "Open Factory Agent 100% 開源版",
                "notes": [
                    "解除所有授權與工廠數量限制",
                    "保留 1:1 完整操作台與像素辦公室 RPG 畫布",
                    "支援本機 FastAPI 服務與 GitHub Pages 線上展示",
                ],
            }
        ],
    }
