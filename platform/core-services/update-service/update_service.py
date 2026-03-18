# AxonOS/platform/core-services/update-service/update_service.py
# ─────────────────────────────────────────────────────────────────
# Copyright (c) 2024 Abdullah — Axon OS Project
# Licensed under AGPL-3.0 (see LICENSE)
#
# PURPOSE: Checks GitHub for new Axon OS releases.
#          Notifies the desktop when an update is available.
#          Downloads and applies updates to Platform Layer ONLY.
#          NEVER modifies Ubuntu Base OS.
#
# RULES (from architecture):
#   ✓ May update: platform/, ai-container/, scripts/
#   ✗ Must NOT touch: /boot/grub, /etc/*, kernel, Ubuntu packages
# ─────────────────────────────────────────────────────────────────

import os
import sys
import json
import logging
import threading
import time
import subprocess
from typing import Optional, Callable

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import (
    AXON_VERSION, UPDATE_CHECK_URL,
    UPDATE_INTERVAL_H, LOG_DIR, ROOT_DIR
)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, "updates.log"),
    level=logging.INFO,
    format="%(asctime)s [UpdateSvc] %(levelname)s %(message)s"
)
log = logging.getLogger("axon.update_service")


class UpdateResult:
    """Holds the result of an update check."""
    def __init__(self):
        self.available    = False
        self.current      = AXON_VERSION
        self.latest       = AXON_VERSION
        self.release_url  = ""
        self.release_notes = ""
        self.error        = None

    def __repr__(self):
        if self.error:
            return f"UpdateResult(error={self.error})"
        if self.available:
            return f"UpdateResult({self.current} → {self.latest})"
        return f"UpdateResult(up-to-date @ {self.current})"


class UpdateService:
    """
    Handles update checking and applying for Axon OS Platform Layer.

    Usage:
        svc = UpdateService(on_update_available=my_callback)
        svc.start_background_checker()   # runs every UPDATE_INTERVAL_H hours
        # OR
        result = svc.check_now()         # manual check
    """

    def __init__(self, on_update_available: Optional[Callable] = None):
        self._callback = on_update_available
        self._running  = False
        self._thread   = None
        self._last_result: Optional[UpdateResult] = None

    # ── Check ─────────────────────────────────────────────────────
    def check_now(self) -> UpdateResult:
        """
        Query GitHub API for latest release.
        Returns UpdateResult. Never raises.
        """
        result = UpdateResult()
        try:
            import urllib.request
            req = urllib.request.Request(
                UPDATE_CHECK_URL,
                headers={"User-Agent": f"AxonOS/{AXON_VERSION}"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())

            latest_tag = data.get("tag_name", "").lstrip("v")
            result.latest       = latest_tag
            result.release_url  = data.get("html_url", "")
            result.release_notes = data.get("body", "")[:500]
            result.available    = self._is_newer(latest_tag, AXON_VERSION)

            self._last_result = result
            log.info("Check complete: current=%s latest=%s available=%s",
                     AXON_VERSION, latest_tag, result.available)

            if result.available and self._callback:
                self._callback(result)

        except Exception as e:
            result.error = str(e)
            log.warning("Update check failed: %s", e)

        return result

    def _is_newer(self, latest: str, current: str) -> bool:
        """Compare semver strings — returns True if latest > current."""
        def to_tuple(v: str):
            try:
                return tuple(int(x) for x in v.split("."))
            except Exception:
                return (0, 0, 0)
        return to_tuple(latest) > to_tuple(current)

    # ── Apply ─────────────────────────────────────────────────────
    def apply_update(self, result: UpdateResult) -> bool:
        """
        Pull latest changes from GitHub via git.
        Only updates Axon files — never touches Ubuntu Base.

        SAFETY CHECKS before running:
          1. Must be a git repository
          2. Must only update allowed paths
          3. Logs everything to update history
        """
        if not result.available:
            log.info("No update to apply")
            return False

        # Verify git is initialized
        git_dir = os.path.join(ROOT_DIR, ".git")
        if not os.path.isdir(git_dir):
            log.error("Cannot update: not a git repository at %s", ROOT_DIR)
            return False

        log.info("Applying update: %s → %s", AXON_VERSION, result.latest)

        try:
            # Pull only Axon-managed directories
            allowed_paths = ["platform/", "ai-container/", "scripts/", "docs/"]
            cmd = ["git", "-C", ROOT_DIR, "pull", "origin", "main",
                   "--", *allowed_paths]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if proc.returncode == 0:
                self._record_update(result.latest, "success", result.release_notes)
                log.info("Update applied successfully: %s", result.latest)
                return True
            else:
                self._record_update(result.latest, "failed", proc.stderr[:200])
                log.error("Update failed: %s", proc.stderr)
                return False

        except subprocess.TimeoutExpired:
            log.error("Update timed out")
            return False
        except Exception as e:
            log.error("Update error: %s", e)
            return False

    def _record_update(self, version: str, status: str, notes: str):
        try:
            sys.path.insert(0, os.path.join(ROOT_DIR, "platform", "core-services"))
            from db_manager import get_connection
            conn = get_connection()
            conn.execute(
                "INSERT INTO update_history (version, status, notes) VALUES (?,?,?)",
                (version, status, notes[:500])
            )
            conn.commit()
            conn.close()
        except Exception as e:
            log.warning("Could not record update history: %s", e)

    # ── Background Checker ────────────────────────────────────────
    def _loop(self):
        while self._running:
            self.check_now()
            time.sleep(UPDATE_INTERVAL_H * 3600)

    def start_background_checker(self):
        if self._running:
            return
        self._running = True
        self._thread  = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        log.info("Background update checker started (every %dh)", UPDATE_INTERVAL_H)

    def stop(self):
        self._running = False


# ── Systemd Service File ──────────────────────────────────────────
SYSTEMD_UNIT = """\
[Unit]
Description=Axon OS Update Service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 {path}/platform/core-services/update-service/update_service.py
Restart=on-failure
RestartSec=60
User={user}
Environment=PYTHONPATH={path}

[Install]
WantedBy=multi-user.target
"""


def generate_systemd_unit(install_path: str, username: str) -> str:
    return SYSTEMD_UNIT.format(path=install_path, user=username)


# ── CLI Test ──────────────────────────────────────────────────────
if __name__ == "__main__":
    def on_update(r):
        print(f"🔔 Update available: {r.current} → {r.latest}")
        print(f"   Release notes: {r.release_notes[:100]}...")

    svc = UpdateService(on_update_available=on_update)
    result = svc.check_now()
    print(result)
