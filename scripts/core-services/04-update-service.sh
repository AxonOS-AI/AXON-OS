#!/bin/bash
# =============================================================================
# Axon OS — 04-update-service.sh
# =============================================================================
# Copyright (c) 2025 Abdullah — Axon OS Project
# Licensed under the Apache License, Version 2.0
# https://www.apache.org/licenses/LICENSE-2.0
# =============================================================================
# الوظيفة: إعداد Update Service لإدارة تحديثات Axon OS
# قابل للاستئناف: نعم
# ملاحظة: يعمل على Axon Layer فقط — لا يمس Ubuntu Base
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
readonly STEP_DONE="${AXON_STATE}/p2-04-update-service.done"
readonly SERVICE_DIR="${AXON_HOME}/platform/core-services"
readonly US_DIR="${SERVICE_DIR}/update-service"

# ─────────────────────────────────────────────
# دالة التنظيف
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
    exit 1
  fi

  if [[ ! -d "${AXON_STATE}" ]]; then
    log_error "مجلد state غير موجود: ${AXON_STATE}"
    exit 1
  fi

  # اختياريان — تحذير فقط
  command -v git    &>/dev/null || log_warn "git غير مثبت - تحديثات GitHub لن تعمل"
  command -v docker &>/dev/null || log_warn "docker غير مثبت - تحديث AI Container لن يعمل"

  log_success "جميع المتطلبات متوفرة"
}

# ─────────────────────────────────────────────
# فحص الاستئناف
# ─────────────────────────────────────────────
if [[ -f "${STEP_DONE}" ]]; then
  log_warn "Update Service مُعدَّ مسبقاً → تخطي"
  exit 0
fi

log_section "Update Service · إعداد إدارة التحديثات"

check_requirements

# ─────────────────────────────────────────────
# إنشاء المجلدات
# ─────────────────────────────────────────────
log_info "إنشاء المجلدات..."
mkdir -p "${US_DIR}" || { log_error "فشل إنشاء: ${US_DIR}"; exit 1; }
mkdir -p "${AXON_HOME}/bin"
log_success "المجلدات جاهزة"

# ─────────────────────────────────────────────
# إنشاء update_service.py
# ─────────────────────────────────────────────
log_info "إنشاء update_service.py..."
cat > "${US_DIR}/update_service.py" << 'PYTHON'
#!/usr/bin/env python3
# =============================================================================
# Axon OS — Update Service
# Copyright (c) 2025 Abdullah — Axon OS Project
# Licensed under Apache License 2.0
# =============================================================================
# ⚠️  يعمل على Axon Layer وAI Container فقط — Ubuntu Base محمي
# =============================================================================

import json
import time
import shutil
import subprocess
import logging
import threading
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime
from enum import Enum

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("axon-update-service")


# ── Enums ───────────────────────────────────────────────────────────────────

class UpdateStatus(str, Enum):
    PENDING     = "pending"
    APPLIED     = "applied"
    FAILED      = "failed"
    ROLLED_BACK = "rolled_back"
    SKIPPED     = "skipped"


class UpdateLayer(str, Enum):
    PLATFORM      = "platform"
    AI_CONTAINER  = "ai-container"


class UpdatePriority(str, Enum):
    CRITICAL = "critical"
    HIGH     = "high"
    NORMAL   = "normal"
    LOW      = "low"


# ── Exceptions ──────────────────────────────────────────────────────────────

class UpdateServiceError(Exception):
    pass

class BackupError(UpdateServiceError):
    pass

class RollbackError(UpdateServiceError):
    pass


# ── Dataclasses ─────────────────────────────────────────────────────────────

@dataclass
class UpdateRecord:
    id:               str
    version:          str
    description:      str
    timestamp:        str
    status:           str
    layer:            str
    priority:         str                  = "normal"
    backup_path:      Optional[str]        = None
    duration_seconds: float                = 0.0
    error_message:    Optional[str]        = None
    metadata:         Dict[str, Any]       = field(default_factory=dict)


@dataclass
class SystemVersion:
    version:           str
    commit:            str
    branch:            str
    last_update:       str
    platform_version:  str
    container_version: str


# ── Service ─────────────────────────────────────────────────────────────────

class UpdateService:
    """
    خدمة تحديثات Axon OS.
    يعمل على Platform Layer وAI Container فقط.
    لا يمس Ubuntu Base أو النواة.
    """

    STATE_DIR    = Path.home() / ".axon" / "updates"
    BACKUP_DIR   = Path.home() / ".axon" / "update-backups"
    HISTORY_FILE = STATE_DIR / "history.json"
    VERSION_FILE = STATE_DIR / "version.json"
    CONFIG_FILE  = STATE_DIR / "config.json"
    AXON_HOME    = Path.home() / "AxonOS"

    ALLOWED_LAYERS   = {UpdateLayer.PLATFORM.value, UpdateLayer.AI_CONTAINER.value}
    PROTECTED_LAYERS = {"ubuntu-base", "kernel", "drivers", "boot"}

    DEFAULT_TIMEOUT   = 300
    CONTAINER_TIMEOUT = 600

    def __init__(self, auto_backup: bool = True):
        self.auto_backup = auto_backup
        self.STATE_DIR.mkdir(parents=True, exist_ok=True)
        self.BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        self._history: List[Dict[str, Any]] = []
        self._config:  Dict[str, Any]       = {}
        self._lock = threading.Lock()
        self._load_history()
        self._load_config()
        logger.info("Update Service جاهز")
        logger.info("⚠️  يعمل على Axon Layer فقط — Ubuntu Base محمي")

    # ── Persistence ─────────────────────────────────────────────────

    def _load_history(self) -> None:
        try:
            if self.HISTORY_FILE.exists():
                data = json.loads(
                    self.HISTORY_FILE.read_text(encoding='utf-8')
                )
                self._history = data if isinstance(data, list) else []
            self._save_history()
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"خطأ في قراءة السجل: {e}")
            self._history = []

    def _save_history(self) -> None:
        try:
            self.HISTORY_FILE.write_text(
                json.dumps(self._history, ensure_ascii=False, indent=2),
                encoding='utf-8'
            )
        except IOError as e:
            logger.error(f"فشل حفظ السجل: {e}")

    def _load_config(self) -> None:
        try:
            if self.CONFIG_FILE.exists():
                self._config = json.loads(
                    self.CONFIG_FILE.read_text(encoding='utf-8')
                )
            else:
                self._config = {
                    "auto_backup":      True,
                    "check_interval":   24,
                    "max_history":      100,
                }
                self._save_config()
        except (json.JSONDecodeError, IOError):
            self._config = {}

    def _save_config(self) -> None:
        try:
            self.CONFIG_FILE.write_text(
                json.dumps(self._config, ensure_ascii=False, indent=2),
                encoding='utf-8'
            )
        except IOError as e:
            logger.error(f"فشل حفظ الإعدادات: {e}")

    # ── الأمان ──────────────────────────────────────────────────────

    def _validate_layer(self, layer: str) -> bool:
        """التحقق من أن الطبقة مسموح بتحديثها."""
        if layer in self.PROTECTED_LAYERS:
            logger.error(
                f"🔒 الطبقة '{layer}' محمية — لا يمكن تعديلها!"
            )
            return False
        if layer not in self.ALLOWED_LAYERS:
            logger.error(
                f"الطبقة '{layer}' غير مسموحة. "
                f"المسموح: {self.ALLOWED_LAYERS}"
            )
            return False
        return True

    def _validate_script_path(self, script: Path) -> bool:
        """التحقق من أن السكربت داخل مجلد Axon فقط."""
        try:
            script.resolve().relative_to(self.AXON_HOME.resolve())
            return True
        except ValueError:
            logger.error(f"السكربت خارج مجلد Axon — مرفوض: {script}")
            return False

    # ── النسخ الاحتياطي ─────────────────────────────────────────────

    def _create_backup(self, layer: str) -> Optional[str]:
        """إنشاء نسخة احتياطية قبل التحديث."""
        target = (
            self.AXON_HOME / "platform"
            if layer == UpdateLayer.PLATFORM.value
            else self.AXON_HOME / "ai-container"
        )

        if not target.exists():
            logger.warning(f"المسار غير موجود للنسخ: {target}")
            return None

        ts          = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.BACKUP_DIR / f"{layer}-backup-{ts}.tar.gz"

        try:
            shutil.make_archive(
                str(backup_path.with_suffix('').with_suffix('')),
                'gztar',
                root_dir=str(target.parent),
                base_dir=target.name,
            )
            logger.info(f"نسخة احتياطية: {backup_path}")
            return str(backup_path)
        except (OSError, shutil.Error) as e:
            logger.error(f"فشل النسخ الاحتياطي: {e}")
            return None

    def list_backups(
        self, layer: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """قائمة النسخ الاحتياطية."""
        backups = []
        pattern = f"{layer}-backup-*.tar.gz" if layer else "*.tar.gz"

        for f in self.BACKUP_DIR.glob(pattern):
            try:
                stat = f.stat()
                backups.append({
                    "name":       f.stem,
                    "path":       str(f),
                    "size_mb":    round(stat.st_size / (1024 ** 2), 2),
                    "created_at": datetime.fromtimestamp(
                        stat.st_ctime
                    ).isoformat(),
                })
            except OSError:
                continue

        backups.sort(key=lambda x: x["created_at"], reverse=True)
        return backups

    # ── التحديثات ────────────────────────────────────────────────────

    def check_git_updates(self) -> Dict[str, Any]:
        """فحص التحديثات من GitHub."""
        result: Dict[str, Any] = {
            "has_updates":    False,
            "current_commit": "",
            "remote_commit":  "",
            "message":        "",
        }

        if not (self.AXON_HOME / ".git").exists():
            result["message"] = "المشروع ليس git repository"
            return result

        try:
            current = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=str(self.AXON_HOME),
                capture_output=True, text=True, timeout=10
            )
            result["current_commit"] = current.stdout.strip()[:8]

            subprocess.run(
                ["git", "fetch", "origin"],
                cwd=str(self.AXON_HOME),
                capture_output=True, timeout=30
            )

            remote = subprocess.run(
                ["git", "rev-parse", "origin/main"],
                cwd=str(self.AXON_HOME),
                capture_output=True, text=True, timeout=10
            )
            result["remote_commit"] = remote.stdout.strip()[:8]
            result["has_updates"]   = (
                result["current_commit"] != result["remote_commit"]
            )
            result["message"] = (
                "تحديثات متاحة ✅"
                if result["has_updates"]
                else "النظام محدّث ✅"
            )

        except subprocess.TimeoutExpired:
            result["message"] = "انتهت مهلة الاتصال بـ GitHub"
        except FileNotFoundError:
            result["message"] = "git غير مثبت"
        except Exception as e:
            result["message"] = f"خطأ: {e}"

        return result

    def apply_git_update(
        self,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> bool:
        """تطبيق تحديث من GitHub."""
        if not (self.AXON_HOME / ".git").exists():
            logger.error("المشروع ليس git repository")
            return False

        record = UpdateRecord(
            id          = f"git-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            version     = "git-pull",
            description = "تحديث من GitHub",
            timestamp   = time.strftime("%Y-%m-%dT%H:%M:%S"),
            status      = UpdateStatus.PENDING.value,
            layer       = UpdateLayer.PLATFORM.value,
        )

        start = time.time()

        if self.auto_backup:
            if progress_callback:
                progress_callback("نسخ احتياطي...", 10)
            record.backup_path = self._create_backup(
                UpdateLayer.PLATFORM.value
            )

        try:
            if progress_callback:
                progress_callback("جلب التحديثات...", 40)

            result = subprocess.run(
                ["git", "pull", "origin", "main"],
                cwd=str(self.AXON_HOME),
                capture_output=True, text=True,
                timeout=self.DEFAULT_TIMEOUT
            )

            if result.returncode == 0:
                record.status = UpdateStatus.APPLIED.value
                logger.info("✅ تم تطبيق تحديث Git")
                if progress_callback:
                    progress_callback("اكتمل", 100)
            else:
                record.status        = UpdateStatus.FAILED.value
                record.error_message = result.stderr
                logger.error(f"فشل: {result.stderr}")

        except subprocess.TimeoutExpired:
            record.status        = UpdateStatus.FAILED.value
            record.error_message = "انتهت المهلة"
        except Exception as e:
            record.status        = UpdateStatus.FAILED.value
            record.error_message = str(e)

        record.duration_seconds = round(time.time() - start, 2)
        with self._lock:
            self._history.append(asdict(record))
            self._save_history()

        return record.status == UpdateStatus.APPLIED.value

    def apply_platform_update(
        self,
        script_path:       str,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> bool:
        """تطبيق تحديث على Platform Layer من سكربت."""
        if not self._validate_layer(UpdateLayer.PLATFORM.value):
            return False

        script = Path(script_path)
        if not self._validate_script_path(script):
            return False

        if not script.exists():
            logger.error(f"السكربت غير موجود: {script_path}")
            return False

        record = UpdateRecord(
            id          = f"plt-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            version     = time.strftime("%Y%m%d-%H%M%S"),
            description = f"Platform update: {script.name}",
            timestamp   = time.strftime("%Y-%m-%dT%H:%M:%S"),
            status      = UpdateStatus.PENDING.value,
            layer       = UpdateLayer.PLATFORM.value,
        )

        start = time.time()

        if self.auto_backup:
            record.backup_path = self._create_backup(
                UpdateLayer.PLATFORM.value
            )

        try:
            result = subprocess.run(
                ["bash", str(script)],
                capture_output=True, text=True,
                timeout=self.DEFAULT_TIMEOUT
            )
            if result.returncode == 0:
                record.status = UpdateStatus.APPLIED.value
                logger.info(f"✅ تم تطبيق التحديث: {script.name}")
            else:
                record.status        = UpdateStatus.FAILED.value
                record.error_message = result.stderr
                logger.error(f"فشل التحديث: {result.stderr}")

        except subprocess.TimeoutExpired:
            record.status        = UpdateStatus.FAILED.value
            record.error_message = f"انتهت المهلة ({self.DEFAULT_TIMEOUT}s)"
        except Exception as e:
            record.status        = UpdateStatus.FAILED.value
            record.error_message = str(e)

        record.duration_seconds = round(time.time() - start, 2)
        with self._lock:
            self._history.append(asdict(record))
            self._save_history()

        return record.status == UpdateStatus.APPLIED.value

    def apply_container_update(
        self,
        rebuild:           bool = True,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> bool:
        """إعادة بناء أو تشغيل AI Container."""
        if not self._validate_layer(UpdateLayer.AI_CONTAINER.value):
            return False

        container_dir = self.AXON_HOME / "ai-container"
        if not container_dir.exists():
            logger.error("مجلد ai-container غير موجود")
            return False

        record = UpdateRecord(
            id          = f"ctr-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            version     = time.strftime("%Y%m%d-%H%M%S"),
            description = "AI Container rebuild" if rebuild else "AI Container restart",
            timestamp   = time.strftime("%Y-%m-%dT%H:%M:%S"),
            status      = UpdateStatus.PENDING.value,
            layer       = UpdateLayer.AI_CONTAINER.value,
        )

        start   = time.time()
        timeout = self.CONTAINER_TIMEOUT

        if self.auto_backup:
            record.backup_path = self._create_backup(
                UpdateLayer.AI_CONTAINER.value
            )

        try:
            if rebuild:
                if progress_callback:
                    progress_callback("إيقاف الحاوية...", 10)
                subprocess.run(
                    ["docker", "compose", "down"],
                    cwd=str(container_dir),
                    capture_output=True, timeout=60
                )

                if progress_callback:
                    progress_callback("بناء الحاوية...", 30)
                result = subprocess.run(
                    ["docker", "compose", "build", "--no-cache"],
                    cwd=str(container_dir),
                    capture_output=True, text=True, timeout=timeout
                )

                if progress_callback:
                    progress_callback("تشغيل الحاوية...", 80)
                subprocess.run(
                    ["docker", "compose", "up", "-d"],
                    cwd=str(container_dir),
                    capture_output=True, timeout=60
                )
            else:
                result = subprocess.run(
                    ["docker", "compose", "restart"],
                    cwd=str(container_dir),
                    capture_output=True, text=True, timeout=120
                )

            if result.returncode == 0:
                record.status = UpdateStatus.APPLIED.value
                logger.info("✅ تم تحديث AI Container")
                if progress_callback:
                    progress_callback("اكتمل", 100)
            else:
                record.status        = UpdateStatus.FAILED.value
                record.error_message = result.stderr or result.stdout
                logger.error(f"فشل: {record.error_message}")

        except subprocess.TimeoutExpired:
            record.status        = UpdateStatus.FAILED.value
            record.error_message = f"انتهت المهلة ({timeout}s)"
        except Exception as e:
            record.status        = UpdateStatus.FAILED.value
            record.error_message = str(e)

        record.duration_seconds = round(time.time() - start, 2)
        with self._lock:
            self._history.append(asdict(record))
            self._save_history()

        return record.status == UpdateStatus.APPLIED.value

    # ── التراجع ──────────────────────────────────────────────────────

    def _rollback_from_backup(self, backup_path: str, layer: str) -> bool:
        backup = Path(backup_path)
        if not backup.exists():
            logger.error(f"النسخة الاحتياطية غير موجودة: {backup_path}")
            return False

        target = (
            self.AXON_HOME / "platform"
            if layer == UpdateLayer.PLATFORM.value
            else self.AXON_HOME / "ai-container"
        )

        try:
            if target.exists():
                shutil.rmtree(target)
            shutil.unpack_archive(backup_path, target.parent)
            logger.info(f"✅ تم التراجع من: {backup_path}")
            return True
        except (OSError, shutil.ReadError) as e:
            logger.error(f"فشل التراجع: {e}")
            return False

    def rollback(
        self,
        update_id: Optional[str] = None,
        layer:     Optional[str] = None,
    ) -> bool:
        backup_path = None

        if update_id:
            for record in reversed(self._history):
                if record.get("id") == update_id:
                    backup_path = record.get("backup_path")
                    layer       = record.get("layer")
                    break
        else:
            backups = self.list_backups(layer)
            if backups:
                backup_path = backups[0]["path"]

        if not backup_path or not layer:
            logger.error("لم يُعثر على نسخة احتياطية صالحة")
            return False

        success = self._rollback_from_backup(backup_path, layer)

        if success:
            rec = UpdateRecord(
                id          = f"rb-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                version     = "rollback",
                description = f"تراجع من: {backup_path}",
                timestamp   = time.strftime("%Y-%m-%dT%H:%M:%S"),
                status      = UpdateStatus.ROLLED_BACK.value,
                layer       = layer,
            )
            with self._lock:
                self._history.append(asdict(rec))
                self._save_history()

        return success

    # ── إصدار النظام ─────────────────────────────────────────────────

    def get_system_version(self) -> SystemVersion:
        commit = "unknown"
        branch = "unknown"

        if (self.AXON_HOME / ".git").exists():
            try:
                commit = subprocess.run(
                    ["git", "rev-parse", "--short", "HEAD"],
                    cwd=str(self.AXON_HOME),
                    capture_output=True, text=True, timeout=5
                ).stdout.strip()
                branch = subprocess.run(
                    ["git", "branch", "--show-current"],
                    cwd=str(self.AXON_HOME),
                    capture_output=True, text=True, timeout=5
                ).stdout.strip()
            except Exception:
                pass

        version_data: Dict[str, str] = {}
        if self.VERSION_FILE.exists():
            try:
                version_data = json.loads(
                    self.VERSION_FILE.read_text(encoding='utf-8')
                )
            except Exception:
                pass

        return SystemVersion(
            version           = version_data.get("version", "1.0.0"),
            commit            = commit,
            branch            = branch,
            last_update       = self._history[-1].get("timestamp", "never")
                                if self._history else "never",
            platform_version  = version_data.get("platform", "1.0.0"),
            container_version = version_data.get("container", "1.0.0"),
        )

    # ── تقارير ───────────────────────────────────────────────────────

    def history(
        self,
        limit: int           = 20,
        layer: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        records = self._history
        if layer:
            records = [r for r in records if r.get("layer") == layer]
        return records[-limit:]

    def summary(self) -> Dict[str, Any]:
        return {
            "total_updates":   len(self._history),
            "applied":         sum(
                1 for u in self._history
                if u.get("status") == UpdateStatus.APPLIED.value
            ),
            "failed":          sum(
                1 for u in self._history
                if u.get("status") == UpdateStatus.FAILED.value
            ),
            "rolled_back":     sum(
                1 for u in self._history
                if u.get("status") == UpdateStatus.ROLLED_BACK.value
            ),
            "protected_layers": list(self.PROTECTED_LAYERS),
            "allowed_layers":   list(self.ALLOWED_LAYERS),
            "backups":          len(self.list_backups()),
            "last_update":      self._history[-1].get("timestamp")
                                if self._history else None,
            "system_version":   asdict(self.get_system_version()),
        }

    def get_config(self) -> Dict[str, Any]:
        return self._config.copy()

    def set_config(self, key: str, value: Any) -> None:
        self._config[key] = value
        self._save_config()
        logger.info(f"تم تحديث الإعداد: {key} = {value}")


def main():
    us = UpdateService()
    print(json.dumps(us.summary(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
PYTHON

log_success "update_service.py تم إنشاؤه"

# ─────────────────────────────────────────────
# اختبار سريع
# ─────────────────────────────────────────────
log_info "اختبار Update Service..."
if python3 "${US_DIR}/update_service.py" &>/dev/null; then
  log_success "Update Service يعمل بشكل صحيح"
else
  log_error "فشل اختبار Update Service"
  exit 1
fi

# ─────────────────────────────────────────────
# إنشاء اختصار
# ─────────────────────────────────────────────
log_info "إنشاء اختصار axon-update..."
cat > "${AXON_HOME}/bin/axon-update" << 'SHORTCUT'
#!/bin/bash
python3 "${HOME}/AxonOS/platform/core-services/update-service/update_service.py" "$@"
SHORTCUT
chmod +x "${AXON_HOME}/bin/axon-update"
log_success "اختصار axon-update جاهز"

# ─────────────────────────────────────────────
# حفظ حالة الاكتمال
# [إصلاح] جميع القيم محاطة بعلامات اقتباس
# ─────────────────────────────────────────────
git_ok="$(command -v git    &>/dev/null && echo 'yes' || echo 'no')"
docker_ok="$(command -v docker &>/dev/null && echo 'yes' || echo 'no')"

cat > "${STEP_DONE}" << EOF
completed="$(date '+%Y-%m-%dT%H:%M:%S')"
version="1.0"
python="$(python3 --version 2>&1 | cut -d' ' -f2)"
git_available="${git_ok}"
docker_available="${docker_ok}"
EOF

log_success "✓ Update Service مكتمل"
