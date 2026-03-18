#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
# File:       platform/tools/01-project-builder.sh
# Purpose:    Scaffold a new Axon OS development project.
#             Creates standard folders (src/data/models/scripts/docs),
#             registers the project in SQLite, and writes a README.
# Layer:      Platform / Tools
# Depends on: platform/core-services/02-project-manager.sh (DB init)
# Usage:      ./01-project-builder.sh --name "MyProject" [--desc "..."]
# Run as:     current user
# Copyright:  (c) 2024 Abdullah — Axon OS Project (AGPL-3.0)
# ─────────────────────────────────────────────────────────────────
set -uo pipefail

AXON_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
LOG="${HOME}/.axonos/logs/tools.log"
log() { echo "[$(date '+%H:%M:%S')] [01-project-builder] $*" | tee -a "$LOG"; }

# ── Parse args ────────────────────────────────────────────────────
PROJECT_NAME=""; PROJECT_DESC=""; PROJECT_TAGS=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --name) PROJECT_NAME="$2"; shift 2 ;;
        --desc) PROJECT_DESC="$2"; shift 2 ;;
        --tags) PROJECT_TAGS="$2"; shift 2 ;;
        *) echo "Usage: $0 --name <n> [--desc <d>] [--tags <t>]"; exit 1 ;;
    esac
done
[[ -z "${PROJECT_NAME}" ]] && { echo "Error: --name required"; exit 1; }

log "Building project: ${PROJECT_NAME}"
export PYTHONPATH="${AXON_ROOT}"

RESULT=$(python3 - <<PYEOF 2>&1
import sys, os
sys.path.insert(0, os.environ['PYTHONPATH'] + '/platform')
sys.path.insert(0, os.environ['PYTHONPATH'] + '/platform/core-services')
sys.path.insert(0, os.environ['PYTHONPATH'] + '/platform/core-services/project-manager')
from core_services_init import bootstrap; from project_manager import ProjectManager
bootstrap(); pm = ProjectManager()
try:
    p = pm.create("${PROJECT_NAME}", description="${PROJECT_DESC}", tags="${PROJECT_TAGS}")
    print("CREATED:" + str(p['id']) + ":" + p['path'])
except ValueError as e:
    print("EXISTS:" + str(e))
PYEOF
)

if echo "${RESULT}" | grep -q "^CREATED:"; then
    PROJECT_PATH=$(echo "${RESULT}" | cut -d: -f3-)
    log "OK: Project registered at ${PROJECT_PATH}"
    for d in src data models scripts docs; do mkdir -p "${PROJECT_PATH}/${d}"; done
    cat > "${PROJECT_PATH}/README.md" <<EOF
# ${PROJECT_NAME}
> Axon OS Project — $(date '+%Y-%m-%d')

${PROJECT_DESC}
EOF
    echo "✓ Project '${PROJECT_NAME}' ready at: ${PROJECT_PATH}"
elif echo "${RESULT}" | grep -q "^EXISTS:"; then
    log "INFO: Project already exists"; echo "INFO: Already exists"
else
    log "FAIL: ${RESULT}"; exit 1
fi
log "01-project-builder.sh ✓"
