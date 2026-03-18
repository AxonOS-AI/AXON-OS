#!/bin/bash
# =============================================================================
# Axon OS — 05-verify-phase2.sh
# =============================================================================
# Copyright (c) 2025 Abdullah — Axon OS Project
# Licensed under the Apache License, Version 2.0
# https://www.apache.org/licenses/LICENSE-2.0
# =============================================================================
# الوظيفة: التحقق من اكتمال جميع خطوات المرحلة الثانية
# قابل للاستئناف: نعم
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
log_section() {
  echo -e "\n${BOLD}${CYAN}══════════════════════════════════════════${RESET}"
  echo -e "${BOLD}${CYAN}  $*${RESET}"
  echo -e "${BOLD}${CYAN}══════════════════════════════════════════${RESET}"
}

# ─────────────────────────────────────────────
# المسارات
# ─────────────────────────────────────────────
readonly AXON_HOME="${HOME}/AxonOS"
readonly AXON_STATE="${HOME}/.axon/state"
readonly STEP_DONE="${AXON_STATE}/p2-05-verify.done"
readonly SERVICE_DIR="${AXON_HOME}/platform/core-services"
readonly LOG_DIR="${HOME}/.axon/logs"
readonly VERIFY_LOG="${LOG_DIR}/verify-phase2.log"

# ─────────────────────────────────────────────
# العدادات
# ─────────────────────────────────────────────
PASSED=0
FAILED=0
WARNINGS=0
ERRORS_LIST=()

# ─────────────────────────────────────────────
# دالة التنظيف — تحفظ السجل دائماً
# ─────────────────────────────────────────────
cleanup() {
  local exit_code=$?
  save_verification_log
  if [[ $exit_code -ne 0 ]]; then
    log_error "فشل التحقق - رمز الخروج: $exit_code"
  fi
}
trap cleanup EXIT

# ─────────────────────────────────────────────
# تهيئة السجل
# ─────────────────────────────────────────────
init() {
  mkdir -p "${LOG_DIR}"
  {
    echo "========================================"
    echo "Axon OS Phase 2 Verification"
    echo "Started: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "========================================"
  } >> "${VERIFY_LOG}"
}

# ─────────────────────────────────────────────
# دوال التحقق المتخصصة
# ─────────────────────────────────────────────

log_verify() {
  echo "[${1}] ${2}" >> "${VERIFY_LOG}"
}

check_file_exists() {
  local description="$1"
  local filepath="$2"
  if [[ -f "${filepath}" ]]; then
    log_success "✓ ${description}"
    log_verify "PASS" "${description}: ${filepath}"
    ((PASSED++))
    return 0
  else
    log_error "✗ ${description} — الملف غير موجود: ${filepath}"
    log_verify "FAIL" "${description}: NOT FOUND"
    ERRORS_LIST+=("${description}: الملف غير موجود")
    ((FAILED++))
    return 1
  fi
}

check_dir_exists() {
  local description="$1"
  local dirpath="$2"
  if [[ -d "${dirpath}" ]]; then
    log_success "✓ ${description}"
    log_verify "PASS" "${description}: ${dirpath}"
    ((PASSED++))
    return 0
  else
    log_error "✗ ${description} — المجلد غير موجود: ${dirpath}"
    log_verify "FAIL" "${description}: NOT FOUND"
    ERRORS_LIST+=("${description}: المجلد غير موجود")
    ((FAILED++))
    return 1
  fi
}

check_file_executable() {
  local description="$1"
  local filepath="$2"
  if [[ -x "${filepath}" ]]; then
    log_success "✓ ${description}"
    log_verify "PASS" "${description}: executable"
    ((PASSED++))
    return 0
  else
    log_warn "⚠ ${description} — الملف غير قابل للتنفيذ"
    log_verify "WARN" "${description}: not executable"
    ((WARNINGS++))
    return 1
  fi
}

check_python_module() {
  local description="$1"
  local module="$2"
  if python3 -c "import ${module}" 2>/dev/null; then
    log_success "✓ ${description}"
    log_verify "PASS" "${description}: ${module}"
    ((PASSED++))
    return 0
  else
    log_error "✗ ${description} — الوحدة غير مثبتة: ${module}"
    log_verify "FAIL" "${description}: NOT INSTALLED"
    ERRORS_LIST+=("${description}: ${module} غير مثبت")
    ((FAILED++))
    return 1
  fi
}

check_json_output() {
  local description="$1"
  local script_path="$2"

  if [[ ! -f "${script_path}" ]]; then
    log_error "✗ ${description} — السكربت غير موجود"
    log_verify "FAIL" "${description}: script not found"
    ERRORS_LIST+=("${description}: السكربت غير موجود")
    ((FAILED++))
    return 1
  fi

  local output exit_code=0
  output=$(python3 "${script_path}" 2>&1) || exit_code=$?

  if [[ ${exit_code} -ne 0 ]]; then
    log_error "✗ ${description} — فشل التنفيذ (exit: ${exit_code})"
    log_verify "FAIL" "${description}: exit code ${exit_code}"
    local err_preview
    err_preview=$(echo "${output}" | head -3 | tr '\n' ' ')
    ERRORS_LIST+=("${description}: ${err_preview}")
    ((FAILED++))
    return 1
  fi

  if echo "${output}" | python3 -m json.tool &>/dev/null; then
    log_success "✓ ${description}"
    log_verify "PASS" "${description}: valid JSON"
    ((PASSED++))
    return 0
  else
    log_error "✗ ${description} — الإخراج ليس JSON صالح"
    log_verify "FAIL" "${description}: invalid JSON"
    ERRORS_LIST+=("${description}: الإخراج ليس JSON صالح")
    ((FAILED++))
    return 1
  fi
}

check_done_file_content() {
  local description="$1"
  local done_file="$2"

  if [[ ! -f "${done_file}" ]]; then
    log_error "✗ ${description} — ملف الحالة غير موجود"
    log_verify "FAIL" "${description}: done file missing"
    ((FAILED++))
    return 1
  fi

  if grep -q "completed=" "${done_file}"; then
    local completed_date
    # [إصلاح] إزالة علامات الاقتباس من القيمة المقروءة
    completed_date=$(grep "completed=" "${done_file}" \
      | cut -d'=' -f2 | tr -d '"')
    log_success "✓ ${description} (تم: ${completed_date})"
    log_verify "PASS" "${description}: completed ${completed_date}"
    ((PASSED++))
    return 0
  else
    log_warn "⚠ ${description} — موجود لكن بدون تاريخ اكتمال"
    log_verify "WARN" "${description}: missing completion date"
    ((WARNINGS++))
    return 1
  fi
}

check_command() {
  local description="$1"
  local cmd="$2"
  if command -v "${cmd}" &>/dev/null; then
    log_success "✓ ${description}: $(${cmd} --version 2>&1 | head -1)"
    log_verify "PASS" "${description}"
    ((PASSED++))
    return 0
  else
    log_warn "⚠ ${description} — غير مثبت: ${cmd}"
    log_verify "WARN" "${description}: not found"
    ((WARNINGS++))
    return 1
  fi
}

# ─────────────────────────────────────────────
# حفظ سجل التحقق
# ─────────────────────────────────────────────
save_verification_log() {
  {
    echo ""
    echo "----------------------------------------"
    echo "Summary:"
    echo "  Total : $((PASSED + FAILED))"
    echo "  Passed: ${PASSED}"
    echo "  Failed: ${FAILED}"
    echo "  Warns : ${WARNINGS}"
    echo "  Status: $([[ ${FAILED} -eq 0 ]] && echo 'SUCCESS' || echo 'FAILED')"
    if [[ ${#ERRORS_LIST[@]} -gt 0 ]]; then
      echo "Errors:"
      for err in "${ERRORS_LIST[@]}"; do
        echo "  - ${err}"
      done
    fi
    echo "========================================"
    echo "Completed: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
  } >> "${VERIFY_LOG}"
}

# ─────────────────────────────────────────────
# فحص الاستئناف
# ─────────────────────────────────────────────
if [[ -f "${STEP_DONE}" ]]; then
  log_warn "التحقق مكتمل مسبقاً → تخطي"
  exit 0
fi

log_section "التحقق من اكتمال المرحلة الثانية"
init

# ─────────────────────────────────────────────
# 1. المتطلبات الأساسية
# ─────────────────────────────────────────────
log_section "المتطلبات الأساسية"

check_command "python3" "python3"

PYTHON_VERSION="$(python3 --version 2>&1 | cut -d' ' -f2)"
PYTHON_MAJOR="$(echo "${PYTHON_VERSION}" | cut -d. -f1)"
PYTHON_MINOR="$(echo "${PYTHON_VERSION}" | cut -d. -f2)"

if [[ ${PYTHON_MAJOR} -ge 3 ]] && [[ ${PYTHON_MINOR} -ge 8 ]]; then
  log_success "✓ Python ${PYTHON_VERSION} (>= 3.8)"
  log_verify "PASS" "Python version: ${PYTHON_VERSION}"
  ((PASSED++))
else
  log_error "✗ Python ${PYTHON_VERSION} — مطلوب 3.8+"
  log_verify "FAIL" "Python too old: ${PYTHON_VERSION}"
  ((FAILED++))
fi

check_dir_exists "مجلد AxonOS"       "${AXON_HOME}"
check_dir_exists "مجلد state"        "${AXON_STATE}"
check_dir_exists "مجلد core-services" "${SERVICE_DIR}"

# ─────────────────────────────────────────────
# 2. ملفات الحالة
# ─────────────────────────────────────────────
log_section "فحص اكتمال الخطوات"

check_done_file_content "Resource Manager" "${AXON_STATE}/p2-01-resource-manager.done"
check_done_file_content "Project Manager"  "${AXON_STATE}/p2-02-project-manager.done"
check_done_file_content "File Manager"     "${AXON_STATE}/p2-03-file-manager.done"
check_done_file_content "Update Service"   "${AXON_STATE}/p2-04-update-service.done"

# ─────────────────────────────────────────────
# 3. ملفات Core Services
# ─────────────────────────────────────────────
log_section "فحص ملفات Core Services"

check_dir_exists  "مجلد resource-manager" "${SERVICE_DIR}/resource-manager"
check_file_exists "resource_manager.py"   "${SERVICE_DIR}/resource-manager/resource_manager.py"

check_dir_exists  "مجلد project-manager"  "${SERVICE_DIR}/project-manager"
check_file_exists "project_manager.py"    "${SERVICE_DIR}/project-manager/project_manager.py"

check_dir_exists  "مجلد file-manager"     "${SERVICE_DIR}/file-manager"
check_file_exists "file_manager.py"       "${SERVICE_DIR}/file-manager/file_manager.py"

check_dir_exists  "مجلد update-service"   "${SERVICE_DIR}/update-service"
check_file_exists "update_service.py"     "${SERVICE_DIR}/update-service/update_service.py"

# ─────────────────────────────────────────────
# 4. المكتبات
# ─────────────────────────────────────────────
log_section "فحص المكتبات"

check_python_module "psutil (مطلوب)"    "psutil"
check_python_module "torch (اختياري)"   "torch"   || true

# ─────────────────────────────────────────────
# 5. الفحص الوظيفي
# ─────────────────────────────────────────────
log_section "الفحص الوظيفي"

check_json_output "Resource Manager يُنتج JSON صالح" \
  "${SERVICE_DIR}/resource-manager/resource_manager.py"

check_json_output "Project Manager يُنتج JSON صالح" \
  "${SERVICE_DIR}/project-manager/project_manager.py"

check_json_output "File Manager يُنتج JSON صالح" \
  "${SERVICE_DIR}/file-manager/file_manager.py"

check_json_output "Update Service يُنتج JSON صالح" \
  "${SERVICE_DIR}/update-service/update_service.py"

# ─────────────────────────────────────────────
# 6. الاختصارات
# ─────────────────────────────────────────────
log_section "فحص الاختصارات"

BIN_DIR="${AXON_HOME}/bin"
if [[ -d "${BIN_DIR}" ]]; then
  for shortcut in axon-resource axon-project axon-file axon-update; do
    check_file_exists "${shortcut}" "${BIN_DIR}/${shortcut}"
    [[ -f "${BIN_DIR}/${shortcut}" ]] && \
      check_file_executable "${shortcut} قابل للتنفيذ" \
        "${BIN_DIR}/${shortcut}"
  done
else
  log_warn "مجلد bin غير موجود: ${BIN_DIR}"
  ((WARNINGS++))
fi

# ─────────────────────────────────────────────
# 7. السلامة
# ─────────────────────────────────────────────
log_section "فحص السلامة"

DISK_USAGE="$(df -h "${HOME}" | awk 'NR==2 {print $5}' | tr -d '%')"
if [[ ${DISK_USAGE} -lt 90 ]]; then
  log_success "✓ مساحة القرص كافية (${DISK_USAGE}% مستخدم)"
  log_verify "PASS" "Disk: ${DISK_USAGE}%"
  ((PASSED++))
else
  log_warn "⚠ مساحة القرص منخفضة (${DISK_USAGE}% مستخدم)"
  log_verify "WARN" "Low disk: ${DISK_USAGE}%"
  ((WARNINGS++))
fi

MEM_AVAILABLE="$(free -m | awk 'NR==2 {print $7}')"
if [[ ${MEM_AVAILABLE} -gt 500 ]]; then
  log_success "✓ الذاكرة كافية (${MEM_AVAILABLE} MB متاح)"
  log_verify "PASS" "Memory: ${MEM_AVAILABLE}MB"
  ((PASSED++))
else
  log_warn "⚠ الذاكرة منخفضة (${MEM_AVAILABLE} MB)"
  log_verify "WARN" "Low memory: ${MEM_AVAILABLE}MB"
  ((WARNINGS++))
fi

# ─────────────────────────────────────────────
# الملخص النهائي
# ─────────────────────────────────────────────
log_section "ملخص المرحلة الثانية"

TOTAL=$((PASSED + FAILED))
echo ""
echo -e "  ${BOLD}الفحوصات:${RESET}"
echo -e "    المجموع  : ${TOTAL}"
echo -e "    ${GREEN}نجح${RESET}     : ${PASSED}"
echo -e "    ${RED}فشل${RESET}     : ${FAILED}"
echo -e "    ${YELLOW}تحذيرات${RESET} : ${WARNINGS}"
echo ""

if [[ ${FAILED} -eq 0 ]]; then
  # [إصلاح] جميع القيم محاطة بعلامات اقتباس
  cat > "${STEP_DONE}" << EOF
completed="$(date '+%Y-%m-%dT%H:%M:%S')"
version="1.0"
total_checks="${TOTAL}"
passed="${PASSED}"
warnings="${WARNINGS}"
python_version="${PYTHON_VERSION}"
verification_log="${VERIFY_LOG}"
EOF

  echo -e "${BOLD}${GREEN}"
  echo "  ╔══════════════════════════════════════════╗"
  echo "  ║   ✓ المرحلة الثانية مكتملة بنجاح!       ║"
  echo "  ║   Axon OS Core Services جاهز            ║"
  echo "  ╚══════════════════════════════════════════╝"
  echo -e "${RESET}"
  log_info "سجل التحقق: ${VERIFY_LOG}"
  log_info "انتظر الإذن للبدء بالمرحلة الثالثة"

else
  echo -e "${BOLD}${RED}"
  echo "  ╔══════════════════════════════════════════╗"
  echo "  ║   ✗ فشل التحقق — ${FAILED} خطأ             ║"
  echo "  ╚══════════════════════════════════════════╝"
  echo -e "${RESET}"

  if [[ ${#ERRORS_LIST[@]} -gt 0 ]]; then
    echo -e "${BOLD}${YELLOW}الأخطاء:${RESET}"
    for err in "${ERRORS_LIST[@]}"; do
      echo -e "  ${RED}•${RESET} ${err}"
    done
    echo ""
  fi

  log_error "أصلح الأخطاء ثم أعد: bash run-phase2.sh"
  log_info  "سجل التحقق: ${VERIFY_LOG}"
  exit 1
fi
