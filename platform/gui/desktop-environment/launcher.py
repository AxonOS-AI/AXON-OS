# AxonOS/platform/gui/desktop-environment/launcher.py
# ─────────────────────────────────────────────────────────────────
# Copyright (c) 2024 Abdullah — Axon OS Project
# Licensed under AGPL-3.0 (see LICENSE)
#
# PURPOSE: Axon OS app launcher.
#          Shows a grid of available Axon tools + search bar.
#          Triggered by the "⬡ Axon" taskbar button or Super key.
#
# NOTE: Visual design deferred. Structure complete.
# ─────────────────────────────────────────────────────────────────

import os
import sys
import logging

PLATFORM_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PLATFORM_DIR)
from config import LOG_DIR, AXON_NAME

log = logging.getLogger("axon.launcher")

try:
    import gi
    gi.require_version("Gtk", "4.0")
    from gi.repository import Gtk, Gdk
    GTK_AVAILABLE = True
except (ImportError, ValueError):
    GTK_AVAILABLE = False


# ── Built-in Axon Apps registry ───────────────────────────────────
# Each entry: (display_name, icon_char, launch_key)
# launch_key maps to the actual module to open (Phase 3+)
AXON_APPS = [
    ("Dashboard",       "📊", "dashboard"),
    ("Project Manager", "📁", "project_manager"),
    ("File Manager",    "🗂", "file_manager"),
    ("Training Console","🤖", "training_console"),
    ("Resource Monitor","📈", "resource_monitor"),
    ("Update Manager",  "🔄", "update_service"),
    ("Settings",        "⚙",  "settings"),
    ("Terminal",        "⬛", "terminal"),
]


class AxonLauncher:
    """
    Full-screen overlay launcher.
    Opens over the desktop when the user clicks ⬡ Axon or presses Super.
    """

    def __init__(self, parent_win=None):
        self._parent  = parent_win
        self._visible = False
        self._window  = None
        if GTK_AVAILABLE and parent_win:
            self._build(parent_win)

    def _build(self, parent_win):
        self._window = Gtk.Window()
        self._window.set_title(f"{AXON_NAME} Launcher")
        self._window.set_transient_for(parent_win)
        self._window.set_modal(True)
        self._window.set_default_size(800, 600)

        # ── Root vertical layout ───────────────────────────────────
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        root.set_margin_top(32)
        root.set_margin_bottom(32)
        root.set_margin_start(32)
        root.set_margin_end(32)
        self._window.set_child(root)

        # ── Search bar ─────────────────────────────────────────────
        self._search = Gtk.SearchEntry()
        self._search.set_placeholder_text("Search apps...")
        self._search.connect("search-changed", self._on_search)
        root.append(self._search)

        # ── App grid ───────────────────────────────────────────────
        self._grid = Gtk.FlowBox()
        self._grid.set_max_children_per_line(4)
        self._grid.set_selection_mode(Gtk.SelectionMode.NONE)
        self._grid.set_homogeneous(True)
        root.append(self._grid)

        self._populate_grid(AXON_APPS)

        # Close on Escape
        key_ctrl = Gtk.EventControllerKey()
        key_ctrl.connect("key-pressed", self._on_key)
        self._window.add_controller(key_ctrl)

    def _make_app_button(self, name: str, icon: str, key: str) -> Gtk.Widget:
        btn = Gtk.Button()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_margin_top(12)
        box.set_margin_bottom(12)

        lbl_icon = Gtk.Label(label=icon)
        lbl_name = Gtk.Label(label=name)
        lbl_name.set_wrap(True)
        lbl_name.set_justify(Gtk.Justification.CENTER)

        box.append(lbl_icon)
        box.append(lbl_name)
        btn.set_child(box)
        btn.connect("clicked", self._on_app_clicked, key, name)
        return btn

    def _populate_grid(self, apps: list) -> None:
        if not GTK_AVAILABLE:
            return
        # Remove existing children
        child = self._grid.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self._grid.remove(child)
            child = next_child
        # Add filtered apps
        for name, icon, key in apps:
            btn = self._make_app_button(name, icon, key)
            self._grid.append(btn)

    def _on_search(self, entry) -> None:
        query = entry.get_text().lower()
        filtered = [a for a in AXON_APPS if query in a[0].lower()] if query else AXON_APPS
        self._populate_grid(filtered)

    def _on_app_clicked(self, btn, key: str, name: str) -> None:
        log.info("Launcher: launching '%s' (key=%s)", name, key)
        self.hide()
        # Phase 3 will implement actual app opening here

    def _on_key(self, ctrl, keyval, keycode, state) -> bool:
        if GTK_AVAILABLE:
            from gi.repository import Gdk
            if keyval == Gdk.KEY_Escape:
                self.hide()
                return True
        return False

    def show(self) -> None:
        if self._window:
            self._window.present()
            self._visible = True

    def hide(self) -> None:
        if self._window:
            self._window.hide()
            self._visible = False

    def toggle(self) -> None:
        if self._visible:
            self.hide()
        else:
            self.show()

    def get_app_names(self) -> list[str]:
        """For headless testing."""
        return [a[0] for a in AXON_APPS]
