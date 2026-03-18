# AxonOS/platform/gui/desktop-environment/window_manager.py
# ─────────────────────────────────────────────────────────────────
# Copyright (c) 2024 Abdullah — Axon OS Project
# Licensed under AGPL-3.0 (see LICENSE)
#
# PURPOSE: Workspace management for Axon OS Desktop.
#          Manages multiple workspaces and the apps inside them.
#          Acts as the container that fills the area below the taskbar.
# ─────────────────────────────────────────────────────────────────

import os
import sys
import logging

PLATFORM_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PLATFORM_DIR)
from config import DEFAULT_WORKSPACE_COUNT, LOG_DIR

log = logging.getLogger("axon.window_manager")

try:
    import gi
    gi.require_version("Gtk", "4.0")
    from gi.repository import Gtk
    GTK_AVAILABLE = True
except (ImportError, ValueError):
    GTK_AVAILABLE = False


class Workspace:
    """A single virtual workspace containing a GTK Stack page."""

    def __init__(self, index: int, stack: "Gtk.Stack"):
        self.index    = index
        self.name     = f"workspace-{index}"
        self._stack   = stack
        self._box     = Gtk.Box(orientation=Gtk.Orientation.VERTICAL) if GTK_AVAILABLE else None
        if GTK_AVAILABLE:
            self._stack.add_titled(self._box, self.name, f"WS {index}")

    def add_widget(self, widget) -> None:
        if self._box:
            self._box.append(widget)

    def activate(self) -> None:
        if self._stack:
            self._stack.set_visible_child_name(self.name)
        log.info("Workspace %d activated", self.index)


class AxonWindowManager:
    """
    Manages workspaces and widget placement.

    Structure:
      GTK Stack (one page per workspace)
        └── Workspace 1..N
              └── app widgets placed here
    """

    def __init__(self):
        self._stack      = None
        self._workspaces = []
        self._active_ws  = 1
        self.widget      = self._build()

    def _build(self):
        if not GTK_AVAILABLE:
            return None

        # Overlay allows floating widgets over the workspace
        overlay = Gtk.Overlay()

        # Stack holds one page per workspace
        self._stack = Gtk.Stack()
        self._stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self._stack.set_hexpand(True)
        self._stack.set_vexpand(True)
        overlay.set_child(self._stack)

        # Create workspaces
        for i in range(1, DEFAULT_WORKSPACE_COUNT + 1):
            ws = Workspace(i, self._stack)
            self._workspaces.append(ws)

        # Activate first workspace
        if self._workspaces:
            self._workspaces[0].activate()

        return overlay

    def switch_to(self, workspace_index: int) -> None:
        idx = workspace_index - 1
        if 0 <= idx < len(self._workspaces):
            self._workspaces[idx].activate()
            self._active_ws = workspace_index

    def get_active_workspace(self) -> int:
        return self._active_ws

    def workspace_count(self) -> int:
        return len(self._workspaces)
