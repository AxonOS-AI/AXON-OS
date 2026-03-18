# AxonOS/platform/gui/desktop-environment/taskbar.py
# ─────────────────────────────────────────────────────────────────
# Copyright (c) 2024 Abdullah — Axon OS Project
# Licensed under AGPL-3.0 (see LICENSE)
#
# PURPOSE: Axon OS taskbar (top panel).
#          Shows: app menu button | workspace switcher |
#                 [spacer] | resource meters | clock | tray
#
# NOTE: Visual design deferred. Structure is complete.
#       Colors/fonts will be applied in the final design phase.
# ─────────────────────────────────────────────────────────────────

import os
import sys
import datetime
import logging

PLATFORM_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PLATFORM_DIR)
sys.path.insert(0, os.path.join(PLATFORM_DIR, "core-services"))
sys.path.insert(0, os.path.join(PLATFORM_DIR, "core-services", "resource-manager"))

from config import AXON_NAME, TASKBAR_HEIGHT, LOG_DIR

log = logging.getLogger("axon.taskbar")

try:
    import gi
    gi.require_version("Gtk", "4.0")
    from gi.repository import Gtk, GLib
    GTK_AVAILABLE = True
except (ImportError, ValueError):
    GTK_AVAILABLE = False


class AxonTaskbar:
    """
    Top panel widget.

    Layout (left → right):
      [⬡ Axon] [WS1][WS2][WS3][WS4]  ----  [CPU xx%][RAM xx%] [HH:MM]
    """

    def __init__(self):
        self._resource_manager = None
        self._clock_label      = None
        self._cpu_label        = None
        self._ram_label        = None
        self.widget            = self._build()
        self._start_resource_monitor()
        if GTK_AVAILABLE:
            self._schedule_updates()

    def _build(self):
        if not GTK_AVAILABLE:
            return None

        # ── Root bar box ───────────────────────────────────────────
        bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        bar.set_size_request(-1, TASKBAR_HEIGHT)
        bar.set_margin_start(8)
        bar.set_margin_end(8)

        # ── Left: Axon menu button ─────────────────────────────────
        menu_btn = Gtk.Button(label=f"⬡ {AXON_NAME}")
        menu_btn.connect("clicked", self._on_menu_clicked)
        bar.append(menu_btn)

        # ── Left: Workspace switcher ───────────────────────────────
        ws_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        for i in range(1, 5):
            ws_btn = Gtk.ToggleButton(label=str(i))
            ws_btn.connect("clicked", self._on_workspace_clicked, i)
            ws_box.append(ws_btn)
        bar.append(ws_box)

        # ── Spacer ─────────────────────────────────────────────────
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        bar.append(spacer)

        # ── Right: Resource meters ─────────────────────────────────
        self._cpu_label = Gtk.Label(label="CPU --%")
        self._ram_label = Gtk.Label(label="RAM --%")
        bar.append(self._cpu_label)
        bar.append(self._ram_label)

        # ── Right: Clock ───────────────────────────────────────────
        self._clock_label = Gtk.Label(label="--:--")
        bar.append(self._clock_label)

        return bar

    def _start_resource_monitor(self):
        try:
            from resource_manager import ResourceManager
            self._resource_manager = ResourceManager()
            self._resource_manager.start()
            log.info("Resource monitor started from taskbar")
        except Exception as e:
            log.warning("Resource monitor unavailable: %s", e)

    def _schedule_updates(self):
        """Schedule periodic UI updates via GLib."""
        GLib.timeout_add_seconds(1,  self._update_clock)
        GLib.timeout_add_seconds(2,  self._update_resources)

    def _update_clock(self) -> bool:
        if self._clock_label:
            now = datetime.datetime.now()
            self._clock_label.set_text(now.strftime("%H:%M"))
        return True   # keep timer running

    def _update_resources(self) -> bool:
        if not self._resource_manager:
            return True
        try:
            snap = self._resource_manager.get_snapshot()
            if self._cpu_label:
                self._cpu_label.set_text(f"CPU {snap.cpu_percent:.0f}%")
            if self._ram_label:
                self._ram_label.set_text(f"RAM {snap.ram_percent:.0f}%")
        except Exception:
            pass
        return True

    def _on_menu_clicked(self, btn):
        log.info("Taskbar: menu clicked")

    def _on_workspace_clicked(self, btn, ws_number: int):
        log.info("Taskbar: workspace %d selected", ws_number)

    def get_clock_text(self) -> str:
        """For headless testing."""
        return datetime.datetime.now().strftime("%H:%M")
