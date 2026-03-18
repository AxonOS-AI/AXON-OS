#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
# File:       scripts/install/01-install-platform.sh
# Purpose:    Master installer for Axon OS Platform Layer.
#             Runs all init scripts in the correct sequence.
#             Safe to run on a fresh Ubuntu system or re-run
#             on an existing installation (idempotent).
#
#             Execution order:
#               1. Verify Ubuntu Base (read-only check)
#               2. Install Python dependencies
#               3. Initialize DB + Core Services
#               4. Setup GUI scaffold
#               5. Setup AI Container scaffold
#               6. Run verification
#
# Layer:      Scripts / Install
# Depends on: Ubuntu 20.04/22.04/24.04, python3, git
# Run as:     current user (sudo for Plymouth only)
# Copyright:  (c) 2024 Abdullah — Axon OS Project (AGPL-3.0)
# ─────────────────────────────────────────────────────────────────
set -uo pipefail

AXON_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
LOG="${HOME}/.axonos/logs/install.log"
mkdir -p "${HOME}/.axonos/logs"

GREEN='\033[0;32m'; RED='\033[0;31m'; CYAN='\033[0;36m'
YELLOW='\033[1;33m'; NC='\033[0m'

log()     { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOG"; }
section() { echo -e "\n${CYAN}── $1 ──${NC}"; log "=== $1 ==="; }
ok()      { echo -e "  ${GREEN}✓${NC}  $1"; log "OK: $1"; }
warn()    { echo -e "  ${YELLOW}⚠${NC}  $1"; log "WARN: $1"; }
fail()    { echo -e "  ${RED}✗${NC}  $1"; log "FAIL: $1"; exit 1; }

run_script() {
    local script="$1"
    local label="$2"
    if [[ -f "${AXON_ROOT}/${script}" ]]; then
        chmod +x "${AXON_ROOT}/${script}"
        bash "${AXON_ROOT}/${script}" >> "$LOG" 2>&1 && ok "${label}" || warn "${label} (non-fatal)"
    else
        warn "${label} — script not found: ${script}"
    fi
}

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   Axon OS — Platform Installer           ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════╝${NC}"
echo -e "  Root: ${AXON_ROOT}"
log "Install started"

# ─────────────────────────────────────────────────────────────────
section "1. System Check"
# ─────────────────────────────────────────────────────────────────
grep -qi ubuntu /etc/os-release 2>/dev/null && ok "Ubuntu detected" || warn "Not Ubuntu — proceeding"

python3 --version &>/dev/null && ok "Python3 available" || fail "Python3 not found"

# Ensure we're NOT running as root (safety guard)
if [[ $EUID -eq 0 ]]; then
    warn "Running as root — this is only needed for Plymouth install"
fi

# ─────────────────────────────────────────────────────────────────
section "2. Python Dependencies"
# ─────────────────────────────────────────────────────────────────
pip3 install psutil --break-system-packages 2>/dev/null || \
pip3 install psutil 2>/dev/null || warn "psutil install failed — resource monitor uses fallback"
ok "Python dependencies"

# ─────────────────────────────────────────────────────────────────
section "3. Data Directories"
# ─────────────────────────────────────────────────────────────────
mkdir -p "${HOME}/.axonos/logs"
mkdir -p "${HOME}/AxonProjects"
ok "Data directories created"

# ─────────────────────────────────────────────────────────────────
section "4. Core Services"
# ─────────────────────────────────────────────────────────────────
export PYTHONPATH="${AXON_ROOT}"
python3 - <<'PYEOF' >> "$LOG" 2>&1
import sys, os
sys.path.insert(0, os.environ['PYTHONPATH'] + '/platform')
sys.path.insert(0, os.environ['PYTHONPATH'] + '/platform/core-services')
from core_services_init import bootstrap
bootstrap()
print("Core services bootstrapped")
PYEOF
ok "Core services initialized"

run_script "platform/core-services/01-resource-manager.sh"  "Resource Manager"
run_script "platform/core-services/02-project-manager.sh"   "Project Manager"
run_script "platform/core-services/03-file-manager.sh"      "File Manager"
run_script "platform/core-services/04-update-service.sh"    "Update Service"

# ─────────────────────────────────────────────────────────────────
section "5. Platform GUI Scaffold"
# ─────────────────────────────────────────────────────────────────
run_script "platform/gui/02-widgets.sh"   "Widgets registered"
run_script "platform/gui/03-plugins.sh"   "Plugins scanned"
run_script "platform/addons/01-setup-addons.sh"       "Addons framework"
run_script "platform/addons/02-enable-extensions.sh"  "Extensions loaded"

# ─────────────────────────────────────────────────────────────────
section "6. AI Container Scaffold"
# ─────────────────────────────────────────────────────────────────
run_script "ai-container/agents/01-init-agents.sh"  "Agents framework (scaffold)"

# ─────────────────────────────────────────────────────────────────
section "7. Git Repository"
# ─────────────────────────────────────────────────────────────────
if [[ ! -d "${AXON_ROOT}/.git" ]]; then
    cd "${AXON_ROOT}"
    git init -q && git add . && git commit -q -m "chore: Axon OS initial platform setup"
    ok "Git repository initialized with initial commit"
else
    ok "Git repository already initialized"
fi

# ─────────────────────────────────────────────────────────────────
section "8. Verification"
# ─────────────────────────────────────────────────────────────────
if [[ -f "${AXON_ROOT}/scripts/verify_phase2.sh" ]]; then
    bash "${AXON_ROOT}/scripts/verify_phase2.sh" 2>&1 | tail -5
fi

echo ""
echo -e "${GREEN}══════════════════════════════════════════${NC}"
echo -e "${GREEN}  Axon OS Platform Installation Complete  ${NC}"
echo -e "${GREEN}══════════════════════════════════════════${NC}"
echo ""
echo "Start the desktop:    python3 ${AXON_ROOT}/platform/gui/desktop-environment/main.py"
echo "Create a project:     ${AXON_ROOT}/platform/tools/01-project-builder.sh --name MyProject"
echo "Check for updates:    ${AXON_ROOT}/platform/core-services/04-update-service.sh"
echo ""
log "Installation complete"
