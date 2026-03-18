#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
# File:       boot/init-scripts/03-init-network.sh
# Purpose:    Verify network is reachable after boot.
#             Required by Update Service and AI Container.
#             Does NOT configure the network — Ubuntu Base owns
#             networking. This script only validates connectivity.
# Layer:      Boot
# Depends on: 01-load-logo.sh, 02-load-progress.sh
# Run as:     current user (no root needed)
# Copyright:  (c) 2024 Abdullah — Axon OS Project (AGPL-3.0)
# ─────────────────────────────────────────────────────────────────
set -uo pipefail

LOG="${HOME}/.axonos/logs/boot.log"
READY_FLAG="${HOME}/.axonos/network_ready"
TIMEOUT=30   # seconds to wait for connectivity
PING_HOST="8.8.8.8"

log() { echo "[$(date '+%H:%M:%S')] [03-init-network] $*" | tee -a "$LOG"; }

log "Checking network connectivity (timeout: ${TIMEOUT}s)..."
rm -f "${READY_FLAG}"

elapsed=0
while [[ $elapsed -lt $TIMEOUT ]]; do
    if ping -c1 -W2 "${PING_HOST}" &>/dev/null; then
        log "OK: Network reachable (${elapsed}s)"
        echo "$(date '+%Y-%m-%d %H:%M:%S')" > "${READY_FLAG}"
        exit 0
    fi
    sleep 2
    elapsed=$((elapsed + 2))
done

log "WARN: Network not reachable after ${TIMEOUT}s"
log "INFO: Update Service and AI Container will retry independently"
# Non-fatal: Axon OS can run offline
exit 0
