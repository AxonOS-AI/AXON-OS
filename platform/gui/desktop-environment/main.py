# AxonOS/platform/gui/desktop-environment/main.py
# ─────────────────────────────────────────────────────────────────
# Copyright (c) 2024 Abdullah — Axon OS Project
# Licensed under AGPL-3.0 (see LICENSE)
#
# PURPOSE: Entry point for the Axon OS Desktop Environment.
#          Initializes all core services, then launches the
#          GTK4 shell (taskbar + desktop workspace).
#
# NOTE:  Visual design (colors, fonts, themes) is deferred to
#        the final phase. This phase builds the structure and
#        service wiring. The shell will run with default GTK
#        styling until the design phase.
#
# DEPENDENCIES:
#   sudo apt install python3-gi gir1.2-gtk-4.0
#   pip install psutil
#
# RUN:
#   python3 main.py
# ─────────────────────────────────────────────────────────────────

import os
import sys
import logging

# ── Path setup ────────────────────────────────────────────────────
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PLATFORM_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))
ROOT_DIR     = os.path.dirname(PLATFORM_DIR)
sys.path.insert(0, PLATFORM_DIR)
sys.path.insert(0, os.path.join(PLATFORM_DIR, "core-services"))

from config import LOG_DIR, AXON_NAME, AXON_VERSION

logging.basicConfig(
    filename=os.path.join(LOG_DIR, "desktop.log"),
    level=logging.INFO,
    format="%(asctime)s [Desktop] %(levelname)s %(message)s"
)
log = logging.getLogger("axon.desktop")

# ── Bootstrap core services ───────────────────────────────────────
try:
    from core_services_init import bootstrap
    bootstrap()
    log.info("Core services bootstrapped")
except Exception as e:
    log.error("Core services bootstrap failed: %s", e)

# ── Import sub-modules ────────────────────────────────────────────
from taskbar      import AxonTaskbar
from window_manager import AxonWindowManager
from launcher     import AxonLauncher

# ── GTK4 ──────────────────────────────────────────────────────────
try:
    import gi
    gi.require_version("Gtk", "4.0")
    gi.require_version("Gdk", "4.0")
    from gi.repository import Gtk, Gdk, GLib
    GTK_AVAILABLE = True
except (ImportError, ValueError):
    GTK_AVAILABLE = False
    log.warning("GTK4 not available — running in headless/test mode")


# ═══════════════════════════════════════════════════════════════════
class AxonDesktop(Gtk.Application if GTK_AVAILABLE else object):
    """
    Main Axon OS Desktop Application.

    Structure:
      AxonDesktop
        ├── AxonTaskbar       (top bar: clock, resources, tray)
        ├── AxonWindowManager (workspace / window stacking)
        └── AxonLauncher      (app grid, search)
    """

    APP_ID = "com.axon.desktop"

    def __init__(self):
        if GTK_AVAILABLE:
            super().__init__(application_id=self.APP_ID)
            self.connect("activate", self._on_activate)
        self._taskbar        = None
        self._window_manager = None
        self._launcher       = None

    def _on_activate(self, app):
        log.info("Axon Desktop activating...")
        self._build_shell(app)

    def _build_shell(self, app):
        """
        Construct the desktop shell components.
        Visual styling intentionally minimal — design deferred.
        """
        # Main window (full screen desktop layer)
        win = Gtk.ApplicationWindow(application=app)
        win.set_title(f"{AXON_NAME} {AXON_VERSION}")
        win.set_default_size(1920, 1080)

        # Root vertical box: [taskbar][workspace]
        root_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        win.set_child(root_box)

        # ── Taskbar (top) ──────────────────────────────────────────
        self._taskbar = AxonTaskbar()
        root_box.append(self._taskbar.widget)

        # ── Workspace area ─────────────────────────────────────────
        self._window_manager = AxonWindowManager()
        root_box.append(self._window_manager.widget)

        # ── Launcher (overlay — shown on hotkey) ───────────────────
        self._launcher = AxonLauncher(parent_win=win)

        win.present()
        log.info("Desktop shell built and presented")

    def launch(self):
        """Start the GTK main loop."""
        if GTK_AVAILABLE:
            self.run(None)
        else:
            self._headless_test()

    def _headless_test(self):
        """Runs service checks without GUI (for CI / verify scripts)."""
        print("[Axon Desktop] Running in headless test mode")
        print(f"  ✓ {AXON_NAME} v{AXON_VERSION}")

        # Test resource manager
        try:
            sys.path.insert(0, os.path.join(PLATFORM_DIR, "core-services", "resource-manager"))
            from resource_manager import ResourceManager
            rm = ResourceManager()
            rm.start()
            import time; time.sleep(3)
            print(f"  ✓ Resources:\n{rm.summary()}")
            rm.stop()
        except Exception as e:
            print(f"  ⚠ Resource manager: {e}")

        # Test project manager
        try:
            sys.path.insert(0, os.path.join(PLATFORM_DIR, "core-services", "project-manager"))
            from project_manager import ProjectManager
            pm = ProjectManager()
            projects = pm.list_all()
            print(f"  ✓ Projects loaded: {len(projects)}")
        except Exception as e:
            print(f"  ⚠ Project manager: {e}")

        print("[Axon Desktop] Headless test complete")


# ── Entry ─────────────────────────────────────────────────────────
def main():
    app = AxonDesktop()
    app.launch()


if __name__ == "__main__":
    main()
