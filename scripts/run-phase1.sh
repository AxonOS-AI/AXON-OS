#!/bin/bash
# =============================================================================
# Axon OS — run-phase1.sh
# =============================================================================
# Copyright (c) 2025 Abdullah — Axon OS Project
# Licensed under the Apache License, Version 2.0
# https://www.apache.org/licenses/LICENSE-2.0
# =============================================================================
# الوظيفة: تشغيل جميع خطوات المرحلة الأولى بالترتيب
# قابل للاستئناف: نعم — يتخطى الخطوات المكتملة تلقائياً
# الاستخدام: bash run-phase1.sh
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

# ─────────────────────────────────────────────
# Banner
# ─────────────────────────────────────────────
echo -e "${BOLD}${CYAN}"
echo "  ╔══════════════════════════════════════════╗"
echo "  ║          Axon OS — Phase 1               ║"
echo "  ║      Foundation & Infrastructure         ║"
echo "  ║  Copyright (c) 2025 Abdullah             ║"
echo "  ╚══════════════════════════════════════════╝"
echo -e "${RESET}"

# ─────────────────────────────────────────────
# المسارات
# ─────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

STEPS=(
  "01-create-structure.sh"
  "02-check-system.sh"
  "03-check-network.sh"
  "04-install-docker.sh"
  "05-init-ai-container.sh"
  "06-verify-installation.sh"
)

DESCRIPTIONS=(
  "إنشاء هيكل المجلدات"
  "فحص متطلبات النظام"
  "فحص الشبكة"
  "تثبيت Docker"
  "تجهيز AI Container"
  "التحقق من اكتمال المرحلة"
)

# ─────────────────────────────────────────────
# تشغيل الخطوات
# ─────────────────────────────────────────────
TOTAL=${#STEPS[@]}

for i in "${!STEPS[@]}"; do
  STEP_NUM=$((i + 1))
  STEP_FILE="${SCRIPT_DIR}/install/${STEPS[$i]}"
  STEP_DESC="${DESCRIPTIONS[$i]}"

  echo ""
  echo -e "${BOLD}[${STEP_NUM}/${TOTAL}] ${STEP_DESC}${RESET}"
  echo "──────────────────────────────────────────"

  if [[ ! -f "${STEP_FILE}" ]]; then
    log_error "ملف غير موجود: ${STEP_FILE}"
    exit 1
  fi

  chmod +x "${STEP_FILE}"

  if bash "${STEP_FILE}"; then
    log_success "✓ الخطوة ${STEP_NUM} مكتملة"
  else
    log_error "✗ فشلت الخطوة ${STEP_NUM}: ${STEP_DESC}"
    log_warn "أصلح المشكلة ثم أعد تشغيل: bash run-phase1.sh"
    log_info "الخطوات المكتملة لن تُعاد"
    exit 1
  fi
done

# ─────────────────────────────────────────────
# النتيجة النهائية
# ─────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}"
echo "  ╔══════════════════════════════════════════╗"
echo "  ║   ✓ المرحلة الأولى مكتملة بنجاح!       ║"
echo "  ║   Axon OS Foundation جاهز               ║"
echo "  ╚══════════════════════════════════════════╝"
echo -e "${RESET}"
log_info "انتظر الإذن للبدء بالمرحلة الثانية"
