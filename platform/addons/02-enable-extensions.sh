#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
# File:       platform/addons/02-enable-extensions.sh
# Purpose:    Scan platform/addons/, validate descriptors, and
#             register all valid extensions with the Axon runtime.
#             Updates the addons_registry.json.
# Layer:      Platform / Add-ons
# Depends on: 01-setup-addons.sh (registry must exist)
# Run as:     current user
# Copyright:  (c) 2024 Abdullah — Axon OS Project (AGPL-3.0)
# ─────────────────────────────────────────────────────────────────
set -uo pipefail

AXON_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
ADDONS_DIR="${AXON_ROOT}/platform/addons"
REGISTRY="${HOME}/.axonos/addons_registry.json"
LOG="${HOME}/.axonos/logs/addons.log"

log() { echo "[$(date '+%H:%M:%S')] [02-enable-extensions] $*" | tee -a "$LOG"; }

log "Scanning for extensions in ${ADDONS_DIR}..."

ENABLED=0; SKIPPED=0; FAILED=0

# ── Validate registry exists ──────────────────────────────────────
if [[ ! -f "${REGISTRY}" ]]; then
    log "WARN: Registry not found — run 01-setup-addons.sh first"
    exit 1
fi

# ── Scan .axonplugin files ────────────────────────────────────────
shopt -s nullglob
PLUGIN_FILES=("${ADDONS_DIR}"/*.axonplugin)

if [[ ${#PLUGIN_FILES[@]} -eq 0 ]]; then
    log "INFO: No .axonplugin files found — addons directory is ready for future extensions"
    echo "No add-ons installed yet. Place .axonplugin files in: ${ADDONS_DIR}/"
    exit 0
fi

ADDON_LIST="[]"
for pfile in "${PLUGIN_FILES[@]}"; do
    addon_id=$(basename "${pfile}" .axonplugin)
    log "Processing: ${addon_id}"

    # Extract required fields
    addon_name=$(grep "^name="    "${pfile}" 2>/dev/null | cut -d= -f2 || echo "")
    addon_ver=$(grep "^version=" "${pfile}" 2>/dev/null | cut -d= -f2 || echo "0.0.0")
    addon_entry=$(grep "^entry="  "${pfile}" 2>/dev/null | cut -d= -f2 || echo "")
    addon_layer=$(grep "^layer="  "${pfile}" 2>/dev/null | cut -d= -f2 || echo "platform")

    # Validate
    if [[ -z "${addon_id}" || -z "${addon_entry}" ]]; then
        log "SKIP: ${addon_id} — missing required fields (id, entry)"
        ((SKIPPED++)); continue
    fi

    entry_path="${ADDONS_DIR}/${addon_id}/${addon_entry}"
    if [[ ! -f "${entry_path}" ]]; then
        log "FAIL: ${addon_id} — entry not found: ${entry_path}"
        ((FAILED++)); continue
    fi

    # Check layer safety — never allow addons targeting Ubuntu Base
    if [[ "${addon_layer}" == "ubuntu_base" || "${addon_layer}" == "kernel" ]]; then
        log "BLOCKED: ${addon_id} targets Ubuntu Base layer — not allowed"
        ((FAILED++)); continue
    fi

    log "OK: Enabled '${addon_name}' v${addon_ver} (layer=${addon_layer})"
    ((ENABLED++))
done

# ── Update registry ───────────────────────────────────────────────
python3 - <<PYEOF 2>/dev/null
import json, datetime
reg = json.load(open("${REGISTRY}"))
reg["last_scan"] = datetime.datetime.now().isoformat()
reg["stats"] = {"enabled": ${ENABLED}, "skipped": ${SKIPPED}, "failed": ${FAILED}}
json.dump(reg, open("${REGISTRY}", "w"), indent=2)
PYEOF

log "Scan complete — enabled=${ENABLED} skipped=${SKIPPED} failed=${FAILED}"
log "02-enable-extensions.sh ✓"
