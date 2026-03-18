#!/bin/bash
# =============================================================================
# Axon OS — 03-check-network.sh
# =============================================================================
# Copyright (c) 2025 Abdullah — Axon OS Project
# Licensed under the Apache License, Version 2.0
# https://www.apache.org/licenses/LICENSE-2.0
# =============================================================================
# الوظيفة: فحص الاتصال بالإنترنت والخوادم المطلوبة
# قابل للاستئناف: نعم — يُعاد تشغيله تلقائياً حتى يتصل
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
AXON_STATE="${HOME}/.axon/state"
STEP_DONE="${AXON_STATE}/03-check-network.done"

MAX_RETRIES=5
RETRY_WAIT=10

# ─────────────────────────────────────────────
# فحص الاستئناف
# ─────────────────────────────────────────────
if [[ -f "${STEP_DONE}" ]]; then
  log_warn "فحص الشبكة مكتمل مسبقاً → تخطي"
  log_info "لإعادة التنفيذ: rm ${STEP_DONE}"
  exit 0
fi

log_section "Step 3 · فحص الشبكة"

mkdir -p "${AXON_STATE}"

# ─────────────────────────────────────────────
# الخوادم المطلوب فحصها
# ─────────────────────────────────────────────
HOSTS=(
  "google.com"
  "github.com"
  "pypi.org"
  "download.pytorch.org"
  "hub.docker.com"
)

# ─────────────────────────────────────────────
# دالة فحص الاتصال مع إعادة المحاولة
# ─────────────────────────────────────────────
check_host() {
  local host="$1"
  local attempt=1

  while [[ "${attempt}" -le "${MAX_RETRIES}" ]]; do
    if ping -c 1 -W 3 "${host}" &>/dev/null; then
      log_success "✓ ${host}"
      return 0
    else
      log_warn "محاولة ${attempt}/${MAX_RETRIES} فشلت: ${host}"
      if [[ "${attempt}" -lt "${MAX_RETRIES}" ]]; then
        log_info "انتظار ${RETRY_WAIT} ثانية..."
        sleep "${RETRY_WAIT}"
      fi
      ((attempt++)) || true
    fi
  done

  log_error "✗ لا يمكن الوصول إلى: ${host}"
  return 1
}

# ─────────────────────────────────────────────
# فحص الاتصال الأساسي
# ─────────────────────────────────────────────
log_info "فحص الاتصال بالإنترنت..."
FAILED=0

for host in "${HOSTS[@]}"; do
  check_host "${host}" || ((FAILED++)) || true
done

# ─────────────────────────────────────────────
# فحص سرعة الاتصال (تقديري)
# ─────────────────────────────────────────────
log_info "فحص جودة الاتصال..."
if command -v curl &>/dev/null; then
  SPEED=$(curl -s -w "%{speed_download}" -o /dev/null \
    --max-time 5 "https://www.google.com" 2>/dev/null || echo "0")
  SPEED_KB=$(echo "${SPEED}" | awk '{printf "%.0f", $1/1024}')
  if [[ "${SPEED_KB}" -gt 100 ]]; then
    log_success "سرعة الاتصال: ~${SPEED_KB} KB/s ✓"
  else
    log_warn "سرعة الاتصال بطيئة: ~${SPEED_KB} KB/s"
    log_warn "قد يستغرق التحميل وقتاً أطول"
  fi
fi

# ─────────────────────────────────────────────
# النتيجة
# ─────────────────────────────────────────────
log_section "النتيجة"

if [[ "${FAILED}" -gt 0 ]]; then
  log_error "${FAILED} خادم غير متاح"
  log_warn "يمكن المتابعة لكن قد يفشل التحميل"
  log_info "تأكد من الاتصال بالإنترنت ثم أعد التشغيل"
  exit 1
fi

echo "completed=$(date '+%Y-%m-%dT%H:%M:%S')" > "${STEP_DONE}"
log_success "✓ الخطوة 3 مكتملة — الشبكة تعمل"
