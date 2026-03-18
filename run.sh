#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
# File:       axon-os/run.sh
# Purpose:    Master runner — تشغيل Axon OS مرحلة بمرحلة
#             مع التحقق من الملفات قبل البدء
# Copyright:  (c) 2024 Abdullah — Axon OS Project (AGPL-3.0)
# Usage:      bash run.sh
# ─────────────────────────────────────────────────────────────────

set -uo pipefail

# ── Colors ────────────────────────────────────────────────────────
GREEN='\033[0;32m'; RED='\033[0;31m'; CYAN='\033[0;36m'
YELLOW='\033[1;33m'; BOLD='\033[1m'; DIM='\033[2m'; NC='\033[0m'

ROOT="$(cd "$(dirname "$0")" && pwd)"

# ═══════════════════════════════════════════════════════════════════
# SECTION 1 — التحقق من وجود جميع الملفات
# ═══════════════════════════════════════════════════════════════════

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
            ((PASS++))
        else
            echo -e "  ${RED}✗${NC}  ${label}"
            echo -e "      ${DIM}→ مفقود: ${file}${NC}"
            ((FAIL++))
        fi
    }

    # ── الجذر ─────────────────────────────────────────────────────
    echo -e "${CYAN}▸ الجذر${NC}"
    chk "LICENSE"    "LICENSE"
    chk "NOTICE"     "NOTICE"
    chk "README.md"  "README.md"

    # ── Boot Layer ────────────────────────────────────────────────
    echo -e "\n${CYAN}▸ Boot Layer${NC}"
    chk "boot/init-scripts/01-load-logo.sh"    "01-load-logo.sh"
    chk "boot/init-scripts/02-load-progress.sh" "02-load-progress.sh"
    chk "boot/init-scripts/03-init-network.sh"  "03-init-network.sh"

    # ── Phase 1 — Splash Simulator ────────────────────────────────
    echo -e "\n${CYAN}▸ Phase 1 — Splash Simulator${NC}"
    chk "phase1_boot/splash_simulator/main.py"          "main.py"
    chk "phase1_boot/splash_simulator/config.py"        "config.py"
    chk "phase1_boot/splash_simulator/animation.py"     "animation.py"
    chk "phase1_boot/splash_simulator/logo_generator.py" "logo_generator.py"

    # ── Phase 1 — Plymouth ────────────────────────────────────────
    echo -e "\n${CYAN}▸ Phase 1 — Plymouth${NC}"
    chk "phase1_boot/plymouth/axon.plymouth"     "axon.plymouth"
    chk "phase1_boot/plymouth/axon.script"       "axon.script"
    chk "phase1_boot/scripts/install_theme.sh"   "install_theme.sh"
    chk "phase1_boot/scripts/check_deps.sh"      "check_deps.sh"

    # ── Platform Config ───────────────────────────────────────────
    echo -e "\n${CYAN}▸ Platform Config${NC}"
    chk "platform/config.py"  "platform/config.py"

    # ── Core Services — Python ────────────────────────────────────
    echo -e "\n${CYAN}▸ Core Services — Python${NC}"
    chk "platform/core-services/db_manager.py"                        "db_manager.py"
    chk "platform/core-services/core_services_init.py"                "core_services_init.py"
    chk "platform/core-services/resource-manager/resource_manager.py" "resource_manager.py"
    chk "platform/core-services/project-manager/project_manager.py"   "project_manager.py"
    chk "platform/core-services/file-manager/file_manager.py"         "file_manager.py"
    chk "platform/core-services/update-service/update_service.py"     "update_service.py"

    # ── Core Services — Shell ─────────────────────────────────────
    echo -e "\n${CYAN}▸ Core Services — Shell${NC}"
    chk "platform/core-services/01-resource-manager.sh" "01-resource-manager.sh"
    chk "platform/core-services/02-project-manager.sh"  "02-project-manager.sh"
    chk "platform/core-services/03-file-manager.sh"     "03-file-manager.sh"
    chk "platform/core-services/04-update-service.sh"   "04-update-service.sh"

    # ── Desktop Environment ───────────────────────────────────────
    echo -e "\n${CYAN}▸ Desktop Environment${NC}"
    chk "platform/gui/desktop-environment/main.py"           "main.py"
    chk "platform/gui/desktop-environment/taskbar.py"        "taskbar.py"
    chk "platform/gui/desktop-environment/window_manager.py" "window_manager.py"
    chk "platform/gui/desktop-environment/launcher.py"       "launcher.py"

    # ── GUI Scripts ───────────────────────────────────────────────
    echo -e "\n${CYAN}▸ GUI Scripts${NC}"
    chk "platform/gui/01-desktop-env.sh" "01-desktop-env.sh"
    chk "platform/gui/02-widgets.sh"     "02-widgets.sh"
    chk "platform/gui/03-plugins.sh"     "03-plugins.sh"

    # ── Tools + Addons ────────────────────────────────────────────
    echo -e "\n${CYAN}▸ Tools + Addons${NC}"
    chk "platform/tools/01-project-builder.sh"    "01-project-builder.sh"
    chk "platform/tools/02-training-console.sh"   "02-training-console.sh"
    chk "platform/addons/01-setup-addons.sh"      "01-setup-addons.sh"
    chk "platform/addons/02-enable-extensions.sh" "02-enable-extensions.sh"

    # ── AI Container ──────────────────────────────────────────────
    echo -e "\n${CYAN}▸ AI Container${NC}"
    chk "ai-container/Dockerfile"                  "Dockerfile"
    chk "ai-container/assistant/01-load-model.sh"  "01-load-model.sh"
    chk "ai-container/assistant/02-init-runtime.sh" "02-init-runtime.sh"
    chk "ai-container/assistant/server.py"         "server.py"
    chk "ai-container/agents/01-init-agents.sh"    "01-init-agents.sh"

    # ── Scripts المركزية ──────────────────────────────────────────
    echo -e "\n${CYAN}▸ Scripts المركزية${NC}"
    chk "scripts/install/01-install-platform.sh" "01-install-platform.sh"
    chk "scripts/update/01-update-platform.sh"   "01-update-platform.sh"
    chk "scripts/utilities/01-cleanup.sh"         "01-cleanup.sh"
    chk "scripts/verify_phase1.sh"               "verify_phase1.sh"
    chk "scripts/verify_phase2.sh"               "verify_phase2.sh"

    # ── النتيجة ───────────────────────────────────────────────────
    echo ""
    echo -e "${CYAN}══════════════════════════════════════════════${NC}"
    echo -e "  ${GREEN}موجود: ${PASS}${NC}  |  ${RED}مفقود: ${FAIL}${NC}"
    echo -e "${CYAN}══════════════════════════════════════════════${NC}"
    echo ""

    if [[ $FAIL -gt 0 ]]; then
        echo -e "  ${RED}❌ يوجد ${FAIL} ملف ناقص — أضفهم قبل المتابعة${NC}"
        echo ""
        return 1
    else
        echo -e "  ${GREEN}✅ جميع الملفات موجودة — جاهز للتنفيذ${NC}"
        echo ""
        return 0
    fi
}

# ═══════════════════════════════════════════════════════════════════
# SECTION 2 — أداة السؤال
# ═══════════════════════════════════════════════════════════════════

ask() {
    local question="$1"
    local answer
    while true; do
        echo -ne "${YELLOW}${question} [y/n]: ${NC}"
        read -r answer
        case "$answer" in
            [Yy]) return 0 ;;
            [Nn]) return 1 ;;
            *)    echo -e "  ${DIM}اكتب y للمتابعة أو n للتوقف${NC}" ;;
        esac
    done
}

run_script() {
    local script="${ROOT}/$1"
    local label="$2"
    if [[ -f "$script" ]]; then
        chmod +x "$script"
        echo -e "  ${DIM}→ تشغيل: $1${NC}"
        bash "$script" && \
            echo -e "  ${GREEN}✓${NC}  ${label}" || \
            echo -e "  ${YELLOW}⚠${NC}  ${label} (تحذير — غير مميت)"
    else
        echo -e "  ${YELLOW}⚠${NC}  ${label} — السكربت غير موجود: $1"
    fi
}

# ═══════════════════════════════════════════════════════════════════
# SECTION 3 — المراحل
# ═══════════════════════════════════════════════════════════════════

phase_header() {
    local num="$1" title="$2"
    echo ""
    echo -e "${CYAN}${BOLD}┌─────────────────────────────────────────────┐${NC}"
    echo -e "${CYAN}${BOLD}│  المرحلة ${num}: ${title}${NC}"
    echo -e "${CYAN}${BOLD}└─────────────────────────────────────────────┘${NC}"
    echo ""
}

phase_done() {
    echo ""
    echo -e "  ${GREEN}✅ المرحلة $1 اكتملت${NC}"
    echo ""
}

# ──────────────────────────────────────────────
phase1() {
    phase_header "1" "Boot Scaffold"
    run_script "boot/init-scripts/01-load-logo.sh"    "تسجيل شعار الإقلاع"
    run_script "boot/init-scripts/02-load-progress.sh" "تثبيت ثيم Plymouth"
    run_script "boot/init-scripts/03-init-network.sh"  "فحص الشبكة"
    run_script "scripts/verify_phase1.sh"              "التحقق من المرحلة 1"
    phase_done "1"
}

# ──────────────────────────────────────────────
phase2() {
    phase_header "2" "Desktop + Core Services"

    echo -e "${CYAN}▸ Core Services${NC}"
    run_script "platform/core-services/01-resource-manager.sh" "Resource Manager"
    run_script "platform/core-services/02-project-manager.sh"  "Project Manager"
    run_script "platform/core-services/03-file-manager.sh"     "File Manager"
    run_script "platform/core-services/04-update-service.sh"   "Update Service"

    echo ""
    echo -e "${CYAN}▸ GUI + Widgets${NC}"
    run_script "platform/gui/02-widgets.sh"   "Widgets"
    run_script "platform/gui/03-plugins.sh"   "Plugins"

    echo ""
    echo -e "${CYAN}▸ Addons${NC}"
    run_script "platform/addons/01-setup-addons.sh"      "Setup Addons"
    run_script "platform/addons/02-enable-extensions.sh" "Enable Extensions"

    run_script "scripts/verify_phase2.sh" "التحقق من المرحلة 2"
    phase_done "2"
}

# ──────────────────────────────────────────────
phase3() {
    phase_header "3" "Tools"
    run_script "platform/gui/01-desktop-env.sh"            "Desktop Environment"
    run_script "platform/tools/01-project-builder.sh"      "Project Builder (اختبار)"
    run_script "platform/tools/02-training-console.sh"     "Training Console"
    phase_done "3"
}

# ──────────────────────────────────────────────
phase4() {
    phase_header "4" "AI Container Scaffold"
    run_script "ai-container/agents/01-init-agents.sh" "Agents Framework"
    echo -e "  ${DIM}↷  Docker runtime مؤجل — يحتاج Docker مثبت${NC}"
    echo -e "  ${DIM}↷  لتشغيل Docker: bash ai-container/assistant/02-init-runtime.sh${NC}"
    phase_done "4"
}

# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

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

    # ── فحص الملفات فقط ──────────────────────────────────────────
    1)
        check_all_files
        ;;

    # ── تشغيل جميع المراحل ───────────────────────────────────────
    2)
        check_all_files || {
            ask "يوجد ملفات ناقصة — هل تريد المتابعة على أي حال؟" || exit 0
        }

        ask "▸ هل تبدأ المرحلة 1 — Boot Scaffold؟" && phase1 || echo -e "${DIM}تم تخطي المرحلة 1${NC}"
        ask "▸ هل تكمل للمرحلة 2 — Desktop + Core Services؟" && phase2 || echo -e "${DIM}تم التوقف${NC}"; exit 0
        ask "▸ هل تكمل للمرحلة 3 — Tools؟" && phase3 || echo -e "${DIM}تم التوقف${NC}"; exit 0
        ask "▸ هل تكمل للمرحلة 4 — AI Container؟" && phase4 || echo -e "${DIM}تم التوقف${NC}"; exit 0

        echo ""
        echo -e "${GREEN}${BOLD}✅ جميع المراحل اكتملت بنجاح!${NC}"
        echo ""
        ;;

    # ── تشغيل مرحلة محددة ────────────────────────────────────────
    3)
        echo ""
        echo "  اختر المرحلة:"
        echo -e "  ${BOLD}1${NC} — Boot Scaffold"
        echo -e "  ${BOLD}2${NC} — Desktop + Core Services"
        echo -e "  ${BOLD}3${NC} — Tools"
        echo -e "  ${BOLD}4${NC} — AI Container"
        echo ""
        echo -ne "${YELLOW}رقم المرحلة [1-4]: ${NC}"
        read -r PHASE_NUM

        case "$PHASE_NUM" in
            1) phase1 ;;
            2) phase2 ;;
            3) phase3 ;;
            4) phase4 ;;
            *) echo -e "${RED}خيار غير صحيح${NC}" ;;
        esac
        ;;

    *)
        echo -e "${RED}خيار غير صحيح${NC}"
        exit 1
        ;;
esac
