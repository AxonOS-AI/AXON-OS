# AxonOS/platform/core-services/file-manager/file_manager.py
# ─────────────────────────────────────────────────────────────────
# Copyright (c) 2024 Abdullah — Axon OS Project
# Licensed under AGPL-3.0 (see LICENSE)
#
# PURPOSE: File system operations for Axon OS.
#          Scoped to user home + AxonProjects — never touches
#          system directories or Ubuntu Base paths.
#
# SAFETY RULE: All paths are validated against ALLOWED_ROOTS.
#              Any attempt to access /etc, /boot, /usr etc. raises
#              PermissionError — protecting the Ubuntu Base layer.
# ─────────────────────────────────────────────────────────────────

import os
import sys
import shutil
import mimetypes
import logging
from pathlib import Path
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import PROJECTS_DIR, DATA_DIR, LOG_DIR

logging.basicConfig(
    filename=os.path.join(LOG_DIR, "filemanager.log"),
    level=logging.INFO,
    format="%(asctime)s [FileMgr] %(levelname)s %(message)s"
)
log = logging.getLogger("axon.file_manager")

# Paths the file manager is allowed to operate inside
ALLOWED_ROOTS = [
    os.path.expanduser("~/AxonProjects"),
    os.path.expanduser("~/Documents"),
    os.path.expanduser("~/Downloads"),
    os.path.expanduser("~/Desktop"),
    DATA_DIR,
]


class FileManager:
    """
    Scoped file system operations for Axon OS.
    All methods enforce path safety before any disk operation.
    """

    # ── Safety ────────────────────────────────────────────────────
    def _safe(self, path: str) -> str:
        """
        Resolve path and verify it is inside an allowed root.
        Raises PermissionError if the path is outside allowed roots.
        This protects Ubuntu Base OS from accidental modification.
        """
        resolved = str(Path(path).resolve())
        for root in ALLOWED_ROOTS:
            if resolved.startswith(str(Path(root).resolve())):
                return resolved
        raise PermissionError(
            f"Axon OS File Manager: path '{path}' is outside allowed directories.\n"
            f"Allowed roots: {ALLOWED_ROOTS}\n"
            f"This restriction protects the Ubuntu Base OS."
        )

    # ── List ──────────────────────────────────────────────────────
    def list_dir(self, path: str) -> list[dict]:
        """
        List directory contents.
        Returns list of dicts with: name, path, type, size, modified.
        """
        safe_path = self._safe(path)
        entries = []
        try:
            for entry in os.scandir(safe_path):
                stat = entry.stat(follow_symlinks=False)
                entries.append({
                    "name":     entry.name,
                    "path":     entry.path,
                    "type":     "directory" if entry.is_dir() else "file",
                    "size":     stat.st_size,
                    "modified": stat.st_mtime,
                    "mime":     mimetypes.guess_type(entry.name)[0] or "unknown"
                })
        except PermissionError as e:
            log.warning("list_dir permission denied: %s", e)
        return sorted(entries, key=lambda x: (x["type"] == "file", x["name"].lower()))

    # ── Read ──────────────────────────────────────────────────────
    def read_text(self, path: str, max_bytes: int = 1024 * 1024) -> str:
        """Read a text file (max 1MB by default)."""
        safe_path = self._safe(path)
        with open(safe_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read(max_bytes)

    # ── Write ─────────────────────────────────────────────────────
    def write_text(self, path: str, content: str) -> bool:
        """Write text to a file, creating parent directories as needed."""
        safe_path = self._safe(path)
        os.makedirs(os.path.dirname(safe_path), exist_ok=True)
        with open(safe_path, "w", encoding="utf-8") as f:
            f.write(content)
        log.info("write_text: %s (%d bytes)", safe_path, len(content))
        return True

    # ── Copy ──────────────────────────────────────────────────────
    def copy(self, src: str, dst: str) -> str:
        safe_src = self._safe(src)
        safe_dst = self._safe(dst)
        if os.path.isdir(safe_src):
            shutil.copytree(safe_src, safe_dst)
        else:
            os.makedirs(os.path.dirname(safe_dst), exist_ok=True)
            shutil.copy2(safe_src, safe_dst)
        log.info("copy: %s → %s", safe_src, safe_dst)
        return safe_dst

    # ── Move ──────────────────────────────────────────────────────
    def move(self, src: str, dst: str) -> str:
        safe_src = self._safe(src)
        safe_dst = self._safe(dst)
        shutil.move(safe_src, safe_dst)
        log.info("move: %s → %s", safe_src, safe_dst)
        return safe_dst

    # ── Delete ────────────────────────────────────────────────────
    def delete(self, path: str) -> bool:
        safe_path = self._safe(path)
        if os.path.isdir(safe_path):
            shutil.rmtree(safe_path)
        else:
            os.remove(safe_path)
        log.info("delete: %s", safe_path)
        return True

    # ── Create Directory ──────────────────────────────────────────
    def mkdir(self, path: str) -> str:
        safe_path = self._safe(path)
        os.makedirs(safe_path, exist_ok=True)
        return safe_path

    # ── Info ──────────────────────────────────────────────────────
    def info(self, path: str) -> Optional[dict]:
        safe_path = self._safe(path)
        if not os.path.exists(safe_path):
            return None
        stat = os.stat(safe_path)
        return {
            "path":     safe_path,
            "name":     os.path.basename(safe_path),
            "type":     "directory" if os.path.isdir(safe_path) else "file",
            "size":     stat.st_size,
            "modified": stat.st_mtime,
            "mime":     mimetypes.guess_type(safe_path)[0] or "unknown"
        }

    # ── Search ────────────────────────────────────────────────────
    def search(self, root: str, query: str,
               max_results: int = 50) -> list[dict]:
        """Simple recursive filename search inside allowed root."""
        safe_root = self._safe(root)
        results   = []
        query_l   = query.lower()
        for dirpath, dirnames, filenames in os.walk(safe_root):
            # Skip hidden directories
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
            for fname in filenames:
                if query_l in fname.lower():
                    full_path = os.path.join(dirpath, fname)
                    results.append(self.info(full_path))
                    if len(results) >= max_results:
                        return results
        return results


# ── CLI Test ──────────────────────────────────────────────────────
if __name__ == "__main__":
    fm = FileManager()
    entries = fm.list_dir(os.path.expanduser("~/AxonProjects"))
    print(f"AxonProjects: {len(entries)} entries")

    # Test safety guard
    try:
        fm.list_dir("/etc")
        print("ERROR: should have raised PermissionError")
    except PermissionError as e:
        print(f"✓ Safety guard working: {str(e)[:80]}")
