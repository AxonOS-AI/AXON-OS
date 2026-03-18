#!/usr/bin/env bash
# axon-os/phase1_boot/scripts/check_deps.sh
# ──────────────────────────────────────────
# Axon OS — Dependency Checker for Phase 1
# Run before installing or building anything.
# ──────────────────────────────────────────

set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASS=0
FAIL=0

check() {
    local label="$1"
    local cmd="$2"
    if eval "$cmd" &>/dev/null; then
        echo -e "  ${GREEN}✓${NC}  $label"
        ((PASS++))
    else
        echo -e "  ${RED}✗${NC}  $label"
        ((FAIL++))
    fi
}

echo ""
echo -e "${CYAN}Axon OS — Phase 1 Dependency Check${NC}"
echo "──────────────────────────────────────"

echo ""
echo "System:"
check "Ubuntu detected"         "grep -qi ubuntu /etc/os-release"
check "Python 3.8+"             "python3 -c 'import sys; assert sys.version_info >= (3,8)'"
check "pip available"           "pip3 --version"
check "Plymouth installed"      "command -v plymouth"
check "update-initramfs"        "command -v update-initramfs"

echo ""
echo "Python packages (simulator):"
check "pygame"                  "python3 -c 'import pygame'"
check "math (stdlib)"           "python3 -c 'import math'"
check "random (stdlib)"         "python3 -c 'import random'"

echo ""
echo "Optional:"
check "PIL/Pillow (logo gen)"   "python3 -c 'from PIL import Image'"
check "git"                     "command -v git"

echo ""
echo "──────────────────────────────────────"
echo -e "  ${GREEN}${PASS} passed${NC}  |  ${RED}${FAIL} failed${NC}"
echo ""

if (( FAIL > 0 )); then
    echo "Install missing Python packages:"
    echo "  pip install pygame Pillow"
    echo ""
fi

if ! command -v plymouth &>/dev/null; then
    echo "Install Plymouth:"
    echo "  sudo apt-get install plymouth plymouth-themes"
    echo ""
fi
