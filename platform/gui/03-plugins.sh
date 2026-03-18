#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
# File:       platform/gui/03-plugins.sh
# Purpose:    Scan the platform/addons/ directory and register any
#             installed Axon OS plugins with the desktop shell.
# Layer:      Platform / GUI
# Depends on: 01-desktop-env.sh, 02-widgets.sh
# Note:       Plugin API stable; visual theming deferred.
# Run as:     current user
# Copyright:  (c) 2024 Abdullah — Axon OS Project (AGPL-3.0)
# ─────────────────────────────────────────────────────────────────
set -uo pipefail

AXON_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
ADDONS_DIR="${AXON_ROOT}/platform/addons"
REGISTRY="${HOME}/.axonos/plugins_registry.json"
LOG="${HOME}/.axonos/logs/desktop.log"

log() { echo "[$(date '+%H:%M:%S')] [03-plugins] $*" | tee -a "$LOG"; }

log "Scanning for Axon OS plugins in ${ADDONS_DIR}..."
mkdir -p "${ADDONS_DIR}"

LOADED=0
FAILED=0

# ── Scan .axonplugin descriptor files ────────────────────────────
if compgen -G "${ADDONS_DIR}/*.axonplugin" &>/dev/null; then
    while IFS= read -r plugin_file; do
        plugin_id=$(basename "${plugin_file}" .axonplugin)
        log "Loading plugin: ${plugin_id}"

        # Validate required fields
        if grep -q "^id=" "${plugin_file}" && grep -q "^entry=" "${plugin_file}"; then
            entry=$(grep "^entry=" "${plugin_file}" | cut -d= -f2)
            if [[ -f "${ADDONS_DIR}/${entry}" ]]; then
                log "OK: Plugin '${plugin_id}' registered (entry: ${entry})"
                ((LOADED++))
            else
                log "WARN: Plugin '${plugin_id}' entry not found: ${entry}"
                ((FAILED++))
            fi
        else
            log "WARN: Plugin '${plugin_id}' missing required fields (id, entry)"
            ((FAILED++))
        fi
    done < <(find "${ADDONS_DIR}" -name "*.axonplugin" -maxdepth 1)
else
    log "INFO: No plugins found in ${ADDONS_DIR} — addons directory ready for future use"
fi

# ── Write registry ────────────────────────────────────────────────
python3 -c "
import json, os, datetime
reg = {'updated': datetime.datetime.now().isoformat(),
       'loaded': ${LOADED}, 'failed': ${FAILED}}
json.dump(reg, open('${REGISTRY}','w'), indent=2)
" 2>/dev/null

log "03-plugins.sh ✓  (loaded=${LOADED} failed=${FAILED})"
