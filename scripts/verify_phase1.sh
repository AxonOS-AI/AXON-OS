#!/usr/bin/env bash
# AxonOS/scripts/verify_phase1.sh
# ─────────────────────────────────────────────────────────────────
# Copyright (c) 2024 Abdullah — Axon OS Project
# Licensed under AGPL-3.0 (see LICENSE)
#
# PURPOSE: Verify that Phase 1 of Axon OS has been completed.
#          Checks file structure, content integrity, and system
#          readiness — WITHOUT modifying anything.
#
# USAGE:
#   chmod +x verify_phase1.sh
#   bash verify_phase1.sh
# ─────────────────────────────────────────────────────────────────

set -uo pipefail

# ── Colors ────────────────────────────────────────────────────────
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
DIM='\033[2m'
NC='\033[0m'

# ── Counters ──────────────────────────────────────────────────────
PASS=0
FAIL=0
WARN=0

# ── Resolve project root (works from any directory) ───────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# ── Helpers ───────────────────────────────────────────────────────
pass() { echo -e "  ${GREEN}✓${NC}  $1"; ((PASS++)); }
fail() { echo -e "  ${RED}✗${NC}  $1"; ((FAIL++)); }
warn() { echo -e "  ${YELLOW}⚠${NC}  $1"; ((WARN++)); }
section() { echo -e "\n${CYAN}▸ $1${NC}"; }

check_file() {
    local path="$1"
    local label="$2"
    if [[ -f "${PROJECT_ROOT}/${path}" ]]; then
        pass "$label"
    else
        fail "$label — not found: ${path}"
    fi
}

check_dir() {
    local path="$1"
    local label="$2"
    if [[ -d "${PROJECT_ROOT}/${path}" ]]; then
        pass "$label"
    else
        fail "$label — not found: ${path}"
    fi
}

check_nonempty() {
    local path="$1"
    local label="$2"
    local full="${PROJECT_ROOT}/${path}"
    if [[ -f "$full" ]] && [[ -s "$full" ]]; then
        pass "$label (not empty)"
    elif [[ -f "$full" ]]; then
        warn "$label (exists but empty)"
    else
        fail "$label — not found: ${path}"
    fi
}

check_contains() {
    local path="$1"
    local keyword="$2"
    local label="$3"
    local full="${PROJECT_ROOT}/${path}"
    if [[ -f "$full" ]] && grep -q "$keyword" "$full" 2>/dev/null; then
        pass "$label"
    elif [[ -f "$full" ]]; then
        warn "$label (file exists but missing keyword: '$keyword')"
    else
        fail "$label — file not found: ${path}"
    fi
}

check_executable() {
    local path="$1"
    local label="$2"
    local full="${PROJECT_ROOT}/${path}"
    if [[ -f "$full" ]] && [[ -x "$full" ]]; then
        pass "$label (executable)"
    elif [[ -f "$full" ]]; then
        warn "$label (exists but not executable — run: chmod +x ${path})"
    else
        fail "$label — not found: ${path}"
    fi
}

# ═══════════════════════════════════════════════════════════════════
echo ""
echo -e "${CYAN}╔═══════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     Axon OS — Phase 1 Verification        ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════╝${NC}"
echo -e "${DIM}  Project root: ${PROJECT_ROOT}${NC}"
# ═══════════════════════════════════════════════════════════════════

# ──────────────────────────────────────────────────────────────────
section "1. Project Root Structure"
# ──────────────────────────────────────────────────────────────────
check_dir  "boot"                            "boot/ directory"
check_dir  "platform"                        "platform/ directory"
check_dir  "ai-container"                    "ai-container/ directory"
check_dir  "scripts"                         "scripts/ directory"
check_file "README.md"                       "README.md"

# ──────────────────────────────────────────────────────────────────
section "2. Boot Layer Files"
# ──────────────────────────────────────────────────────────────────
check_dir  "boot/splash"                     "boot/splash/"
check_dir  "boot/init-scripts"               "boot/init-scripts/"
check_dir  "boot/config"                     "boot/config/"

# Plymouth theme (NOTE: boot screen is deferred to last phase,
# but the directory stubs must exist as scaffolding)
check_dir  "boot/splash/plymouth"            "Plymouth theme directory (scaffold)"

# ──────────────────────────────────────────────────────────────────
section "3. Phase 1 Boot Simulator (Splash Preview)"
# ──────────────────────────────────────────────────────────────────
# These files were built in Phase 1 (simulator path may differ
# depending on where the user placed them).
# Check both possible locations.

SPLASH_A="phase1_boot/splash_simulator"
SPLASH_B="boot/splash/simulator"

if [[ -d "${PROJECT_ROOT}/${SPLASH_A}" ]]; then
    SIM_PATH="$SPLASH_A"
    pass "Simulator directory found at: ${SPLASH_A}"
elif [[ -d "${PROJECT_ROOT}/${SPLASH_B}" ]]; then
    SIM_PATH="$SPLASH_B"
    pass "Simulator directory found at: ${SPLASH_B}"
else
    fail "Splash simulator directory not found (checked: ${SPLASH_A} | ${SPLASH_B})"
    SIM_PATH=""
fi

if [[ -n "$SIM_PATH" ]]; then
    check_nonempty  "${SIM_PATH}/main.py"            "main.py (entry point)"
    check_nonempty  "${SIM_PATH}/config.py"          "config.py (settings)"
    check_nonempty  "${SIM_PATH}/animation.py"       "animation.py (engine)"
    check_nonempty  "${SIM_PATH}/logo_generator.py"  "logo_generator.py"

    check_contains  "${SIM_PATH}/config.py"    "OS_NAME"       "config.py contains OS_NAME"
    check_contains  "${SIM_PATH}/config.py"    "BOOT_MESSAGES" "config.py contains BOOT_MESSAGES"
    check_contains  "${SIM_PATH}/main.py"      "BootSplash"    "main.py contains BootSplash class"
    check_contains  "${SIM_PATH}/animation.py" "ProgressBar"   "animation.py contains ProgressBar"
    check_contains  "${SIM_PATH}/animation.py" "Particle"      "animation.py contains Particle"
fi

# ──────────────────────────────────────────────────────────────────
section "4. Plymouth Theme Files (scaffold — visual deferred)"
# ──────────────────────────────────────────────────────────────────
PLYM_A="phase1_boot/plymouth"
PLYM_B="boot/splash/plymouth"

if [[ -d "${PROJECT_ROOT}/${PLYM_A}" ]]; then
    PLYM_PATH="$PLYM_A"
    pass "Plymouth directory found at: ${PLYM_A}"
elif [[ -d "${PROJECT_ROOT}/${PLYM_B}" ]]; then
    PLYM_PATH="$PLYM_B"
    pass "Plymouth directory found at: ${PLYM_B}"
else
    warn "Plymouth directory not found — visual boot screen deferred to last phase (OK)"
    PLYM_PATH=""
fi

if [[ -n "$PLYM_PATH" ]]; then
    check_nonempty "${PLYM_PATH}/axon.plymouth" "axon.plymouth (theme config)"
    check_nonempty "${PLYM_PATH}/axon.script"   "axon.script (animation)"
fi

# ──────────────────────────────────────────────────────────────────
section "5. Install & Utility Scripts"
# ──────────────────────────────────────────────────────────────────
SCRIPT_A="phase1_boot/scripts"
SCRIPT_B="scripts/install"

if [[ -d "${PROJECT_ROOT}/${SCRIPT_A}" ]]; then
    check_executable "${SCRIPT_A}/install_theme.sh"  "install_theme.sh"
    check_executable "${SCRIPT_A}/check_deps.sh"     "check_deps.sh"
elif [[ -d "${PROJECT_ROOT}/${SCRIPT_B}" ]]; then
    check_executable "${SCRIPT_B}/install_theme.sh"  "install_theme.sh"
    check_executable "${SCRIPT_B}/check_deps.sh"     "check_deps.sh"
else
    warn "Scripts directory not found at ${SCRIPT_A} or ${SCRIPT_B}"
fi

# ──────────────────────────────────────────────────────────────────
section "6. Documentation"
# ──────────────────────────────────────────────────────────────────
check_nonempty "README.md"              "README.md"
check_nonempty "docs/PHASE1_NOTES.md"  "docs/PHASE1_NOTES.md"

check_contains "README.md" "Axon OS"   "README.md mentions Axon OS"
check_contains "README.md" "Phase"     "README.md mentions Phases"

# ──────────────────────────────────────────────────────────────────
section "7. Python Environment Check (for simulator)"
# ──────────────────────────────────────────────────────────────────
if command -v python3 &>/dev/null; then
    PY_VER=$(python3 -c 'import sys; print(".".join(map(str,sys.version_info[:2])))')
    if python3 -c 'import sys; assert sys.version_info >= (3,8)' 2>/dev/null; then
        pass "Python ${PY_VER} >= 3.8"
    else
        fail "Python ${PY_VER} < 3.8 — upgrade required"
    fi
else
    fail "Python 3 not found"
fi

if python3 -c 'import pygame' 2>/dev/null; then
    pass "pygame installed (simulator ready)"
else
    warn "pygame not installed — run: pip install pygame"
fi

# ──────────────────────────────────────────────────────────────────
section "8. Git Repository Check"
# ──────────────────────────────────────────────────────────────────
if [[ -d "${PROJECT_ROOT}/.git" ]]; then
    pass "Git repository initialized"
    COMMITS=$(git -C "${PROJECT_ROOT}" rev-list --count HEAD 2>/dev/null || echo "0")
    if [[ "$COMMITS" -gt 0 ]]; then
        pass "Git has ${COMMITS} commit(s)"
    else
        warn "Git initialized but no commits yet — run: git add . && git commit -m 'Phase 1'"
    fi
else
    warn "Git not initialized — run: git init && git add . && git commit -m 'Phase 1'"
fi

# ──────────────────────────────────────────────────────────────────
section "9. LICENSE & Copyright (required for open source)"
# ──────────────────────────────────────────────────────────────────
if [[ -f "${PROJECT_ROOT}/LICENSE" ]]; then
    pass "LICENSE file exists"
else
    warn "LICENSE file missing — needed for GitHub open source + IP protection"
fi

if [[ -f "${PROJECT_ROOT}/NOTICE" ]]; then
    pass "NOTICE file exists"
else
    warn "NOTICE file missing — recommended for attribution protection"
fi

# ═══════════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════════
TOTAL=$((PASS + FAIL + WARN))

echo ""
echo -e "${CYAN}═══════════════════════════════════════════${NC}"
echo -e "  Results: ${GREEN}${PASS} passed${NC} | ${RED}${FAIL} failed${NC} | ${YELLOW}${WARN} warnings${NC}"
echo -e "${CYAN}═══════════════════════════════════════════${NC}"
echo ""

if [[ $FAIL -eq 0 && $WARN -eq 0 ]]; then
    echo -e "  ${GREEN}✅ Phase 1 COMPLETE — all checks passed.${NC}"
    echo -e "  ${DIM}Ready to begin Phase 2: Desktop Environment.${NC}"
    exit 0
elif [[ $FAIL -eq 0 ]]; then
    echo -e "  ${YELLOW}⚠️  Phase 1 MOSTLY COMPLETE — warnings only.${NC}"
    echo -e "  ${DIM}Review warnings above before proceeding to Phase 2.${NC}"
    exit 0
else
    echo -e "  ${RED}❌ Phase 1 INCOMPLETE — ${FAIL} item(s) missing.${NC}"
    echo -e "  ${DIM}Fix the failures above before proceeding to Phase 2.${NC}"
    exit 1
fi
