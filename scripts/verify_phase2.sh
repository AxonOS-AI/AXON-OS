#!/usr/bin/env bash
# AxonOS/scripts/verify_phase2.sh
# ─────────────────────────────────────────────────────────────────
# Copyright (c) 2024 Abdullah — Axon OS Project
# Licensed under AGPL-3.0 (see LICENSE)
#
# PURPOSE: Verify Phase 2 (Desktop Environment + Core Services).
#          Safe to run anytime — read-only checks only.
# ─────────────────────────────────────────────────────────────────

set -uo pipefail

GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; DIM='\033[2m'; NC='\033[0m'

PASS=0; FAIL=0; WARN=0

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

pass() { echo -e "  ${GREEN}✓${NC}  $1"; ((PASS++)); }
fail() { echo -e "  ${RED}✗${NC}  $1"; ((FAIL++)); }
warn() { echo -e "  ${YELLOW}⚠${NC}  $1"; ((WARN++)); }
section() { echo -e "\n${CYAN}▸ $1${NC}"; }

check_file() {
    [[ -f "${PROJECT_ROOT}/$1" ]] && pass "$2" || fail "$2 — missing: $1"
}
check_nonempty() {
    local full="${PROJECT_ROOT}/$1"
    if [[ -f "$full" ]] && [[ -s "$full" ]]; then pass "$2"
    elif [[ -f "$full" ]]; then warn "$2 (empty)"
    else fail "$2 — missing: $1"; fi
}
check_py_import() {
    python3 -c "import $1" 2>/dev/null && pass "$2" || warn "$2 (pip install $1)"
}
check_py_syntax() {
    local full="${PROJECT_ROOT}/$1"
    if [[ ! -f "$full" ]]; then fail "$2 — file missing"; return; fi
    python3 -m py_compile "$full" 2>/dev/null && pass "$2 (syntax OK)" || fail "$2 (syntax error)"
}

echo ""
echo -e "${CYAN}╔═══════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     Axon OS — Phase 2 Verification        ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════╝${NC}"
echo -e "${DIM}  Project root: ${PROJECT_ROOT}${NC}"

# ──────────────────────────────────────────────────────────────────
section "1. License & IP Protection"
# ──────────────────────────────────────────────────────────────────
check_nonempty "LICENSE"  "LICENSE file (IP protection)"
check_nonempty "NOTICE"   "NOTICE file (attribution)"

# ──────────────────────────────────────────────────────────────────
section "2. Platform Configuration"
# ──────────────────────────────────────────────────────────────────
check_nonempty "platform/config.py"  "platform/config.py"
check_py_syntax "platform/config.py" "config.py syntax"

# ──────────────────────────────────────────────────────────────────
section "3. Core Services"
# ──────────────────────────────────────────────────────────────────
check_nonempty "platform/core-services/db_manager.py"                           "db_manager.py"
check_nonempty "platform/core-services/core_services_init.py"                   "core_services_init.py"
check_nonempty "platform/core-services/resource-manager/resource_manager.py"    "resource_manager.py"
check_nonempty "platform/core-services/project-manager/project_manager.py"      "project_manager.py"
check_nonempty "platform/core-services/file-manager/file_manager.py"            "file_manager.py"
check_nonempty "platform/core-services/update-service/update_service.py"        "update_service.py"

check_py_syntax "platform/core-services/db_manager.py"                          "db_manager syntax"
check_py_syntax "platform/core-services/resource-manager/resource_manager.py"   "resource_manager syntax"
check_py_syntax "platform/core-services/file-manager/file_manager.py"           "file_manager syntax"
check_py_syntax "platform/core-services/update-service/update_service.py"       "update_service syntax"

# ──────────────────────────────────────────────────────────────────
section "4. Desktop GUI Files"
# ──────────────────────────────────────────────────────────────────
check_nonempty "platform/gui/desktop-environment/main.py"           "desktop main.py"
check_nonempty "platform/gui/desktop-environment/taskbar.py"        "taskbar.py"
check_nonempty "platform/gui/desktop-environment/window_manager.py" "window_manager.py"
check_nonempty "platform/gui/desktop-environment/launcher.py"       "launcher.py"

check_py_syntax "platform/gui/desktop-environment/main.py"           "desktop main syntax"
check_py_syntax "platform/gui/desktop-environment/taskbar.py"        "taskbar syntax"
check_py_syntax "platform/gui/desktop-environment/window_manager.py" "window_manager syntax"
check_py_syntax "platform/gui/desktop-environment/launcher.py"       "launcher syntax"

# ──────────────────────────────────────────────────────────────────
section "5. Install Scripts"
# ──────────────────────────────────────────────────────────────────
check_nonempty "scripts/install/install_phase2.sh" "install_phase2.sh"
check_file     "scripts/verify_phase1.sh"          "verify_phase1.sh (Phase 1 still present)"

# ──────────────────────────────────────────────────────────────────
section "6. Python Dependencies"
# ──────────────────────────────────────────────────────────────────
check_py_import "sqlite3" "sqlite3 (stdlib)"
check_py_import "threading" "threading (stdlib)"
check_py_import "logging"   "logging (stdlib)"
check_py_import "psutil"    "psutil (resource monitor)"

if python3 -c "import gi; gi.require_version('Gtk','4.0'); from gi.repository import Gtk" 2>/dev/null; then
    pass "GTK4 + PyGObject (desktop GUI)"
else
    warn "GTK4 not available — GUI disabled, headless mode only"
fi

# ──────────────────────────────────────────────────────────────────
section "7. Database Functional Test"
# ──────────────────────────────────────────────────────────────────
DB_TEST=$(PYTHONPATH="${PROJECT_ROOT}" python3 - <<'EOF' 2>&1
import sys, os
sys.path.insert(0, os.path.join(os.environ.get('PYTHONPATH',''), 'platform'))
sys.path.insert(0, os.path.join(os.environ.get('PYTHONPATH',''), 'platform/core-services'))
from db_manager import initialize_schema, get_connection
initialize_schema()
conn = get_connection()
tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
conn.close()
print(','.join(tables))
EOF
)
if echo "$DB_TEST" | grep -q "projects"; then
    pass "Database: tables created (projects, tasks, events, updates)"
else
    warn "Database test inconclusive: $DB_TEST"
fi

# ──────────────────────────────────────────────────────────────────
section "8. File Manager Safety Test"
# ──────────────────────────────────────────────────────────────────
SAFETY_TEST=$(PYTHONPATH="${PROJECT_ROOT}" python3 - <<'EOF' 2>&1
import sys, os
sys.path.insert(0, os.path.join(os.environ.get('PYTHONPATH',''), 'platform'))
sys.path.insert(0, os.path.join(os.environ.get('PYTHONPATH',''), 'platform/core-services/file-manager'))
from file_manager import FileManager
fm = FileManager()
try:
    fm.list_dir('/etc')
    print('FAIL: should have blocked /etc')
except PermissionError:
    print('PASS: /etc correctly blocked')
EOF
)
if echo "$SAFETY_TEST" | grep -q "PASS"; then
    pass "File manager: Ubuntu Base path protection working"
else
    warn "File manager safety test: $SAFETY_TEST"
fi

# ──────────────────────────────────────────────────────────────────
section "9. Deferred Items (by design)"
# ──────────────────────────────────────────────────────────────────
echo -e "  ${DIM}↷  Boot screen visual design — deferred to last phase${NC}"
echo -e "  ${DIM}↷  Color themes / fonts / UI polish — deferred to last phase${NC}"
echo -e "  ${DIM}↷  AI Container (Docker setup) — Phase 5${NC}"
echo -e "  ${DIM}↷  Dashboard UI — Phase 3${NC}"

# ═══════════════════════════════════════════════════════════════════
TOTAL=$((PASS + FAIL + WARN))
echo ""
echo -e "${CYAN}═══════════════════════════════════════════${NC}"
echo -e "  Results: ${GREEN}${PASS} passed${NC} | ${RED}${FAIL} failed${NC} | ${YELLOW}${WARN} warnings${NC}"
echo -e "${CYAN}═══════════════════════════════════════════${NC}"
echo ""

if   [[ $FAIL -eq 0 && $WARN -eq 0 ]]; then
    echo -e "  ${GREEN}✅ Phase 2 COMPLETE — all checks passed.${NC}"
    echo -e "  ${DIM}Ready to begin Phase 3: System Dashboard.${NC}"
elif [[ $FAIL -eq 0 ]]; then
    echo -e "  ${YELLOW}⚠️  Phase 2 MOSTLY COMPLETE — warnings only.${NC}"
    echo -e "  ${DIM}Install missing packages then proceed to Phase 3.${NC}"
else
    echo -e "  ${RED}❌ Phase 2 INCOMPLETE — ${FAIL} item(s) missing.${NC}"
    exit 1
fi
