#!/usr/bin/env bash
# Open Factory Agent — Local Launcher
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${OPENFACTORY_PYTHON:-$(command -v python3 || true)}"
PORT="${OPENFACTORY_PORT:-8765}"
URL="http://127.0.0.1:$PORT/"
DATA_DIR="${OPENFACTORY_DATA_DIR:-$HOME/.openfactory/data}"
LOG_DIR="${OPENFACTORY_LOG_DIR:-$HOME/.openfactory/logs}"
PID_FILE="$DATA_DIR/server.pid"

if [ -z "$PYTHON" ]; then
  echo "Error: Python 3 is required. Please install python3." >&2
  exit 1
fi

mkdir -p "$DATA_DIR" "$LOG_DIR"

if curl --noproxy '*' -fsS --max-time 2 "$URL/api/config" >/dev/null 2>&1; then
  echo "==> Open Factory Agent is already running at $URL"
  if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$URL" >/dev/null 2>&1 || true
  elif command -v open >/dev/null 2>&1; then
    open "$URL" >/dev/null 2>&1 || true
  fi
  exit 0
fi

cd "$SCRIPT_DIR"
echo "==> Starting Open Factory Agent on port $PORT..."
OPENFACTORY_DATA_DIR="$DATA_DIR" nohup "$PYTHON" "$SCRIPT_DIR/server.py" > "$LOG_DIR/server.log" 2>&1 &
SERVER_PID=$!
echo "$SERVER_PID" > "$PID_FILE"

for _ in {1..20}; do
  if curl --noproxy '*' -fsS --max-time 1 "$URL/api/config" >/dev/null 2>&1; then
    echo "==> Open Factory Agent started successfully!"
    echo "==> Web Interface: $URL"
    echo "==> Data Directory: $DATA_DIR"
    echo "==> Log File: $LOG_DIR/server.log"
    if [ "${OPENFACTORY_NO_BROWSER:-0}" != "1" ]; then
      if command -v xdg-open >/dev/null 2>&1; then
        xdg-open "$URL" >/dev/null 2>&1 || true
      elif command -v open >/dev/null 2>&1; then
        open "$URL" >/dev/null 2>&1 || true
      fi
    fi
    exit 0
  fi
  kill -0 "$SERVER_PID" 2>/dev/null || break
  sleep 0.5
done

rm -f "$PID_FILE"
echo "Error: Open Factory Agent failed to start. Check $LOG_DIR/server.log" >&2
exit 1
