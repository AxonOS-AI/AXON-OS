# AxonOS/platform/gui/desktop-environment/main.py
# Copyright (c) 2024 Abdullah -- Axon OS Project (AGPL-3.0)

import os, sys, logging, math

_HERE       = os.path.dirname(os.path.abspath(__file__))
_GUI_DIR    = os.path.dirname(_HERE)
_PLATFORM   = os.path.dirname(_GUI_DIR)
_ROOT       = os.path.dirname(_PLATFORM)
_THEMES_DIR = os.path.join(_GUI_DIR, "themes")
_WALL_DIR   = os.path.join(_GUI_DIR, "wallpaper")
_CORE_DIR   = os.path.join(_PLATFORM, "core-services")
_RM_DIR     = os.path.join(_CORE_DIR, "resource-manager")

for _p in [_ROOT, _PLATFORM, _CORE_DIR, _RM_DIR, _THEMES_DIR, _WALL_DIR, _GUI_DIR]:
    if _p not in sys.path: sys.path.insert(0, _p)

import sys as _sys_log
_sys_log.path.insert(0, _PLATFORM)
try:
    from logger import get_gui_logger
    log = get_gui_logger()
except Exception:
    import logging as _lg
    _lg.basicConfig(level=_lg.INFO)
    log = _lg.getLogger("axon.desktop")

AXON_NAME    = "Axon OS"
AXON_VERSION = "1.0.0"

try:
    import gi
    gi.require_version("Gtk", "4.0")
    gi.require_version("Gdk", "4.0")
    from gi.repository import Gtk, Gdk, GLib
    import cairo
    GTK_OK = True
except Exception as e:
    GTK_OK = False
    log.error("GTK4: %s", e)

from taskbar         import AxonTaskbar
from side_panel      import SidePanel
from launcher        import AxonLauncher
from dashboard_panel import DashboardPanel

import sys as _sys_pm
_sys_pm.path.insert(0, _PLATFORM)
try:
    import process_manager as _pm
    PM_OK = True
except Exception:
    PM_OK = False
    _pm = None

try:
    from ask_axon import AskAxonWindow
    ASK_OK = True
except Exception:
    ASK_OK = False

try:
    from colors import get_theme, toggle_theme, save_theme
    COLORS_OK = True
except Exception:
    COLORS_OK = False

try:
    from wallpaper_engine import WallpaperEngine
    _wallpaper_engine = WallpaperEngine()
    WALL_OK = True
except Exception as e:
    WALL_OK = False
    log.warning("Wallpaper: %s", e)


def _btn_css(dark):
    if dark:
        return (
            "button {"
            " background: rgba(0,212,255,0.20);"
            " border: 2px solid rgba(0,212,255,0.85);"
            " border-radius: 18px; }"
            " button label {"
            " color: #FFFFFF;"
            " font-family: monospace;"
            " font-weight: bold;"
            " font-size: 12px; }"
        ).encode()
    else:
        return (
            "button {"
            " background: #003878;"
            " border: 2px solid #001A40;"
            " border-radius: 18px; }"
            "button:hover {"
            " background: #00509A; }"
            "button > label {"
            " color: #FFFFFF;"
            " font-family: monospace;"
            " font-weight: bold;"
            " font-size: 12px; }"
        ).encode()


def _draw_icon(cr, cx, cy, size, icon_key, dark):
    p  = (0.00, 0.83, 1.00) if dark else (0.00, 0.30, 0.70)
    p2 = (0.42, 0.24, 0.88) if dark else (0.25, 0.12, 0.60)
    bg = 0.15 if dark else 0.12
    s  = size / 44.0

    cr.save()
    cr.translate(cx, cy)
    cr.scale(s, s)
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.set_line_join(cairo.LINE_JOIN_ROUND)

    if icon_key == "dashboard":
        for ox, oy in [(-6,-6),(5,-6),(-6,5),(5,5)]:
            cr.rectangle(ox, oy, 9, 9)
            cr.set_source_rgba(*p, bg); cr.fill_preserve()
            cr.set_source_rgba(*p, 1); cr.set_line_width(1.5); cr.stroke()

    elif icon_key == "terminal":
        cr.move_to(-10,-5); cr.line_to(-2,0); cr.line_to(-10,5)
        cr.set_source_rgba(*p, 1); cr.set_line_width(2); cr.stroke()
        cr.rectangle(0, 3, 12, 2.5)
        cr.set_source_rgba(*p, 1); cr.fill()

    elif icon_key == "files":
        cr.move_to(-12,0); cr.line_to(-12,15); cr.line_to(12,15)
        cr.line_to(12,3); cr.line_to(4,3); cr.line_to(1,0); cr.close_path()
        cr.set_source_rgba(*p, bg); cr.fill_preserve()
        cr.set_source_rgba(*p, 1); cr.set_line_width(2); cr.stroke()

    elif icon_key == "ai":
        pts = [(0,-11),(8,-5),(10,4),(4,12),(-4,12),(-10,4),(-8,-5)]
        for i in range(len(pts)):
            x1,y1 = pts[i]; x2,y2 = pts[(i+1)%len(pts)]
            cr.move_to(x1,y1); cr.line_to(x2,y2)
            cr.set_source_rgba(*p2, 0.5); cr.set_line_width(1); cr.stroke()
        for dx,dy in pts:
            cr.arc(dx, dy, 2.5, 0, 2*math.pi)
            cr.set_source_rgba(*p, 1); cr.fill()
        cr.arc(0, 0, 4, 0, 2*math.pi)
        cr.set_source_rgba(*p2, 0.25); cr.fill()

    elif icon_key == "settings":
        for i in range(8):
            a = i * math.pi / 4
            cr.move_to(math.cos(a)*7, math.sin(a)*7)
            cr.line_to(math.cos(a)*12, math.sin(a)*12)
            cr.set_source_rgba(*p, 1); cr.set_line_width(2); cr.stroke()
        cr.arc(0,0,5,0,2*math.pi)
        cr.set_source_rgba(*p, bg); cr.fill_preserve()
        cr.set_source_rgba(*p, 1); cr.set_line_width(2); cr.stroke()
        cr.arc(0,0,2.5,0,2*math.pi)
        cr.set_source_rgba(*p, 1); cr.fill()

    elif icon_key == "axonai":
        cr.rectangle(-9,-9,18,18)
        if dark:
            cr.set_source_rgba(0.02,0.03,0.09,0.92)
        else:
            cr.set_source_rgba(0.94,0.95,0.96,0.95)
        cr.fill_preserve()
        cr.set_source_rgba(*p, 1); cr.set_line_width(2); cr.stroke()
        for x in [-5,5]:
            cr.move_to(x,-9); cr.line_to(x,-13)
            cr.move_to(x,9);  cr.line_to(x,13)
            cr.set_source_rgba(*p,0.8); cr.set_line_width(1.5); cr.stroke()
        for y in [-4,4]:
            cr.move_to(-9,y); cr.line_to(-13,y)
            cr.move_to(9,y);  cr.line_to(13,y)
            cr.set_source_rgba(*p,0.8); cr.set_line_width(1.5); cr.stroke()
        cr.select_font_face("Courier New", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(9)
        ext = cr.text_extents("Ax")
        cr.move_to(-ext.width/2-ext.x_bearing, -ext.height/2-ext.y_bearing)
        cr.set_source_rgba(*p,1); cr.show_text("Ax")

    cr.restore()


class IconButton(Gtk.Box):
    def __init__(self, name, icon_key, dark=True, on_click=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.set_size_request(78, 85)
        self._name     = name
        self._icon_key = icon_key
        self._dark     = dark
        self._callback = on_click
        self._hovered  = False

        self._area = Gtk.DrawingArea()
        self._area.set_size_request(78, 60)
        self._area.set_draw_func(self._draw)
        self.append(self._area)

        self._label = Gtk.Label(label=name)
        self.append(self._label)

        click = Gtk.GestureClick()
        click.connect("pressed", self._on_press)
        self.add_controller(click)

        motion = Gtk.EventControllerMotion()
        motion.connect("enter", self._on_enter)
        motion.connect("leave", self._on_leave)
        self.add_controller(motion)

        self._update_style()

    def _update_style(self):
        # Icon box style
        if self._dark:
            box_css = (
                "box { background: rgba(5,8,18,0.82);"
                " border: 2px solid rgba(0,212,255,0.65);"
                " border-radius: 12px; padding: 4px; }"
            ).encode()
        else:
            box_css = (
                "box { background: rgba(255,255,255,0.92);"
                " border: 2px solid rgba(0,30,110,0.60);"
                " border-radius: 12px; padding: 4px; }"
            ).encode()
        bp = Gtk.CssProvider()
        bp.load_from_data(box_css)
        self.get_style_context().add_provider(bp, 800)

        # Label: white text + dark shadow background always
        lbl_css = (
            "label { color: #FFFFFF;"
            " background: rgba(0,0,0,0.65);"
            " border-radius: 4px;"
            " padding: 2px 6px;"
            " font-size: 10px;"
            " font-weight: bold;"
            " font-family: monospace; }"
        ).encode()
        lp = Gtk.CssProvider()
        lp.load_from_data(lbl_css)
        self._label.get_style_context().add_provider(lp, 900)

    def _draw(self, area, cr, w, h):
        cx, cy = w/2, h/2-2
        size   = min(w,h)*0.85
        if self._hovered:
            col = (0,0.83,1.0) if self._dark else (0,0.30,0.70)
            cr.set_source_rgba(*col, 0.18)
            cr.rectangle(0,0,w,h); cr.fill()
        _draw_icon(cr, cx, cy, size, self._icon_key, self._dark)

    def _on_press(self, gesture, n, x, y):
        if self._callback: self._callback(self._name, self._icon_key)

    def _on_enter(self, ctrl, x, y):
        self._hovered = True; self._area.queue_draw()

    def _on_leave(self, ctrl):
        self._hovered = False; self._area.queue_draw()

    def set_theme(self, dark):
        self._dark = dark
        self._update_style()
        self._area.queue_draw()


DESKTOP_ICONS = [
    ("Dashboard", "dashboard"),
    ("Terminal",  "terminal"),
    ("Files",     "files"),
    ("AI",        "ai"),
    ("Settings",  "settings"),
    ("Axon AI",   "axonai"),
]


class AxonDesktop(Gtk.Application if GTK_OK else object):
    APP_ID = "com.axon.desktop"

    def __init__(self):
        if GTK_OK:
            super().__init__(application_id=self.APP_ID)
            self.connect("activate", self._on_activate)
        self._taskbar       = None
        self._launcher      = None
        self._ask_axon      = None
        self._dark          = True
        self._icons_visible = True
        self._icon_btns     = []
        self._icons_box     = None
        self._toggle_btn    = None
        self._bottom_btns   = []
        self._dashboard     = None
        self._side_panel    = None

    def _on_activate(self, app):
        self._load_css()
        win = Gtk.ApplicationWindow(application=app)
        win.set_title(f"{AXON_NAME} {AXON_VERSION}")
        win.set_default_size(1280, 800)

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        win.set_child(root)

        self._taskbar = AxonTaskbar(on_theme_toggle=self._on_theme_toggle)
        root.append(self._taskbar.widget)

        overlay = Gtk.Overlay()
        overlay.set_vexpand(True); overlay.set_hexpand(True)

        if WALL_OK:
            drawing = Gtk.DrawingArea()
            drawing.set_vexpand(True); drawing.set_hexpand(True)
            drawing.set_draw_func(_wallpaper_engine.draw)
            GLib.timeout_add(33, _wallpaper_engine.tick, drawing)

            # الشعار قابل للضغط
            wc = Gtk.GestureClick()
            wc.connect("pressed", self._on_logo_click)
            drawing.add_controller(wc)

            overlay.set_child(drawing)
        else:
            bg = Gtk.Box(); bg.set_vexpand(True); bg.set_hexpand(True)
            overlay.set_child(bg)

        # Icons right side
        # SidePanel جديد
        self._side_panel = SidePanel(
            overlay, dark=self._dark, on_icon=self._on_icon)
        self._icons_scroll = None
        self._icons_box    = None

        # ── Entry Point — Start AI Project ───────────────────────
        import cairo as _ep_cairo, math as _ep_math

        entry_wrap = Gtk.Box()
        entry_wrap.set_valign(Gtk.Align.CENTER)
        entry_wrap.set_halign(Gtk.Align.CENTER)

        self._entry_btn = Gtk.DrawingArea()
        self._entry_btn.set_size_request(160, 160)
        self._entry_hovered = False
        self._entry_t = 0

        def draw_entry(area, cr, w, h):
            t = self._entry_t
            cx, cy = w/2, h/2

            # Outer pulse rings
            for i in range(3):
                phase = t*0.03 + i*_ep_math.pi*2/3
                r = 65 + 6*_ep_math.sin(phase)
                a = 0.08 + 0.05*_ep_math.sin(phase)
                cr.set_source_rgba(0.00, 0.83, 1.00, a)
                cr.set_line_width(1.5)
                cr.arc(cx, cy, r, 0, 2*_ep_math.pi)
                cr.stroke()

            # Main circle bg
            r_main = 56 + (3 if self._entry_hovered else 0)
            cr.set_source_rgba(0.02, 0.05, 0.15, 0.92)
            cr.arc(cx, cy, r_main, 0, 2*_ep_math.pi)
            cr.fill()

            # Border
            glow = 0.5 + 0.5*_ep_math.sin(t*0.05)
            cr.set_source_rgba(0.00, 0.83, 1.00,
                               0.90 if self._entry_hovered else 0.55 + 0.2*glow)
            cr.set_line_width(2.5)
            cr.arc(cx, cy, r_main, 0, 2*_ep_math.pi)
            cr.stroke()

            # AI chip icon
            ps = 18
            cr.set_source_rgba(0.02, 0.05, 0.15, 0.95)
            def rrect(x,y,w2,h2,r2):
                cr.new_sub_path()
                cr.arc(x+r2,y+r2,r2,_ep_math.pi,_ep_math.pi*1.5)
                cr.arc(x+w2-r2,y+r2,r2,_ep_math.pi*1.5,0)
                cr.arc(x+w2-r2,y+h2-r2,r2,0,_ep_math.pi*0.5)
                cr.arc(x+r2,y+h2-r2,r2,_ep_math.pi*0.5,_ep_math.pi)
                cr.close_path()
            rrect(cx-ps, cy-ps-16, ps*2, ps*2, 5)
            cr.fill()
            cr.set_source_rgba(0.00, 0.83, 1.00, 0.9)
            cr.set_line_width(2)
            rrect(cx-ps, cy-ps-16, ps*2, ps*2, 5)
            cr.stroke()
            # Pins
            for x in [-12, 12]:
                for dy, ey in [(-ps-16, -ps-16-14),(ps-16, ps-16+14)]:
                    cr.move_to(cx+x, cy+dy)
                    cr.line_to(cx+x, cy+ey)
                    cr.set_source_rgba(0.00,0.83,1.00,0.6)
                    cr.set_line_width(1.5); cr.stroke()
            for y in [-6, 6]:
                for dx, ex in [(-ps, -ps-14),(ps, ps+14)]:
                    cr.move_to(cx+dx, cy+y-16)
                    cr.line_to(cx+ex, cy+y-16)
                    cr.set_source_rgba(0.00,0.83,1.00,0.6)
                    cr.set_line_width(1.5); cr.stroke()
            # Ax text
            cr.select_font_face("Courier New",
                _ep_cairo.FONT_SLANT_NORMAL, _ep_cairo.FONT_WEIGHT_BOLD)
            cr.set_font_size(12)
            ext = cr.text_extents("Ax")
            cr.set_source_rgba(0.00, 0.83, 1.00, 1.0)
            cr.move_to(cx-ext.width/2-ext.x_bearing,
                       cy-10-ext.height/2-ext.y_bearing)
            cr.show_text("Ax")

            # Main text
            cr.set_font_size(10)
            cr.set_source_rgba(0.93, 0.95, 0.98,
                               1.0 if self._entry_hovered else 0.85)
            txt = "Ask Axon"
            ext2 = cr.text_extents(txt)
            cr.move_to(cx-ext2.width/2-ext2.x_bearing, cy+32)
            cr.show_text(txt)

            # Sub text
            cr.set_font_size(9)
            cr.set_source_rgba(0.00, 0.83, 1.00, 0.55)
            sub = "What do you want to do?"
            ext3 = cr.text_extents(sub)
            cr.move_to(cx-ext3.width/2-ext3.x_bearing, cy+46)
            cr.show_text(sub)

        self._entry_btn.set_draw_func(draw_entry)

        # Animation
        def tick_entry():
            self._entry_t += 1
            self._entry_btn.queue_draw()
            return True
        GLib.timeout_add(33, tick_entry)

        # Hover
        em = Gtk.EventControllerMotion()
        em.connect("enter", lambda c,x,y: setattr(self,"_entry_hovered",True))
        em.connect("leave", lambda c: setattr(self,"_entry_hovered",False))
        self._entry_btn.add_controller(em)

        # Click
        ec = Gtk.GestureClick()
        ec.connect("pressed", self._on_logo_click)
        self._entry_btn.add_controller(ec)

        entry_wrap.append(self._entry_btn)
        overlay.add_overlay(entry_wrap)

        # Bottom buttons
        # ── زر القائمة الصغير ──────────────────────────────────
        import cairo as _cairo_btn, math as _math_btn

        self._panel_visible = False

        # Panel الذي يحتوي الأزرار الثلاثة
        self._action_panel = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self._action_panel.set_valign(Gtk.Align.END)
        self._action_panel.set_halign(Gtk.Align.CENTER)
        self._action_panel.set_margin_bottom(72)
        self._action_panel.set_visible(False)

        def _make_action_btn(icon, label, color, callback):
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
            box.set_size_request(64, 58)

            area = Gtk.DrawingArea()
            area.set_size_request(64, 36)

            def draw_icon(a, cr, w, h, c=color, i=icon):
                cr.set_source_rgba(*c, 0.18)
                cr.arc(w/2, h/2, 16, 0, 2*_math_btn.pi)
                cr.fill()
                cr.set_source_rgba(*c, 0.90)
                cr.set_line_width(2.0)
                cr.arc(w/2, h/2, 16, 0, 2*_math_btn.pi)
                cr.stroke()
                cr.set_source_rgba(*c, 1.0)
                cr.select_font_face("monospace",
                    _cairo_btn.FONT_SLANT_NORMAL,
                    _cairo_btn.FONT_WEIGHT_BOLD)
                cr.set_font_size(14)
                ext = cr.text_extents(i)
                cr.move_to(w/2 - ext.width/2 - ext.x_bearing,
                           h/2 - ext.height/2 - ext.y_bearing)
                cr.show_text(i)

            area.set_draw_func(draw_icon)

            lbl = Gtk.Label(label=label)
            p = Gtk.CssProvider()
            p.load_from_data(
                b"label { color: #FFFFFF;"
                b" background: rgba(0,0,0,0.65);"
                b" border-radius: 4px;"
                b" padding: 1px 5px;"
                b" font-size: 9px;"
                b" font-family: monospace;"
                b" font-weight: bold; }")
            lbl.get_style_context().add_provider(
                p, Gtk.STYLE_PROVIDER_PRIORITY_USER + 999)
            # force inline color
            lbl2 = Gtk.CssProvider()
            lbl2.load_from_data(
                b"* { color: #FFFFFF;"
                b" background: rgba(0,0,0,0.65); }")
            lbl.get_style_context().add_provider(
                lbl2, Gtk.STYLE_PROVIDER_PRIORITY_USER + 9999)

            click = Gtk.GestureClick()
            click.connect("pressed", lambda g,n,x,y: callback(None))
            area.add_controller(click)

            # Panel CSS
            pc = Gtk.CssProvider()
            pc.load_from_data(
                b"box { background: rgba(3,5,14,0.88);"
                b" border: 1px solid rgba(0,212,255,0.30);"
                b" border-radius: 14px; padding: 4px; }")
            box.get_style_context().add_provider(pc, 900)

            box.append(area)
            box.append(lbl)
            return box

        self._toggle_btn  = None
        self._apps_btn    = None
        self._restart_btn = None

        btn_hide  = _make_action_btn(
            "⊟", "Icons",
            (0.00, 0.83, 1.00),
            lambda *a: self._side_panel.toggle() if self._side_panel else None)
        btn_apps  = _make_action_btn(
            "⊞", "Apps",
            (0.42, 0.78, 1.00),
            self._on_launcher_btn)
        btn_restart = _make_action_btn(
            "↺", "Restart",
            (1.00, 0.42, 0.42),
            self._on_force_restart)

        self._action_panel.append(btn_hide)
        self._action_panel.append(btn_apps)
        self._action_panel.append(btn_restart)
        self._bottom_btns = []
        overlay.add_overlay(self._action_panel)

        # ── زر التبديل الصغير ────────────────────────────────────
        toggle_wrap = Gtk.Box()
        toggle_wrap.set_valign(Gtk.Align.END)
        toggle_wrap.set_halign(Gtk.Align.CENTER)
        toggle_wrap.set_margin_bottom(18)

        self._fab = Gtk.DrawingArea()
        self._fab.set_size_request(44, 44)
        self._fab_hovered = False

        def draw_fab(a, cr, w, h):
            dark = self._dark
            c = (0.00, 0.83, 1.00) if dark else (0.00, 0.35, 0.75)
            pulse = 0.5 + 0.5 * _math_btn.sin(self._fab_t * 0.06)

            # Glow
            cr.set_source_rgba(*c, 0.08 * pulse)
            cr.arc(w/2, h/2, 22, 0, 2*_math_btn.pi)
            cr.fill()

            # Circle background
            cr.set_source_rgba(0.02, 0.05, 0.12, 0.92)
            cr.arc(w/2, h/2, 18, 0, 2*_math_btn.pi)
            cr.fill()

            # Border
            cr.set_source_rgba(*c, 0.85 if self._fab_hovered else 0.55)
            cr.set_line_width(2.0)
            cr.arc(w/2, h/2, 18, 0, 2*_math_btn.pi)
            cr.stroke()

            # Icon — dots (menu)
            if self._panel_visible:
                # X icon
                cr.set_source_rgba(*c, 1.0)
                cr.set_line_width(2.0)
                cr.move_to(w/2-6, h/2-6); cr.line_to(w/2+6, h/2+6); cr.stroke()
                cr.move_to(w/2+6, h/2-6); cr.line_to(w/2-6, h/2+6); cr.stroke()
            else:
                # 3 dots
                cr.set_source_rgba(*c, 1.0)
                for dy in [-5, 0, 5]:
                    cr.arc(w/2, h/2+dy, 2.5, 0, 2*_math_btn.pi)
                    cr.fill()

        self._fab.set_draw_func(draw_fab)
        self._fab_t = 0
        GLib.timeout_add(50, self._tick_fab)

        fab_click = Gtk.GestureClick()
        fab_click.connect("pressed", self._on_fab_click)
        self._fab.add_controller(fab_click)

        fab_motion = Gtk.EventControllerMotion()
        fab_motion.connect("enter", lambda c,x,y: setattr(self,"_fab_hovered",True) or self._fab.queue_draw())
        fab_motion.connect("leave", lambda c: setattr(self,"_fab_hovered",False) or self._fab.queue_draw())
        self._fab.add_controller(fab_motion)

        toggle_wrap.append(self._fab)
        overlay.add_overlay(toggle_wrap)
        root.append(overlay)

        # Dashboard panel
        self._dashboard = DashboardPanel(overlay, self._dark)
        if self._taskbar:
            self._taskbar.set_dashboard_callback(self._on_dashboard_toggle)
            self._dashboard.set_rm(self._taskbar._rm)
            self._dashboard.set_gpu_info(self._taskbar._gpu_info)

        self._launcher  = AxonLauncher(parent_win=win, dark=self._dark)
        if ASK_OK:
            self._ask_axon = AskAxonWindow(
                dark=self._dark,
                on_submit=self._on_ask_axon_submit)

        kc = Gtk.EventControllerKey()
        kc.connect("key-pressed", self._on_key)
        win.add_controller(kc)

        win.present()
        log.info("Desktop ready")

    def _refresh_btn_style(self):
        txt = "#FFFFFF"
        bg  = "rgba(0,212,255,0.20)" if self._dark else "rgba(0,30,100,0.92)"
        bd  = "rgba(0,212,255,0.80)" if self._dark else "rgba(0,30,100,1.0)"
        for b in self._bottom_btns:
            p = Gtk.CssProvider()
            p.load_from_data((
                f"button {{ background: {bg}; border: 2px solid {bd};"
                f" border-radius: 18px; }}"
                f"button > label {{ color: {txt};"
                f" font-family: monospace; font-weight: bold; font-size: 12px; }}"
            ).encode())
            b.get_style_context().add_provider(p, 900)

    
    def _tick_fab(self):
        self._fab_t += 1
        if hasattr(self, "_fab") and self._fab:
            self._fab.queue_draw()
        return True

    def _on_logo_click(self, gesture, n, x, y):
        """الضغط على زر Ask Axon في المنتصف."""
        if self._ask_axon:
            self._ask_axon.toggle()
        elif self._launcher:
            self._launcher.show()

    def _on_ask_axon_submit(self, intent_text: str):
        """استقبال intent من المستخدم — جاهز للـ Orchestrator.""""
        log.info("Intent received: %s", intent_text)

    def _on_fab_click(self, gesture, n, x, y):
        self._panel_visible = not self._panel_visible
        self._action_panel.set_visible(self._panel_visible)
        if hasattr(self, "_fab"): self._fab.queue_draw()

    def _on_toggle_icons(self, btn):
        if self._side_panel:
            self._side_panel.toggle()

    def _on_force_restart(self, btn):
        log.warning("Force restart")
        try:
            dialog = Gtk.MessageDialog(
                transient_for=None, modal=True,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.YES_NO,
                text="Force Restart Axon OS?")
            dialog.connect("response", self._on_restart_response)
            dialog.present()
        except Exception as e:
            log.error("Restart dialog: %s", e); self._do_restart()

    def _on_restart_response(self, dialog, response):
        dialog.destroy()
        if response == Gtk.ResponseType.YES: self._do_restart()

    def _do_restart(self):
        axon_root = os.path.expanduser("~/AxonOS")
        main_py   = f"{axon_root}/platform/gui/desktop-environment/main.py"
        if PM_OK:
            _pm.launch("restart_desktop",
                       ["bash", "-c", f"sleep 1 && python3 {main_py} &"],
                       single_instance=False)
        else:
            import subprocess
            subprocess.Popen(
                ["bash", "-c", f"sleep 1 && python3 {main_py} &"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if GTK_OK: self.quit()

    def _on_dashboard_toggle(self):
        if self._dashboard:
            self._dashboard.toggle()

    def _on_theme_toggle(self):
        self._dark = True  # dark only
        self._apply_theme()

    def _on_icon(self, name, key):
        log.info("Icon clicked: %s", key)

        if key == "dashboard":
            if self._dashboard:
                self._dashboard.toggle()

        elif key == "terminal":
            if PM_OK:
                _pm.launch_app("terminal")
            else:
                import subprocess
                try: subprocess.Popen(["gnome-terminal"])
                except Exception as e: log.error("Terminal: %s", e)

        elif key == "files":
            if PM_OK:
                _pm.launch_app("file_manager")
            else:
                import subprocess
                try: subprocess.Popen(["nautilus"])
                except Exception as e: log.error("Files: %s", e)

        elif key == "ai":
            try:
                import sys
                _ASSIST = os.path.join(
                    os.path.expanduser("~/AxonOS/platform/gui/assistant"))
                if _ASSIST not in sys.path:
                    sys.path.insert(0, _ASSIST)
                from assistant_window import AssistantWindow
                if not hasattr(self, "_assistant") or self._assistant is None:
                    self._assistant = AssistantWindow()
                self._assistant.show()
            except Exception as e:
                log.error("Assistant: %s", e)
                if PM_OK:
                    _pm.launch("ai_fallback", [
                        "gnome-terminal", "--", "python3",
                        os.path.expanduser(
                            "~/AxonOS/platform/gui/assistant/assistant_window.py")
                    ])

        elif key == "settings":
            if PM_OK:
                _pm.launch_app("settings")
            else:
                import subprocess
                try: subprocess.Popen(["gnome-control-center"])
                except Exception as e: log.error("Settings: %s", e)

        elif key == "axonai":
            if self._launcher:
                self._launcher.toggle()

    def _on_launcher_btn(self, btn):
        if self._launcher: self._launcher.toggle()

    def _on_key(self, ctrl, keyval, code, state):
        if keyval in (Gdk.KEY_Super_L, Gdk.KEY_F1):
            if self._launcher: self._launcher.toggle()
            return True
        if keyval == Gdk.KEY_F2:
            self._on_toggle_icons(None); return True
        return False

    def _load_css(self):
        if not GTK_OK: return
        css_name = "axon-dark.css" if self._dark else "axon-light.css"
        css_path = os.path.join(_THEMES_DIR, css_name)
        if os.path.exists(css_path):
            try:
                p = Gtk.CssProvider()
                p.load_from_path(css_path)
                Gtk.StyleContext.add_provider_for_display(
                    Gdk.Display.get_default(), p,
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            except Exception as e:
                log.warning("CSS: %s", e)

    def _apply_theme(self):
        self._load_css()
        pass  # no bottom btns
        if self._side_panel:
            self._side_panel.set_theme(self._dark)
        if self._taskbar and hasattr(self._taskbar, "set_theme"):
            self._taskbar.set_theme(self._dark)
        if self._launcher and hasattr(self._launcher, "set_theme"):
            self._launcher.set_theme(self._dark)
        if self._dashboard and hasattr(self._dashboard, "set_theme"):
            self._dashboard.set_theme(self._dark)
        log.info("Theme: %s", "dark" if self._dark else "light")

    def launch(self):
        if GTK_OK: self.run(None)
        else: print(f"[Axon Desktop] Headless - {AXON_NAME} {AXON_VERSION}")


def main():
    app = AxonDesktop()
    app.launch()

if __name__ == "__main__":
    main()
