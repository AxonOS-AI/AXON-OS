#!/bin/bash
# =============================================================================
# Axon OS — 03-file-manager.sh
# =============================================================================
# Copyright (c) 2025 Abdullah — Axon OS Project
# Licensed under the Apache License, Version 2.0
# https://www.apache.org/licenses/LICENSE-2.0
# =============================================================================
# الوظيفة: إعداد File Manager لإدارة ملفات Axon OS
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
readonly STEP_DONE="${AXON_STATE}/p2-03-file-manager.done"
readonly SERVICE_DIR="${AXON_HOME}/platform/core-services"
readonly FM_DIR="${SERVICE_DIR}/file-manager"

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
  log_success "جميع المتطلبات متوفرة"
}

# ─────────────────────────────────────────────
# فحص الاستئناف
# ─────────────────────────────────────────────
if [[ -f "${STEP_DONE}" ]]; then
  log_warn "File Manager مُعدَّ مسبقاً → تخطي"
  exit 0
fi

log_section "File Manager · إعداد إدارة الملفات"

check_requirements

# ─────────────────────────────────────────────
# إنشاء المجلدات
# ─────────────────────────────────────────────
log_info "إنشاء المجلدات..."
mkdir -p "${FM_DIR}" || { log_error "فشل إنشاء: ${FM_DIR}"; exit 1; }
mkdir -p "${AXON_HOME}/bin"
log_success "المجلدات جاهزة"

# ─────────────────────────────────────────────
# إنشاء file_manager.py
# ─────────────────────────────────────────────
log_info "إنشاء file_manager.py..."
cat > "${FM_DIR}/file_manager.py" << 'PYTHON'
#!/usr/bin/env python3
# =============================================================================
# Axon OS — File Manager
# Copyright (c) 2025 Abdullah — Axon OS Project
# Licensed under Apache License 2.0
# =============================================================================

import os
import json
import shutil
import hashlib
import zipfile
import tarfile
import fnmatch
import logging
import threading
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("axon-file-manager")


# ── Exceptions ──────────────────────────────────────────────────────────────

class FileManagerError(Exception):
    pass

class SecurityError(FileManagerError):
    """محاولة الوصول لملف خارج المسار المسموح."""
    pass


# ── Constants ───────────────────────────────────────────────────────────────

ALLOWED_EXTENSIONS: Dict[str, set] = {
    "model":    {".pt", ".pth", ".bin", ".gguf", ".safetensors", ".onnx", ".h5", ".pkl"},
    "dataset":  {".csv", ".tsv", ".json", ".jsonl", ".parquet", ".txt", ".arrow"},
    "config":   {".yaml", ".yml", ".json", ".toml", ".ini", ".env", ".cfg"},
    "script":   {".py", ".sh", ".bash"},
    "log":      {".log", ".txt", ".out"},
    "archive":  {".zip", ".tar", ".gz", ".bz2", ".xz"},
    "document": {".pdf", ".md", ".rst"},
}

ALLOWED_BASE_PATHS = [
    Path.home() / "AxonOS",
    Path.home() / ".axon",
]


# ── Dataclasses ─────────────────────────────────────────────────────────────

@dataclass
class FileInfo:
    name:        str
    path:        str
    size_bytes:  int
    size_mb:     float
    extension:   str
    file_type:   str
    checksum:    str
    modified_at: str
    is_readable: bool
    is_writable: bool


@dataclass
class DirectoryInfo:
    path:          str
    total_files:   int
    total_dirs:    int
    total_size_mb: float
    file_types:    Dict[str, int] = field(default_factory=dict)


# ── Manager ─────────────────────────────────────────────────────────────────

class FileManager:
    """مدير ملفات Axon OS — قراءة / نسخ / نقل / حذف / ضغط بأمان."""

    BASE_DIR   = Path.home() / "AxonOS"
    TRASH_DIR  = Path.home() / ".axon" / "trash"
    BACKUP_DIR = Path.home() / ".axon" / "backups"
    CHUNK_SIZE = 1024 * 1024   # 1 MB
    _lock      = threading.Lock()

    def __init__(self, strict_security: bool = True):
        self.strict_security = strict_security
        self.TRASH_DIR.mkdir(parents=True, exist_ok=True)
        self.BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        logger.info("File Manager جاهز")

    # ── الأمان ──────────────────────────────────────────────────────

    def _validate_path(self, path: Path) -> Path:
        """
        التحقق من أن المسار داخل النطاق المسموح.
        يمنع path traversal هجمات.
        """
        try:
            resolved = path.resolve()
        except (OSError, RuntimeError) as e:
            raise SecurityError(f"مسار غير صالح: {path} - {e}")

        if not self.strict_security:
            return resolved

        for allowed in ALLOWED_BASE_PATHS:
            try:
                resolved.relative_to(allowed.resolve())
                return resolved
            except ValueError:
                continue

        raise SecurityError(
            f"الوصول مرفوض: {resolved}\n"
            f"المسارات المسموحة: {[str(p) for p in ALLOWED_BASE_PATHS]}"
        )

    # ── معلومات ─────────────────────────────────────────────────────

    def _file_type(self, ext: str) -> str:
        for ftype, exts in ALLOWED_EXTENSIONS.items():
            if ext.lower() in exts:
                return ftype
        return "unknown"

    def _checksum(self, path: Path) -> str:
        h = hashlib.md5()
        try:
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(self.CHUNK_SIZE), b""):
                    h.update(chunk)
            return h.hexdigest()
        except OSError:
            return "error"

    def info(self, path: str) -> Optional[FileInfo]:
        p = Path(path)
        try:
            p = self._validate_path(p)
        except SecurityError as e:
            logger.error(str(e))
            return None

        if not p.exists() or not p.is_file():
            logger.error(f"الملف غير موجود: {path}")
            return None

        stat = p.stat()
        return FileInfo(
            name        = p.name,
            path        = str(p),
            size_bytes  = stat.st_size,
            size_mb     = round(stat.st_size / (1024 ** 2), 3),
            extension   = p.suffix.lower(),
            file_type   = self._file_type(p.suffix),
            checksum    = self._checksum(p),
            modified_at = datetime.fromtimestamp(stat.st_mtime).isoformat(),
            is_readable = os.access(p, os.R_OK),
            is_writable = os.access(p, os.W_OK),
        )

    def dir_info(self, directory: str) -> Optional[DirectoryInfo]:
        d = Path(directory)
        try:
            d = self._validate_path(d)
        except SecurityError as e:
            logger.error(str(e))
            return None

        if not d.exists() or not d.is_dir():
            return None

        total_files  = 0
        total_dirs   = 0
        total_size   = 0
        file_types: Dict[str, int] = {}

        for item in d.rglob("*"):
            if item.is_file():
                total_files += 1
                total_size  += item.stat().st_size
                ft = self._file_type(item.suffix)
                file_types[ft] = file_types.get(ft, 0) + 1
            elif item.is_dir():
                total_dirs += 1

        return DirectoryInfo(
            path          = str(d),
            total_files   = total_files,
            total_dirs    = total_dirs,
            total_size_mb = round(total_size / (1024 ** 2), 2),
            file_types    = file_types,
        )

    def list_dir(
        self,
        directory: str,
        pattern:   str  = "*",
        recursive: bool = False,
    ) -> List[dict]:
        d = Path(directory)
        try:
            d = self._validate_path(d)
        except SecurityError as e:
            logger.error(str(e))
            return []

        if not d.exists():
            return []

        glob_fn = d.rglob if recursive else d.glob
        files   = []
        for f in sorted(glob_fn(pattern)):
            if f.is_file():
                info = self.info(str(f))
                if info:
                    files.append(asdict(info))
        return files

    # ── عمليات ──────────────────────────────────────────────────────

    def copy(
        self,
        src:               str,
        dst:               str,
        progress_callback: Optional[Callable[[int], None]] = None,
    ) -> bool:
        src_p, dst_p = Path(src), Path(dst)
        try:
            src_p = self._validate_path(src_p)
            dst_p = self._validate_path(dst_p)
        except SecurityError as e:
            logger.error(str(e))
            return False

        if not src_p.exists():
            logger.error(f"المصدر غير موجود: {src}")
            return False

        with self._lock:
            dst_p.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_p, dst_p)

        logger.info(f"تم النسخ: {src} → {dst}")
        if progress_callback:
            progress_callback(100)
        return True

    def move(self, src: str, dst: str) -> bool:
        src_p, dst_p = Path(src), Path(dst)
        try:
            src_p = self._validate_path(src_p)
            dst_p = self._validate_path(dst_p)
        except SecurityError as e:
            logger.error(str(e))
            return False

        if not src_p.exists():
            logger.error(f"المصدر غير موجود: {src}")
            return False

        dst_p.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src_p), str(dst_p))
        logger.info(f"تم النقل: {src} → {dst}")
        return True

    def delete(self, path: str, safe: bool = True) -> bool:
        p = Path(path)
        try:
            p = self._validate_path(p)
        except SecurityError as e:
            logger.error(str(e))
            return False

        if not p.exists():
            logger.error(f"الملف غير موجود: {path}")
            return False

        if safe:
            self.TRASH_DIR.mkdir(parents=True, exist_ok=True)
            shutil.move(str(p), str(self.TRASH_DIR / p.name))
            logger.info(f"نُقل للمهملات: {path}")
        else:
            p.unlink()
            logger.info(f"حُذف نهائياً: {path}")
        return True

    def search(
        self,
        directory:      str,
        query:          str,
        search_content: bool = False,
    ) -> List[dict]:
        d = Path(directory)
        try:
            d = self._validate_path(d)
        except SecurityError as e:
            logger.error(str(e))
            return []

        results = []
        q = query.lower()

        for f in d.rglob("*"):
            if not f.is_file():
                continue
            if q in f.name.lower():
                info = self.info(str(f))
                if info:
                    results.append(asdict(info))
                continue
            if search_content:
                try:
                    if q in f.read_text(errors='ignore').lower():
                        info = self.info(str(f))
                        if info:
                            results.append(asdict(info))
                except OSError:
                    pass

        return results

    def find_duplicates(self, directory: str) -> Dict[str, List[str]]:
        d = Path(directory)
        try:
            d = self._validate_path(d)
        except SecurityError as e:
            logger.error(str(e))
            return {}

        checksums: Dict[str, List[str]] = {}
        for f in d.rglob("*"):
            if f.is_file():
                cs = self._checksum(f)
                checksums.setdefault(cs, []).append(str(f))

        return {cs: paths for cs, paths in checksums.items() if len(paths) > 1}

    # ── ضغط وفك ضغط ─────────────────────────────────────────────────

    def compress(
        self,
        sources:           List[str],
        output:            str,
        compression:       str = "zip",
        progress_callback: Optional[Callable[[int], None]] = None,
    ) -> bool:
        output_path = Path(output)
        valid_sources = []

        for s in sources:
            try:
                sp = self._validate_path(Path(s))
                if sp.exists():
                    valid_sources.append(sp)
            except SecurityError:
                logger.warning(f"تم تخطي مسار غير مسموح: {s}")

        if not valid_sources:
            logger.error("لا توجد ملفات صالحة للضغط")
            return False

        try:
            if compression == "zip":
                with zipfile.ZipFile(output_path, 'w',
                                     zipfile.ZIP_DEFLATED) as zf:
                    total = len(valid_sources)
                    for i, src in enumerate(valid_sources):
                        zf.write(src, src.name)
                        if progress_callback:
                            progress_callback(int((i + 1) / total * 100))

            elif compression in ("tar", "tar.gz", "tar.bz2"):
                mode = "w" if compression == "tar" \
                    else f"w:{compression.split('.')[-1]}"
                with tarfile.open(output_path, mode) as tf:
                    total = len(valid_sources)
                    for i, src in enumerate(valid_sources):
                        tf.add(src, arcname=src.name)
                        if progress_callback:
                            progress_callback(int((i + 1) / total * 100))
            else:
                logger.error(f"نوع ضغط غير مدعوم: {compression}")
                return False

            logger.info(f"تم الضغط: {output}")
            return True

        except OSError as e:
            logger.error(f"فشل الضغط: {e}")
            return False

    def extract(
        self,
        archive:           str,
        destination:       str,
        progress_callback: Optional[Callable[[int], None]] = None,
    ) -> bool:
        arc_p  = Path(archive)
        dest_p = Path(destination)

        try:
            arc_p  = self._validate_path(arc_p)
            dest_p = self._validate_path(dest_p)
        except SecurityError as e:
            logger.error(str(e))
            return False

        if not arc_p.exists():
            logger.error(f"الأرشيف غير موجود: {archive}")
            return False

        try:
            dest_p.mkdir(parents=True, exist_ok=True)
            dest_resolved = dest_p.resolve()

            if arc_p.suffix == ".zip":
                with zipfile.ZipFile(arc_p, 'r') as zf:
                    members = zf.namelist()
                    total   = len(members)
                    for i, member in enumerate(members):
                        # [إصلاح] منع path traversal داخل الأرشيف
                        member_path = (dest_p / member).resolve()
                        if not str(member_path).startswith(
                            str(dest_resolved)
                        ):
                            logger.warning(f"تم تخطي ملف مشبوه: {member}")
                            continue
                        zf.extract(member, dest_p)
                        if progress_callback:
                            progress_callback(int((i + 1) / total * 100))

            elif arc_p.suffix in (".tar", ".gz", ".bz2", ".xz"):
                with tarfile.open(arc_p, 'r:*') as tf:
                    members = tf.getmembers()
                    total   = len(members)
                    for i, member in enumerate(members):
                        # [إصلاح] منع path traversal داخل tar
                        member_path = (dest_p / member.name).resolve()
                        if not str(member_path).startswith(
                            str(dest_resolved)
                        ):
                            logger.warning(f"تم تخطي ملف مشبوه: {member.name}")
                            continue
                        tf.extract(member, dest_p)
                        if progress_callback:
                            progress_callback(int((i + 1) / total * 100))
            else:
                logger.error(f"نوع ملف غير مدعوم: {arc_p.suffix}")
                return False

            logger.info(f"تم فك الضغط: {archive} → {destination}")
            return True

        except (OSError, zipfile.BadZipFile, tarfile.TarError) as e:
            logger.error(f"فشل فك الضغط: {e}")
            return False

    # ── النسخ الاحتياطي ─────────────────────────────────────────────

    def backup(
        self,
        source: str,
        name:   Optional[str] = None,
    ) -> Optional[str]:
        src_p = Path(source)
        try:
            src_p = self._validate_path(src_p)
        except SecurityError as e:
            logger.error(str(e))
            return None

        if not src_p.exists():
            logger.error(f"المصدر غير موجود: {source}")
            return None

        ts          = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = name or f"{src_p.stem}_backup_{ts}"
        backup_path = self.BACKUP_DIR / f"{backup_name}.zip"

        return str(backup_path) if self.compress(
            [str(src_p)], str(backup_path)
        ) else None

    def restore_backup(self, backup_path: str, destination: str) -> bool:
        return self.extract(backup_path, destination)

    def list_backups(self) -> List[Dict[str, Any]]:
        backups = []
        for f in self.BACKUP_DIR.glob("*.zip"):
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

    # ── إحصائيات ────────────────────────────────────────────────────

    def disk_usage(self, directory: Optional[str] = None) -> Dict[str, Any]:
        d = Path(directory) if directory else self.BASE_DIR
        try:
            d = self._validate_path(d)
        except SecurityError:
            d = Path.home()

        try:
            usage = shutil.disk_usage(d)
            return {
                "total_gb": round(usage.total / (1024 ** 3), 2),
                "used_gb":  round(usage.used  / (1024 ** 3), 2),
                "free_gb":  round(usage.free  / (1024 ** 3), 2),
                "percent":  round(usage.used / usage.total * 100, 1),
                "path":     str(d),
            }
        except OSError as e:
            logger.error(f"فشل قراءة القرص: {e}")
            return {}

    def summary(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "disk":    self.disk_usage(),
            "directories": {},
            "trash":   {
                "path":  str(self.TRASH_DIR),
                "items": len(list(self.TRASH_DIR.iterdir()))
                         if self.TRASH_DIR.exists() else 0,
            },
            "backups": {
                "path":  str(self.BACKUP_DIR),
                "count": len(list(self.BACKUP_DIR.glob("*.zip")))
                         if self.BACKUP_DIR.exists() else 0,
            },
        }

        for subdir in ["ai-container/models", "platform", "scripts"]:
            d = self.BASE_DIR / subdir
            if d.exists():
                di = self.dir_info(str(d))
                if di:
                    result["directories"][subdir] = asdict(di)

        return result


def main():
    fm = FileManager()
    print(json.dumps(fm.summary(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
PYTHON

log_success "file_manager.py تم إنشاؤه"

# ─────────────────────────────────────────────
# اختبار سريع
# ─────────────────────────────────────────────
log_info "اختبار File Manager..."
if python3 "${FM_DIR}/file_manager.py" &>/dev/null; then
  log_success "File Manager يعمل بشكل صحيح"
else
  log_error "فشل اختبار File Manager"
  exit 1
fi

# ─────────────────────────────────────────────
# إنشاء اختصار
# ─────────────────────────────────────────────
log_info "إنشاء اختصار axon-file..."
cat > "${AXON_HOME}/bin/axon-file" << 'SHORTCUT'
#!/bin/bash
python3 "${HOME}/AxonOS/platform/core-services/file-manager/file_manager.py" "$@"
SHORTCUT
chmod +x "${AXON_HOME}/bin/axon-file"
log_success "اختصار axon-file جاهز"

# ─────────────────────────────────────────────
# حفظ حالة الاكتمال
# [إصلاح] جميع القيم محاطة بعلامات اقتباس
# ─────────────────────────────────────────────
cat > "${STEP_DONE}" << EOF
completed="$(date '+%Y-%m-%dT%H:%M:%S')"
version="1.0"
python="$(python3 --version 2>&1 | cut -d' ' -f2)"
security="strict"
EOF

log_success "✓ File Manager مكتمل"
