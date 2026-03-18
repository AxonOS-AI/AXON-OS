#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
# File:       scripts/update/01-update-platform.sh
# Purpose:    Pull latest Axon OS changes from GitHub and apply
#             them to Platform Layer and AI Container only.
#             NEVER modifies: Ubuntu Base, kernel, /etc, /boot.
#
# Safety rules enforced:
#   ✓ Only pulls: platform/ ai-container/ scripts/ docs/ boot/
#   ✗ Never pulls: / /etc /boot /usr /var/lib
#   ✗ Never runs: apt upgrade, kernel updates
#
# Layer:      Scripts / Update
# Depends on: git, network connectivity
# Run as:     current user
# Copyright:  (c) 2024 Abdullah — Axon OS Project (AGPL-3.0)
# ─────────────────────────────────────────────────────────────────
set -uo pipefail

AXON_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
LOG="${HOME}/.axonos/logs/updates.log"
NET_FLAG="${HOME}/.axonos/network_ready"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'

log()  { echo "[$(date '+%H:%M:%S')] [update] $*" | tee -a "$LOG"; }
ok()   { echo -e "  ${GREEN}✓${NC}  $1"; log "OK: $1"; }
warn() { echo -e "  ${YELLOW}⚠${NC}  $1"; log "WARN: $1"; }

echo -e "\n${CYAN}── Axon OS Platform Update ──${NC}"

# ── Safety: must be inside Axon repo ─────────────────────────────
if [[ ! -d "${AXON_ROOT}/.git" ]]; then
    warn "Not a git repository — cannot update. Initialize with:"
    warn "  cd ${AXON_ROOT} && git init && git remote add origin <url>"
    exit 0
fi

# ── Network check ─────────────────────────────────────────────────
if [[ ! -f "${NET_FLAG}" ]]; then
    if ! ping -c1 -W3 8.8.8.8 &>/dev/null; then
        warn "No network — skipping update check"
        exit 0
    fi
fi

# ── Check current version ────────────────────────────────────────
CURRENT_VERSION=$(grep -r "AXON_VERSION" "${AXON_ROOT}/platform/config.py" 2>/dev/null \
    | grep -oP '"[\d.]+"' | tr -d '"' | head -1 || echo "unknown")
log "Current version: ${CURRENT_VERSION}"

# ── Stash local changes ───────────────────────────────────────────
log "Stashing local changes..."
git -C "${AXON_ROOT}" stash --include-untracked -q 2>/dev/null || true

# ── Pull ONLY Axon-managed paths ─────────────────────────────────
AXON_PATHS=("platform/" "ai-container/" "scripts/" "docs/" "boot/")
log "Pulling updates for: ${AXON_PATHS[*]}"

git -C "${AXON_ROOT}" fetch origin main --quiet 2>&1 | tee -a "$LOG"

for path in "${AXON_PATHS[@]}"; do
    git -C "${AXON_ROOT}" checkout origin/main -- "${path}" 2>/dev/null && \
        ok "Updated: ${path}" || warn "No changes: ${path}"
done

# ── Restore stash ─────────────────────────────────────────────────
git -C "${AXON_ROOT}" stash pop -q 2>/dev/null || true

# ── Record update ─────────────────────────────────────────────────
NEW_VERSION=$(grep -r "AXON_VERSION" "${AXON_ROOT}/platform/config.py" 2>/dev/null \
    | grep -oP '"[\d.]+"' | tr -d '"' | head -1 || echo "unknown")

export PYTHONPATH="${AXON_ROOT}"
python3 - <<PYEOF 2>/dev/null
import sys, os
sys.path.insert(0, os.environ['PYTHONPATH'] + '/platform')
sys.path.insert(0, os.environ['PYTHONPATH'] + '/platform/core-services')
from db_manager import get_connection, initialize_schema
initialize_schema()
conn = get_connection()
conn.execute("INSERT INTO update_history (version, status, notes) VALUES (?,?,?)",
    ("${NEW_VERSION}", "success", "Updated via 01-update-platform.sh"))
conn.commit(); conn.close()
PYEOF

ok "Update complete — version: ${CURRENT_VERSION} → ${NEW_VERSION}"
log "01-update-platform.sh ✓"
