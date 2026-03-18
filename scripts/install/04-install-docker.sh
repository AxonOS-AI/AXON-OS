#!/bin/bash
# =============================================================================
# Axon OS — 04-install-docker.sh
# =============================================================================
# Copyright (c) 2025 Abdullah — Axon OS Project
# Licensed under the Apache License, Version 2.0
# https://www.apache.org/licenses/LICENSE-2.0
# =============================================================================
# الوظيفة: تثبيت وإعداد Docker لتشغيل AI Container
# قابل للاستئناف: نعم — يتخطى التثبيت إذا كان موجوداً
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
STEP_DONE="${AXON_STATE}/04-install-docker.done"
SUDO="sudo"

# ─────────────────────────────────────────────
# فحص الاستئناف
# ─────────────────────────────────────────────
if [[ -f "${STEP_DONE}" ]]; then
  log_warn "Docker مثبت مسبقاً → تخطي"
  log_info "لإعادة التنفيذ: rm ${STEP_DONE}"
  exit 0
fi

log_section "Step 4 · تثبيت Docker"

mkdir -p "${AXON_STATE}"

# ─────────────────────────────────────────────
# فحص هل Docker مثبت مسبقاً
# ─────────────────────────────────────────────
if command -v docker &>/dev/null; then
  DOCKER_VER=$(docker --version 2>&1 | cut -d',' -f1)
  log_success "Docker موجود مسبقاً: ${DOCKER_VER}"

  # التحقق من أن Docker يعمل
  if docker info &>/dev/null; then
    log_success "Docker يعمل بشكل صحيح"
  else
    log_warn "Docker مثبت لكن لا يعمل — محاولة التشغيل..."
    ${SUDO} systemctl start docker || log_warn "تعذر تشغيل Docker"
  fi

  echo "completed=$(date '+%Y-%m-%dT%H:%M:%S')" > "${STEP_DONE}"
  log_success "✓ الخطوة 4 مكتملة"
  exit 0
fi

# ─────────────────────────────────────────────
# تثبيت Docker
# ─────────────────────────────────────────────
log_info "تثبيت Docker..."

# إزالة النسخ القديمة إن وجدت
log_info "إزالة النسخ القديمة..."
${SUDO} apt-get remove -y \
  docker docker-engine docker.io containerd runc 2>/dev/null || true

# تثبيت المتطلبات
log_info "تثبيت المتطلبات..."
${SUDO} apt-get update -y
${SUDO} apt-get install -y \
  ca-certificates curl gnupg lsb-release

# إضافة Docker GPG Key
log_info "إضافة Docker GPG Key..."
${SUDO} install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  | ${SUDO} gpg --dearmor -o /etc/apt/keyrings/docker.gpg
${SUDO} chmod a+r /etc/apt/keyrings/docker.gpg

# إضافة Docker Repository
log_info "إضافة Docker Repository..."
echo \
  "deb [arch=$(dpkg --print-architecture) \
  signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" \
  | ${SUDO} tee /etc/apt/sources.list.d/docker.list > /dev/null

# تثبيت Docker
log_info "تثبيت Docker Engine..."
${SUDO} apt-get update -y
${SUDO} apt-get install -y \
  docker-ce \
  docker-ce-cli \
  containerd.io \
  docker-buildx-plugin \
  docker-compose-plugin

# ─────────────────────────────────────────────
# إعداد Docker
# ─────────────────────────────────────────────
log_info "تشغيل Docker Service..."
${SUDO} systemctl enable docker
${SUDO} systemctl start docker

# إضافة المستخدم لمجموعة docker
CURRENT_USER="${SUDO_USER:-${USER}}"
log_info "إضافة ${CURRENT_USER} لمجموعة docker..."
${SUDO} usermod -aG docker "${CURRENT_USER}"
log_warn "سيتم تفعيل الصلاحيات بعد إعادة تسجيل الدخول"

# ─────────────────────────────────────────────
# التحقق من التثبيت
# ─────────────────────────────────────────────
log_info "التحقق من Docker..."
if docker --version &>/dev/null; then
  log_success "Docker: $(docker --version)"
else
  log_error "فشل تثبيت Docker"
  exit 1
fi

echo "completed=$(date '+%Y-%m-%dT%H:%M:%S')" > "${STEP_DONE}"
log_success "✓ الخطوة 4 مكتملة — Docker جاهز"
