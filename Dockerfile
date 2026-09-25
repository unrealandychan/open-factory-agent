# Open Factory Agent — 100% Free & Open Source Local-First Workflow Platform
FROM python:3.12-slim

LABEL maintainer="Eddie Chan <unrealandychan>"
LABEL description="Open Factory Agent — Autonomous workflow automation and local AI factory platform"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    OPENFACTORY_PORT=8765 \
    OPENFACTORY_DATA_DIR=/app/data \
    AUTOMONEY_NO_BROWSER=1

WORKDIR /app

# Install minimal runtime dependencies (curl for healthchecks & script steps, ffmpeg for media tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ffmpeg \
    ca-certificates \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Copy application source and assets
COPY server.py scheduler.py autostart.py VERSION CHANGELOG.md ./
COPY workflows.default.json ./
COPY index.html ./
COPY assets/ ./assets/
COPY open-factory-logo.png open-factory-header-logo.png workflow-factory-icon.png favicon.svg ./

# Create data directory for volume mounting
RUN mkdir -p /app/data

EXPOSE 8765

HEALTHCHECK --interval=15s --timeout=5s --start-period=5s --retries=3 \
  CMD curl --noproxy '*' -f http://127.0.0.1:8765/api/config || exit 1

ENTRYPOINT ["python3", "server.py"]
