#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
# File:       platform/addons/01-setup-addons.sh
# Purpose:    Initialize the Axon OS add-ons framework.
#             Creates the addon registry, validates the addons
#             directory structure, and writes the addon manifest.
# Layer:      Platform / Add-ons
# Depends on: platform/core-services/02-project-manager.sh (DB ready)
# Run as:     current user
# Copyright:  (c) 2024 Abdullah — Axon OS Project (AGPL-3.0)
# ─────────────────────────────────────────────────────────────────
set -uo pipefail

AXON_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
ADDONS_DIR="${AXON_ROOT}/platform/addons"
REGISTRY="${HOME}/.axonos/addons_registry.json"
LOG="${HOME}/.axonos/logs/addons.log"

log() { echo "[$(date '+%H:%M:%S')] [01-setup-addons] $*" | tee -a "$LOG"; }

log "Initializing Axon OS Add-ons Framework..."

# ── Create addon sub-directories ──────────────────────────────────
for subdir in installed available disabled cache; do
    mkdir -p "${ADDONS_DIR}/${subdir}"
done
log "OK: Addon directories ready"

# ── Write addon manifest schema ───────────────────────────────────
MANIFEST="${ADDONS_DIR}/ADDON_MANIFEST.md"
if [[ ! -f "${MANIFEST}" ]]; then
cat > "${MANIFEST}" <<'EOF'
# Axon OS — Add-on Manifest

Each add-on must have a `.axonplugin` descriptor file with:

```ini
[addon]
id=my_addon
name=My Addon
version=1.0.0
description=What this addon does
entry=main.py
layer=platform
requires=
```

Place descriptor in: platform/addons/
Place code in:       platform/addons/<id>/

The add-on loader (02-enable-extensions.sh) scans this directory
and registers valid add-ons with the desktop shell.
EOF
log "OK: Addon manifest written"
fi

# ── Initialize registry JSON ──────────────────────────────────────
python3 - <<PYEOF 2>/dev/null
import json, os, datetime
registry = {
    "version": "1.0.0",
    "created": datetime.datetime.now().isoformat(),
    "addons": [],
    "note": "Managed by Axon OS — do not edit manually"
}
if not os.path.exists("${REGISTRY}"):
    json.dump(registry, open("${REGISTRY}", "w"), indent=2)
    print("Registry created")
else:
    print("Registry already exists")
PYEOF

log "OK: Add-ons framework initialized"
log "INFO: To install an add-on, place it in ${ADDONS_DIR}/"
log "INFO: Then run: ./02-enable-extensions.sh"
log "01-setup-addons.sh ✓"
