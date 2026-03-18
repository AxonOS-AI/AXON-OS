#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
# File:       boot/init-scripts/02-load-progress.sh
# Purpose:    Install Axon OS Plymouth theme and activate the
#             boot progress bar animation.
# Layer:      Boot
# Depends on: 01-load-logo.sh  (logo asset must exist first)
# Deferred:   Animation colors and visual polish → final phase.
# Run as:     root
# Copyright:  (c) 2024 Abdullah — Axon OS Project (AGPL-3.0)
# ─────────────────────────────────────────────────────────────────
set -uo pipefail

AXON_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PLYMOUTH_SRC="${AXON_ROOT}/boot/splash/plymouth"
PLYMOUTH_DST="/usr/share/plymouth/themes/axon"
LOG="${HOME}/.axonos/logs/boot.log"
mkdir -p "$(dirname "$LOG")"

log() { echo "[$(date '+%H:%M:%S')] [02-load-progress] $*" | tee -a "$LOG"; }

log "Installing Axon OS Plymouth theme..."

if ! command -v plymouth &>/dev/null; then
    log "WARN: Plymouth not found — install with: sudo apt install plymouth"
    exit 0
fi

# ── Copy theme files ──────────────────────────────────────────────
mkdir -p "${PLYMOUTH_DST}"

for f in axon.plymouth axon.script; do
    if [[ -f "${PLYMOUTH_SRC}/${f}" ]]; then
        cp "${PLYMOUTH_SRC}/${f}" "${PLYMOUTH_DST}/${f}"
        log "OK: Copied ${f}"
    else
        log "WARN: ${f} not found at ${PLYMOUTH_SRC} — visual boot deferred"
    fi
done

# ── Activate theme ────────────────────────────────────────────────
if command -v plymouth-set-default-theme &>/dev/null; then
    plymouth-set-default-theme axon 2>/dev/null && \
        log "OK: Axon set as default Plymouth theme" || \
        log "WARN: Could not set default theme — run manually after reboot"
fi

# ── Rebuild initramfs to apply changes ────────────────────────────
if command -v update-initramfs &>/dev/null; then
    log "Rebuilding initramfs (this takes ~30s)..."
    update-initramfs -u 2>&1 | tail -2 | while IFS= read -r l; do log "$l"; done
    log "OK: initramfs rebuilt"
else
    log "WARN: update-initramfs not found — skipping"
fi

log "02-load-progress.sh ✓"
