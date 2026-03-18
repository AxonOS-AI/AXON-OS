#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
# File:       scripts/utilities/01-cleanup.sh
# Purpose:    Clean up Axon OS temporary files, old logs, and
#             cached data. Safe to run anytime — never touches
#             project data or Ubuntu Base OS files.
#
# What it cleans:
#   ~/.axonos/logs/     → rotates logs older than 7 days
#   ~/.axonos/*.pid     → removes stale PID files
#   ai-container/cache/ → clears model download cache
#   /tmp/axon-*         → removes Axon temp files
#
# What it NEVER touches:
#   ~/AxonProjects/     → user project data
#   ~/.axonos/axonos.db → project database
#   Ubuntu Base OS      → protected
#
# Layer:      Scripts / Utilities
# Depends on: None
# Run as:     current user
# Copyright:  (c) 2024 Abdullah — Axon OS Project (AGPL-3.0)
# ─────────────────────────────────────────────────────────────────
set -uo pipefail

AXON_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
AXON_DATA="${HOME}/.axonos"
LOG="${AXON_DATA}/logs/cleanup.log"
LOG_RETENTION_DAYS=7

GREEN='\033[0;32m'; CYAN='\033[0;36m'; NC='\033[0m'

log()  { echo "[$(date '+%H:%M:%S')] [cleanup] $*" | tee -a "$LOG"; }
ok()   { echo -e "  ${GREEN}✓${NC}  $1"; }

echo -e "\n${CYAN}── Axon OS Cleanup ──${NC}"
log "Starting cleanup..."
FREED=0

# ── Rotate old log files ──────────────────────────────────────────
LOG_COUNT=0
while IFS= read -r old_log; do
    SIZE=$(stat -c%s "${old_log}" 2>/dev/null || echo 0)
    rm -f "${old_log}"
    FREED=$((FREED + SIZE))
    ((LOG_COUNT++))
done < <(find "${AXON_DATA}/logs" -name "*.log" -mtime "+${LOG_RETENTION_DAYS}" 2>/dev/null)
[[ ${LOG_COUNT} -gt 0 ]] && ok "Rotated ${LOG_COUNT} old log files" || ok "Logs: nothing to rotate"

# ── Truncate large current logs (keep last 1000 lines) ───────────
TRUNCATED=0
while IFS= read -r big_log; do
    LINES=$(wc -l < "${big_log}")
    if [[ "${LINES}" -gt 1000 ]]; then
        tail -1000 "${big_log}" > "${big_log}.tmp" && mv "${big_log}.tmp" "${big_log}"
        ((TRUNCATED++))
    fi
done < <(find "${AXON_DATA}/logs" -name "*.log" -size "+500k" 2>/dev/null)
[[ ${TRUNCATED} -gt 0 ]] && ok "Truncated ${TRUNCATED} large log(s) to last 1000 lines"

# ── Clean stale PID files ─────────────────────────────────────────
PID_COUNT=0
while IFS= read -r pid_file; do
    PID=$(cat "${pid_file}" 2>/dev/null || echo "")
    if [[ -n "${PID}" ]] && ! kill -0 "${PID}" 2>/dev/null; then
        rm -f "${pid_file}"
        ((PID_COUNT++))
    fi
done < <(find "${AXON_DATA}" -name "*.pid" 2>/dev/null)
[[ ${PID_COUNT} -gt 0 ]] && ok "Removed ${PID_COUNT} stale PID file(s)" || ok "PIDs: all valid"

# ── Clean AI container cache ──────────────────────────────────────
AI_CACHE="${AXON_ROOT}/ai-container/cache"
if [[ -d "${AI_CACHE}" ]]; then
    CACHE_SIZE=$(du -sh "${AI_CACHE}" 2>/dev/null | cut -f1 || echo "0")
    rm -rf "${AI_CACHE:?}"/*
    ok "AI container cache cleared (was ${CACHE_SIZE})"
fi

# ── Clean /tmp/axon-* files ───────────────────────────────────────
TMP_COUNT=$(find /tmp -name "axon-*" -maxdepth 1 2>/dev/null | wc -l)
[[ ${TMP_COUNT} -gt 0 ]] && find /tmp -name "axon-*" -maxdepth 1 -delete 2>/dev/null
[[ ${TMP_COUNT} -gt 0 ]] && ok "Removed ${TMP_COUNT} temp file(s) from /tmp" || ok "Temp files: none found"

# ── Clean Python __pycache__ inside Axon dirs ─────────────────────
CACHE_COUNT=$(find "${AXON_ROOT}" -name "__pycache__" -type d 2>/dev/null | wc -l)
[[ ${CACHE_COUNT} -gt 0 ]] && find "${AXON_ROOT}" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
[[ ${CACHE_COUNT} -gt 0 ]] && ok "Cleared ${CACHE_COUNT} Python cache dir(s)"

# ── Summary ───────────────────────────────────────────────────────
FREED_KB=$((FREED / 1024))
echo ""
ok "Cleanup complete — freed ~${FREED_KB}KB"
log "Cleanup complete — freed ~${FREED_KB}KB"
log "01-cleanup.sh ✓"
