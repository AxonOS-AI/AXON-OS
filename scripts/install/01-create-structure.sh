#!/bin/bash
# =============================================================================
# Axon OS — 01-create-structure.sh
# =============================================================================
# Copyright (c) 2025 Abdullah — Axon OS Project
# Licensed under the Apache License, Version 2.0
# https://www.apache.org/licenses/LICENSE-2.0
# =============================================================================
# الوظيفة: إنشاء هيكل مجلدات Axon OS الكامل
# قابل للاستئناف: نعم — يتخطى المجلدات الموجودة مسبقاً
# =============================================================================

set -euo pipefail

# ─────────────────────────────────────────────
# ANSI Colors
# ─────────────────────────────────────────────
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
# المسارات الأساسية
# ─────────────────────────────────────────────
AXON_HOME="${HOME}/AxonOS"
AXON_STATE="${HOME}/.axon/state"
STEP_DONE="${AXON_STATE}/01-create-structure.done"

# ─────────────────────────────────────────────
# فحص الاستئناف
# ─────────────────────────────────────────────
if [[ -f "${STEP_DONE}" ]]; then
  log_warn "هيكل المجلدات موجود مسبقاً → تخطي"
  log_info "لإعادة التنفيذ: rm ${STEP_DONE}"
  exit 0
fi

log_section "Step 1 · إنشاء هيكل المجلدات"

# ─────────────────────────────────────────────
# قائمة المجلدات
# ─────────────────────────────────────────────
DIRS=(
  "${AXON_HOME}/boot/splash"
  "${AXON_HOME}/boot/init-scripts"
  "${AXON_HOME}/boot/config"
  "${AXON_HOME}/platform/gui"
  "${AXON_HOME}/platform/core-services"
  "${AXON_HOME}/platform/tools"
  "${AXON_HOME}/platform/addons"
  "${AXON_HOME}/ai-container/assistant"
  "${AXON_HOME}/ai-container/models"
  "${AXON_HOME}/ai-container/libraries"
  "${AXON_HOME}/ai-container/agents"
  "${AXON_HOME}/scripts/install"
  "${AXON_HOME}/scripts/update"
  "${AXON_HOME}/scripts/utilities"
  "${AXON_HOME}/docs"
  "${AXON_STATE}"
)

# ─────────────────────────────────────────────
# إنشاء المجلدات
# ─────────────────────────────────────────────
CREATED=0
SKIPPED=0

for dir in "${DIRS[@]}"; do
  if [[ -d "${dir}" ]]; then
    log_warn "موجود مسبقاً: ${dir}"
    ((SKIPPED++)) || true
  else
    mkdir -p "${dir}"
    log_success "تم إنشاء: ${dir}"
    ((CREATED++)) || true
  fi
done

# ─────────────────────────────────────────────
# ملفات .gitkeep للمجلدات الفارغة
# ─────────────────────────────────────────────
log_info "إنشاء ملفات .gitkeep..."
find "${AXON_HOME}" -type d -empty -exec touch {}/.gitkeep \;

# ─────────────────────────────────────────────
# حفظ حالة الاكتمال
# ─────────────────────────────────────────────
mkdir -p "${AXON_STATE}"
echo "completed=$(date '+%Y-%m-%dT%H:%M:%S')" > "${STEP_DONE}"

log_section "النتيجة"
log_success "تم إنشاء:  ${CREATED} مجلد"
log_warn    "تم تخطي:   ${SKIPPED} مجلد"
log_success "✓ الخطوة 1 مكتملة"
