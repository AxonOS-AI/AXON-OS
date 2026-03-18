#!/bin/bash
# =============================================================================
# Axon OS — run-phase2.sh
# =============================================================================
# Copyright (c) 2025 Abdullah — Axon OS Project
# Licensed under the Apache License, Version 2.0
# https://www.apache.org/licenses/LICENSE-2.0
# =============================================================================
# الوظيفة: تشغيل جميع خطوات المرحلة الثانية بالترتيب
# قابل للاستئناف: نعم — يتخطى الخطوات المكتملة تلقائياً
# الاستخدام: bash run-phase2.sh
# =============================================================================

set -euo pipefail

# ─────────────────────────────────────────────
# الألوان
# ─────────────────────────────────────────────
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly CYAN='\033[0;36m'
readonly BOLD='\033[1m'
readonly RESET='\033[0m'

# ─────────────────────────────────────────────
# دوال التسجيل
# ─────────────────────────────────────────────
log_info()    { echo -e "${CYAN}[INFO]${RESET}  $*"; }
log_success() { echo -e "${GREEN}[OK]${RESET}    $*"; }
log_warn()    { echo -e "${YELLOW}[WARN]${RESET}  $*"; }
log_error()   { echo -e "${RED}[ERROR]${RESET} $*" >&2; }

# ─────────────────────────────────────────────
# المتغيرات العامة
# ─────────────────────────────────────────────
readonly AXON_STATE="${HOME}/.axon/state"
readonly AXON_ROOT="${HOME}/AxonOS"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ─────────────────────────────────────────────
# دالة التنظيف عند الخروج
# ─────────────────────────────────────────────
cleanup() {
  local exit_code=$?
  if [[ $exit_code -ne 0 ]]; then
    echo ""
    log_error "تم الخروج برمز: $exit_code"
  fi
}
trap cleanup EXIT

# ─────────────────────────────────────────────
# التحقق من المتطلبات
# [إصلاح] كل رسائل log ترسل لـ stderr مباشرة
# لتجنب دمجها مع القيم المُعادة من الدوال
# ─────────────────────────────────────────────
check_prerequisites() {
  if [[ ! -d "${AXON_STATE}" ]]; then
    log_error "مجلد state غير موجود: ${AXON_STATE}"
    log_info  "تأكد من تشغيل المرحلة الأولى بشكل صحيح"
    exit 1
  fi

  if [[ ! -f "${AXON_STATE}/06-verify.done" ]]; then
    log_error "المرحلة الأولى غير مكتملة!"
    log_info  "شغّل أولاً: bash ${AXON_ROOT}/scripts/run-phase1.sh"
    exit 1
  fi
}

# ─────────────────────────────────────────────
# الحصول على مسار core-services
# [إصلاح] دالة منفصلة تعيد المسار فقط — بدون log
# حتى لا تختلط رسائل log مع القيمة المُعادة
# ─────────────────────────────────────────────
get_core_services_dir() {
  if [[ -d "${SCRIPT_DIR}/core-services" ]]; then
    echo "${SCRIPT_DIR}/core-services"
    return 0
  fi

  if [[ -d "${AXON_ROOT}/scripts/core-services" ]]; then
    echo "${AXON_ROOT}/scripts/core-services"
    return 0
  fi

  # الخطأ يذهب لـ stderr فقط
  echo -e "${RED}[ERROR]${RESET} مجلد core-services غير موجود!" >&2
  echo -e "${CYAN}[INFO]${RESET}  المسارات المتوقعة:" >&2
  echo -e "${CYAN}[INFO]${RESET}    - ${SCRIPT_DIR}/core-services" >&2
  echo -e "${CYAN}[INFO]${RESET}    - ${AXON_ROOT}/scripts/core-services" >&2
  exit 1
}

# ─────────────────────────────────────────────
# Banner
# ─────────────────────────────────────────────
show_banner() {
  echo -e "${BOLD}${CYAN}"
  echo "  ╔══════════════════════════════════════════╗"
  echo "  ║          Axon OS — Phase 2               ║"
  echo "  ║           Core Services                  ║"
  echo "  ║  Copyright (c) 2025 Abdullah             ║"
  echo "  ╚══════════════════════════════════════════╝"
  echo -e "${RESET}"
}

# ─────────────────────────────────────────────
# تشغيل خطوة واحدة
# ─────────────────────────────────────────────
run_step() {
  local step_num="$1"
  local step_file="$2"
  local step_desc="$3"
  local total_steps="$4"

  echo ""
  echo -e "${BOLD}[${step_num}/${total_steps}] ${step_desc}${RESET}"
  echo "──────────────────────────────────────────"

  if [[ ! -f "${step_file}" ]]; then
    log_error "ملف غير موجود: ${step_file}"
    return 1
  fi

  if [[ ! -x "${step_file}" ]]; then
    chmod +x "${step_file}"
  fi

  if bash "${step_file}"; then
    log_success "✓ الخطوة ${step_num} مكتملة"
    return 0
  else
    log_error "✗ فشلت الخطوة ${step_num}: ${step_desc}"
    log_warn  "أصلح المشكلة ثم أعد: bash run-phase2.sh"
    log_info  "الخطوات المكتملة لن تُعاد"
    return 1
  fi
}

# ─────────────────────────────────────────────
# الدالة الرئيسية
# ─────────────────────────────────────────────
main() {
  show_banner
  check_prerequisites

  local core_services_dir
  core_services_dir="$(get_core_services_dir)"

  local -a STEPS=(
    "01-resource-manager.sh"
    "02-project-manager.sh"
    "03-file-manager.sh"
    "04-update-service.sh"
    "05-verify-phase2.sh"
  )

  local -a DESCRIPTIONS=(
    "Resource Manager — إدارة CPU/GPU/RAM"
    "Project Manager — إدارة المشاريع"
    "File Manager — إدارة الملفات"
    "Update Service — إدارة التحديثات"
    "التحقق من اكتمال المرحلة الثانية"
  )

  local total="${#STEPS[@]}"

  for i in "${!STEPS[@]}"; do
    local step_num=$((i + 1))
    local step_file="${core_services_dir}/${STEPS[$i]}"
    local step_desc="${DESCRIPTIONS[$i]}"

    if ! run_step "${step_num}" "${step_file}" "${step_desc}" "${total}"; then
      exit 1
    fi
  done

  echo ""
  echo -e "${BOLD}${GREEN}"
  echo "  ╔══════════════════════════════════════════╗"
  echo "  ║   ✓ المرحلة الثانية مكتملة بنجاح!       ║"
  echo "  ║   Axon OS Core Services جاهز            ║"
  echo "  ╚══════════════════════════════════════════╝"
  echo -e "${RESET}"
  log_info "انتظر الإذن للبدء بالمرحلة الثالثة"
}

main "$@"
