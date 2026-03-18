#!/bin/bash
# =============================================================================
# Axon OS — 02-project-manager.sh
# =============================================================================
# Copyright (c) 2025 Abdullah — Axon OS Project
# Licensed under the Apache License, Version 2.0
# https://www.apache.org/licenses/LICENSE-2.0
# =============================================================================
# الوظيفة: إعداد Project Manager لإدارة مشاريع Axon OS
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
readonly STEP_DONE="${AXON_STATE}/p2-02-project-manager.done"
readonly SERVICE_DIR="${AXON_HOME}/platform/core-services"
readonly PM_DIR="${SERVICE_DIR}/project-manager"
readonly PROJECTS_DIR="${HOME}/.axon/projects"

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
  log_warn "Project Manager مُعدَّ مسبقاً → تخطي"
  exit 0
fi

log_section "Project Manager · إعداد إدارة المشاريع"

check_requirements

# ─────────────────────────────────────────────
# إنشاء المجلدات
# ─────────────────────────────────────────────
log_info "إنشاء المجلدات..."
mkdir -p "${PM_DIR}" || { log_error "فشل إنشاء: ${PM_DIR}"; exit 1; }
mkdir -p "${PROJECTS_DIR}" || { log_error "فشل إنشاء: ${PROJECTS_DIR}"; exit 1; }
mkdir -p "${AXON_HOME}/bin"
log_success "المجلدات جاهزة"

# ─────────────────────────────────────────────
# إنشاء project_manager.py
# ─────────────────────────────────────────────
log_info "إنشاء project_manager.py..."
cat > "${PM_DIR}/project_manager.py" << 'PYTHON'
#!/usr/bin/env python3
# =============================================================================
# Axon OS — Project Manager
# Copyright (c) 2025 Abdullah — Axon OS Project
# Licensed under Apache License 2.0
# =============================================================================

import json
import re
import shutil
import time
import logging
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict, Any
from enum import Enum

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("axon-project-manager")


# ── Enums ───────────────────────────────────────────────────────────────────

class ProjectType(str, Enum):
    TRAINING   = "training"
    INFERENCE  = "inference"
    DATASET    = "dataset"
    FINETUNING = "finetuning"
    EVALUATION = "evaluation"
    CUSTOM     = "custom"

    @classmethod
    def valid_types(cls) -> List[str]:
        return [t.value for t in cls]


class ProjectStatus(str, Enum):
    ACTIVE   = "active"
    ARCHIVED = "archived"
    DELETED  = "deleted"

    @classmethod
    def valid_statuses(cls) -> List[str]:
        return [s.value for s in cls]


# ── Exceptions ──────────────────────────────────────────────────────────────

class ProjectManagerError(Exception):
    pass


# ── Dataclass ───────────────────────────────────────────────────────────────

@dataclass
class Project:
    name:        str
    description: str
    type:        str
    created_at:  str
    updated_at:  str
    status:      str                      = "active"
    tags:        List[str]                = field(default_factory=list)
    metadata:    Dict[str, Any]           = field(default_factory=dict)
    version:     str                      = "1.0.0"

    def __post_init__(self):
        if self.type not in ProjectType.valid_types():
            logger.warning(f"نوع غير معروف: {self.type} → custom")
            self.type = ProjectType.CUSTOM.value
        if self.status not in ProjectStatus.valid_statuses():
            logger.warning(f"حالة غير معروفة: {self.status} → active")
            self.status = ProjectStatus.ACTIVE.value


# ── Manager ─────────────────────────────────────────────────────────────────

class ProjectManager:
    """مدير مشاريع Axon OS."""

    PROJECTS_DIR = Path.home() / ".axon" / "projects"
    INDEX_FILE   = Path.home() / ".axon" / "projects-index.json"
    BACKUP_DIR   = Path.home() / ".axon" / "projects-backup"

    def __init__(self):
        self.PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
        self.BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        self._index: Dict[str, str] = {}
        self._load_index()
        logger.info("Project Manager جاهز")

    # ── Index ────────────────────────────────────────────────────────

    def _load_index(self) -> None:
        try:
            if self.INDEX_FILE.exists():
                data = json.loads(
                    self.INDEX_FILE.read_text(encoding='utf-8')
                )
                self._index = data if isinstance(data, dict) else {}
            else:
                self._index = {}
            self._save_index()
        except json.JSONDecodeError as e:
            logger.error(f"خطأ في قراءة الفهرس: {e}")
            self._backup_corrupted_index()
            self._index = {}

    def _save_index(self) -> None:
        try:
            self.INDEX_FILE.write_text(
                json.dumps(self._index, ensure_ascii=False, indent=2),
                encoding='utf-8'
            )
        except IOError as e:
            raise ProjectManagerError(f"فشل حفظ الفهرس: {e}")

    def _backup_corrupted_index(self) -> None:
        if self.INDEX_FILE.exists():
            backup = self.BACKUP_DIR / f"index-backup-{int(time.time())}.json"
            try:
                shutil.copy2(self.INDEX_FILE, backup)
                logger.info(f"نسخة احتياطية: {backup}")
            except IOError:
                pass

    # ── Utilities ────────────────────────────────────────────────────

    @staticmethod
    def _sanitize_name(name: str) -> str:
        sanitized = re.sub(r'[<>:"/\\|?*\s]+', '-', name)
        sanitized = re.sub(r'-+', '-', sanitized).strip('-')
        if not sanitized:
            raise ProjectManagerError("اسم المشروع غير صالح")
        return sanitized.lower()

    def _now(self) -> str:
        return time.strftime("%Y-%m-%dT%H:%M:%S")

    # ── CRUD ─────────────────────────────────────────────────────────

    def create(
        self,
        name:        str,
        description: str                  = "",
        type:        str                  = "custom",
        tags:        Optional[List[str]]  = None,
        metadata:    Optional[Dict[str, Any]] = None,
    ) -> Project:
        safe_name = self._sanitize_name(name)
        if safe_name in self._index:
            raise ProjectManagerError(f"المشروع '{safe_name}' موجود مسبقاً")

        now     = self._now()
        project = Project(
            name        = safe_name,
            description = description,
            type        = type,
            created_at  = now,
            updated_at  = now,
            tags        = tags or [],
            metadata    = metadata or {},
        )

        project_dir = self.PROJECTS_DIR / safe_name
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / "project.json").write_text(
            json.dumps(asdict(project), ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

        self._index[safe_name] = str(project_dir)
        self._save_index()
        logger.info(f"تم إنشاء المشروع: {safe_name}")
        return project

    def get(self, name: str) -> Optional[Project]:
        safe_name = self._sanitize_name(name)
        if safe_name not in self._index:
            return None
        meta = Path(self._index[safe_name]) / "project.json"
        if not meta.exists():
            return None
        return Project(**json.loads(meta.read_text(encoding='utf-8')))

    def update(self, name: str, **kwargs) -> bool:
        project = self.get(name)
        if not project:
            logger.warning(f"المشروع '{name}' غير موجود")
            return False

        for key, value in kwargs.items():
            if hasattr(project, key):
                setattr(project, key, value)

        project.updated_at = self._now()
        meta = Path(self._index[self._sanitize_name(name)]) / "project.json"
        meta.write_text(
            json.dumps(asdict(project), ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
        logger.info(f"تم تحديث المشروع: {name}")
        return True

    def list_all(
        self,
        status: Optional[str] = None,
        type:   Optional[str] = None,
        tags:   Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        projects = []
        for name in self._index:
            p = self.get(name)
            if not p or p.status == "deleted":
                continue
            if status and p.status != status:
                continue
            if type and p.type != type:
                continue
            if tags and not any(tag in p.tags for tag in tags):
                continue
            projects.append(asdict(p))
        projects.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
        return projects

    def search(self, query: str) -> List[Dict[str, Any]]:
        q = query.lower()
        return [
            asdict(p) for name in self._index
            if (p := self.get(name))
            and p.status != "deleted"
            and (q in p.name.lower()
                 or q in p.description.lower()
                 or any(q in tag.lower() for tag in p.tags))
        ]

    def archive(self, name: str) -> bool:
        p = self.get(name)
        if not p:
            return False
        if p.status == "archived":
            return True
        return self.update(name, status="archived")

    def restore(self, name: str) -> bool:
        p = self.get(name)
        if not p:
            return False
        if p.status == "active":
            return True
        return self.update(name, status="active")

    def delete(self, name: str, permanent: bool = False) -> bool:
        safe_name = self._sanitize_name(name)
        if safe_name not in self._index:
            return False
        if permanent:
            try:
                shutil.rmtree(self._index[safe_name], ignore_errors=True)
                del self._index[safe_name]
                self._save_index()
            except OSError as e:
                logger.error(f"فشل الحذف: {e}")
                return False
        else:
            self.update(name, status="deleted")
        logger.info(f"تم حذف المشروع: {name}")
        return True

    def duplicate(self, source: str, target: str) -> Optional[Project]:
        src = self.get(source)
        if not src:
            return None
        return self.create(
            name        = target,
            description = f"نسخة من {source}: {src.description}",
            type        = src.type,
            tags        = src.tags.copy(),
            metadata    = src.metadata.copy(),
        )

    def export_index(self, output_path: Optional[Path] = None) -> Path:
        output = output_path or self.BACKUP_DIR / f"export-{int(time.time())}.json"
        output.write_text(
            json.dumps({
                "exported_at":     time.strftime("%Y-%m-%dT%H:%M:%S"),
                "total_projects":  len(self._index),
                "projects":        self.list_all(),
            }, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
        logger.info(f"تم التصدير: {output}")
        return output

    def summary(self) -> Dict[str, Any]:
        all_p = self.list_all()
        by_type: Dict[str, int] = {}
        for p in all_p:
            by_type[p["type"]] = by_type.get(p["type"], 0) + 1

        all_tags: List[str] = []
        for p in all_p:
            all_tags.extend(p.get("tags", []))
        tag_counts: Dict[str, int] = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

        return {
            "total":    len(all_p),
            "by_status": {
                "active":   sum(1 for p in all_p if p["status"] == "active"),
                "archived": sum(1 for p in all_p if p["status"] == "archived"),
            },
            "by_type":        by_type,
            "popular_tags":   dict(
                sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            ),
            "recent_projects": [p["name"] for p in all_p[:5]],
        }


def main():
    pm = ProjectManager()
    print(json.dumps(pm.summary(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
PYTHON

log_success "project_manager.py تم إنشاؤه"

# ─────────────────────────────────────────────
# اختبار سريع
# ─────────────────────────────────────────────
log_info "اختبار Project Manager..."
if python3 "${PM_DIR}/project_manager.py" &>/dev/null; then
  log_success "Project Manager يعمل بشكل صحيح"
else
  log_error "فشل اختبار Project Manager"
  exit 1
fi

# ─────────────────────────────────────────────
# إنشاء اختصار
# ─────────────────────────────────────────────
log_info "إنشاء اختصار axon-project..."
cat > "${AXON_HOME}/bin/axon-project" << 'SHORTCUT'
#!/bin/bash
python3 "${HOME}/AxonOS/platform/core-services/project-manager/project_manager.py" "$@"
SHORTCUT
chmod +x "${AXON_HOME}/bin/axon-project"
log_success "اختصار axon-project جاهز"

# ─────────────────────────────────────────────
# حفظ حالة الاكتمال
# [إصلاح] جميع القيم محاطة بعلامات اقتباس
# ─────────────────────────────────────────────
total_projects="$(python3 -c "
import json, pathlib
f = pathlib.Path.home() / '.axon' / 'projects-index.json'
print(len(json.loads(f.read_text())) if f.exists() else 0)
" 2>/dev/null || echo "0")"

cat > "${STEP_DONE}" << EOF
completed="$(date '+%Y-%m-%dT%H:%M:%S')"
version="1.0"
python="$(python3 --version 2>&1 | cut -d' ' -f2)"
total_projects="${total_projects}"
EOF

log_success "✓ Project Manager مكتمل"
