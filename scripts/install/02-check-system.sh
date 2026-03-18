#!/bin/bash
# =============================================================================
# Axon OS — 02-check-system.sh
# =============================================================================
# Copyright (c) 2025 Abdullah — Axon OS Project
# Licensed under the Apache License, Version 2.0
# https://www.apache.org/licenses/LICENSE-2.0
# =============================================================================
# الوظيفة: فحص متطلبات النظام الأساسية
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
AXON_STATE="${HOME}/.axon/state"
STEP_DONE="${AXON_STATE}/02-check-system.done"
REPORT_FILE="${AXON_STATE}/system-report.txt"

# ─────────────────────────────────────────────
# فحص الاستئناف
# ─────────────────────────────────────────────
if [[ -f "${STEP_DONE}" ]]; then
  log_warn "فحص النظام مكتمل مسبقاً → تخطي"
  log_info "لإعادة التنفيذ: rm ${STEP_DONE}"
  exit 0
fi

log_section "Step 2 · فحص متطلبات النظام"

ERRORS=0
mkdir -p "${AXON_STATE}"

# ─────────────────────────────────────────────
# فحص نظام التشغيل
# ─────────────────────────────────────────────
log_info "فحص نظام التشغيل..."
OS_NAME=$(lsb_release -is 2>/dev/null || echo "Unknown")
OS_VERSION=$(lsb_release -rs 2>/dev/null || echo "Unknown")
OS_CODENAME=$(lsb_release -cs 2>/dev/null || echo "Unknown")

log_info "النظام: ${OS_NAME} ${OS_VERSION} (${OS_CODENAME})"

if [[ "${OS_NAME}" != "Ubuntu" ]]; then
  log_warn "النظام ليس Ubuntu — قد تحدث مشاكل"
else
  log_success "Ubuntu ${OS_VERSION} مدعوم"
fi

# ─────────────────────────────────────────────
# فحص Python
# ─────────────────────────────────────────────
log_info "فحص Python..."
if command -v python3 &>/dev/null; then
  PYTHON_VER=$(python3 --version 2>&1)
  log_success "Python: ${PYTHON_VER}"
else
  log_error "Python3 غير مثبت"
  ((ERRORS++)) || true
fi

# ─────────────────────────────────────────────
# فحص pip
# ─────────────────────────────────────────────
log_info "فحص pip..."
if command -v pip3 &>/dev/null; then
  PIP_VER=$(pip3 --version 2>&1 | cut -d' ' -f1-2)
  log_success "pip: ${PIP_VER}"
else
  log_error "pip3 غير مثبت"
  ((ERRORS++)) || true
fi

# ─────────────────────────────────────────────
# فحص Docker
# ─────────────────────────────────────────────
log_info "فحص Docker..."
if command -v docker &>/dev/null; then
  DOCKER_VER=$(docker --version 2>&1 | cut -d',' -f1)
  log_success "Docker: ${DOCKER_VER}"
else
  log_warn "Docker غير مثبت — سيتم تثبيته في الخطوة 4"
fi

# ─────────────────────────────────────────────
# فحص Git
# ─────────────────────────────────────────────
log_info "فحص Git..."
if command -v git &>/dev/null; then
  GIT_VER=$(git --version 2>&1)
  log_success "${GIT_VER}"
else
  log_warn "Git غير مثبت"
fi

# ─────────────────────────────────────────────
# فحص GPU
# ─────────────────────────────────────────────
log_info "فحص GPU..."
if command -v nvidia-smi &>/dev/null; then
  GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1)
  log_success "GPU: ${GPU_NAME}"
  GPU_AVAILABLE="true"
else
  log_warn "لا يوجد NVIDIA GPU — سيعمل على CPU"
  GPU_AVAILABLE="false"
fi

# ─────────────────────────────────────────────
# فحص RAM
# ─────────────────────────────────────────────
log_info "فحص RAM..."
RAM_GB=$(free -g | awk '/^Mem:/{print $2}')
if [[ "${RAM_GB}" -ge 8 ]]; then
  log_success "RAM: ${RAM_GB} GB ✓"
elif [[ "${RAM_GB}" -ge 4 ]]; then
  log_warn "RAM: ${RAM_GB} GB — الحد الأدنى، قد يكون الأداء بطيئاً"
else
  log_error "RAM: ${RAM_GB} GB — أقل من الحد الأدنى (4 GB)"
  ((ERRORS++)) || true
fi

# ─────────────────────────────────────────────
# فحص مساحة القرص
# ─────────────────────────────────────────────
log_info "فحص مساحة القرص..."
DISK_FREE=$(df -BG "${HOME}" | awk 'NR==2{print $4}' | tr -d 'G')
if [[ "${DISK_FREE}" -ge 20 ]]; then
  log_success "مساحة فارغة: ${DISK_FREE} GB ✓"
elif [[ "${DISK_FREE}" -ge 10 ]]; then
  log_warn "مساحة فارغة: ${DISK_FREE} GB — قليلة"
else
  log_error "مساحة فارغة: ${DISK_FREE} GB — غير كافية (الحد الأدنى 10 GB)"
  ((ERRORS++)) || true
fi

# ─────────────────────────────────────────────
# حفظ تقرير النظام
# ─────────────────────────────────────────────
cat > "${REPORT_FILE}" << EOF
# Axon OS — System Report
generated=$(date '+%Y-%m-%dT%H:%M:%S')
os=${OS_NAME} ${OS_VERSION}
ram_gb=${RAM_GB}
disk_free_gb=${DISK_FREE}
gpu_available=${GPU_AVAILABLE}
errors=${ERRORS}
EOF

log_success "تم حفظ التقرير: ${REPORT_FILE}"

# ─────────────────────────────────────────────
# النتيجة النهائية
# ─────────────────────────────────────────────
log_section "النتيجة"

if [[ "${ERRORS}" -gt 0 ]]; then
  log_error "فشل الفحص — ${ERRORS} مشكلة يجب حلها أولاً"
  exit 1
fi

echo "completed=$(date '+%Y-%m-%dT%H:%M:%S')" > "${STEP_DONE}"
log_success "✓ الخطوة 2 مكتملة — النظام جاهز"
