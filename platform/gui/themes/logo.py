# AxonOS/platform/gui/themes/logo.py
# ─────────────────────────────────────────────────────────────────
# Copyright (c) 2024 Abdullah — Axon OS Project (AGPL-3.0)
# Purpose: Animated Axon OS logo renderer using Cairo + GTK4.
#          Draws: processor body + Ax text + 12 neural nodes
#                 + 6 inner nodes + flowing pulses.
#          Works in both Dark and Light themes.
# Usage:   logo = AxonLogo(size=120, dark=True)
#          drawing_area.set_draw_func(logo.draw)
#          GLib.timeout_add(33, logo.tick_and_redraw, drawing_area)
# ─────────────────────────────────────────────────────────────────

import os
import sys
import math
import time
import logging
from typing import Optional

log = logging.getLogger("axon.logo")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from colors import AxonDark, AxonLight, hex_to_rgba

try:
    import gi
    gi.require_version("Gtk", "4.0")
    from gi.repository import Gtk, GLib
    import cairo
    GTK_OK = True
except (ImportError, ValueError):
    GTK_OK = False
    log.warning("GTK4/Cairo not available — logo in headless mode")


class AxonLogo:
    """
    Animated Axon OS logo.

    Features:
    - Processor body with pins (flashing activity)
    - 'Ax' text in center
    - 12 outer neural nodes orbiting
    - 6 inner nodes orbiting counter-direction
    - Flowing pulses on connections
    - Pulse rings expanding from center
    - Adapts colors to Dark / Light theme
    """

    def __init__(self, size: int = 120, dark: bool = True,
                 speed: float = 1.0):
        self.size  = size
        self.dark  = dark
        self.speed = speed
        self._t    = 0.0
        self._start = time.time()

        # Apply theme colors
        self._apply_theme(dark)

        # Neural network nodes
        self._outer = self._make_nodes(12, radius_ratio=0.40, speed=0.006)
        self._inner = self._make_nodes(6,  radius_ratio=0.25, speed=0.004,
                                       offset=math.pi/6, reverse=True)

        # Connection pairs between outer nodes
        self._conns = [
            (0,2),(1,5),(2,8),(3,7),(4,10),(5,11),
            (6,9),(7,1),(8,4),(9,3),(10,6),(11,0),
        ]

        # Flowing pulses
        import random
        random.seed(42)
        self._pulses = [
            {
                "conn": c,
                "pos":  random.random(),
                "speed": 0.005 + random.random() * 0.007,
            }
            for c in self._conns
        ]

    def _apply_theme(self, dark: bool) -> None:
        """Set color tuples (r, g, b, a) for current theme."""
        if dark:
            self.col_cyan      = hex_to_rgba("#00D4FF", 1.0)
            self.col_cyan_dim  = hex_to_rgba("#00D4FF", 0.25)
            self.col_cyan_glow = hex_to_rgba("#00D4FF", 0.08)
            self.col_purple    = hex_to_rgba("#6C3CE1", 0.80)
            self.col_panel     = hex_to_rgba("#050812", 0.97)
            self.col_pin_hi    = hex_to_rgba("#00D4FF", 0.90)
            self.col_pin_lo    = hex_to_rgba("#00D4FF", 0.25)
            self.col_conn      = hex_to_rgba("#00D4FF", 0.08)
            self.col_inner_ln  = hex_to_rgba("#6C3CE1", 0.12)
        else:
            self.col_cyan      = hex_to_rgba("#0064C8", 1.0)
            self.col_cyan_dim  = hex_to_rgba("#0064C8", 0.22)
            self.col_cyan_glow = hex_to_rgba("#0064C8", 0.07)
            self.col_purple    = hex_to_rgba("#5230B0", 0.75)
            self.col_panel     = hex_to_rgba("#F0F2F5", 0.97)
            self.col_pin_hi    = hex_to_rgba("#0064C8", 0.85)
            self.col_pin_lo    = hex_to_rgba("#0064C8", 0.20)
            self.col_conn      = hex_to_rgba("#0064C8", 0.07)
            self.col_inner_ln  = hex_to_rgba("#5230B0", 0.10)

    def set_theme(self, dark: bool) -> None:
        """Switch theme at runtime."""
        self.dark = dark
        self._apply_theme(dark)

    def _make_nodes(self, count: int, radius_ratio: float,
                    speed: float, offset: float = 0.0,
                    reverse: bool = False) -> list:
        import random
        nodes = []
        for i in range(count):
            angle = i * (math.pi * 2 / count) + offset
            nodes.append({
                "a":     angle,
                "r":     radius_ratio,
                "pulse": random.uniform(0, math.pi * 2),
                "speed": speed + random.uniform(0, speed * 0.5),
                "rev":   reverse,
            })
        return nodes

    def _node_pos(self, node: dict, cx: float, cy: float,
                  radius: float) -> tuple:
        """Return (x, y) of a node at current time."""
        direction = -1 if node["rev"] else 1
        angle = node["a"] + direction * self._t * self.speed * node["speed"] * 60
        r = node["r"] * radius
        return cx + math.cos(angle) * r, cy + math.sin(angle) * r

    # ── Main draw function ────────────────────────────────────────

    def draw(self, area, cr: "cairo.Context", w: int, h: int) -> None:
        """
        GTK4 DrawingArea draw function.
        Connect with: drawing_area.set_draw_func(logo.draw)
        """
        self._render(cr, w, h)

    def _render(self, cr: "cairo.Context", w: int, h: int) -> None:
        cx, cy = w / 2, h / 2
        radius = min(w, h) / 2 * 0.92
        ps     = radius * 0.30   # processor half-size

        # ── Connection lines (outer) ──────────────────────────────
        for a_idx, b_idx in self._conns:
            ax, ay = self._node_pos(self._outer[a_idx], cx, cy, radius)
            bx, by = self._node_pos(self._outer[b_idx], cx, cy, radius)
            cr.set_source_rgba(*self.col_conn)
            cr.set_line_width(0.5)
            cr.move_to(ax, ay)
            cr.line_to(bx, by)
            cr.stroke()

        # ── Inner node connections ────────────────────────────────
        prev = None
        for node in self._inner:
            x, y = self._node_pos(node, cx, cy, radius)
            if prev:
                cr.set_source_rgba(*self.col_inner_ln)
                cr.set_line_width(0.4)
                cr.move_to(*prev)
                cr.line_to(x, y)
                cr.stroke()
                # inner to center
                cr.set_source_rgba(*self.col_inner_ln)
                cr.move_to(x, y)
                cr.line_to(cx, cy)
                cr.stroke()
            prev = (x, y)
        # close inner ring
        if self._inner:
            x0, y0 = self._node_pos(self._inner[0], cx, cy, radius)
            xn, yn = self._node_pos(self._inner[-1], cx, cy, radius)
            cr.set_source_rgba(*self.col_inner_ln)
            cr.set_line_width(0.4)
            cr.move_to(xn, yn)
            cr.line_to(x0, y0)
            cr.stroke()

        # ── Flowing pulses ────────────────────────────────────────
        for p in self._pulses:
            p["pos"] += p["speed"] * self.speed
            if p["pos"] > 1.0:
                p["pos"] = 0.0
            a_idx, b_idx = p["conn"]
            ax, ay = self._node_pos(self._outer[a_idx], cx, cy, radius)
            bx, by = self._node_pos(self._outer[b_idx], cx, cy, radius)
            px = ax + (bx - ax) * p["pos"]
            py = ay + (by - ay) * p["pos"]
            cr.set_source_rgba(*self.col_cyan)
            cr.arc(px, py, radius * 0.018, 0, math.pi * 2)
            cr.fill()

        # ── Outer neural nodes ────────────────────────────────────
        for node in self._outer:
            node["pulse"] += node["speed"] * self.speed * 2
            glow = 0.4 + 0.4 * math.sin(node["pulse"])
            x, y = self._node_pos(node, cx, cy, radius)
            # glow ring
            r_glow = radius * 0.045
            cr.set_source_rgba(*self.col_cyan[:3], glow * 0.20)
            cr.arc(x, y, r_glow, 0, math.pi * 2)
            cr.fill()
            # core dot
            cr.set_source_rgba(*self.col_cyan[:3], 0.5 + glow * 0.5)
            cr.arc(x, y, radius * 0.024, 0, math.pi * 2)
            cr.fill()

        # ── Inner nodes ───────────────────────────────────────────
        for node in self._inner:
            node["pulse"] += node["speed"] * self.speed * 2.5
            glow = 0.4 + 0.4 * math.sin(node["pulse"])
            x, y = self._node_pos(node, cx, cy, radius)
            cr.set_source_rgba(*self.col_purple[:3], 0.5 + glow * 0.4)
            cr.arc(x, y, radius * 0.028, 0, math.pi * 2)
            cr.fill()

        # ── Pulse rings ───────────────────────────────────────────
        for i in range(3):
            phase = self._t * self.speed * 0.04 + i * math.pi * 2 / 3
            ring_r = ps * 0.55 + i * ps * 0.35 + ps * 0.08 * math.sin(phase)
            ring_a = 0.06 + 0.04 * math.sin(phase)
            cr.set_source_rgba(*self.col_cyan[:3], ring_a)
            cr.set_line_width(0.8)
            cr.arc(cx, cy, ring_r, 0, math.pi * 2)
            cr.stroke()

        # ── Processor body ────────────────────────────────────────
        self._draw_processor(cr, cx, cy, ps)

        # Advance time
        self._t += 1.0

    def _draw_processor(self, cr, cx: float, cy: float, ps: float) -> None:
        """Draw the central processor with pins and 'Ax' text."""

        # Body shadow glow
        cr.set_source_rgba(*self.col_cyan[:3], 0.18)
        self._rounded_rect(cr, cx - ps - 2, cy - ps - 2,
                           (ps + 2) * 2, (ps + 2) * 2, ps * 0.18)
        cr.fill()

        # Body fill
        cr.set_source_rgba(*self.col_panel)
        self._rounded_rect(cr, cx - ps, cy - ps, ps * 2, ps * 2, ps * 0.16)
        cr.fill()

        # Body border
        cr.set_source_rgba(*self.col_cyan)
        cr.set_line_width(1.8)
        self._rounded_rect(cr, cx - ps, cy - ps, ps * 2, ps * 2, ps * 0.16)
        cr.stroke()

        # Inner die
        die = ps * 0.65
        cr.set_source_rgba(*self.col_purple[:3], 0.35)
        cr.set_line_width(0.8)
        self._rounded_rect(cr, cx - die, cy - die, die * 2, die * 2, ps * 0.10)
        cr.stroke()

        # Grid lines inside
        for off in [-ps * 0.28, 0.0, ps * 0.28]:
            cr.set_source_rgba(*self.col_cyan[:3], 0.09)
            cr.set_line_width(0.6)
            cr.move_to(cx + off, cy - ps + ps * 0.24)
            cr.line_to(cx + off, cy + ps - ps * 0.24)
            cr.stroke()
            cr.move_to(cx - ps + ps * 0.24, cy + off)
            cr.line_to(cx + ps - ps * 0.24, cy + off)
            cr.stroke()

        # Pins (4 sides, 4 pins each)
        pin_offsets = [-ps * 0.48, -ps * 0.18, ps * 0.18, ps * 0.48]
        pin_len     = ps * 0.30

        for off in pin_offsets:
            flash = math.sin(self._t * 0.06 + off) > 0.75
            col   = self.col_pin_hi if flash else self.col_pin_lo
            cr.set_source_rgba(*col)
            cr.set_line_width(1.3)
            # top
            cr.move_to(cx + off, cy - ps)
            cr.line_to(cx + off, cy - ps - pin_len)
            cr.stroke()
            # bottom
            cr.move_to(cx + off, cy + ps)
            cr.line_to(cx + off, cy + ps + pin_len)
            cr.stroke()
            # left
            cr.move_to(cx - ps, cy + off)
            cr.line_to(cx - ps - pin_len, cy + off)
            cr.stroke()
            # right
            cr.move_to(cx + ps, cy + off)
            cr.line_to(cx + ps + pin_len, cy + off)
            cr.stroke()

        # 'Ax' text
        font_size = ps * 0.65
        cr.set_source_rgba(*self.col_cyan)
        cr.select_font_face("Courier New",
                            cairo.FONT_SLANT_NORMAL if GTK_OK else 0,
                            cairo.FONT_WEIGHT_BOLD  if GTK_OK else 1)
        cr.set_font_size(font_size)
        extents = cr.text_extents("Ax")
        tx = cx - extents.width  / 2 - extents.x_bearing
        ty = cy - extents.height / 2 - extents.y_bearing
        cr.move_to(tx, ty)
        cr.show_text("Ax")

    def _rounded_rect(self, cr, x: float, y: float,
                      w: float, h: float, r: float) -> None:
        """Draw a rounded rectangle path."""
        cr.new_sub_path()
        cr.arc(x + r,     y + r,     r, math.pi,       math.pi * 1.5)
        cr.arc(x + w - r, y + r,     r, math.pi * 1.5, 0)
        cr.arc(x + w - r, y + h - r, r, 0,              math.pi * 0.5)
        cr.arc(x + r,     y + h - r, r, math.pi * 0.5, math.pi)
        cr.close_path()

    # ── GTK4 helpers ──────────────────────────────────────────────

    def tick_and_redraw(self, area) -> bool:
        """
        GLib timer callback — call every 33ms (~30fps).
        Returns True to keep the timer alive.
        """
        area.queue_draw()
        return True

    def create_widget(self, size: Optional[int] = None) -> "Gtk.DrawingArea":
        """Create and return a GTK4 DrawingArea with this logo."""
        if not GTK_OK:
            log.error("GTK4 not available")
            return None
        s = size or self.size
        area = Gtk.DrawingArea()
        area.set_size_request(s, s)
        area.set_draw_func(self.draw)
        GLib.timeout_add(33, self.tick_and_redraw, area)
        return area


# ── Convenience factory ───────────────────────────────────────────

def make_logo_widget(size: int = 120, dark: bool = True) -> "Gtk.DrawingArea":
    """Shortcut: create a logo widget ready to embed in any GTK4 layout."""
    logo = AxonLogo(size=size, dark=dark)
    return logo.create_widget(size)


# ── CLI test (headless) ───────────────────────────────────────────
if __name__ == "__main__":
    print("=== Axon OS Logo ===")
    logo = AxonLogo(size=120, dark=True)
    print(f"Size:    {logo.size}px")
    print(f"Theme:   {'Dark' if logo.dark else 'Light'}")
    print(f"Nodes:   {len(logo._outer)} outer / {len(logo._inner)} inner")
    print(f"Pulses:  {len(logo._pulses)} flowing")
    print(f"GTK4:    {'available' if GTK_OK else 'not available'}")
    print("Syntax: OK")
