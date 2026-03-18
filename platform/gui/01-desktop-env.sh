#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
# File:       platform/gui/01-desktop-env.sh
# Purpose:    Launch the Axon OS Desktop Environment (GTK4 shell).
#             Bootstraps core services then starts the GUI process.
# Layer:      Platform / GUI
# Depends on: platform/config.py, core-services DB initialized
#             boot/init-scripts/03-init-network.sh (optional)
# Run as:     current user (no root)
# Copyright:  (c) 2024 Abdullah — Axon OS Project (AGPL-3.0)
# ─────────────────────────────────────────────────────────────────
set -uo pipefail

AXON_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DESKTOP_MAIN="${AXON_ROOT}/platform/gui/desktop-environment/main.py"
LOG="${HOME}/.axonos/logs/desktop.log"

log() { echo "[$(date '+%H:%M:%S')] [01-desktop-env] $*" | tee -a "$LOG"; }

log "Starting Axon OS Desktop Environment..."

# ── Check Python ──────────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    log "FAIL: python3 not found"; exit 1
fi

PY_VER=$(python3 -c 'import sys; print(".".join(map(str,sys.version_info[:2])))')
log "Python ${PY_VER} detected"

# ── Check main entry point ────────────────────────────────────────
if [[ ! -f "${DESKTOP_MAIN}" ]]; then
    log "FAIL: Desktop main.py not found at ${DESKTOP_MAIN}"; exit 1
fi

# ── Check GTK4 ────────────────────────────────────────────────────
if python3 -c "import gi; gi.require_version('Gtk','4.0'); from gi.repository import Gtk" 2>/dev/null; then
    log "OK: GTK4 available — launching full GUI"
    MODE="gui"
else
    log "WARN: GTK4 not available — launching in headless/test mode"
    log "INFO: Install GTK4 with: sudo apt install python3-gi gir1.2-gtk-4.0"
    MODE="headless"
fi

# ── Launch ────────────────────────────────────────────────────────
export PYTHONPATH="${AXON_ROOT}"
log "Launching desktop (mode=${MODE})..."
python3 "${DESKTOP_MAIN}" >> "$LOG" 2>&1 &
DESKTOP_PID=$!

echo "${DESKTOP_PID}" > "${HOME}/.axonos/desktop.pid"
log "Desktop PID=${DESKTOP_PID} — stored at ~/.axonos/desktop.pid"
log "01-desktop-env.sh ✓"
