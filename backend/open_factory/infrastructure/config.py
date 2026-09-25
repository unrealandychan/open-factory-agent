"""Configuration and runtime paths for Open Factory Agent."""

import os
from pathlib import Path

# Base Paths
DEFAULT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = Path(os.environ.get("OFA_DATA_DIR", DEFAULT_ROOT / "data")).expanduser().resolve()
DATA_DIR.mkdir(parents=True, exist_ok=True)

OUTPUTS_DIR = DATA_DIR / "outputs"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

WORKFLOWS_PATH = DATA_DIR / "workflows.json"
SCHEDULES_PATH = DATA_DIR / "schedules.json"

# Server Settings
HOST = os.environ.get("OFA_HOST", "0.0.0.0")
PORT = int(os.environ.get("OFA_PORT", "8765"))
