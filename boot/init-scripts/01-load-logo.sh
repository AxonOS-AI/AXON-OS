#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
# File:       boot/init-scripts/01-load-logo.sh
# Purpose:    Register the Axon OS logo asset with Plymouth.
#             Creates the theme directory and copies the logo PNG.
# Layer:      Boot
# Depends on: None  (first in boot sequence)
# Deferred:   Actual logo visual design → final phase.
#             This script wires the PATH only.
# Run as:     root
# Copyright:  (c) 2024 Abdullah — Axon OS Project (AGPL-3.0)
# ─────────────────────────────────────────────────────────────────
set -uo pipefail

AXON_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PLYMOUTH_DIR="/usr/share/plymouth/themes/axon"
LOGO_SRC="${AXON_ROOT}/boot/splash/plymouth/assets/axon_logo.png"
LOG="${HOME}/.axonos/logs/boot.log"
mkdir -p "$(dirname "$LOG")"

log() { echo "[$(date '+%H:%M:%S')] [01-load-logo] $*" | tee -a "$LOG"; }

# ── Safety guard: never touch Ubuntu Base ────────────────────────
for forbidden in "/boot/grub" "/etc/default/grub" "/vmlinuz"; do
    if [[ "${PLYMOUTH_DIR}" == "${forbidden}"* ]]; then
        log "ABORT: refusing to touch Ubuntu Base path: ${forbidden}"; exit 1
    fi
done

log "Registering Axon OS logo asset..."

if ! command -v plymouth &>/dev/null; then
    log "WARN: Plymouth not installed — visual boot deferred to final phase"
    exit 0
fi

mkdir -p "${PLYMOUTH_DIR}/assets"

if [[ -f "${LOGO_SRC}" ]]; then
    cp "${LOGO_SRC}" "${PLYMOUTH_DIR}/assets/axon_logo.png"
    log "OK: Logo copied → ${PLYMOUTH_DIR}/assets/axon_logo.png"
else
    log "INFO: Logo PNG not found — placeholder registered (final phase will replace)"
    python3 -c "
import base64, os
b64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='
p = '${PLYMOUTH_DIR}/assets/axon_logo.png'
os.makedirs(os.path.dirname(p), exist_ok=True)
open(p,'wb').write(base64.b64decode(b64))
" 2>/dev/null || log "WARN: Could not write placeholder"
fi

log "01-load-logo.sh ✓"
