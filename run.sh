#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
# File:       axon-os/run.sh
# Purpose:    Master runner — تشغيل Axon OS مرحلة بمرحلة
# Copyright:  (c) 2024 Abdullah — Axon OS Project (AGPL-3.0)
# ─────────────────────────────────────────────────────────────────

set -uo pipefail

GREEN='\033[0;32m'; RED='\033[0;31m'; CYAN='\033[0;36m'
YELLOW='\033[1;33m'; BOLD='\033[1m'; DIM='\033[2m'; NC='\033[0m'

ROOT="$(cd "$(dirname "$0")" && pwd)"

# ══════════════════════════════════════════════════════════════════
# SECTION 1 — فحص الملفات
# ══════════════════════════════════════════════════════════════════

check_all_files() {
    echo ""
    echo -e "${CYAN}${BOLD}╔══════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}${BOLD}║   Axon OS — فحص الملفات الكاملة             ║${NC}"
    echo -e "${CYAN}${BOLD}╚══════════════════════════════════════════════╝${NC}"
    echo ""

    local PASS=0 FAIL=0

    chk() {
        local file="$1" label="$2"
        if [[ -f "${ROOT}/${file}" ]]; then
            echo -e "  ${GREEN}✓${NC}  ${label}"
            PASS=$((PASS+1))
        else
            echo -e "  ${RED}✗${NC}  ${label}"
            echo -e "      ${DIM}→ مفقود: ${file}${NC}"
            FAIL=$((FAIL+1))
        fi
    }

    echo -e "${CYAN}▸ الجذر${NC}"
    chk "LICENSE"   "LICENSE"
    chk "NOTICE"    "NOTICE"
    chk "README.md" "README.md"
    chk "axon.sh"   "axon.sh"

    echo -e "\n${CYAN}▸ Boot Layer${NC}"
    chk "boot/init-scripts/01-load-logo.sh"     "01-load-logo.sh"
    chk "boot/init-scripts/02-load-progress.sh" "02-load-progress.sh"
    chk "boot/init-scripts/03-init-network.sh"  "03-init-network.sh"

    echo -e "\n${CYAN}▸ Phase 1 — Splash Simulator${NC}"
    chk "phase1_boot/splash_simulator/main.py"           "main.py"
    chk "phase1_boot/splash_simulator/config.py"         "config.py"
    chk "phase1_boot/splash_simulator/animation.py"      "animation.py"
    chk "phase1_boot/splash_simulator/logo_generator.py" "logo_generator.py"

    echo -e "\n${CYAN}▸ Phase 1 — Plymouth${NC}"
    chk "phase1_boot/plymouth/axon.plymouth"   "axon.plymouth"
    chk "phase1_boot/plymouth/axon.script"     "axon.script"
    chk "phase1_boot/scripts/install_theme.sh" "install_theme.sh"
    chk "phase1_boot/scripts/check_deps.sh"    "check_deps.sh"

    echo -e "\n${CYAN}▸ Core Services${NC}"
    chk "platform/config.py"                                        "config.py"
    chk "platform/core-services/db_manager.py"                      "db_manager.py"
    chk "platform/core-services/core_services_init.py"              "core_services_init.py"
    chk "platform/core-services/resource-manager/resource_manager.py" "resource_manager.py"
    chk "platform/core-services/project-manager/project_manager.py" "project_manager.py"
    chk "platform/core-services/file-manager/file_manager.py"       "file_manager.py"
    chk "platform/core-services/update-service/update_service.py"   "update_service.py"
    chk "platform/core-services/01-resource-manager.sh"             "01-resource-manager.sh"
    chk "platform/core-services/02-project-manager.sh"              "02-project-manager.sh"
    chk "platform/core-services/03-file-manager.sh"                 "03-file-manager.sh"
    chk "platform/core-services/04-update-service.sh"               "04-update-service.sh"

    echo -e "\n${CYAN}▸ GPU System${NC}"
    chk "platform/core-services/resource-manager/gpu_detector.py" "gpu_detector.py"
    chk "platform/core-services/resource-manager/gpu_setup.py"    "gpu_setup.py"

    echo -e "\n${CYAN}▸ Desktop Environment${NC}"
    chk "platform/gui/desktop-environment/main.py"           "main.py"
    chk "platform/gui/desktop-environment/taskbar.py"        "taskbar.py"
    chk "platform/gui/desktop-environment/window_manager.py" "window_manager.py"
    chk "platform/gui/desktop-environment/launcher.py"       "launcher.py"

    echo -e "\n${CYAN}▸ Theme System${NC}"
    chk "platform/gui/themes/colors.py"      "colors.py"
    chk "platform/gui/themes/logo.py"        "logo.py"
    chk "platform/gui/themes/axon-dark.css"  "axon-dark.css"
    chk "platform/gui/themes/axon-light.css" "axon-light.css"
    chk "platform/gui/assets/axon_logo.svg"  "axon_logo.svg"

    echo -e "\n${CYAN}▸ Wallpapers${NC}"
    chk "platform/gui/wallpaper/wallpaper_engine.py" "wallpaper_engine.py"
    chk "platform/gui/wallpaper/neural_dark.py"      "neural_dark.py"
    chk "platform/gui/wallpaper/deep_space.py"       "deep_space.py"
    chk "platform/gui/wallpaper/cyber_grid.py"       "cyber_grid.py"
    chk "platform/gui/wallpaper/aurora_wave.py"      "aurora_wave.py"
    chk "platform/gui/wallpaper/neural_light.py"     "neural_light.py"
    chk "platform/gui/wallpaper/dawn_light.py"       "dawn_light.py"

    echo -e "\n${CYAN}▸ First Boot + Assistant + Notifications${NC}"
    chk "platform/gui/first_boot/welcome.py"              "welcome.py"
    chk "platform/gui/first_boot/setup_wizard.py"         "setup_wizard.py"
    chk "platform/gui/assistant/assistant_window.py"      "assistant_window.py"
    chk "platform/gui/notifications/notifications.py"     "notifications.py"

    echo -e "\n${CYAN}▸ Dashboard${NC}"
    chk "platform/gui/dashboard/dashboard_main.py" "dashboard_main.py"
    chk "platform/gui/dashboard/dashboard_data.py" "dashboard_data.py"
    chk "platform/gui/dashboard/widgets.py"        "widgets.py"

    echo -e "\n${CYAN}▸ AI Container${NC}"
    chk "ai-container/Dockerfile"                    "Dockerfile"
    chk "ai-container/assistant/model_loader.py"     "model_loader.py"
    chk "ai-container/assistant/inference.py"        "inference.py"
    chk "ai-container/assistant/server.py"           "server.py"
    chk "ai-container/assistant/01-load-model.sh"    "01-load-model.sh"
    chk "ai-container/assistant/02-init-runtime.sh"  "02-init-runtime.sh"
    chk "ai-container/agents/01-init-agents.sh"      "01-init-agents.sh"
    chk "ai-container/agents/orchestrator.py"        "orchestrator.py"
    chk "ai-container/agents/system_agent.py"        "system_agent.py"

    echo -e "\n${CYAN}▸ Scripts${NC}"
    chk "scripts/install/01-install-platform.sh"  "01-install-platform.sh"
    chk "scripts/update/01-update-platform.sh"    "01-update-platform.sh"
    chk "scripts/update/02-verify-update.sh"      "02-verify-update.sh"
    chk "scripts/update/03-rollback.sh"           "03-rollback.sh"
    chk "scripts/update/update_manager.py"        "update_manager.py"
    chk "scripts/utilities/01-cleanup.sh"         "01-cleanup.sh"
    chk "scripts/startup/safe_mode.sh"            "safe_mode.sh"
    chk "scripts/axon-ai.sh"                      "axon-ai.sh"
    chk "scripts/verify_phase1.sh"                "verify_phase1.sh"
    chk "scripts/verify_phase2.sh"                "verify_phase2.sh"
    chk "scripts/verify_phases_5_6_7.sh"          "verify_phases_5_6_7.sh"
    chk "scripts/test_integration.sh"             "test_integration.sh"

    echo ""
    echo -e "${CYAN}══════════════════════════════════════════════${NC}"
    echo -e "  ${GREEN}موجود: ${PASS}${NC}  |  ${RED}مفقود: ${FAIL}${NC}"
    echo -e "${CYAN}══════════════════════════════════════════════${NC}"
    echo ""

    if [[ $FAIL -gt 0 ]]; then
        echo -e "  ${RED}❌ يوجد ${FAIL} ملف ناقص${NC}"
        echo ""
        return 1
    else
        echo -e "  ${GREEN}✅ جميع الملفات موجودة — جاهز للتنفيذ${NC}"
        echo ""
        return 0
    fi
}

# ══════════════════════════════════════════════════════════════════
# SECTION 2 — أدوات مساعدة
# ══════════════════════════════════════════════════════════════════

ask() {
    local answer
    while true; do
        echo -ne "${YELLOW}$1 [y/n]: ${NC}"
        read -r answer
        case "$answer" in
            [Yy]) return 0 ;;
            [Nn]) return 1 ;;
            *) echo -e "  ${DIM}اكتب y أو n${NC}" ;;
        esac
    done
}

run_script() {
    local script="${ROOT}/$1" label="$2"
    if [[ -f "$script" ]]; then
        chmod +x "$script"
        echo -e "  ${DIM}→ تشغيل: $1${NC}"
        bash "$script" && \
            echo -e "  ${GREEN}✓${NC}  ${label}" || \
            echo -e "  ${YELLOW}⚠${NC}  ${label} (تحذير)"
    else
        echo -e "  ${YELLOW}⚠${NC}  ${label} — غير موجود: $1"
    fi
}

py_run() {
    local script="${ROOT}/$1" label="$2"
    if [[ -f "$script" ]]; then
        echo -e "  ${DIM}→ تشغيل: $1${NC}"
        python3 "$script" && \
            echo -e "  ${GREEN}✓${NC}  ${label}" || \
            echo -e "  ${YELLOW}⚠${NC}  ${label} (تحذير)"
    else
        echo -e "  ${YELLOW}⚠${NC}  ${label} — غير موجود: $1"
    fi
}

phase_header() {
    echo ""
    echo -e "${CYAN}${BOLD}┌─────────────────────────────────────────────┐${NC}"
    echo -e "${CYAN}${BOLD}│  المرحلة $1: $2${NC}"
    echo -e "${CYAN}${BOLD}└─────────────────────────────────────────────┘${NC}"
    echo ""
}

phase_done() {
    echo ""
    echo -e "  ${GREEN}✅ المرحلة $1 اكتملت${NC}"
    echo ""
}

# ══════════════════════════════════════════════════════════════════
# SECTION 3 — المراحل
# ══════════════════════════════════════════════════════════════════

phase1() {
    phase_header "1" "Boot Scaffold"
    run_script "boot/init-scripts/01-load-logo.sh"     "تسجيل شعار الإقلاع"
    run_script "boot/init-scripts/02-load-progress.sh" "تثبيت ثيم Plymouth"
    run_script "boot/init-scripts/03-init-network.sh"  "فحص الشبكة"
    run_script "scripts/verify_phase1.sh"              "التحقق من المرحلة 1"
    phase_done "1"
}

phase2() {
    phase_header "2" "Desktop + Core Services"
    echo -e "${CYAN}▸ Core Services${NC}"
    run_script "platform/core-services/01-resource-manager.sh" "Resource Manager"
    run_script "platform/core-services/02-project-manager.sh"  "Project Manager"
    run_script "platform/core-services/03-file-manager.sh"     "File Manager"
    run_script "platform/core-services/04-update-service.sh"   "Update Service"
    echo -e "\n${CYAN}▸ GUI + Widgets${NC}"
    run_script "platform/gui/02-widgets.sh" "Widgets"
    run_script "platform/gui/03-plugins.sh" "Plugins"
    echo -e "\n${CYAN}▸ Addons${NC}"
    run_script "platform/addons/01-setup-addons.sh"      "Setup Addons"
    run_script "platform/addons/02-enable-extensions.sh" "Enable Extensions"
    run_script "scripts/verify_phase2.sh" "التحقق من المرحلة 2"
    phase_done "2"
}

phase3() {
    phase_header "3" "Tools"
    run_script "platform/gui/01-desktop-env.sh"        "Desktop Environment"
    run_script "platform/tools/01-project-builder.sh"  "Project Builder"
    run_script "platform/tools/02-training-console.sh" "Training Console"
    phase_done "3"
}

phase4() {
    phase_header "4" "AI Container Scaffold"
    run_script "ai-container/agents/01-init-agents.sh" "Agents Framework"
    echo -e "  ${DIM}↷  Docker: bash ai-container/assistant/02-init-runtime.sh${NC}"
    phase_done "4"
}

phase5() {
    phase_header "5" "Theme System"
    echo -e "${CYAN}▸ فحص الألوان والثيمات${NC}"
    py_run "platform/gui/themes/colors.py" "Color System"
    echo -e "${CYAN}▸ GPU Detection${NC}"
    py_run "platform/core-services/resource-manager/gpu_detector.py" "GPU Detector"
    echo -e "${CYAN}▸ GPU Setup${NC}"
    python3 "${ROOT}/platform/core-services/resource-manager/gpu_setup.py" --check 2>/dev/null && \
        echo -e "  ${GREEN}✓${NC}  GPU Setup OK" || \
        echo -e "  ${YELLOW}⚠${NC}  GPU Setup (تحذير)"
    phase_done "5"
}

phase6() {
    phase_header "6" "Wallpaper System"
    py_run "platform/gui/wallpaper/wallpaper_engine.py" "Wallpaper Engine (6 خلفيات)"
    phase_done "6"
}

phase7() {
    phase_header "7" "First Boot + Assistant + Notifications"
    echo -e "${CYAN}▸ First Boot${NC}"
    py_run "platform/gui/first_boot/welcome.py"      "Welcome Screen"
    py_run "platform/gui/first_boot/setup_wizard.py" "Setup Wizard"
    echo -e "\n${CYAN}▸ AI Assistant${NC}"
    py_run "platform/gui/assistant/assistant_window.py" "Assistant Window"
    echo -e "\n${CYAN}▸ Notifications${NC}"
    py_run "platform/gui/notifications/notifications.py" "Notification System"
    phase_done "7"
}

phase8() {
    phase_header "8" "AI + Terminal"
    echo -e "${CYAN}▸ Model Loader${NC}"
    py_run "ai-container/assistant/model_loader.py" "Model Loader + CodeGen Small"
    echo -e "\n${CYAN}▸ axon-ai CLI${NC}"
    run_script "scripts/axon-ai.sh" "axon-ai --help" <<< "--help" 2>/dev/null || \
        bash "${ROOT}/scripts/axon-ai.sh" --help 2>/dev/null && \
        echo -e "  ${GREEN}✓${NC}  axon-ai CLI جاهز" || \
        echo -e "  ${YELLOW}⚠${NC}  axon-ai CLI"
    phase_done "8"
}

phase9() {
    phase_header "9" "System Launcher"
    echo -e "${CYAN}▸ axon.sh${NC}"
    bash "${ROOT}/axon.sh" status 2>/dev/null && \
        echo -e "  ${GREEN}✓${NC}  axon.sh يعمل" || \
        echo -e "  ${YELLOW}⚠${NC}  axon.sh (تحذير)"
    echo -e "\n${CYAN}▸ Safe Mode${NC}"
    bash -n "${ROOT}/scripts/startup/safe_mode.sh" 2>/dev/null && \
        echo -e "  ${GREEN}✓${NC}  safe_mode.sh syntax OK" || \
        echo -e "  ${RED}✗${NC}  safe_mode.sh syntax error"
    phase_done "9"
}

phase_integration() {
    phase_header "T" "Integration Tests (الاختبار الشامل)"
    bash "${ROOT}/scripts/test_integration.sh"
}

# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════

echo ""
echo -e "${CYAN}${BOLD}╔══════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}${BOLD}║        Axon OS — Master Runner               ║${NC}"
echo -e "${CYAN}${BOLD}║     تشغيل النظام مرحلة بمرحلة               ║${NC}"
echo -e "${CYAN}${BOLD}╚══════════════════════════════════════════════╝${NC}"
echo ""
echo "  الخيارات المتاحة:"
echo -e "  ${BOLD}1${NC} — فحص الملفات فقط"
echo -e "  ${BOLD}2${NC} — تشغيل جميع المراحل"
echo -e "  ${BOLD}3${NC} — تشغيل مرحلة محددة"
echo ""
echo -ne "${YELLOW}اختر [1/2/3]: ${NC}"
read -r CHOICE

case "$CHOICE" in
    1) check_all_files ;;

    2)
        check_all_files || {
            ask "يوجد ملفات ناقصة — هل تريد المتابعة؟" || exit 0
        }
        ask "▸ المرحلة 1 — Boot Scaffold؟"             && phase1
        ask "▸ المرحلة 2 — Desktop + Core Services؟"   && phase2
        ask "▸ المرحلة 3 — Tools؟"                     && phase3
        ask "▸ المرحلة 4 — AI Container Scaffold؟"     && phase4
        ask "▸ المرحلة 5 — Theme System؟"              && phase5
        ask "▸ المرحلة 6 — Wallpapers؟"                && phase6
        ask "▸ المرحلة 7 — First Boot + Assistant؟"    && phase7
        ask "▸ المرحلة 8 — AI + Terminal؟"             && phase8
        ask "▸ المرحلة 9 — System Launcher؟"           && phase9
        ask "▸ الاختبار الشامل؟"                       && phase_integration
        echo ""
        echo -e "${GREEN}${BOLD}✅ جميع المراحل اكتملت!${NC}"
        echo ""
        ;;

    3)
        echo ""
        echo "  اختر المرحلة:"
        echo -e "  ${BOLD}1${NC} — Boot Scaffold"
        echo -e "  ${BOLD}2${NC} — Desktop + Core Services"
        echo -e "  ${BOLD}3${NC} — Tools"
        echo -e "  ${BOLD}4${NC} — AI Container Scaffold"
        echo -e "  ${BOLD}5${NC} — Theme System"
        echo -e "  ${BOLD}6${NC} — Wallpapers"
        echo -e "  ${BOLD}7${NC} — First Boot + Assistant + Notifications"
        echo -e "  ${BOLD}8${NC} — AI + Terminal"
        echo -e "  ${BOLD}9${NC} — System Launcher"
        echo -e "  ${BOLD}T${NC} — Integration Tests"
        echo ""
        echo -ne "${YELLOW}رقم المرحلة [1-9/T]: ${NC}"
        read -r PHASE_NUM

        case "$PHASE_NUM" in
            1) phase1 ;;
            2) phase2 ;;
            3) phase3 ;;
            4) phase4 ;;
            5) phase5 ;;
            6) phase6 ;;
            7) phase7 ;;
            8) phase8 ;;
            9) phase9 ;;
            T|t) phase_integration ;;
            *) echo -e "${RED}خيار غير صحيح${NC}" ;;
        esac
        ;;

    *) echo -e "${RED}خيار غير صحيح${NC}"; exit 1 ;;
esac
