#!/usr/bin/env bash
# Open Factory Agent — One-Line Installer
# Usage: curl -fsSL https://raw.githubusercontent.com/unrealandychan/open-factory-agent/main/install.sh | bash
set -euo pipefail

REPO_URL="https://github.com/unrealandychan/open-factory-agent.git"
INSTALL_DIR="${OPENFACTORY_INSTALL_DIR:-$HOME/.open-factory-agent}"
BIN_DIR="$HOME/.local/bin"
CLI_NAME="open-factory-agent"

echo "=========================================================="
echo "  🚀 Installing Open Factory Agent (100% Free & Open Source)"
echo "=========================================================="

# Check Python 3
if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: Python 3 is required. Please install Python 3.10+ first." >&2
  exit 1
fi

# Clone or pull repository
if [ -d "$INSTALL_DIR/.git" ]; then
  echo "==> Existing installation found at $INSTALL_DIR. Updating..."
  cd "$INSTALL_DIR"
  git fetch --depth=1 origin main
  git reset --hard origin/main
else
  echo "==> Cloning Open Factory Agent into $INSTALL_DIR..."
  mkdir -p "$(dirname "$INSTALL_DIR")"
  git clone --depth=1 "$REPO_URL" "$INSTALL_DIR"
  cd "$INSTALL_DIR"
fi

# Make scripts executable
chmod +x "$INSTALL_DIR/start.sh" "$INSTALL_DIR/stop.sh"

# Create launcher wrapper in ~/.local/bin
mkdir -p "$BIN_DIR"
cat << 'EOF' > "$BIN_DIR/$CLI_NAME"
#!/usr/bin/env bash
INSTALL_DIR="${OPENFACTORY_INSTALL_DIR:-$HOME/.open-factory-agent}"

case "${1:-start}" in
  start)
    "$INSTALL_DIR/start.sh"
    ;;
  stop)
    "$INSTALL_DIR/stop.sh"
    ;;
  restart)
    "$INSTALL_DIR/stop.sh"
    sleep 1
    "$INSTALL_DIR/start.sh"
    ;;
  status)
    PORT="${OPENFACTORY_PORT:-8765}"
    if curl --noproxy '*' -fsS --max-time 2 "http://127.0.0.1:$PORT/api/config" >/dev/null 2>&1; then
      echo "Open Factory Agent is running on http://127.0.0.1:$PORT/"
    else
      echo "Open Factory Agent is stopped."
    fi
    ;;
  docker)
    cd "$INSTALL_DIR" && docker compose up -d
    ;;
  update)
    echo "==> Updating Open Factory Agent..."
    cd "$INSTALL_DIR"
    git pull origin main
    echo "==> Update complete! Restarting..."
    "$INSTALL_DIR/stop.sh"
    sleep 1
    "$INSTALL_DIR/start.sh"
    ;;
  version)
    cat "$INSTALL_DIR/VERSION" 2>/dev/null || echo "1.0.0"
    ;;
  help|--help|-h)
    echo "Usage: open-factory-agent [start|stop|restart|status|update|docker|version]"
    ;;
  *)
    echo "Unknown command: $1. Run 'open-factory-agent help' for usage." >&2
    exit 1
    ;;
esac
EOF

chmod +x "$BIN_DIR/$CLI_NAME"

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
  echo ""
  echo "Note: $BIN_DIR is not in your PATH."
  echo "Add it to your shell config (~/.bashrc or ~/.zshrc):"
  echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
  echo ""
fi

echo ""
echo "=========================================================="
echo "  🎉 Installation Successful!"
echo "=========================================================="
echo ""
echo "Run the platform with:"
echo "  $BIN_DIR/$CLI_NAME start"
echo ""
echo "Starting Open Factory Agent now..."
"$BIN_DIR/$CLI_NAME" start
