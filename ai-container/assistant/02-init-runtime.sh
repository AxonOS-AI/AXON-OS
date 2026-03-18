#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
# File:       ai-container/assistant/02-init-runtime.sh
# Purpose:    Build and start the Axon OS AI Docker container.
#             Mounts models/, libraries/, and agents/ directories.
#             Exposes REST API on localhost:8080 for Platform Layer.
#             NEVER modifies Ubuntu Base OS files.
# Layer:      AI Container
# Depends on: Docker installed, 01-load-model.sh (optional models)
# Run as:     current user (docker group)
# Copyright:  (c) 2024 Abdullah — Axon OS Project (AGPL-3.0)
# ─────────────────────────────────────────────────────────────────
set -uo pipefail

AXON_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
CONTAINER_NAME="axon-ai-runtime"
IMAGE_NAME="axon-os/ai-runtime:1.0.0"
DOCKERFILE="${AXON_ROOT}/ai-container/Dockerfile"
API_PORT="8080"
LOG="${HOME}/.axonos/logs/ai_container.log"

log() { echo "[$(date '+%H:%M:%S')] [02-init-runtime] $*" | tee -a "$LOG"; }

log "Initializing Axon OS AI Runtime..."

# ── Docker check ──────────────────────────────────────────────────
if ! command -v docker &>/dev/null; then
    log "WARN: Docker not installed"
    log "INFO: Install Docker with: sudo apt install docker.io && sudo usermod -aG docker \$USER"
    echo "Docker not available — AI Container is Phase 5. Skipping."
    exit 0
fi

if ! docker info &>/dev/null; then
    log "WARN: Docker daemon not running — start with: sudo systemctl start docker"
    exit 0
fi

# ── Stop existing container if running ───────────────────────────
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    log "INFO: Removing existing container '${CONTAINER_NAME}'..."
    docker stop "${CONTAINER_NAME}" 2>/dev/null || true
    docker rm   "${CONTAINER_NAME}" 2>/dev/null || true
fi

# ── Generate Dockerfile if missing ───────────────────────────────
if [[ ! -f "${DOCKERFILE}" ]]; then
    log "INFO: Dockerfile not found — generating..."
    cat > "${DOCKERFILE}" <<'DOCKERFILE_EOF'
# ─────────────────────────────────────────────────────────────────
# Axon OS — AI Runtime Container
# Copyright (c) 2024 Abdullah — AGPL-3.0
# Base: python:3.11-slim (NOT Ubuntu Base — separate container)
# ─────────────────────────────────────────────────────────────────
FROM python:3.11-slim

LABEL maintainer="Abdullah — Axon OS Project"
LABEL version="1.0.0"
LABEL description="Axon OS AI Runtime"

WORKDIR /axon

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python AI libraries
RUN pip install --no-cache-dir \
    torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu \
    transformers \
    huggingface_hub \
    fastapi uvicorn \
    numpy pandas

# Copy assistant and agent code
COPY assistant/ /axon/assistant/
COPY agents/    /axon/agents/
COPY libraries/ /axon/libraries/

# Volumes (mounted from host)
VOLUME ["/axon/models"]

EXPOSE 8080

CMD ["python3", "/axon/assistant/server.py"]
DOCKERFILE_EOF
    log "OK: Dockerfile generated"
fi

# ── Build image ───────────────────────────────────────────────────
log "Building AI runtime image (this may take a few minutes)..."
docker build \
    -t "${IMAGE_NAME}" \
    -f "${DOCKERFILE}" \
    "${AXON_ROOT}/ai-container" \
    2>&1 | tail -5 | while IFS= read -r l; do log "  $l"; done

if [[ "${PIPESTATUS[0]}" -ne 0 ]]; then
    log "FAIL: Docker build failed — check ${LOG}"; exit 1
fi
log "OK: Image built: ${IMAGE_NAME}"

# ── Start container ───────────────────────────────────────────────
log "Starting container '${CONTAINER_NAME}' on port ${API_PORT}..."
docker run -d \
    --name "${CONTAINER_NAME}" \
    --restart unless-stopped \
    -p "127.0.0.1:${API_PORT}:8080" \
    -v "${AXON_ROOT}/ai-container/models:/axon/models" \
    -v "${HOME}/.axonos/logs:/axon/logs" \
    "${IMAGE_NAME}" 2>&1 | tee -a "$LOG"

# ── Health check ──────────────────────────────────────────────────
log "Waiting for container to be ready..."
for i in {1..15}; do
    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        log "OK: Container '${CONTAINER_NAME}' is running"
        echo "${CONTAINER_NAME}" > "${HOME}/.axonos/ai_container.name"
        log "02-init-runtime.sh ✓"
        exit 0
    fi
    sleep 2
done

log "FAIL: Container did not start within 30s"; exit 1
