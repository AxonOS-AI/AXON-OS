#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
# File:       platform/gui/02-widgets.sh
# Purpose:    Load Axon OS desktop widgets (clock, resource meters,
#             notification tray) into the running desktop shell.
# Layer:      Platform / GUI
# Depends on: 01-desktop-env.sh  (desktop must be running)
# Note:       Widget visual styling deferred to final phase.
# Run as:     current user
# Copyright:  (c) 2024 Abdullah — Axon OS Project (AGPL-3.0)
# ─────────────────────────────────────────────────────────────────
set -uo pipefail

AXON_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PID_FILE="${HOME}/.axonos/desktop.pid"
LOG="${HOME}/.axonos/logs/desktop.log"

log() { echo "[$(date '+%H:%M:%S')] [02-widgets] $*" | tee -a "$LOG"; }

# ── Verify desktop is running ─────────────────────────────────────
if [[ ! -f "${PID_FILE}" ]]; then
    log "WARN: Desktop PID file not found — run 01-desktop-env.sh first"
    exit 1
fi

DESKTOP_PID=$(cat "${PID_FILE}")
if ! kill -0 "${DESKTOP_PID}" 2>/dev/null; then
    log "WARN: Desktop process ${DESKTOP_PID} not running"
    exit 1
fi

log "Desktop running (PID=${DESKTOP_PID}) — loading widgets..."

# ── Register built-in widgets ─────────────────────────────────────
WIDGETS_DIR="${AXON_ROOT}/platform/gui/plugins"
mkdir -p "${WIDGETS_DIR}"

declare -A WIDGETS=(
    ["clock"]="Taskbar clock — live HH:MM display"
    ["resource_meter"]="CPU + RAM + GPU usage bars"
    ["notification_tray"]="System notification area"
    ["workspace_switcher"]="Virtual workspace buttons"
)

for widget_id in "${!WIDGETS[@]}"; do
    desc="${WIDGETS[$widget_id]}"
    WIDGET_CONF="${WIDGETS_DIR}/${widget_id}.conf"
    if [[ ! -f "${WIDGET_CONF}" ]]; then
        cat > "${WIDGET_CONF}" <<EOF
# Axon OS Widget Configuration
# Widget:  ${widget_id}
# Purpose: ${desc}
# Visual styling: deferred to final design phase
[widget]
id=${widget_id}
enabled=true
position=taskbar
EOF
        log "OK: Registered widget: ${widget_id}"
    else
        log "INFO: Widget already registered: ${widget_id}"
    fi
done

log "02-widgets.sh ✓  (${#WIDGETS[@]} widgets registered)"
