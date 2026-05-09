# AxonOS/platform/gui/desktop-environment/dashboard_panel.py
# Copyright (c) 2024 Abdullah -- Axon OS Project (AGPL-3.0)
# Purpose: Floating Cairo dashboard panel on desktop

import os, sys, math, datetime, logging, json

_HERE     = os.path.dirname(os.path.abspath(__file__))
_GUI_DIR  = os.path.dirname(_HERE)
_PLATFORM = os.path.dirname(_GUI_DIR)
_CORE_DIR = os.path.join(_PLATFORM, "core-services")
_RM_DIR   = os.path.join(_CORE_DIR, "resource-manager")

for _p in [_PLATFORM, _CORE_DIR, _RM_DIR, _GUI_DIR]:
    if _p not in sys.path: sys.path.insert(0, _p)

log = logging.getLogger("axon.dashboard_panel")

try:
    import gi
    gi.require_version("Gtk", "4.0")
    from gi.repository import Gtk, Gdk, GLib
    import cairo
    GTK_OK = True
except Exception:
    GTK_OK = False


class DashboardPanel:
    """
    Floating dashboard panel drawn with Cairo.
    Shows CPU / RAM / DISK / GPU / Training / Clock
    Toggled from taskbar button.
    """

    PANEL_W = 340
    PANEL_H = 420

    def __init__(self, overlay, dark=True, rm=None, gpu_info=None):
        self._overlay   = overlay
        self._dark      = dark
        self._rm        = rm
        self._gpu_info  = gpu_info
        self._visible   = False
        self._anim_alpha = 0.0   # 0 = hidden, 1 = fully shown
        self._anim_dir   = 0     # +1 show, -1 hide

        # Live data
        self._cpu   = 0.0
        self._ram   = 0.0
        self._disk  = 0.0
        self._gpu   = 0.0
        self._train = 0.0
        self._temp  = None
        self._gpu_label = "CPU"
        self._history_cpu  = [0.0] * 30
        self._history_ram  = [0.0] * 30
        self._t = 0

        self._build()

    def _build(self):
        if not GTK_OK: return

        # Outer box — positioned bottom-left on overlay
        self._box = Gtk.Box()
        self._box.set_size_request(self.PANEL_W, self.PANEL_H)
        self._box.set_valign(Gtk.Align.END)
        self._box.set_halign(Gtk.Align.START)
        self._box.set_margin_start(16)
        self._box.set_margin_bottom(70)
        self._box.set_visible(False)

        self._area = Gtk.DrawingArea()
        self._area.set_size_request(self.PANEL_W, self.PANEL_H)
        self._area.set_draw_func(self._draw)
        self._box.append(self._area)

        self._overlay.add_overlay(self._box)

        # Click to dismiss
        click = Gtk.GestureClick()
        click.connect("pressed", self._on_click)
        self._area.add_controller(click)

        # Drag to move
        drag = Gtk.GestureDrag()
        drag.connect("drag-begin",  self._on_drag_begin)
        drag.connect("drag-update", self._on_drag_update)
        self._area.add_controller(drag)
        self._drag_start = (0, 0)

        GLib.timeout_add(33, self._tick_anim)

    # ── Drag ──────────────────────────────────────────────────────
    def _on_drag_begin(self, gesture, x, y):
        m = self._box.get_margin_start()
        b = self._box.get_margin_bottom()
        self._drag_start = (m, b)

    def _on_drag_update(self, gesture, dx, dy):
        ms, mb = self._drag_start
        self._box.set_margin_start(max(0, int(ms + dx)))
        self._box.set_margin_bottom(max(0, int(mb - dy)))

    def _on_click(self, gesture, n, x, y):
        pass  # click inside panel does nothing

    # ── Animation tick ────────────────────────────────────────────
    def _tick_anim(self):
        if self._anim_dir == 1:
            self._anim_alpha = min(1.0, self._anim_alpha + 0.08)
            if self._anim_alpha >= 1.0:
                self._anim_dir = 0
        elif self._anim_dir == -1:
            self._anim_alpha = max(0.0, self._anim_alpha - 0.08)
            if self._anim_alpha <= 0.0:
                self._anim_dir = 0
                self._box.set_visible(False)

        self._t += 1
        if self._box.get_visible():
            self._area.queue_draw()
        return True

    # ── Toggle ────────────────────────────────────────────────────
    def toggle(self):
        if not self._visible:
            self.show()
        else:
            self.hide()

    def show(self):
        self._visible = True
        self._box.set_visible(True)
        self._anim_dir = 1
        self._update_data()

    def hide(self):
        self._visible = False
        self._anim_dir = -1

    def set_theme(self, dark):
        self._dark = dark
        self._area.queue_draw()

    def set_rm(self, rm):
        self._rm = rm

    def set_gpu_info(self, gpu_info):
        self._gpu_info = gpu_info

    # ── Data update ───────────────────────────────────────────────
    def _update_data(self):
        try:
            if self._rm:
                s = self._rm.get_snapshot()
                self._cpu  = s.cpu_percent
                self._ram  = s.ram_percent
                self._disk = s.disk_percent
                self._history_cpu.append(self._cpu)
                self._history_cpu = self._history_cpu[-30:]
                self._history_ram.append(self._ram)
                self._history_ram = self._history_ram[-30:]
        except Exception: pass

        try:
            from gpu_detector import get_gpu_info
            gi = self._gpu_info or get_gpu_info()
            self._gpu       = gi.utilization_pct
            self._gpu_label = gi.status_label
            self._temp      = gi.temperature_c
        except Exception: pass

        try:
            p = os.path.expanduser("~/.axonos/training_progress.json")
            if os.path.exists(p):
                data = json.loads(open(p).read())
                self._train = float(data.get("progress", 0.0))
        except Exception: pass

        GLib.timeout_add_seconds(2, self._update_data)

    # ── Draw ──────────────────────────────────────────────────────
    def _draw(self, area, cr, w, h):
        a = self._anim_alpha
        if a <= 0: return

        dark = self._dark
        cyan   = (0.00, 0.83, 1.00)
        purp   = (0.42, 0.24, 0.88)
        green  = (0.11, 0.78, 0.46)
        amber  = (1.00, 0.62, 0.00)
        txt    = (0.93, 0.93, 0.98) if dark else (0.08, 0.09, 0.18)
        txt2   = (0.55, 0.65, 0.78) if dark else (0.38, 0.45, 0.58)
        bg     = (0.03, 0.05, 0.12, 0.94 * a) if dark else (0.96, 0.97, 0.99, 0.96 * a)
        bdbg   = (0.00, 0.83, 1.00, 0.60 * a) if dark else (0.00, 0.35, 0.75, 0.60 * a)

        pad = 18
        r   = 18  # corner radius

        # ── Panel background ──────────────────────────────────────
        self._rrect(cr, 0, 0, w, h, r)
        cr.set_source_rgba(*bg)
        cr.fill()

        # Border gradient
        cr.set_source_rgba(*bdbg)
        cr.set_line_width(1.8)
        self._rrect(cr, 0, 0, w, h, r)
        cr.stroke()

        # Top accent line
        cr.set_source_rgba(*cyan, 0.9 * a)
        cr.set_line_width(2.5)
        cr.move_to(r, 0); cr.line_to(w - r, 0); cr.stroke()

        # ── Header ────────────────────────────────────────────────
        self._draw_header(cr, w, pad, a, dark, cyan, txt)

        y = 60

        # ── CPU gauge ─────────────────────────────────────────────
        y = self._draw_gauge_row(cr, pad, y, w - pad*2,
            "CPU", self._cpu, cyan, dark, a, txt, txt2,
            self._history_cpu)
        y += 8

        # ── RAM gauge ─────────────────────────────────────────────
        y = self._draw_gauge_row(cr, pad, y, w - pad*2,
            "RAM", self._ram, purp, dark, a, txt, txt2,
            self._history_ram)
        y += 8

        # ── DISK gauge ────────────────────────────────────────────
        y = self._draw_gauge_row(cr, pad, y, w - pad*2,
            "DISK", self._disk, green, dark, a, txt, txt2)
        y += 8

        # ── GPU gauge ─────────────────────────────────────────────
        y = self._draw_gauge_row(cr, pad, y, w - pad*2,
            f"GPU {self._gpu_label}", self._gpu, amber, dark, a, txt, txt2)
        y += 12

        # ── Training progress ─────────────────────────────────────
        y = self._draw_training(cr, pad, y, w - pad*2, a, cyan, txt, txt2, dark)
        y += 14

        # ── Clock + temp ──────────────────────────────────────────
        self._draw_footer(cr, pad, y, w, h, a, dark, cyan, txt, txt2)

    def _draw_header(self, cr, w, pad, a, dark, cyan, txt):
        # Ax logo mini
        cx, cy = 28, 28
        cr.set_source_rgba(*cyan, 0.9 * a)
        cr.set_line_width(1.5)
        cr.rectangle(cx - 12, cy - 12, 24, 24)
        cr.stroke()
        cr.select_font_face("Courier New", cairo.FONT_SLANT_NORMAL,
                            cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(11)
        ext = cr.text_extents("Ax")
        cr.move_to(cx - ext.width/2 - ext.x_bearing,
                   cy - ext.height/2 - ext.y_bearing)
        cr.set_source_rgba(*cyan, a)
        cr.show_text("Ax")

        # Title
        cr.set_font_size(13)
        cr.set_source_rgba(*txt, a)
        cr.move_to(50, 22)
        cr.show_text("AXON  MONITOR")

        # Subtitle
        cr.set_font_size(9)
        cr.set_source_rgba(*txt, 0.5 * a)
        cr.move_to(50, 36)
        cr.show_text("System Dashboard")

        # Separator line
        cr.set_source_rgba(*cyan, 0.25 * a)
        cr.set_line_width(1)
        cr.move_to(18, 50); cr.line_to(w - 18, 50); cr.stroke()

    def _draw_gauge_row(self, cr, x, y, bw, label, value,
                        color, dark, a, txt, txt2, history=None):
        """Draw a labeled gauge bar with optional sparkline."""
        bar_h = 8
        bar_w = bw - 90
        bar_x = x + 72

        # Label
        cr.set_source_rgba(*txt, 0.85 * a)
        cr.select_font_face("Courier New", cairo.FONT_SLANT_NORMAL,
                            cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(10)
        cr.move_to(x, y + bar_h)
        cr.show_text(label)

        # Bar background
        self._rrect(cr, bar_x, y, bar_w, bar_h, bar_h/2)
        bg_a = 0.12 if dark else 0.10
        cr.set_source_rgba(*color, bg_a * a)
        cr.fill()

        # Bar fill
        fill_w = max(4, bar_w * value / 100)
        self._rrect(cr, bar_x, y, fill_w, bar_h, bar_h/2)

        # Color based on value
        if value > 85:
            fc = (1.0, 0.25, 0.25)
        elif value > 65:
            fc = (1.0, 0.62, 0.00)
        else:
            fc = color
        cr.set_source_rgba(*fc, 0.90 * a)
        cr.fill()

        # Value text
        cr.set_source_rgba(*txt2, 0.9 * a)
        cr.set_font_size(10)
        val_str = f"{value:.0f}%"
        ext = cr.text_extents(val_str)
        cr.move_to(bar_x + bar_w + 6, y + bar_h)
        cr.show_text(val_str)

        # Sparkline (mini chart)
        if history and len(history) > 1:
            sp_x = bar_x
            sp_y = y + bar_h + 4
            sp_w = bar_w
            sp_h = 14
            cr.set_source_rgba(*color, 0.18 * a)
            cr.rectangle(sp_x, sp_y, sp_w, sp_h)
            cr.fill()

            pts = history[-30:]
            step = sp_w / max(len(pts) - 1, 1)
            cr.move_to(sp_x, sp_y + sp_h - (pts[0]/100) * sp_h)
            for i, v in enumerate(pts[1:], 1):
                cr.line_to(sp_x + i * step,
                           sp_y + sp_h - (v / 100) * sp_h)
            cr.set_source_rgba(*color, 0.80 * a)
            cr.set_line_width(1.2)
            cr.stroke()
            return y + bar_h + sp_h + 8

        return y + bar_h + 10

    def _draw_training(self, cr, x, y, bw, a, cyan, txt, txt2, dark):
        cr.set_source_rgba(*txt, 0.85 * a)
        cr.select_font_face("Courier New", cairo.FONT_SLANT_NORMAL,
                            cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(10)
        cr.move_to(x, y + 10)
        cr.show_text("TRAIN")

        # Animated progress bar
        bar_x = x + 72
        bar_w = bw - 90
        bar_h = 10

        self._rrect(cr, bar_x, y, bar_w, bar_h, bar_h/2)
        cr.set_source_rgba(*cyan, 0.10 * a)
        cr.fill()

        fill_w = max(4, bar_w * self._train / 100)
        # Animated shimmer
        shimmer = 0.5 + 0.5 * math.sin(self._t * 0.08)
        self._rrect(cr, bar_x, y, fill_w, bar_h, bar_h/2)
        cr.set_source_rgba(*cyan, (0.70 + 0.25 * shimmer) * a)
        cr.fill()

        cr.set_source_rgba(*txt2, 0.9 * a)
        cr.set_font_size(10)
        cr.move_to(bar_x + bar_w + 6, y + 10)
        cr.show_text(f"{self._train:.0f}%")

        return y + bar_h + 6

    def _draw_footer(self, cr, pad, y, w, h, a, dark, cyan, txt, txt2):
        # Separator
        cr.set_source_rgba(*cyan, 0.20 * a)
        cr.set_line_width(1)
        cr.move_to(pad, y); cr.line_to(w - pad, y); cr.stroke()

        y += 12

        # Clock
        now = datetime.datetime.now()
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%a %d %b")

        cr.select_font_face("Courier New", cairo.FONT_SLANT_NORMAL,
                            cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(22)
        cr.set_source_rgba(*cyan, 0.95 * a)
        ext = cr.text_extents(time_str)
        cr.move_to(w/2 - ext.width/2 - ext.x_bearing, y + 22)
        cr.show_text(time_str)

        cr.set_font_size(10)
        cr.set_source_rgba(*txt2, 0.7 * a)
        ext2 = cr.text_extents(date_str)
        cr.move_to(w/2 - ext2.width/2 - ext2.x_bearing, y + 38)
        cr.show_text(date_str)

        # Temperature
        if self._temp:
            temp_str = f"GPU {self._temp:.0f}°C"
            cr.set_font_size(10)
            tc = (1.0, 0.35, 0.35) if self._temp > 80 else \
                 (1.0, 0.62, 0.00) if self._temp > 65 else (0.11, 0.78, 0.46)
            cr.set_source_rgba(*tc, 0.9 * a)
            cr.move_to(w - pad - 60, y + 22)
            cr.show_text(temp_str)

        # Drag hint
        cr.set_font_size(8)
        cr.set_source_rgba(*txt2, 0.35 * a)
        hint = "drag to move"
        ext3 = cr.text_extents(hint)
        cr.move_to(w/2 - ext3.width/2, h - 8)
        cr.show_text(hint)

    def _rrect(self, cr, x, y, w, h, r):
        cr.new_sub_path()
        cr.arc(x+r,   y+r,   r, math.pi,     math.pi*1.5)
        cr.arc(x+w-r, y+r,   r, math.pi*1.5, 0)
        cr.arc(x+w-r, y+h-r, r, 0,           math.pi*0.5)
        cr.arc(x+r,   y+h-r, r, math.pi*0.5, math.pi)
        cr.close_path()
