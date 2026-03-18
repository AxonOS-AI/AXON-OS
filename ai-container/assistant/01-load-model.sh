#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
# File:       ai-container/assistant/01-load-model.sh
# Purpose:    Pull and register an AI model inside the Docker
#             container. Supports HuggingFace model IDs and
#             local .gguf / .safetensors files.
# Layer:      AI Container
# Depends on: Docker installed, ai-container/assistant/02-init-runtime.sh
# Usage:
#   ./01-load-model.sh --model "microsoft/phi-2"
#   ./01-load-model.sh --local /path/to/model.gguf
# Run as:     current user (docker group)
# Copyright:  (c) 2024 Abdullah — Axon OS Project (AGPL-3.0)
# ─────────────────────────────────────────────────────────────────
set -uo pipefail

AXON_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
MODELS_DIR="${AXON_ROOT}/ai-container/models"
CONTAINER_NAME="axon-ai-runtime"
LOG="${HOME}/.axonos/logs/ai_container.log"

log() { echo "[$(date '+%H:%M:%S')] [01-load-model] $*" | tee -a "$LOG"; }

# ── Parse args ────────────────────────────────────────────────────
MODEL_ID=""; LOCAL_PATH=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --model) MODEL_ID="$2";   shift 2 ;;
        --local) LOCAL_PATH="$2"; shift 2 ;;
        *) echo "Usage: $0 --model <hf-id> | --local <path>"; exit 1 ;;
    esac
done

[[ -z "${MODEL_ID}" && -z "${LOCAL_PATH}" ]] && {
    echo "Error: provide --model <id> or --local <path>"; exit 1; }

log "Starting model load process..."
mkdir -p "${MODELS_DIR}"

# ── Docker availability check ─────────────────────────────────────
if ! command -v docker &>/dev/null; then
    log "WARN: Docker not installed — AI Container deferred to Phase 5"
    echo "Docker not available. Saving model reference for Phase 5 setup."
    # Save reference for later
    echo "${MODEL_ID:-local:${LOCAL_PATH}}" >> "${MODELS_DIR}/pending_models.txt"
    log "INFO: Model reference saved to pending_models.txt"
    exit 0
fi

# ── Load local model ──────────────────────────────────────────────
if [[ -n "${LOCAL_PATH}" ]]; then
    if [[ ! -f "${LOCAL_PATH}" ]]; then
        log "FAIL: Local model file not found: ${LOCAL_PATH}"; exit 1
    fi
    MODEL_FILENAME=$(basename "${LOCAL_PATH}")
    cp "${LOCAL_PATH}" "${MODELS_DIR}/${MODEL_FILENAME}"
    log "OK: Local model copied → ${MODELS_DIR}/${MODEL_FILENAME}"

    # Register model in container
    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        docker exec "${CONTAINER_NAME}" python3 -c "
import json, os
registry_path = '/axon/models/registry.json'
os.makedirs(os.path.dirname(registry_path), exist_ok=True)
reg = json.load(open(registry_path)) if os.path.exists(registry_path) else {'models': []}
reg['models'].append({'id': '${MODEL_FILENAME}', 'type': 'local', 'path': '/axon/models/${MODEL_FILENAME}'})
json.dump(reg, open(registry_path, 'w'), indent=2)
print('Model registered in container')
" && log "OK: Model registered inside container"
    fi

# ── Download HuggingFace model ────────────────────────────────────
elif [[ -n "${MODEL_ID}" ]]; then
    log "Downloading model: ${MODEL_ID}"

    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        docker exec "${CONTAINER_NAME}" python3 -c "
from huggingface_hub import snapshot_download
path = snapshot_download(repo_id='${MODEL_ID}', local_dir='/axon/models/${MODEL_ID}')
print(f'Downloaded to: {path}')
" 2>&1 | tee -a "$LOG" && log "OK: Model downloaded: ${MODEL_ID}" || {
            log "FAIL: Download failed — check container logs"; exit 1; }
    else
        log "INFO: Container not running — saving for Phase 5 setup"
        echo "${MODEL_ID}" >> "${MODELS_DIR}/pending_models.txt"
    fi
fi

log "01-load-model.sh ✓"
