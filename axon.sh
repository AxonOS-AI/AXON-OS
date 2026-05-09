#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
# File:       axon.sh
# Purpose:    Axon OS — single command system launcher.
#             Starts all services, checks dependencies,
#             supports safe mode, bilingual output.
# Layer:      Root / Startup
# Usage:
#   bash axon.sh start           — full system
#   bash axon.sh start --safe    — minimal (no AI Container)
#   bash axon.sh status          — show running services
#   bash axon.sh stop            — stop all services
#   bash axon.sh --lang ar       — Arabic output
# Copyright:  (c) 2024 Abdullah — Axon OS Project (AGPL-3.0)
# ─────────────────────────────────────────────────────────────────

set -uo pipefail

# ── Paths ─────────────────────────────────────────────────────────
AXON_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${HOME}/.axonos/logs"
PID_DIR="${HOME}/.axonos"
CONFIG="${HOME}/.axonos/config.json"

mkdir -p "${LOG_DIR}" "${PID_DIR}"

# ── Colors ────────────────────────────────────────────────────────
GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; DIM='\033[2m'; NC='\033[0m'

# ── Language ──────────────────────────────────────────────────────
LANG_CODE="en"

# Try to read from config
if [[ -f "$CONFIG" ]]; then
    SAVED_LANG=$(python3 -c "
import json, sys
try:
    print(json.load(open('${CONFIG}')).get('language','en'))
except: print('en')
" 2>/dev/null)
    LANG_CODE="${SAVED_LANG:-en}"
fi

# Override via CLI flag
for arg in "$@"; do
    [[ "$arg" == "--lang" ]] && { shift; LANG_CODE="${1:-en}"; break; }
    [[ "$arg" == "--lang=ar" ]] && { LANG_CODE="ar"; break; }
    [[ "$arg" == "--lang=en" ]] && { LANG_CODE="en"; break; }
done

# ── i18n ──────────────────────────────────────────────────────────
t() {
    local key="$1"
    if [[ "$LANG_CODE" == "ar" ]]; then
        case "$key" in
            title)       echo "نظام Axon OS" ;;
            starting)    echo "جاري تشغيل النظام..." ;;
            safe_mode)   echo "الوضع الآمن — بدون AI Container" ;;
            checking)    echo "فحص المتطلبات..." ;;
            dep_ok)      echo "✓  المتطلبات جاهزة" ;;
            dep_fail)    echo "✗  متطلب ناقص: $2" ;;
            gpu_detect)  echo "→  اكتشاف كرت الشاشة..." ;;
            core_start)  echo "→  تشغيل الخدمات الأساسية..." ;;
            core_ok)     echo "✓  الخدمات الأساسية تعمل" ;;
            desktop_start) echo "→  تشغيل سطح المكتب..." ;;
            desktop_ok)  echo "✓  سطح المكتب يعمل" ;;
            ai_start)    echo "→  تشغيل AI Container..." ;;
            ai_ok)       echo "✓  AI Container يعمل على منفذ 8080" ;;
            ai_skip)     echo "↷  AI Container — مؤجل (الوضع الآمن)" ;;
            done)        echo "✅ Axon OS جاهز" ;;
            stopping)    echo "جاري إيقاف النظام..." ;;
            stopped)     echo "✓  النظام أُوقف" ;;
            status_hdr)  echo "حالة Axon OS" ;;
            running)     echo "يعمل" ;;
            stopped_s)   echo "متوقف" ;;
            *)           echo "$key" ;;
        esac
    else
        case "$key" in
            title)       echo "Axon OS System" ;;
            starting)    echo "Starting Axon OS..." ;;
            safe_mode)   echo "Safe Mode — AI Container skipped" ;;
            checking)    echo "Checking dependencies..." ;;
            dep_ok)      echo "✓  Dependencies OK" ;;
            dep_fail)    echo "✗  Missing dependency: $2" ;;
            gpu_detect)  echo "→  Detecting GPU..." ;;
            core_start)  echo "→  Starting Core Services..." ;;
            core_ok)     echo "✓  Core Services running" ;;
            desktop_start) echo "→  Starting Desktop..." ;;
            desktop_ok)  echo "✓  Desktop running" ;;
            ai_start)    echo "→  Starting AI Container..." ;;
            ai_ok)       echo "✓  AI Container running on :8080" ;;
            ai_skip)     echo "↷  AI Container — skipped (safe mode)" ;;
            done)        echo "✅ Axon OS is ready" ;;
            stopping)    echo "Stopping Axon OS..." ;;
            stopped)     echo "✓  System stopped" ;;
            status_hdr)  echo "Axon OS Status" ;;
            running)     echo "running" ;;
            stopped_s)   echo "stopped" ;;
            *)           echo "$key" ;;
        esac
    fi
}

# ── Logging ───────────────────────────────────────────────────────
log() {
    echo "[$(date '+%H:%M:%S')] $*" >> "${LOG_DIR}/startup.log"
}

ok()   { echo -e "  ${GREEN}✓${NC}  $1"; log "OK: $1"; }
fail() { echo -e "  ${RED}✗${NC}  $1"; log "FAIL: $1"; }
info() { echo -e "  ${CYAN}→${NC}  $1"; log "INFO: $1"; }
warn() { echo -e "  ${YELLOW}⚠${NC}  $1"; log "WARN: $1"; }

# ── Header ────────────────────────────────────────────────────────
print_header() {
    echo ""
    echo -e "${CYAN}${BOLD}╔══════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}${BOLD}║         $(t title)         ║${NC}"
    echo -e "${CYAN}${BOLD}║                v1.0.0                        ║${NC}"
    echo -e "${CYAN}${BOLD}╚══════════════════════════════════════════════╝${NC}"
    echo ""
}

# ── Dependency check ──────────────────────────────────────────────
check_deps() {
    info "$(t checking)"
    local FAIL=0

    for cmd in python3 git; do
        if command -v "$cmd" &>/dev/null; then
            ok "$cmd"
        else
            fail "$(t dep_fail "$cmd")"
            FAIL=$((FAIL+1))
        fi
    done

    # Python version
    PY_VER=$(python3 -c "import sys; print(sys.version_info.major*10+sys.version_info.minor)" 2>/dev/null || echo 0)
    if [[ $PY_VER -ge 38 ]]; then
        ok "Python $(python3 --version 2>&1 | cut -d' ' -f2)"
    else
        fail "Python 3.8+ required"
        FAIL=$((FAIL+1))
    fi

    # Docker (optional — needed for AI Container)
    if command -v docker &>/dev/null; then
        ok "Docker $(docker --version 2>/dev/null | cut -d' ' -f3 | tr -d ',')"
    else
        warn "Docker not installed — AI Container will be skipped"
    fi

    return $FAIL
}

# ── GPU setup ─────────────────────────────────────────────────────
run_gpu_setup() {
    info "$(t gpu_detect)"
    local GPU_SCRIPT="${AXON_ROOT}/platform/core-services/resource-manager/gpu_setup.py"
    if [[ -f "$GPU_SCRIPT" ]]; then
        python3 "$GPU_SCRIPT" --check ${LANG_CODE:+--${LANG_CODE}} 2>/dev/null | \
            grep -E "(✓|✗|→|⚠|Backend|device|GPU|CPU)" | head -5 | \
            while IFS= read -r line; do echo "     $line"; done
    else
        warn "gpu_setup.py not found"
    fi
}

# ── Core Services ─────────────────────────────────────────────────
start_core() {
    info "$(t core_start)"

    # Run core service scripts in order
    for script in \
        "${AXON_ROOT}/platform/core-services/01-resource-manager.sh" \
        "${AXON_ROOT}/platform/core-services/02-project-manager.sh" \
        "${AXON_ROOT}/platform/core-services/03-file-manager.sh" \
        "${AXON_ROOT}/platform/core-services/04-update-service.sh"; do
        if [[ -f "$script" ]]; then
            bash "$script" >> "${LOG_DIR}/startup.log" 2>&1 || true
        fi
    done

    ok "$(t core_ok)"
    log "Core services started"
}

# ── Desktop Environment ───────────────────────────────────────────
start_desktop() {
    info "$(t desktop_start)"

    DESKTOP_MAIN="${AXON_ROOT}/platform/gui/desktop-environment/main.py"
    if [[ ! -f "$DESKTOP_MAIN" ]]; then
        warn "Desktop main.py not found"
        return
    fi

    # Check if already running
    if [[ -f "${PID_DIR}/desktop.pid" ]]; then
        PID=$(cat "${PID_DIR}/desktop.pid")
        if kill -0 "$PID" 2>/dev/null; then
            warn "Desktop already running (PID $PID)"
            return
        fi
    fi

    # Check if DISPLAY is available
    if [[ -z "${DISPLAY:-}" ]] && [[ -z "${WAYLAND_DISPLAY:-}" ]]; then
        warn "No display found — desktop skipped"
        return
    fi

    python3 "${DESKTOP_MAIN}" >> "${LOG_DIR}/gui.log" 2>&1 &
    DESK_PID=$!
    echo $DESK_PID > "${PID_DIR}/desktop.pid"
    sleep 1

    if kill -0 $DESK_PID 2>/dev/null; then
        ok "$(t desktop_ok)"
    else
        warn "Desktop failed to start — check ${LOG_DIR}/gui.log"
    fi
}

# ── AI Container ──────────────────────────────────────────────────
start_ai() {
    info "$(t ai_start)"

    if ! command -v docker &>/dev/null; then
        warn "Docker not found — AI Container skipped"
        return
    fi

    # Check if already running
    if docker ps --format '{{.Names}}' 2>/dev/null | grep -q "axon-ai-runtime"; then
        ok "AI Container already running"
        return
    fi

    local RUNTIME_SCRIPT="${AXON_ROOT}/ai-container/assistant/02-init-runtime.sh"
    if [[ -f "$RUNTIME_SCRIPT" ]]; then
        bash "$RUNTIME_SCRIPT" >> "${LOG_DIR}/ai_container.log" 2>&1 &
        sleep 3

        # Health check
        if curl -sf "http://localhost:8080/health" > /dev/null 2>&1; then
            ok "$(t ai_ok)"
        else
            warn "AI Container started but health check failed"
            warn "Check: ${LOG_DIR}/ai_container.log"
        fi
    else
        warn "02-init-runtime.sh not found"
    fi
}

# ── Stop all ──────────────────────────────────────────────────────
cmd_stop() {
    print_header
    info "$(t stopping)"

    # Stop desktop
    if [[ -f "${PID_DIR}/desktop.pid" ]]; then
        PID=$(cat "${PID_DIR}/desktop.pid")
        kill "$PID" 2>/dev/null && ok "Desktop stopped" || true
        rm -f "${PID_DIR}/desktop.pid"
    fi

    # Stop resource manager
    if [[ -f "${PID_DIR}/resource_manager.pid" ]]; then
        PID=$(cat "${PID_DIR}/resource_manager.pid")
        kill "$PID" 2>/dev/null && ok "Resource manager stopped" || true
        rm -f "${PID_DIR}/resource_manager.pid"
    fi

    # Stop AI Container
    if command -v docker &>/dev/null; then
        if docker ps --format '{{.Names}}' 2>/dev/null | grep -q "axon-ai-runtime"; then
            docker stop axon-ai-runtime >> "${LOG_DIR}/startup.log" 2>&1 && \
                ok "AI Container stopped" || true
        fi
    fi

    echo ""
    ok "$(t stopped)"
    log "System stopped"
}

# ── Status ────────────────────────────────────────────────────────
cmd_status() {
    print_header
    echo -e "  ${BOLD}$(t status_hdr)${NC}"
    echo -e "  ${DIM}────────────────────────────────────${NC}"

    # Desktop
    if [[ -f "${PID_DIR}/desktop.pid" ]]; then
        PID=$(cat "${PID_DIR}/desktop.pid")
        if kill -0 "$PID" 2>/dev/null; then
            echo -e "  ${GREEN}●${NC}  Desktop          $(t running) (PID $PID)"
        else
            echo -e "  ${RED}●${NC}  Desktop          $(t stopped_s)"
        fi
    else
        echo -e "  ${DIM}●  Desktop          $(t stopped_s)${NC}"
    fi

    # Resource Manager
    if [[ -f "${PID_DIR}/resource_manager.pid" ]]; then
        PID=$(cat "${PID_DIR}/resource_manager.pid")
        if kill -0 "$PID" 2>/dev/null; then
            echo -e "  ${GREEN}●${NC}  Resource Monitor $(t running)"
        else
            echo -e "  ${RED}●${NC}  Resource Monitor $(t stopped_s)"
        fi
    else
        echo -e "  ${DIM}●  Resource Monitor $(t stopped_s)${NC}"
    fi

    # AI Container
    if command -v docker &>/dev/null; then
        if docker ps --format '{{.Names}}' 2>/dev/null | grep -q "axon-ai-runtime"; then
            echo -e "  ${GREEN}●${NC}  AI Container     $(t running) (:8080)"
        else
            echo -e "  ${RED}●${NC}  AI Container     $(t stopped_s)"
        fi
    else
        echo -e "  ${DIM}●  AI Container     no docker${NC}"
    fi

    # AI health check
    if curl -sf "http://localhost:8080/health" > /dev/null 2>&1; then
        MODE=$(curl -sf "http://localhost:8080/health" 2>/dev/null | \
               python3 -c "import sys,json; print(json.load(sys.stdin).get('mode','?'))" 2>/dev/null)
        echo -e "  ${GREEN}●${NC}  AI API           $(t running) (mode: ${MODE})"
    else
        echo -e "  ${DIM}●  AI API           offline${NC}"
    fi

    echo ""
    echo -e "  ${DIM}Logs: ${LOG_DIR}/${NC}"
    echo ""
}

# ── Full start ────────────────────────────────────────────────────
cmd_start() {
    local SAFE_MODE=0
    for arg in "$@"; do
        [[ "$arg" == "--safe" || "$arg" == "--safe-mode" ]] && SAFE_MODE=1
    done

    print_header

    if [[ $SAFE_MODE -eq 1 ]]; then
        echo -e "  ${YELLOW}$(t safe_mode)${NC}\n"
        log "Starting in safe mode"
        bash "${AXON_ROOT}/scripts/startup/safe_mode.sh" --lang "${LANG_CODE}"
        return
    fi

    log "Starting full system"
    info "$(t starting)"
    echo ""

    # 1. Dependencies
    check_deps || {
        echo ""
        fail "Dependency check failed — run with --safe for minimal mode"
        exit 1
    }
    echo ""

    # 2. GPU
    run_gpu_setup
    echo ""

    # 3. Core Services
    start_core
    echo ""

    # 4. Desktop
    start_desktop
    echo ""

    # 5. AI Container
    start_ai
    echo ""

    # 6. First boot wizard (if needed)
    if python3 - << 'PYEOF' 2>/dev/null
import json, os
try:
    data = json.load(open(os.path.expanduser("~/.axonos/config.json")))
    sys.exit(0 if data.get("first_boot_done") else 1)
except: import sys; sys.exit(1)
PYEOF
    then
        : # not first boot
    else
        info "First boot detected — launching setup wizard"
        WIZARD="${AXON_ROOT}/platform/gui/first_boot/setup_wizard.py"
        if [[ -f "$WIZARD" ]]; then
            python3 "$WIZARD" >> "${LOG_DIR}/startup.log" 2>&1 &
        fi
    fi

    echo -e "${CYAN}══════════════════════════════════════════════${NC}"
    echo -e "  ${GREEN}${BOLD}$(t done)${NC}"
    echo -e "  ${DIM}axon-ai \"your prompt\"  — use AI from terminal${NC}"
    echo -e "  ${DIM}bash axon.sh status   — check services${NC}"
    echo -e "${CYAN}══════════════════════════════════════════════${NC}"
    echo ""
    log "System started successfully"
}

# ── Main ──────────────────────────────────────────────────────────
COMMAND="${1:-start}"

case "$COMMAND" in
    start)        cmd_start  "$@" ;;
    stop)         cmd_stop ;;
    status)       cmd_status ;;
    restart)      cmd_stop; sleep 1; cmd_start ;;
    --help|-h)
        echo -e "${CYAN}Axon OS — System Launcher${NC}"
        echo ""
        echo "  axon.sh start          — start full system"
        echo "  axon.sh start --safe   — safe mode (no AI)"
        echo "  axon.sh stop           — stop all services"
        echo "  axon.sh status         — show service status"
        echo "  axon.sh restart        — restart all"
        echo "  axon.sh --lang ar      — Arabic output"
        echo ""
        ;;
    *)
        # Allow: bash axon.sh --lang ar start
        cmd_start "$@"
        ;;
esac
