#!/bin/bash
# =============================================================================
# Axon OS — 01-resource-manager.sh
# =============================================================================
# Copyright (c) 2025 Abdullah — Axon OS Project
# Licensed under the Apache License, Version 2.0
# https://www.apache.org/licenses/LICENSE-2.0
# =============================================================================
# الوظيفة: إعداد Resource Manager لمراقبة CPU/GPU/RAM
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
readonly STEP_DONE="${AXON_STATE}/p2-01-resource-manager.done"
readonly SERVICE_DIR="${AXON_HOME}/platform/core-services"
readonly RM_DIR="${SERVICE_DIR}/resource-manager"

# ─────────────────────────────────────────────
# دالة التنظيف
# [إصلاح] يحذف ملف .done إذا فشل التثبيت
# حتى لا يبقى ملف ناقص يخدع الاستئناف
# ─────────────────────────────────────────────
cleanup() {
  local exit_code=$?
  if [[ $exit_code -ne 0 ]]; then
    log_error "فشل في الإعداد - رمز الخروج: $exit_code"
    [[ -f "${STEP_DONE}" ]] && rm -f "${STEP_DONE}"
  fi
}
trap cleanup EXIT

# ─────────────────────────────────────────────
# التحقق من المتطلبات
# ─────────────────────────────────────────────
check_requirements() {
  log_info "التحقق من المتطلبات..."

  if ! command -v python3 &>/dev/null; then
    log_error "python3 غير مثبت!"
    log_info  "قم بتثبيته: sudo apt install python3"
    exit 1
  fi

  if ! command -v pip3 &>/dev/null; then
    log_error "pip3 غير مثبت!"
    log_info  "قم بتثبيته: sudo apt install python3-pip"
    exit 1
  fi

  if [[ ! -d "${AXON_STATE}" ]]; then
    log_error "مجلد state غير موجود: ${AXON_STATE}"
    log_info  "تأكد من تشغيل المرحلة الأولى"
    exit 1
  fi

  log_success "جميع المتطلبات متوفرة"
}

# ─────────────────────────────────────────────
# فحص الاستئناف
# ─────────────────────────────────────────────
if [[ -f "${STEP_DONE}" ]]; then
  log_warn "Resource Manager مُعدَّ مسبقاً → تخطي"
  exit 0
fi

log_section "Resource Manager · إعداد مراقبة الموارد"

check_requirements

# ─────────────────────────────────────────────
# إنشاء المجلدات
# ─────────────────────────────────────────────
log_info "إنشاء المجلدات..."
mkdir -p "${RM_DIR}" || {
  log_error "فشل إنشاء المجلد: ${RM_DIR}"
  exit 1
}
# [إصلاح] إنشاء مجلد bin هنا لتجنب الفشل لاحقاً
mkdir -p "${AXON_HOME}/bin"
log_success "المجلدات جاهزة"

# ─────────────────────────────────────────────
# تثبيت psutil
# ─────────────────────────────────────────────
log_info "تثبيت مكتبة psutil..."
if python3 -c "import psutil" &>/dev/null; then
  log_warn "psutil مثبتة مسبقاً → تخطي"
else
  # [إصلاح] pip_flags كمتغير عادي (ليس local خارج دالة)
  pip_flags="--timeout 300 --retries 20"

  if pip3 install --help 2>/dev/null | grep -q "break-system-packages"; then
    pip_flags="${pip_flags} --break-system-packages"
  fi

  if pip3 install ${pip_flags} psutil; then
    log_success "psutil تم تثبيتها"
  else
    log_error "فشل تثبيت psutil"
    exit 1
  fi
fi

# ─────────────────────────────────────────────
# إنشاء resource_manager.py
# ─────────────────────────────────────────────
log_info "إنشاء resource_manager.py..."
cat > "${RM_DIR}/resource_manager.py" << 'PYTHON'
#!/usr/bin/env python3
# =============================================================================
# Axon OS — Resource Manager
# Copyright (c) 2025 Abdullah — Axon OS Project
# Licensed under Apache License 2.0
# =============================================================================

import psutil
import json
import time
import logging
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, List

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("axon-resource-manager")


@dataclass
class ResourceSnapshot:
    """لقطة من موارد النظام في لحظة معينة."""
    timestamp:        str
    cpu_percent:      float
    cpu_count:        int
    ram_used_gb:      float
    ram_total_gb:     float
    ram_percent:      float
    disk_used_gb:     float
    disk_free_gb:     float
    disk_percent:     float
    gpu_available:    bool
    gpu_name:         str
    gpu_memory_used:  Optional[float] = None
    gpu_memory_total: Optional[float] = None


class ResourceManager:
    """
    مراقب موارد النظام لـ Axon OS.
    يقرأ CPU / RAM / Disk / GPU ويحفظ التقارير.
    """

    LOG_DIR     = Path.home() / ".axon" / "logs"
    REPORT_FILE = "resource-report.json"

    def __init__(self):
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)
        self._gpu_available = False
        self._gpu_name      = "none"
        self._torch         = None
        self._detect_gpu()
        logger.info("Resource Manager جاهز")

    # ── اكتشاف GPU ─────────────────────────────────────────────────

    def _detect_gpu(self) -> None:
        """اكتشاف GPU إن وجد."""
        try:
            import torch
            self._torch         = torch
            self._gpu_available = torch.cuda.is_available()
            if self._gpu_available:
                self._gpu_name = torch.cuda.get_device_name(0)
                logger.info(f"تم اكتشاف GPU: {self._gpu_name}")
            else:
                self._gpu_name = "none (CUDA unavailable)"
        except ImportError:
            self._gpu_available = False
            self._gpu_name      = "torch not installed"

    def _get_gpu_memory(self) -> tuple:
        """الحصول على معلومات ذاكرة GPU."""
        if not self._gpu_available or self._torch is None:
            return None, None
        try:
            used  = self._torch.cuda.memory_allocated(0) / (1024 ** 3)
            total = self._torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
            return round(used, 2), round(total, 2)
        except Exception as e:
            logger.warning(f"فشل قراءة ذاكرة GPU: {e}")
            return None, None

    # ── قراءة آمنة للموارد ─────────────────────────────────────────

    def _safe_cpu_percent(self) -> float:
        try:
            return psutil.cpu_percent(interval=0.5)
        except Exception as e:
            logger.error(f"فشل قراءة CPU: {e}")
            return 0.0

    def _safe_memory(self):
        try:
            return psutil.virtual_memory()
        except Exception as e:
            logger.error(f"فشل قراءة الذاكرة: {e}")
            from collections import namedtuple
            M = namedtuple('M', ['used', 'total', 'percent'])
            return M(0, 1, 0)

    def _safe_disk(self):
        try:
            return psutil.disk_usage(str(Path.home()))
        except Exception as e:
            logger.error(f"فشل قراءة القرص: {e}")
            from collections import namedtuple
            D = namedtuple('D', ['used', 'free', 'total', 'percent'])
            return D(0, 1, 1, 0)

    # ── واجهة عامة ─────────────────────────────────────────────────

    def snapshot(self) -> ResourceSnapshot:
        """قراءة موارد النظام الحالية."""
        cpu              = self._safe_cpu_percent()
        ram              = self._safe_memory()
        disk             = self._safe_disk()
        gpu_used, gpu_tot = self._get_gpu_memory()

        return ResourceSnapshot(
            timestamp        = time.strftime("%Y-%m-%dT%H:%M:%S"),
            cpu_percent      = cpu,
            cpu_count        = psutil.cpu_count() or 1,
            ram_used_gb      = round(ram.used  / (1024 ** 3), 2),
            ram_total_gb     = round(ram.total / (1024 ** 3), 2),
            ram_percent      = ram.percent,
            disk_used_gb     = round(disk.used / (1024 ** 3), 2),
            disk_free_gb     = round(disk.free / (1024 ** 3), 2),
            disk_percent     = disk.percent,
            gpu_available    = self._gpu_available,
            gpu_name         = self._gpu_name,
            gpu_memory_used  = gpu_used,
            gpu_memory_total = gpu_tot,
        )

    def report(self) -> dict:
        """إرجاع تقرير كامل مع تحذيرات ذكية."""
        snap     = self.snapshot()
        data     = asdict(snap)
        warnings: List[str] = []

        if snap.ram_percent > 95:
            warnings.append(f"🚨 RAM حرجة ({snap.ram_percent}%)")
        elif snap.ram_percent > 85:
            warnings.append(f"⚠️ RAM عالية ({snap.ram_percent}%)")

        if snap.cpu_percent > 98:
            warnings.append(f"🚨 CPU مشبعة ({snap.cpu_percent}%)")
        elif snap.cpu_percent > 90:
            warnings.append(f"⚠️ CPU عالي ({snap.cpu_percent}%)")

        if snap.disk_free_gb < 5:
            warnings.append(f"🚨 مساحة القرص حرجة ({snap.disk_free_gb} GB)")
        elif snap.disk_free_gb < 10:
            warnings.append(f"⚠️ مساحة القرص منخفضة ({snap.disk_free_gb} GB)")

        if (self._gpu_available
                and snap.gpu_memory_used is not None
                and snap.gpu_memory_total is not None
                and snap.gpu_memory_total > 0):
            gpu_pct = (snap.gpu_memory_used / snap.gpu_memory_total) * 100
            if gpu_pct > 90:
                warnings.append(f"⚠️ ذاكرة GPU ممتلئة ({gpu_pct:.1f}%)")

        data["warnings"] = warnings
        data["status"]   = (
            "critical" if len(warnings) >= 2
            else "warning" if warnings
            else "ok"
        )
        return data

    def save_report(self) -> Path:
        """حفظ تقرير الموارد في ملف JSON."""
        report   = self.report()
        log_file = self.LOG_DIR / self.REPORT_FILE
        log_file.write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
        return log_file

    def monitor(self, interval: int = 30, cycles: int = 0) -> None:
        """
        مراقبة مستمرة للموارد.
        interval: الفترة بالثواني بين كل قراءة
        cycles: عدد الدورات (0 = بلا نهاية)
        """
        logger.info(f"بدء المراقبة — كل {interval} ثانية")
        count = 0
        try:
            while cycles == 0 or count < cycles:
                # إعادة اكتشاف GPU كل 10 دورات
                if count % 10 == 0:
                    self._detect_gpu()

                report = self.report()
                icon   = "✅" if report["status"] == "ok" else "⚠️"
                logger.info(
                    f"{icon} CPU: {report['cpu_percent']:.1f}% | "
                    f"RAM: {report['ram_percent']:.1f}% | "
                    f"Disk: {report['disk_free_gb']:.1f} GB free"
                )
                for w in report["warnings"]:
                    logger.warning(w)

                self.save_report()
                count += 1

                if cycles == 0 or count < cycles:
                    time.sleep(interval)

        except KeyboardInterrupt:
            logger.info("⏹️ توقفت المراقبة")
        except Exception as e:
            logger.error(f"خطأ في المراقبة: {e}")

    def get_process_info(self, limit: int = 10) -> List[dict]:
        """أكثر العمليات استهلاكاً للموارد."""
        processes = []
        for proc in psutil.process_iter(
            ['pid', 'name', 'cpu_percent', 'memory_percent']
        ):
            try:
                processes.append({
                    'pid':    proc.info['pid'],
                    'name':   proc.info['name'],
                    'cpu':    proc.info['cpu_percent']    or 0,
                    'memory': proc.info['memory_percent'] or 0,
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        processes.sort(key=lambda x: x['cpu'], reverse=True)
        return processes[:limit]


def main():
    rm     = ResourceManager()
    report = rm.report()
    print(json.dumps(report, ensure_ascii=False, indent=2))

    print("\n📊 أكثر العمليات استهلاكاً:")
    print("-" * 50)
    for proc in rm.get_process_info(5):
        print(
            f"  {proc['name'][:30]:<30} "
            f"CPU: {proc['cpu']:>5.1f}%  "
            f"RAM: {proc['memory']:>5.1f}%"
        )


if __name__ == "__main__":
    main()
PYTHON

log_success "resource_manager.py تم إنشاؤه"

# ─────────────────────────────────────────────
# اختبار سريع
# ─────────────────────────────────────────────
log_info "اختبار Resource Manager..."
if python3 "${RM_DIR}/resource_manager.py" &>/dev/null; then
  log_success "Resource Manager يعمل بشكل صحيح"
else
  log_error "فشل اختبار Resource Manager"
  exit 1
fi

# ─────────────────────────────────────────────
# إنشاء اختصار
# ─────────────────────────────────────────────
log_info "إنشاء اختصار axon-resource..."
cat > "${AXON_HOME}/bin/axon-resource" << 'SHORTCUT'
#!/bin/bash
python3 "${HOME}/AxonOS/platform/core-services/resource-manager/resource_manager.py" "$@"
SHORTCUT
chmod +x "${AXON_HOME}/bin/axon-resource"
log_success "اختصار axon-resource جاهز"

# ─────────────────────────────────────────────
# حفظ حالة الاكتمال
# [إصلاح] جميع القيم محاطة بعلامات اقتباس
# ─────────────────────────────────────────────
cat > "${STEP_DONE}" << EOF
completed="$(date '+%Y-%m-%dT%H:%M:%S')"
version="1.0"
python="$(python3 --version 2>&1 | cut -d' ' -f2)"
psutil="$(python3 -c "import psutil; print(psutil.__version__)" 2>/dev/null || echo "unknown")"
EOF

log_success "✓ Resource Manager مكتمل"
