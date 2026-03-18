#!/bin/bash
# =============================================================================
# Axon OS — 06-verify-installation.sh
# =============================================================================
# Copyright (c) 2025 Abdullah — Axon OS Project
# Licensed under the Apache License, Version 2.0
# https://www.apache.org/licenses/LICENSE-2.0
# =============================================================================
# الوظيفة: التحقق من اكتمال جميع خطوات المرحلة الأولى
# قابل للاستئناف: نعم
# =============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

log_info()    { echo -e "${CYAN}[INFO]${RESET}  $*"; }
log_success() { echo -e "${GREEN}[OK]${RESET}    $*"; }
log_warn()    { echo -e "${YELLOW}[WARN]${RESET}  $*"; }
log_error()   { echo -e "${RED}[ERROR]${RESET} $*" >&2; }
log_section() {
  echo -e "\n${BOLD}${CYAN}══════════════════════════════════════════${RESET}"
  echo -e "${BOLD}${CYAN}  $*${RESET}"
  echo -e "${BOLD}${CYAN}══════════════════════════════════════════${RESET}"
}

# ─────────────────────────────────────────────
# المسارات
# ─────────────────────────────────────────────
AXON_HOME="${HOME}/AxonOS"
AXON_STATE="${HOME}/.axon/state"
STEP_DONE="${AXON_STATE}/06-verify.done"

# ─────────────────────────────────────────────
# فحص الاستئناف
# ─────────────────────────────────────────────
if [[ -f "${STEP_DONE}" ]]; then
  log_warn "التحقق مكتمل مسبقاً → تخطي"
  log_info "لإعادة التنفيذ: rm ${STEP_DONE}"
  exit 0
fi

log_section "Step 6 · التحقق من اكتمال المرحلة الأولى"

PASSED=0
FAILED=0

# ─────────────────────────────────────────────
# دالة التحقق
# ─────────────────────────────────────────────
check() {
  local description="$1"
  local condition="$2"

  if eval "${condition}" &>/dev/null; then
    log_success "✓ ${description}"
    ((PASSED++)) || true
  else
    log_error "✗ ${description}"
    ((FAILED++)) || true
  fi
}

# ─────────────────────────────────────────────
# فحص ملفات الحالة
# ─────────────────────────────────────────────
log_info "فحص اكتمال الخطوات..."
check "الخطوة 1 — هيكل المجلدات"   "[[ -f '${AXON_STATE}/01-create-structure.done' ]]"
check "الخطوة 2 — فحص النظام"      "[[ -f '${AXON_STATE}/02-check-system.done' ]]"
check "الخطوة 3 — فحص الشبكة"      "[[ -f '${AXON_STATE}/03-check-network.done' ]]"
check "الخطوة 4 — Docker"           "[[ -f '${AXON_STATE}/04-install-docker.done' ]]"
check "الخطوة 5 — AI Container"     "[[ -f '${AXON_STATE}/05-init-ai-container.done' ]]"

# ─────────────────────────────────────────────
# فحص المجلدات الأساسية
# ─────────────────────────────────────────────
log_info "فحص هيكل المجلدات..."
check "مجلد boot/"              "[[ -d '${AXON_HOME}/boot' ]]"
check "مجلد platform/"         "[[ -d '${AXON_HOME}/platform' ]]"
check "مجلد ai-container/"     "[[ -d '${AXON_HOME}/ai-container' ]]"
check "مجلد scripts/"          "[[ -d '${AXON_HOME}/scripts' ]]"
check "مجلد docs/"             "[[ -d '${AXON_HOME}/docs' ]]"

# ─────────────────────────────────────────────
# فحص ملفات AI Container
# ─────────────────────────────────────────────
log_info "فحص ملفات AI Container..."
check "Dockerfile"              "[[ -f '${AXON_HOME}/ai-container/Dockerfile' ]]"
check "docker-compose.yml"      "[[ -f '${AXON_HOME}/ai-container/docker-compose.yml' ]]"
check "requirements.txt"        "[[ -f '${AXON_HOME}/ai-container/requirements.txt' ]]"
check "assistant/main.py"       "[[ -f '${AXON_HOME}/ai-container/assistant/main.py' ]]"

# ─────────────────────────────────────────────
# فحص ملفات المشروع
# ─────────────────────────────────────────────
log_info "فحص ملفات المشروع..."
check "LICENSE"                 "[[ -f '${AXON_HOME}/LICENSE' ]]"
check "NOTICE"                  "[[ -f '${AXON_HOME}/NOTICE' ]]"
check ".gitignore"              "[[ -f '${AXON_HOME}/.gitignore' ]]"
check ".env.example"            "[[ -f '${AXON_HOME}/.env.example' ]]"
check "CONTRIBUTING.md"         "[[ -f '${AXON_HOME}/CONTRIBUTING.md' ]]"

# ─────────────────────────────────────────────
# فحص البرامج المثبتة
# ─────────────────────────────────────────────
log_info "فحص البرامج المثبتة..."
check "Python3"                 "command -v python3"
check "pip3"                    "command -v pip3"
check "Docker"                  "command -v docker"
check "Git"                     "command -v git"

# ─────────────────────────────────────────────
# طباعة الملخص
# ─────────────────────────────────────────────
log_section "ملخص المرحلة الأولى"

TOTAL=$((PASSED + FAILED))
echo -e "  المجموع  : ${TOTAL} فحص"
echo -e "  ${GREEN}نجح${RESET}     : ${PASSED}"
echo -e "  ${RED}فشل${RESET}     : ${FAILED}"
echo ""

if [[ "${FAILED}" -eq 0 ]]; then
  echo "completed=$(date '+%Y-%m-%dT%H:%M:%S')" > "${STEP_DONE}"
  echo -e "${BOLD}${GREEN}"
  echo "  ╔══════════════════════════════════════╗"
  echo "  ║   ✓ المرحلة الأولى مكتملة بنجاح!   ║"
  echo "  ║   Axon OS Foundation جاهز           ║"
  echo "  ╚══════════════════════════════════════╝"
  echo -e "${RESET}"
  log_info "الخطوة التالية: انتظر إذن البدء بالمرحلة الثانية"
else
  echo -e "${BOLD}${RED}"
  echo "  ╔══════════════════════════════════════╗"
  echo "  ║   ✗ ${FAILED} خطوة تحتاج إعادة تنفيذ   ║"
  echo "  ╚══════════════════════════════════════╝"
  echo -e "${RESET}"
  log_info "شغّل السكربتات الفاشلة ثم أعد تشغيل هذا الملف"
  exit 1
fi
