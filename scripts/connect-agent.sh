#!/usr/bin/env bash
# Open Factory Agent — Local Agent Helper
# Quickly test or set up local agent webhook connections
set -euo pipefail

PORT="${OPENFACTORY_PORT:-8765}"
WEBHOOK_PORT="${AGENT_WEBHOOK_PORT:-8644}"
WEBHOOK_ROUTE="agent-task"
WEBHOOK_URL="http://127.0.0.1:${WEBHOOK_PORT}/webhooks/${WEBHOOK_ROUTE}"

echo "=========================================================="
echo "  🤖 Open Factory Agent — Local Agent Setup Helper"
echo "=========================================================="

echo "Configured Webhook Target: $WEBHOOK_URL"
echo ""

# Check if a webhook listener is running on port 8644
if curl -fsS --max-time 1 "http://127.0.0.1:${WEBHOOK_PORT}/health" >/dev/null 2>&1 || \
   curl -fsS --max-time 1 "http://127.0.0.1:${WEBHOOK_PORT}/" >/dev/null 2>&1; then
  echo "✓ Found active Agent service listening on port ${WEBHOOK_PORT}!"
else
  echo "ℹ No agent listening on port ${WEBHOOK_PORT} yet."
  echo ""
  echo "You can launch an agent webhook in a separate terminal with one of:"
  echo ""
  echo "  1) Hermes Agent:"
  echo "     hermes agent start --webhook-port ${WEBHOOK_PORT}"
  echo ""
  echo "  2) Local FastAPI / Flask webhook mock:"
  echo "     python3 -m http.server ${WEBHOOK_PORT}"
  echo ""
  echo "  3) Pi / Claude Code CLI via webhook bridge:"
  echo "     npx @agent-bridge/cli --port ${WEBHOOK_PORT} --target pi"
  echo ""
fi

# Send agent test ping to Open Factory Agent server
echo "Testing connection to Open Factory Agent server..."
if curl --noproxy '*' -fsS --max-time 2 "http://127.0.0.1:${PORT}/api/config" >/dev/null 2>&1; then
  echo "✓ Open Factory Agent server is running on http://127.0.0.1:${PORT}/"
  echo "  Agent settings can be configured via Web UI Settings -> Agent Settings."
else
  echo "ℹ Open Factory Agent server is not running yet. Start it with: ./start.sh"
fi
