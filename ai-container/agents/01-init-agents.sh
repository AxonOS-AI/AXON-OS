#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
# File:       ai-container/agents/01-init-agents.sh
# Purpose:    Initialize the Axon OS AI Agents System inside the
#             Docker container. Registers agent definitions and
#             starts the agent orchestrator process.
#             Agents System is marked as FUTURE — scaffold only.
# Layer:      AI Container
# Depends on: ai-container/assistant/02-init-runtime.sh (container running)
# Run as:     current user (docker group)
# Copyright:  (c) 2024 Abdullah — Axon OS Project (AGPL-3.0)
# ─────────────────────────────────────────────────────────────────
set -uo pipefail

AXON_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
AGENTS_DIR="${AXON_ROOT}/ai-container/agents"
CONTAINER_NAME="axon-ai-runtime"
AGENTS_REGISTRY="${HOME}/.axonos/agents_registry.json"
LOG="${HOME}/.axonos/logs/ai_container.log"

log() { echo "[$(date '+%H:%M:%S')] [01-init-agents] $*" | tee -a "$LOG"; }

log "Initializing Axon OS Agents System..."

# ── Create agents directory structure ────────────────────────────
mkdir -p "${AGENTS_DIR}"/{definitions,state,logs}

# ── Write initial agent definitions (scaffold) ───────────────────
AGENT_DEF="${AGENTS_DIR}/definitions/system_agent.json"
if [[ ! -f "${AGENT_DEF}" ]]; then
    cat > "${AGENT_DEF}" <<'EOF'
{
    "id": "system_agent",
    "name": "Axon System Agent",
    "version": "1.0.0",
    "status": "scaffold",
    "description": "Core system automation agent — monitors platform health and triggers maintenance tasks",
    "capabilities": [
        "monitor_resources",
        "trigger_updates",
        "cleanup_logs",
        "notify_user"
    ],
    "trigger": "scheduled",
    "schedule": "0 * * * *",
    "layer": "ai_container",
    "note": "Full implementation in Phase 5 — Agents System"
}
EOF
    log "OK: System agent definition created"
fi

# ── Initialize registry ───────────────────────────────────────────
python3 - <<'PYEOF' 2>/dev/null
import json, datetime, os

registry_path = os.path.expanduser("~/.axonos/agents_registry.json")
registry = {
    "version": "1.0.0",
    "initialized": datetime.datetime.now().isoformat(),
    "status": "scaffold",
    "agents": [],
    "note": "Agents System is planned for Phase 5 — framework initialized"
}

agents_dir = os.path.expanduser("${AGENTS_DIR}/definitions")
for fname in os.listdir(agents_dir):
    if fname.endswith(".json"):
        try:
            with open(os.path.join(agents_dir, fname)) as f:
                agent = json.load(f)
            registry["agents"].append({
                "id": agent.get("id"),
                "name": agent.get("name"),
                "status": agent.get("status", "scaffold")
            })
        except Exception as e:
            print(f"WARN: Could not load {fname}: {e}")

json.dump(registry, open(registry_path, "w"), indent=2)
print(f"Registry written: {len(registry['agents'])} agent(s)")
PYEOF

# ── Docker check ──────────────────────────────────────────────────
if ! command -v docker &>/dev/null; then
    log "INFO: Docker not available — Agents System deferred to Phase 5"
    log "INFO: Agent definitions and registry initialized locally"
    exit 0
fi

if ! docker ps --format '{{.Names}}' 2>/dev/null | grep -q "^${CONTAINER_NAME}$"; then
    log "INFO: Container not running — agent runtime will start in Phase 5"
    exit 0
fi

# ── Register agents inside container ─────────────────────────────
docker exec "${CONTAINER_NAME}" python3 -c "
import os, json
os.makedirs('/axon/agents/state', exist_ok=True)
print('Agents framework ready inside container')
" 2>/dev/null && log "OK: Agents framework registered in container"

log "01-init-agents.sh ✓  (scaffold ready — full implementation: Phase 5)"
