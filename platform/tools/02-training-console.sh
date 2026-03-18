#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
# File:       platform/tools/02-training-console.sh
# Purpose:    Launch the Axon OS Training Console.
#             Monitors active AI training jobs inside the Docker
#             container and streams logs to the terminal.
# Layer:      Platform / Tools
# Depends on: ai-container/assistant/02-init-runtime.sh (Docker running)
#             platform/core-services/01-resource-manager.sh
# Usage:      ./02-training-console.sh [--project <name>] [--watch]
# Run as:     current user
# Copyright:  (c) 2024 Abdullah — Axon OS Project (AGPL-3.0)
# ─────────────────────────────────────────────────────────────────
set -uo pipefail

AXON_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
LOG="${HOME}/.axonos/logs/training.log"
CONTAINER_NAME="axon-ai-runtime"

log() { echo "[$(date '+%H:%M:%S')] [02-training-console] $*" | tee -a "$LOG"; }

# ── Parse args ────────────────────────────────────────────────────
PROJECT_NAME=""; WATCH_MODE=false
while [[ $# -gt 0 ]]; do
    case "$1" in
        --project) PROJECT_NAME="$2"; shift 2 ;;
        --watch)   WATCH_MODE=true; shift ;;
        *) echo "Usage: $0 [--project <name>] [--watch]"; exit 1 ;;
    esac
done

log "Starting Training Console..."

# ── Check Docker availability ─────────────────────────────────────
if ! command -v docker &>/dev/null; then
    log "WARN: Docker not installed — AI Container deferred to Phase 5"
    echo "Training Console: Docker not available yet."
    echo "AI Container setup is planned for Phase 5."
    exit 0
fi

# ── Check if AI container is running ─────────────────────────────
if ! docker ps --format '{{.Names}}' 2>/dev/null | grep -q "^${CONTAINER_NAME}$"; then
    log "WARN: AI container '${CONTAINER_NAME}' not running"
    echo "AI runtime container not started. Run ai-container/assistant/02-init-runtime.sh first."
    exit 0
fi

# ── Show resource snapshot ────────────────────────────────────────
echo "══════════════════════════════════════"
echo "  Axon OS — Training Console"
echo "══════════════════════════════════════"

export PYTHONPATH="${AXON_ROOT}"
python3 - <<'PYEOF' 2>/dev/null
import sys, os, time
sys.path.insert(0, os.environ['PYTHONPATH'] + '/platform')
sys.path.insert(0, os.environ['PYTHONPATH'] + '/platform/core-services/resource-manager')
from resource_manager import ResourceManager
rm = ResourceManager(); rm.start(); time.sleep(2)
print(rm.summary()); rm.stop()
PYEOF

# ── Watch container logs ──────────────────────────────────────────
if [[ "${WATCH_MODE}" == true ]]; then
    log "Streaming container logs (Ctrl+C to stop)..."
    docker logs -f "${CONTAINER_NAME}"
else
    log "Showing last 50 lines of container logs..."
    docker logs --tail 50 "${CONTAINER_NAME}" 2>&1 | tee -a "$LOG"
fi

log "02-training-console.sh ✓"
