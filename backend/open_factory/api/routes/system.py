"""System health and diagnostic endpoints."""

import os
import platform
from fastapi import APIRouter
from open_factory import __version__
from open_factory.infrastructure.config import DATA_DIR, OUTPUTS_DIR

router = APIRouter(prefix="/system", tags=["System"])


@router.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "version": __version__,
        "platform": platform.platform(),
        "python_version": platform.python_version(),
    }


@router.get("/info")
def system_info():
    """System directories and status."""
    return {
        "version": __version__,
        "data_dir": str(DATA_DIR),
        "outputs_dir": str(OUTPUTS_DIR),
        "os": os.name,
    }
