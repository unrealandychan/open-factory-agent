#!/usr/bin/env bash
# Open Factory Agent — Stop Server
set -euo pipefail

PORT="${OPENFACTORY_PORT:-8765}"
DATA_DIR="${OPENFACTORY_DATA_DIR:-$HOME/.openfactory/data}"
PID_FILE="$DATA_DIR/server.pid"

stopped=0

if [ -f "$PID_FILE" ]; then
  PID="$(cat "$PID_FILE")"
  if kill -0 "$PID" 2>/dev/null; then
    echo "==> Stopping Open Factory Agent process $PID..."
    kill "$PID" 2>/dev/null || true
    for _ in {1..10}; do
      if ! kill -0 "$PID" 2>/dev/null; then
        stopped=1
        break
      fi
      sleep 0.3
    done
    if [ "$stopped" -eq 0 ]; then
      kill -9 "$PID" 2>/dev/null || true
    fi
  fi
  rm -f "$PID_FILE"
fi

# Fallback: check if anything is listening on the port
if command -v fuser >/dev/null 2>&1; then
  fuser -k "${PORT}/tcp" 2>/dev/null || true
fi

echo "==> Open Factory Agent has been stopped."
