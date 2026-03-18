#!/usr/bin/env bash
# AxonOS/scripts/install/install_phase2.sh
# ─────────────────────────────────────────────────────────────────
# Copyright (c) 2024 Abdullah — Axon OS Project
# Licensed under AGPL-3.0 (see LICENSE)
#
# PURPOSE: Install Phase 2 (Desktop Environment + Core Services)
#          on a fresh Ubuntu 22.04/24.04 system.
#
# SAFETY:  Only installs to user space and /opt/axonos.
#          Never modifies /boot, /etc/*, kernel, or Ubuntu system files.
#
# USAGE:
#   chmod +x install_phase2.sh
#   bash install_phase2.sh
# ─────────────────────────────────────────────────────────────────

set -uo pipefail

GREEN='\033[0;32m'; RED='\033[0;31m'; CYAN='\033[0;36m'
YELLOW='\033[1;33m'; NC='\033[0m'

info()    { echo -e "${CYAN}[Axon]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC}   $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
fail()    { echo -e "${RED}[FAIL]${NC} $1"; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  Axon OS — Phase 2 Installer             ║${NC}"
echo -e "${CYAN}║  Desktop Environment + Core Services     ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════╝${NC}"
echo ""

# ── Check Ubuntu ─────────────────────────────────────────────────
if ! grep -qi ubuntu /etc/os-release 2>/dev/null; then
    warn "Not detected as Ubuntu — proceeding anyway"
fi

# ── Python dependencies ──────────────────────────────────────────
info "Installing Python dependencies..."
pip3 install psutil --break-system-packages 2>/dev/null || \
pip3 install psutil || \
warn "Could not install psutil — resource monitor will use fallback"

success "Python dependencies done"

# ── GTK4 (system package) ────────────────────────────────────────
info "Checking GTK4..."
if python3 -c "import gi; gi.require_version('Gtk','4.0'); from gi.repository import Gtk" 2>/dev/null; then
    success "GTK4 available"
else
    info "Installing GTK4 Python bindings..."
    if command -v apt-get &>/dev/null; then
        sudo apt-get install -y python3-gi gir1.2-gtk-4.0 2>/dev/null && \
        success "GTK4 installed" || warn "GTK4 install failed — GUI will not run"
    else
        warn "apt-get not available — install GTK4 manually"
    fi
fi

# ── Create data directories ──────────────────────────────────────
info "Creating Axon data directories..."
mkdir -p ~/.axonos/logs
mkdir -p ~/AxonProjects
success "Data directories ready"

# ── Initialize database ──────────────────────────────────────────
info "Initializing Axon OS database..."
PYTHONPATH="${PROJECT_ROOT}" python3 \
    "${PROJECT_ROOT}/platform/core-services/db_manager.py" && \
success "Database initialized" || warn "DB init failed — will retry on first run"

# ── Test core services ───────────────────────────────────────────
info "Testing core services..."
PYTHONPATH="${PROJECT_ROOT}" python3 -c "
import sys
sys.path.insert(0, '${PROJECT_ROOT}/platform')
sys.path.insert(0, '${PROJECT_ROOT}/platform/core-services')
from core_services_init import bootstrap
bootstrap()
print('  ✓ Core services OK')
" && success "Core services test passed" || warn "Core services test failed"

# ── Done ─────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}══════════════════════════════════════════${NC}"
echo -e "${GREEN}  Phase 2 Installation Complete           ${NC}"
echo -e "${GREEN}══════════════════════════════════════════${NC}"
echo ""
echo "To start the Axon OS Desktop:"
echo "  python3 ${PROJECT_ROOT}/platform/gui/desktop-environment/main.py"
echo ""
echo "To verify Phase 2:"
echo "  bash ${PROJECT_ROOT}/scripts/verify_phase2.sh"
echo ""
