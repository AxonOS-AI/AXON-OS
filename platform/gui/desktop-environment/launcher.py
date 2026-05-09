# AxonOS/platform/gui/desktop-environment/launcher.py
# Copyright (c) 2024 Abdullah -- Axon OS Project (AGPL-3.0)

import os, sys, logging, math

_HERE     = os.path.dirname(os.path.abspath(__file__))
_GUI_DIR  = os.path.dirname(_HERE)
_PLATFORM = os.path.dirname(_GUI_DIR)
_ROOT     = os.path.dirname(_PLATFORM)
_THEMES   = os.path.join(_GUI_DIR, "themes")

for _p in [_ROOT, _PLATFORM, _THEMES]:
    if _p not in sys.path: sys.path.insert(0, _p)

log = logging.getLogger("axon.launcher")

try:
    import gi
    gi.require_version("Gtk", "4.0")
    from gi.repository import Gtk, Gdk, GLib
    import cairo
    GTK_OK = True
except (ImportError, ValueError):
    GTK_OK = False

AXON_NAME = "AXON"

# ── App Registry ─────────────────────────────────────────────────────
# التطبيقات تُقرأ من apps_config.json — لا تعدّل هذه القائمة يدوياً
_DEFAULT_APPS = [
    ("Firefox",          "firefox",   "firefox",          "web",    "blue"),
    ("Jupyter Notebook", "jupyter",   "jupyter-notebook", "ai",     "purple"),
    ("Dashboard",        "dashboard", "dashboard",        "system", "cyan"),
    ("Project Manager",  "project",   "project_manager",  "tools",  "purple"),
    ("File Manager",     "files",     "file_manager",     "tools",  "cyan"),
    ("Training Console", "training",  "training_console", "ai",     "green"),
    ("AI Assistant",     "ai",        "ai_assistant",     "ai",     "purple"),
    ("Jupyter Lab",      "jupyter",   "jupyter_lab",      "ai",     "green"),
    ("Resource Monitor", "monitor",   "resource_monitor", "system", "cyan"),
    ("Update Manager",   "update",    "update_manager",   "system", "green"),
    ("Settings",         "settings",  "settings",         "system", "cyan"),
    ("Terminal",         "terminal",  "terminal",         "tools",  "green"),
    ("Model Loader",     "model",     "model_loader",     "ai",     "purple"),
]

def _load_apps():
    import json as _json
    import os as _os
    _cfg = _os.path.join(_PLATFORM, "apps_config.json")
    try:
        with open(_cfg, "r", encoding="utf-8") as _f:
            _data = _json.load(_f)
        _apps = [
            (a["name"], a["icon"], a["cmd"], a["category"], a["color"])
            for a in _data.get("apps", [])
        ]
        if not _apps:
            raise ValueError("قائمة التطبيقات فارغة")
        log.info("apps_config.json loaded: %d apps", len(_apps))
        return _apps
    except FileNotFoundError:
        log.warning("apps_config.json غير موجود — تحميل القائمة الافتراضية")
        return _DEFAULT_APPS
    except Exception as _e:
        log.error("خطأ في apps_config.json: %s — تحميل القائمة الافتراضية", _e)
        return _DEFAULT_APPS

AXON_APPS = _load_apps()

def _draw_app_icon(cr, cx, cy, size, icon_key, dark, color_hint="cyan"):
    s = size / 44.0
    if color_hint == "cyan":
        c = (0.00, 0.83, 1.00) if dark else (0.00, 0.39, 0.78)
    elif color_hint == "purple":
        c = (0.42, 0.24, 0.88) if dark else (0.32, 0.19, 0.69)
    else:
        c = (0.11, 0.62, 0.46) if dark else (0.07, 0.50, 0.36)

    bg = 0.14 if dark else 0.10
    cr.save()
    cr.translate(cx, cy)
    cr.scale(s, s)
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.set_line_join(cairo.LINE_JOIN_ROUND)

    if icon_key == "dashboard":
        for ox, oy in [(-7,-7),(2,-7),(-7,2),(2,2)]:
            cr.rectangle(ox, oy, 8, 8)
            cr.set_source_rgba(*c, bg); cr.fill_preserve()
            cr.set_source_rgba(*c, 1); cr.set_line_width(1.5); cr.stroke()

    elif icon_key == "project":
        for ox in [-10, -1, 8]:
            cr.rectangle(ox, -12, 7, 22)
            cr.set_source_rgba(*c, bg); cr.fill_preserve()
            cr.set_source_rgba(*c, 1); cr.set_line_width(1.5); cr.stroke()
        for ox, h in [(-9,-8),(-9,-1),(0,-8),(0,-1),(9,-8)]:
            cr.rectangle(ox, h, 5, 5)
            cr.set_source_rgba(*c, 0.5); cr.fill()

    elif icon_key == "files":
        cr.move_to(-13,-2); cr.line_to(-13,13); cr.line_to(13,13)
        cr.line_to(13,1); cr.line_to(4,1); cr.line_to(1,-2); cr.close_path()
        cr.set_source_rgba(*c, bg); cr.fill_preserve()
        cr.set_source_rgba(*c, 1); cr.set_line_width(2); cr.stroke()
        for y in [4,7,10]:
            cr.move_to(-9,y); cr.line_to(9,y)
            cr.set_source_rgba(*c, 0.5); cr.set_line_width(1); cr.stroke()

    elif icon_key == "training":
        pts = [(-13,10),(-7,4),(0,8),(7,-2),(13,-10)]
        cr.move_to(*pts[0])
        for p in pts[1:]: cr.line_to(*p)
        cr.set_source_rgba(*c, 1); cr.set_line_width(2.5); cr.stroke()
        for x,y in pts:
            cr.arc(x,y,2.5,0,2*math.pi)
            cr.set_source_rgba(*c, 1); cr.fill()
        cr.move_to(-13,13); cr.line_to(-13,-13)
        cr.move_to(-13,13); cr.line_to(13,13)
        cr.set_source_rgba(*c, 0.3); cr.set_line_width(1); cr.stroke()

    elif icon_key == "ai":
        left = [(-13,-8),(-13,0),(-13,8)]
        mid  = [(0,-5),(0,5)]
        right= [(13,-8),(13,8)]
        for x1,y1 in left:
            for x2,y2 in mid:
                cr.move_to(x1,y1); cr.line_to(x2,y2)
                cr.set_source_rgba(*c, 0.3); cr.set_line_width(1); cr.stroke()
        for x1,y1 in mid:
            for x2,y2 in right:
                cr.move_to(x1,y1); cr.line_to(x2,y2)
                cr.set_source_rgba(*c, 0.3); cr.set_line_width(1); cr.stroke()
        for x,y in left+mid+right:
            cr.arc(x,y,3,0,2*math.pi)
            cr.set_source_rgba(*c, 1); cr.fill()

    elif icon_key == "monitor":
        cr.rectangle(-13,-10,26,18)
        cr.set_source_rgba(*c, bg); cr.fill_preserve()
        cr.set_source_rgba(*c, 1); cr.set_line_width(2); cr.stroke()
        cr.move_to(-4,8); cr.line_to(-6,13)
        cr.move_to(4,8);  cr.line_to(6,13)
        cr.move_to(-8,13); cr.line_to(8,13)
        cr.set_source_rgba(*c, 1); cr.set_line_width(1.5); cr.stroke()
        pts2=[(-9,0),(-5,0),(-3,-5),(0,5),(3,-3),(5,0),(9,0)]
        cr.move_to(*pts2[0])
        for p in pts2[1:]: cr.line_to(*p)
        cr.set_source_rgba(*c, 1); cr.set_line_width(1.5); cr.stroke()

    elif icon_key == "update":
        cr.arc(0,0,10,math.pi*0.2,math.pi*1.9)
        cr.set_source_rgba(*c, 1); cr.set_line_width(2.5); cr.stroke()
        cr.move_to(8,-6); cr.line_to(12,-1); cr.line_to(4,-1)
        cr.set_source_rgba(*c, 1); cr.fill()
        cr.move_to(0,-4); cr.line_to(0,4)
        cr.move_to(-3,2); cr.line_to(0,5); cr.line_to(3,2)
        cr.set_source_rgba(*c, 0.7); cr.set_line_width(1.5); cr.stroke()

    elif icon_key == "settings":
        for i in range(8):
            a = i*math.pi/4
            cr.move_to(math.cos(a)*7,math.sin(a)*7)
            cr.line_to(math.cos(a)*12,math.sin(a)*12)
            cr.set_source_rgba(*c, 1); cr.set_line_width(2.5); cr.stroke()
        cr.arc(0,0,6,0,2*math.pi)
        cr.set_source_rgba(*c, bg); cr.fill_preserve()
        cr.set_source_rgba(*c, 1); cr.set_line_width(2); cr.stroke()
        cr.arc(0,0,2.5,0,2*math.pi)
        cr.set_source_rgba(*c, 1); cr.fill()

    elif icon_key == "terminal":
        cr.rectangle(-13,-12,26,22)
        cr.set_source_rgba(*c, bg); cr.fill_preserve()
        cr.set_source_rgba(*c, 1); cr.set_line_width(2); cr.stroke()
        cr.rectangle(-13,-12,26,5)
        cr.set_source_rgba(*c, 0.2); cr.fill()
        for dx in [-8,-4,0]:
            cr.arc(dx,-10,1.5,0,2*math.pi)
            cr.set_source_rgba(*c, 0.7); cr.fill()
        cr.move_to(-9,-3); cr.line_to(-3,0); cr.line_to(-9,3)
        cr.set_source_rgba(*c, 1); cr.set_line_width(2); cr.stroke()
        cr.rectangle(-1,2,8,2)
        cr.set_source_rgba(*c, 0.8); cr.fill()

    elif icon_key == "firefox":
        # Firefox icon (théière stylisée)
        cr.arc(0, 0, 12, 0, 2*math.pi)
        cr.set_source_rgba(*c, bg); cr.fill_preserve()
        cr.set_source_rgba(*c, 1); cr.set_line_width(1.5); cr.stroke()
        # جسم الثعلب
        cr.save()
        cr.translate(6, -2)
        cr.scale(0.8, 0.9)
        cr.arc(0, 0, 5, 0, 2*math.pi)
        cr.set_source_rgba(1, 0.5, 0.2, 0.9)
        cr.fill()
        cr.restore()
        # أذن
        cr.move_to(8, -10); cr.line_to(12, -14); cr.line_to(12, -8); cr.close_path()
        cr.set_source_rgba(1, 0.5, 0.2, 0.9); cr.fill()
        # عين
        cr.arc(10, -2, 1.2, 0, 2*math.pi)
        cr.set_source_rgba(0, 0, 0, 1); cr.fill()
    elif icon_key == "jupyter":
        # Jupyter icon — دائرة + حلقات
        cr.arc(0, -4, 10, 0, 2*math.pi)
        cr.set_source_rgba(*c, 0.12); cr.fill_preserve()
        cr.set_source_rgba(*c, 1); cr.set_line_width(2); cr.stroke()
        cr.arc(0, -4, 5, 0, 2*math.pi)
        cr.set_source_rgba(*c, 0.3); cr.fill()
        for i in range(3):
            a = i * 2 * math.pi / 3 - math.pi/2
            cx2 = math.cos(a) * 7
            cy2 = math.sin(a) * 7 - 4
            cr.arc(cx2, cy2, 2.5, 0, 2*math.pi)
            cr.set_source_rgba(*c, 1); cr.fill()
        # J text
        cr.select_font_face("Courier New", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(8)
        cr.set_source_rgba(*c, 1)
        cr.move_to(-3, 12); cr.show_text("nb")

    elif icon_key == "model":
        cr.rectangle(-10,-10,20,20)
        cr.set_source_rgba(*c, bg); cr.fill_preserve()
        cr.set_source_rgba(*c, 1); cr.set_line_width(2); cr.stroke()
        cr.rectangle(-6,-6,12,12)
        cr.set_source_rgba(*c, 0.12); cr.fill_preserve()
        cr.set_source_rgba(*c, 1); cr.set_line_width(1); cr.stroke()
        for x in [-4,4]:
            cr.move_to(x,-10); cr.line_to(x,-14)
            cr.move_to(x,10);  cr.line_to(x,14)
            cr.set_source_rgba(*c, 0.8); cr.set_line_width(1.5); cr.stroke()
        for y in [-4,4]:
            cr.move_to(-10,y); cr.line_to(-14,y)
            cr.move_to(10,y);  cr.line_to(14,y)
            cr.set_source_rgba(*c, 0.8); cr.set_line_width(1.5); cr.stroke()
        cr.select_font_face("monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(7)
        ext = cr.text_extents("AI")
        cr.move_to(-ext.width/2-ext.x_bearing, -ext.height/2-ext.y_bearing)
        cr.set_source_rgba(*c, 1); cr.show_text("AI")

    cr.restore()


class AppCard(Gtk.Box):
    BADGE_COL = {
        "ai":     (0.42, 0.24, 0.88),
        "system": (0.00, 0.60, 0.80),
        "tools":  (0.11, 0.62, 0.46),
    }

    def __init__(self, name, icon_key, cmd_key, cat, color_hint, dark=True, on_click=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._icon_key  = icon_key
        self._color     = color_hint
        self._dark      = dark
        self._hovered   = False
        self._callback  = on_click
        self._cmd_key   = cmd_key
        self._name      = name
        self._cat       = cat
        self.set_size_request(130, 118)
        self.set_margin_top(4); self.set_margin_bottom(4)
        self.set_margin_start(4); self.set_margin_end(4)

        self._area = Gtk.DrawingArea()
        self._area.set_size_request(130, 68)
        self._area.set_draw_func(self._draw_card)
        self.append(self._area)

        self._lbl = Gtk.Label(label=name)
        self._lbl.set_wrap(True)
        self._lbl.set_justify(Gtk.Justification.CENTER)
        self._lbl.set_margin_top(3)
        self._lbl.set_margin_start(4); self._lbl.set_margin_end(4)
        self.append(self._lbl)

        self._badge = Gtk.Label(label=cat.upper())
        self._badge.set_margin_top(2)
        self.append(self._badge)

        click = Gtk.GestureClick()
        click.connect("pressed", self._on_press)
        self.add_controller(click)

        motion = Gtk.EventControllerMotion()
        motion.connect("enter", self._on_enter)
        motion.connect("leave", self._on_leave)
        self.add_controller(motion)

        self._apply_style()

    def _apply_style(self):
        d = self._dark
        txt = "#E8EDF5" if d else "#0F172A"
        bg  = "rgba(10,14,26,0.95)" if d else "rgba(255,255,255,0.95)"
        bd  = "rgba(0,212,255,0.30)" if d else "rgba(15,23,42,0.25)"

        css = f"""
        box {{
            background: {bg};
            border: 1.5px solid {bd};
            border-radius: 14px;
        }}
        label {{ color: {txt}; font-family: "Courier New", monospace; font-size: 11px; }}
        """.encode()
        p = Gtk.CssProvider()
        p.load_from_data(css)
        self.get_style_context().add_provider(p, Gtk.STYLE_PROVIDER_PRIORITY_USER + 1)

        bc = self.BADGE_COL.get(self._cat, (0.5,0.5,0.5))
        badge_css = (
            f'label {{ color: rgba({int(bc[0]*255)},{int(bc[1]*255)},{int(bc[2]*255)},1);'
            f' background: rgba({int(bc[0]*255)},{int(bc[1]*255)},{int(bc[2]*255)},0.15);'
            f' border-radius: 8px; padding: 1px 6px; font-size: 9px; font-weight: bold; }}'
        ).encode()
        bp = Gtk.CssProvider()
        bp.load_from_data(badge_css)
        self._badge.get_style_context().add_provider(bp, Gtk.STYLE_PROVIDER_PRIORITY_USER + 2)

    def _draw_card(self, area, cr, w, h):
        if self._hovered:
            cr.set_source_rgba(0.00, 0.83 if self._dark else 0.39, 1.00, 0.10)
            cr.rectangle(0, 0, w, h)
            cr.fill()
        _draw_app_icon(cr, w/2, h/2, min(w,h)*0.75, self._icon_key, self._dark, self._color)

    def _on_enter(self, ctrl, x, y):
        self._hovered = True
        self._area.queue_draw()
        bd = "rgba(0,212,255,0.85)" if self._dark else "rgba(15,23,42,0.70)"
        css = f"box {{ border: 1.5px solid {bd}; border-radius: 14px; }}".encode()
        p = Gtk.CssProvider()
        p.load_from_data(css)
        self.get_style_context().add_provider(p, Gtk.STYLE_PROVIDER_PRIORITY_USER + 3)

    def _on_leave(self, ctrl):
        self._hovered = False
        self._area.queue_draw()
        self._apply_style()

    def _on_press(self, gesture, n, x, y):
        if self._callback: self._callback(self._cmd_key, self._name)

    def set_theme(self, dark):
        self._dark = dark
        self._apply_style()
        self._area.queue_draw()


class AxonLauncher:
    def __init__(self, parent_win=None, dark=True):
        self._parent     = parent_win
        self._visible    = False
        self._window     = None
        self._grid       = None
        self._search     = None
        self._filter_cat = None
        self._dark       = dark
        self._cards      = []
        if GTK_OK and parent_win:
            self._build(parent_win)

    def _build(self, parent):
        self._window = Gtk.Window()
        self._window.set_title(f"{AXON_NAME} OS — Launcher")
        self._window.set_transient_for(parent)
        self._window.set_modal(True)
        self._window.set_default_size(860, 620)
        self._window.connect("close-request", self._on_close_request)
        self._apply_window_theme()

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        root.set_margin_top(18); root.set_margin_bottom(18)
        root.set_margin_start(18); root.set_margin_end(18)
        self._window.set_child(root)

        # Header
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        logo = Gtk.DrawingArea()
        logo.set_size_request(72, 34)
        logo.set_draw_func(self._draw_logo)
        header.append(logo)

        title = Gtk.Label(label="AXON OS")
        tc = "color: #00D4FF;" if self._dark else "color: #0064C8;"
        tcss = f"label {{ font-family: 'Courier New',monospace; font-size: 19px; font-weight: bold; {tc} }}".encode()
        tp = Gtk.CssProvider(); tp.load_from_data(tcss)
        title.get_style_context().add_provider(tp, Gtk.STYLE_PROVIDER_PRIORITY_USER+1)
        header.append(title)

        sp = Gtk.Box(); sp.set_hexpand(True)
        header.append(sp)

        self._search = Gtk.SearchEntry()
        self._search.set_placeholder_text("Search apps...")
        self._search.set_size_request(210, 34)
        self._search.connect("search-changed", self._on_search)
        header.append(self._search)
        root.append(header)

        # Separator
        sep = Gtk.DrawingArea()
        sep.set_size_request(-1, 2)
        sep.set_draw_func(self._draw_sep)
        root.append(sep)

        # Category buttons
        cat_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        cat_box.set_margin_top(4)
        self._cat_btns = {}
        for cat, lbl in [(None,"⊞  All"),("system","⚙  System"),("tools","🛠  Tools"),("ai","◉  AI")]:
            b = Gtk.ToggleButton(label=lbl)
            if cat is None: b.set_active(True)
            self._style_cat_btn(b, cat is None)
            b.connect("clicked", self._on_category, cat)
            self._cat_btns[str(cat)] = b
            cat_box.append(b)
        root.append(cat_box)

        # Grid
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_margin_top(8)
        self._grid = Gtk.FlowBox()
        self._grid.set_max_children_per_line(5)
        self._grid.set_min_children_per_line(3)
        self._grid.set_selection_mode(Gtk.SelectionMode.NONE)
        self._grid.set_homogeneous(True)
        self._grid.set_row_spacing(10)
        self._grid.set_column_spacing(10)
        scroll.set_child(self._grid)
        root.append(scroll)

        self._populate(AXON_APPS)

        kc = Gtk.EventControllerKey()
        kc.connect("key-pressed", self._on_key)
        self._window.add_controller(kc)

    def _draw_logo(self, area, cr, w, h):
        c = (0.00, 0.83, 1.00) if self._dark else (0.00, 0.39, 0.78)
        cr.rectangle(3, 3, w-6, h-6)
        cr.set_source_rgba(*c, 0.12); cr.fill_preserve()
        cr.set_source_rgba(*c, 0.7); cr.set_line_width(1.5); cr.stroke()
        cr.select_font_face("Courier New", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(15)
        ext = cr.text_extents("Ax")
        cr.move_to(w/2-ext.width/2-ext.x_bearing, h/2-ext.height/2-ext.y_bearing)
        cr.set_source_rgba(*c, 1); cr.show_text("Ax")

    def _draw_sep(self, area, cr, w, h):
        c = (0.00, 0.83, 1.00) if self._dark else (0.00, 0.39, 0.78)
        g = cairo.LinearGradient(0,0,w,0)
        g.add_color_stop_rgba(0.0, *c, 0.0)
        g.add_color_stop_rgba(0.3, *c, 0.8)
        g.add_color_stop_rgba(0.7, *c, 0.8)
        g.add_color_stop_rgba(1.0, *c, 0.0)
        cr.set_source(g); cr.rectangle(0,0,w,2); cr.fill()

    def _style_cat_btn(self, btn, active=False):
        if active:
            css = (
                "button { background: rgba(0,212,255,0.20); border: 1.5px solid rgba(0,212,255,0.70);"
                " border-radius: 20px; color: #00D4FF; font-family: monospace;"
                " font-size: 12px; font-weight: bold; padding: 2px 14px; }"
            ) if self._dark else (
                "button { background: rgba(0,100,200,0.15); border: 1.5px solid #0064C8;"
                " border-radius: 20px; color: #0064C8; font-family: monospace;"
                " font-size: 12px; font-weight: bold; padding: 2px 14px; }"
            )
        else:
            css = (
                "button { background: rgba(255,255,255,0.04); border: 1.5px solid rgba(255,255,255,0.10);"
                " border-radius: 20px; color: #8899BB; font-family: monospace;"
                " font-size: 12px; padding: 2px 14px; }"
            ) if self._dark else (
                "button { background: rgba(0,0,0,0.04); border: 1.5px solid rgba(0,0,0,0.12);"
                " border-radius: 20px; color: #4A6080; font-family: monospace;"
                " font-size: 12px; padding: 2px 14px; }"
            )
        p = Gtk.CssProvider(); p.load_from_data(css.encode())
        btn.get_style_context().add_provider(p, Gtk.STYLE_PROVIDER_PRIORITY_USER+1)

    def _apply_window_theme(self):
        if not self._window: return
        css = b"""
        window { background-color: #070A14; }
        window > * { background-color: #070A14; color: #E8EDF5; }
        box { background-color: transparent; }
        label { color: #E8EDF5; }
        searchentry { background-color: #111827; color: #E8EDF5;
            border: 1.5px solid rgba(0,212,255,0.35); border-radius: 8px;
            caret-color: #00D4FF; font-family: "Courier New",monospace; }
        searchentry:focus { border-color: rgba(0,212,255,0.75); }
        scrolledwindow, viewport { background-color: transparent; }
        flowbox, flowboxchild { background-color: transparent; }
        """ if self._dark else b"""
        window { background-color: #F0F2F5; }
        window > * { background-color: #F0F2F5; color: #0F172A; }
        box { background-color: transparent; }
        label { color: #0F172A; }
        searchentry { background-color: #FFFFFF; color: #0F172A;
            border: 1.5px solid rgba(15,23,42,0.30); border-radius: 8px;
            caret-color: #0064C8; font-family: "Courier New",monospace; }
        searchentry:focus { border-color: rgba(0,100,200,0.75); }
        scrolledwindow, viewport { background-color: transparent; }
        flowbox, flowboxchild { background-color: transparent; }
        """
        p = Gtk.CssProvider(); p.load_from_data(css)
        self._window.get_style_context().add_provider(p, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    def _populate(self, apps):
        if not GTK_OK: return
        self._cards = []
        child = self._grid.get_first_child()
        while child:
            nxt = child.get_next_sibling()
            self._grid.remove(child)
            child = nxt
        for name, icon_key, cmd_key, cat, color in apps:
            card = AppCard(name, icon_key, cmd_key, cat, color,
                           dark=self._dark, on_click=self._on_app)
            self._cards.append(card)
            self._grid.append(card)

    def _filtered(self, q="", cat=None):
        r = AXON_APPS
        if cat: r = [a for a in r if a[3] == cat]
        if q:   r = [a for a in r if q.lower() in a[0].lower()]
        return r

    def set_theme(self, dark):
        self._dark = dark
        self._apply_window_theme()
        for card in self._cards: card.set_theme(dark)
        if self._window: self._window.queue_draw()

    def _on_close_request(self, win):
        self.hide(); return True

    def _on_search(self, e):
        self._populate(self._filtered(e.get_text(), self._filter_cat))

    def _on_category(self, btn, cat):
        self._filter_cat = cat
        q = self._search.get_text() if self._search else ""
        self._populate(self._filtered(q, cat))

    def _on_app(self, key, name):
        import subprocess
        log.info("Launching: %s (%s)", name, key)
        self.hide()
        try:
            if key == "terminal":
                subprocess.Popen(["gnome-terminal"])
            elif key == "file_manager":
                subprocess.Popen(["nautilus"])
            elif key == "ai_assistant":
                import sys
                _dir = os.path.join(
                    os.path.dirname(os.path.dirname(
                    os.path.abspath(__file__))), "assistant")
                if _dir not in sys.path: sys.path.insert(0, _dir)
                from assistant_window import AssistantWindow
                if not hasattr(self, "_assistant") or not self._assistant:
                    self._assistant = AssistantWindow()
                self._assistant.show()
            elif key == "settings":
                subprocess.Popen(["gnome-control-center"])
            elif key == "resource_monitor":
                subprocess.Popen(["gnome-system-monitor"])
            elif key == "firefox":
                subprocess.Popen(["firefox"])
            else:
                subprocess.Popen(["gnome-terminal"])
                subprocess.Popen(["gnome-terminal"])
        except Exception as e:
            log.error("Launch error %s: %s", key, e)

    def _on_key(self, ctrl, keyval, code, state):
        if GTK_OK and keyval == Gdk.KEY_Escape:
            self.hide(); return True
        return False

    def show(self):
        if self._window:
            if self._search: self._search.set_text("")
            self._populate(AXON_APPS)
            self._window.present(); self._visible = True

    def hide(self):
        if self._window:
            self._window.hide(); self._visible = False

    def toggle(self):
        self.hide() if self._visible else self.show()

    def get_app_names(self):
        return [a[0] for a in AXON_APPS]
