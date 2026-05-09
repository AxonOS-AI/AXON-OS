# AxonOS/platform/gui/wallpaper/wallpaper_engine.py
# ─────────────────────────────────────────────────────────────────
# Copyright (c) 2024 Abdullah — Axon OS Project (AGPL-3.0)
# Purpose: Wallpaper engine — manages 6 animated wallpapers,
#          rotates every 30 seconds, smooth fade transitions,
#          logo watermark adapts to dark/light theme.
# Layer:   Platform / GUI
# Depends: GTK4, Cairo, colors.py
# ─────────────────────────────────────────────────────────────────

import os
import sys
import math
import time
import random
import logging
from typing import Optional, List

log = logging.getLogger("axon.wallpaper")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import gi
    gi.require_version("Gtk", "4.0")
    from gi.repository import Gtk, GLib
    import cairo
    GTK_OK = True
except (ImportError, ValueError):
    GTK_OK = False
    log.warning("GTK4/Cairo not available — wallpaper in headless mode")

WALLPAPER_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH   = os.path.expanduser("~/.axonos/wallpaper.txt")
ROTATE_SEC    = 30
FPS           = 30
FRAME_MS      = int(1000 / FPS)


# ── Base Wallpaper ────────────────────────────────────────────────

class BaseWallpaper:
    """
    Base class for all Axon OS wallpapers.
    Subclass and implement render(cr, w, h, t, dark).
    """

    name: str = "Base"
    dark_only: bool = False

    def __init__(self):
        self._t = 0
        random.seed(self.name)
        self._init()

    def _init(self) -> None:
        """Override to initialise particles/nodes on first load."""
        pass

    def render(self, cr: "cairo.Context", w: int, h: int,
               t: float, dark: bool) -> None:
        """Draw one frame. Override in subclass."""
        raise NotImplementedError

    def tick(self) -> None:
        self._t += 1

    def _logo_watermark(self, cr, cx: float, cy: float,
                        radius: float, dark: bool, alpha: float = 1.0) -> None:
        """
        Draw the Ax processor logo — large, clear circuit traces.
        Used by all wallpapers.
        """
        cyan  = (0.00, 0.83, 1.00) if dark else (0.00, 0.35, 0.75)
        purp  = (0.42, 0.23, 0.88) if dark else (0.30, 0.15, 0.70)
        panel = (0.02, 0.03, 0.09, 0.96) if dark else (0.96, 0.97, 0.99, 0.96)
        t = self._t

        ps = radius * 0.55   # bigger body

        # ── Outer glow ────────────────────────────────────────────
        for ring in range(4):
            rr = ps * (1.15 + ring * 0.18)
            a  = (0.06 - ring * 0.012) * alpha
            cr.set_source_rgba(*cyan, a)
            cr.set_line_width(1.0)
            cr.arc(cx, cy, rr, 0, math.pi * 2)
            cr.stroke()

        # ── Circuit traces (lines going out from corners) ─────────
        corners = [
            (cx - ps, cy - ps, -1, -1),
            (cx + ps, cy - ps,  1, -1),
            (cx - ps, cy + ps, -1,  1),
            (cx + ps, cy + ps,  1,  1),
        ]
        trace_len = ps * 0.85
        trace_gap = ps * 0.30

        for bx, by, dx, dy in corners:
            flash = math.sin(t * 0.05 + bx * 0.01) * 0.5 + 0.5
            la = (0.55 + 0.45 * flash) * alpha
            cr.set_source_rgba(*cyan, la)
            cr.set_line_width(2.0)
            # horizontal trace
            cr.move_to(bx, by + dy * trace_gap)
            cr.line_to(bx + dx * trace_len, by + dy * trace_gap)
            cr.stroke()
            # vertical trace
            cr.move_to(bx + dx * trace_gap, by)
            cr.line_to(bx + dx * trace_gap, by + dy * trace_len)
            cr.stroke()
            # corner dot
            cr.arc(bx + dx * trace_gap,
                   by + dy * trace_gap, 3.5, 0, math.pi * 2)
            cr.set_source_rgba(*cyan, la)
            cr.fill()

        # ── Side circuit nodes ────────────────────────────────────
        offsets = [-ps * 0.38, 0, ps * 0.38]
        pin_len = ps * 0.55

        for off in offsets:
            flash = math.sin(t * 0.07 + off * 0.02) > 0.60
            la = (0.90 if flash else 0.40) * alpha
            cr.set_source_rgba(*cyan, la)
            cr.set_line_width(2.2)

            # top pin
            cr.move_to(cx + off, cy - ps)
            cr.line_to(cx + off, cy - ps - pin_len)
            cr.stroke()
            # bottom pin
            cr.move_to(cx + off, cy + ps)
            cr.line_to(cx + off, cy + ps + pin_len)
            cr.stroke()
            # left pin
            cr.move_to(cx - ps, cy + off)
            cr.line_to(cx - ps - pin_len, cy + off)
            cr.stroke()
            # right pin
            cr.move_to(cx + ps, cy + off)
            cr.line_to(cx + ps + pin_len, cy + off)
            cr.stroke()

            # pin endpoint dots
            for px, py in [
                (cx + off, cy - ps - pin_len),
                (cx + off, cy + ps + pin_len),
                (cx - ps - pin_len, cy + off),
                (cx + ps + pin_len, cy + off),
            ]:
                cr.arc(px, py, 3.0, 0, math.pi * 2)
                cr.set_source_rgba(*cyan, la)
                cr.fill()

        # ── Body ─────────────────────────────────────────────────
        cr.set_source_rgba(*panel)
        self._rrect(cr, cx - ps, cy - ps, ps * 2, ps * 2, ps * 0.14)
        cr.fill()

        cr.set_source_rgba(*cyan, 0.95 * alpha)
        cr.set_line_width(2.8)
        self._rrect(cr, cx - ps, cy - ps, ps * 2, ps * 2, ps * 0.14)
        cr.stroke()

        # ── Inner die ────────────────────────────────────────────
        die = ps * 0.62
        cr.set_source_rgba(*purp, 0.18 * alpha)
        self._rrect(cr, cx - die, cy - die, die * 2, die * 2, ps * 0.08)
        cr.fill()
        cr.set_source_rgba(*purp, 0.75 * alpha)
        cr.set_line_width(1.8)
        self._rrect(cr, cx - die, cy - die, die * 2, die * 2, ps * 0.08)
        cr.stroke()

        # ── Inner circuit grid ───────────────────────────────────
        grid_step = die * 0.45
        cr.set_line_width(0.8)
        for gx in [-grid_step, 0, grid_step]:
            for gy in [-grid_step, 0, grid_step]:
                if gx == 0 and gy == 0: continue
                cr.arc(cx + gx, cy + gy, 2.5, 0, math.pi * 2)
                cr.set_source_rgba(*purp, 0.55 * alpha)
                cr.fill()
        # connect grid dots
        for gx in [-grid_step, 0, grid_step]:
            cr.move_to(cx + gx, cy - grid_step)
            cr.line_to(cx + gx, cy + grid_step)
            cr.set_source_rgba(*purp, 0.25 * alpha)
            cr.set_line_width(0.8)
            cr.stroke()
        for gy in [-grid_step, 0, grid_step]:
            cr.move_to(cx - grid_step, cy + gy)
            cr.line_to(cx + grid_step, cy + gy)
            cr.set_source_rgba(*purp, 0.25 * alpha)
            cr.stroke()

        # ── Ax text ───────────────────────────────────────────────
        fs = ps * 0.72
        cr.select_font_face("Courier New", 0, 1)
        cr.set_font_size(fs)
        ext = cr.text_extents("Ax")
        cr.set_source_rgba(*cyan, alpha)
        cr.move_to(cx - ext.width / 2 - ext.x_bearing,
                   cy - ext.height / 2 - ext.y_bearing)
        cr.show_text("Ax")

        # ── Animated pulse ring ───────────────────────────────────
        pulse = ps * 0.68 + ps * 0.08 * math.sin(t * 0.05)
        cr.set_source_rgba(*cyan, 0.20 * alpha)
        cr.set_line_width(1.5)
        cr.arc(cx, cy, pulse, 0, math.pi * 2)
        cr.stroke()

    def _rrect(self, cr, x, y, w, h, r):
        cr.new_sub_path()
        cr.arc(x+r,   y+r,   r, math.pi,     math.pi*1.5)
        cr.arc(x+w-r, y+r,   r, math.pi*1.5, 0)
        cr.arc(x+w-r, y+h-r, r, 0,           math.pi*0.5)
        cr.arc(x+r,   y+h-r, r, math.pi*0.5, math.pi)
        cr.close_path()


# ── Wallpaper Engine ──────────────────────────────────────────────

class WallpaperEngine:
    """
    Manages wallpaper loading, rotation, and fade transitions.

    Usage (GTK4):
        engine = WallpaperEngine()
        area   = engine.create_widget()
        window.set_child(area)
    """

    def __init__(self, rotate_sec: int = ROTATE_SEC):
        self._rotate_sec  = rotate_sec
        self._current_idx = self._load_saved_index()
        self._next_idx    = -1
        self._alpha       = 1.0      # current wallpaper opacity
        self._transitioning = False
        self._last_switch = time.time()
        self._dark        = self._load_dark()
        self._wallpapers: List[BaseWallpaper] = []
        self._widget: Optional["Gtk.DrawingArea"] = None
        self._load_wallpapers()

    def _load_wallpapers(self) -> None:
        """Import and instantiate all wallpaper classes."""
        wall_modules = [
            ("axon_splash", "AxonSplash"),
        ]
        for mod_name, cls_name in wall_modules:
            try:
                mod_path = os.path.join(WALLPAPER_DIR, mod_name + ".py")
                if not os.path.exists(mod_path):
                    log.warning("Wallpaper module missing: %s", mod_name)
                    continue
                import importlib.util
                spec = importlib.util.spec_from_file_location(mod_name, mod_path)
                mod  = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                cls  = getattr(mod, cls_name)
                self._wallpapers.append(cls())
                log.info("Loaded wallpaper: %s", cls_name)
            except Exception as e:
                log.error("Failed to load wallpaper %s: %s", cls_name, e)

        if not self._wallpapers:
            log.warning("No wallpapers loaded — using fallback")
            self._wallpapers = [_FallbackWallpaper()]

        self._current_idx = min(self._current_idx, len(self._wallpapers) - 1)

    def _load_saved_index(self) -> int:
        path = os.path.expanduser("~/.axonos/wallpaper.txt")
        try:
            return max(0, int(open(path).read().strip()))
        except Exception:
            return 0

    def _save_index(self, idx: int) -> None:
        os.makedirs(os.path.expanduser("~/.axonos"), exist_ok=True)
        with open(os.path.expanduser("~/.axonos/wallpaper.txt"), "w") as f:
            f.write(str(idx))

    def _load_dark(self) -> bool:
        path = os.path.expanduser("~/.axonos/theme.txt")
        try:
            return open(path).read().strip().lower() != "light"
        except Exception:
            return True

    def set_dark(self, dark: bool) -> None:
        self._dark = dark

    def switch_to(self, idx: int) -> None:
        """Start fade transition to wallpaper at index."""
        if idx == self._current_idx or self._transitioning:
            return
        self._next_idx      = idx % len(self._wallpapers)
        self._transitioning = True
        self._last_switch   = time.time()

    def next_wallpaper(self) -> None:
        self.switch_to((self._current_idx + 1) % len(self._wallpapers))

    def prev_wallpaper(self) -> None:
        self.switch_to((self._current_idx - 1) % len(self._wallpapers))

    @property
    def current_name(self) -> str:
        if self._wallpapers:
            return self._wallpapers[self._current_idx].name
        return "None"

    @property
    def count(self) -> int:
        return len(self._wallpapers)

    # ── Draw ──────────────────────────────────────────────────────

    def draw(self, area, cr: "cairo.Context", w: int, h: int) -> None:
        """GTK4 DrawingArea draw function."""
        if not self._wallpapers:
            cr.set_source_rgb(0.02, 0.03, 0.07)
            cr.paint()
            return

        current = self._wallpapers[self._current_idx]

        # Auto-rotate timer
        if time.time() - self._last_switch > self._rotate_sec:
            self.next_wallpaper()

        # Handle fade transition
        if self._transitioning:
            self._alpha = max(0.0, self._alpha - 0.04)
            if self._alpha <= 0.0:
                self._current_idx   = self._next_idx
                self._next_idx      = -1
                self._transitioning = False
                self._alpha         = 1.0
                self._save_index(self._current_idx)
                current = self._wallpapers[self._current_idx]
        elif self._alpha < 1.0:
            self._alpha = min(1.0, self._alpha + 0.04)

        # Draw with alpha
        cr.push_group()
        current.render(cr, w, h, current._t, self._dark)
        cr.pop_group_to_source()
        cr.paint_with_alpha(self._alpha)

        current.tick()

    def tick(self, widget) -> bool:
        """GLib timer callback — 30fps."""
        if widget:
            widget.queue_draw()
        return True

    def create_widget(self) -> Optional["Gtk.DrawingArea"]:
        """Create a GTK4 DrawingArea widget for this engine."""
        if not GTK_OK:
            log.error("GTK4 not available")
            return None
        area = Gtk.DrawingArea()
        area.set_hexpand(True)
        area.set_vexpand(True)
        area.set_draw_func(self.draw)
        GLib.timeout_add(FRAME_MS, self.tick, area)
        self._widget = area
        return area


# ── Fallback wallpaper (used if no files loaded) ──────────────────

class _FallbackWallpaper(BaseWallpaper):
    name = "Fallback"

    def render(self, cr, w, h, t, dark):
        bg = (0.02, 0.03, 0.07) if dark else (0.94, 0.95, 0.96)
        cr.set_source_rgb(*bg)
        cr.paint()
        self._logo_watermark(cr, w/2, h/2, min(w,h)*0.15, dark, 0.3)


# ── CLI test ──────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Axon OS Wallpaper Engine ===")
    engine = WallpaperEngine()
    print(f"Wallpapers loaded: {engine.count}")
    print(f"Current:           {engine.current_name}")
    print(f"Dark mode:         {engine._dark}")
    print(f"Rotate every:      {engine._rotate_sec}s")
    print(f"GTK4:              {'available' if GTK_OK else 'not available'}")
    print("Syntax: OK")
