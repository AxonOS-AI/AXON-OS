# AxonOS/platform/gui/desktop-environment/taskbar.py
# Copyright (c) 2024 Abdullah -- Axon OS Project (AGPL-3.0)

import os, sys, datetime, logging, json

_HERE        = os.path.dirname(os.path.abspath(__file__))
_GUI_DIR     = os.path.dirname(_HERE)
_PLATFORM    = os.path.dirname(_GUI_DIR)
_ROOT        = os.path.dirname(_PLATFORM)
_THEMES_DIR  = os.path.join(_GUI_DIR, "themes")
_RM_DIR      = os.path.join(_PLATFORM, "core-services", "resource-manager")
_CORE_DIR    = os.path.join(_PLATFORM, "core-services")

for _p in [_ROOT, _PLATFORM, _CORE_DIR, _RM_DIR, _THEMES_DIR, _GUI_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

log = logging.getLogger("axon.taskbar")

try:
    import gi
    gi.require_version("Gtk", "4.0")
    from gi.repository import Gtk, GLib, Gdk
    GTK_OK = True
except (ImportError, ValueError):
    GTK_OK = False

AXON_NAME      = "AXON"
TASKBAR_HEIGHT = 44

DARK_CSS = b"""
box#taskbar {
    background: rgba(3,5,14,0.97);
    border-bottom: 1.5px solid rgba(0,212,255,0.25);
}
button {
    background: rgba(0,212,255,0.10);
    border: 1.5px solid rgba(0,212,255,0.50);
    border-radius: 8px;
    color: #00D4FF;
    font-family: "Courier New", monospace;
    font-size: 11px;
    font-weight: bold;
    padding: 2px 10px;
    box-shadow: none;
}
button:hover {
    background: rgba(0,212,255,0.25);
    border-color: #00D4FF;
    color: #FFFFFF;
}
togglebutton {
    background: rgba(5,8,18,0.80);
    border: 1.5px solid rgba(0,212,255,0.30);
    border-radius: 6px;
    color: #4A6080;
    font-family: monospace;
    font-size: 11px;
    padding: 2px 8px;
}
togglebutton:checked {
    background: rgba(0,212,255,0.20);
    border-color: #00D4FF;
    color: #00D4FF;
}
label {
    color: #E8EDF5;
    font-family: "Courier New", monospace;
    font-size: 11px;
}
progressbar trough {
    background: rgba(5,8,18,0.80);
    border-radius: 4px;
    min-height: 4px;
}
progressbar progress {
    background: #00D4FF;
    border-radius: 4px;
}
"""

LIGHT_CSS = b"""
box#taskbar {
    background: rgba(240,242,245,0.97);
    border-bottom: 1.5px solid rgba(0,56,120,0.25);
}
button {
    background: rgba(0,56,120,0.12);
    border: 1.5px solid rgba(0,56,120,0.55);
    border-radius: 8px;
    color: #003878;
    font-family: "Courier New", monospace;
    font-size: 11px;
    font-weight: bold;
    padding: 2px 10px;
    box-shadow: none;
}
button:hover {
    background: rgba(0,56,120,0.25);
    color: #001A40;
}
togglebutton {
    background: rgba(240,242,245,0.90);
    border: 1.5px solid rgba(0,56,120,0.30);
    border-radius: 6px;
    color: #4A6080;
    font-family: monospace;
    font-size: 11px;
    padding: 2px 8px;
}
togglebutton:checked {
    background: rgba(0,56,120,0.18);
    border-color: #003878;
    color: #003878;
}
label {
    color: #0F172A;
    font-family: "Courier New", monospace;
    font-size: 11px;
}
progressbar trough {
    background: rgba(0,56,120,0.15);
    border-radius: 4px;
    min-height: 4px;
}
progressbar progress {
    background: #003878;
    border-radius: 4px;
}
"""


class AxonTaskbar:
    def __init__(self, on_theme_toggle=None):
        self._on_theme_toggle    = on_theme_toggle
        self._on_dashboard_toggle = None
        self._rm          = None
        self._gpu_info    = None
        self._cpu_box     = None
        self._ram_box     = None
        self._disk_box    = None
        self._gpu_label   = None
        self._gpu_badge   = None
        self._train_bar   = None
        self._train_label = None
        self._clock_label = None
        self._ws_buttons  = []
        self._dark        = True
        self._dash_btn    = None

        self.widget = self._build()
        self._apply_css()
        self._start_rm()
        if GTK_OK:
            self._schedule()

    def _build(self):
        if not GTK_OK: return None

        bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        bar.set_name("taskbar")
        bar.set_size_request(-1, TASKBAR_HEIGHT)
        bar.set_margin_start(8); bar.set_margin_end(8)

        # Logo
        logo = Gtk.Button(label=f"Ax {AXON_NAME}")
        logo.connect("clicked", self._on_menu)
        bar.append(logo)

        # Workspace
        ws_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        for i in range(1, 5):
            b = Gtk.ToggleButton(label=str(i))
            b.connect("clicked", self._on_ws, i)
            self._ws_buttons.append(b)
            ws_box.append(b)
        if self._ws_buttons:
            self._ws_buttons[0].set_active(True)
        bar.append(ws_box)

        # Spacer
        sp = Gtk.Box(); sp.set_hexpand(True)
        bar.append(sp)

        # Metrics
        self._cpu_box  = self._metric("CPU",  "N/A")
        self._ram_box  = self._metric("RAM",  "N/A")
        self._disk_box = self._metric("DISK", "N/A")
        bar.append(self._cpu_box)
        bar.append(self._ram_box)
        bar.append(self._disk_box)

        # GPU
        gpu_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        self._gpu_label = Gtk.Label(label="GPU")
        self._gpu_badge = Gtk.Label(label="N/A")
        gpu_box.append(self._gpu_label)
        gpu_box.append(self._gpu_badge)
        bar.append(gpu_box)

        # Training
        train_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        tlbl = Gtk.Label(label="Train")
        self._train_bar = Gtk.ProgressBar()
        self._train_bar.set_fraction(0.0)
        self._train_bar.set_size_request(60, 4)
        self._train_label = Gtk.Label(label="0%")
        train_box.append(tlbl)
        train_box.append(self._train_bar)
        train_box.append(self._train_label)
        bar.append(train_box)

        # Dashboard
        self._dash_btn = Gtk.Button(label="Monitor")
        self._dash_btn.connect("clicked", self._on_dashboard)
        bar.append(self._dash_btn)



        # Clock
        self._clock_label = Gtk.Label(label="--:--")
        bar.append(self._clock_label)

        return bar

    def _metric(self, label, value):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        box.append(Gtk.Label(label=label))
        val = Gtk.Label(label=value)
        box.append(val)
        box._val = val
        return box

    def _apply_css(self):
        if not GTK_OK or not self.widget: return
        css = DARK_CSS if self._dark else LIGHT_CSS
        p = Gtk.CssProvider()
        p.load_from_data(css)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(), p,
            Gtk.STYLE_PROVIDER_PRIORITY_USER + 999)

    def _start_rm(self):
        try:
            from resource_manager import ResourceManager
            self._rm = ResourceManager(); self._rm.start()
        except Exception as e:
            log.warning("ResourceManager: %s", e)
        try:
            from gpu_detector import get_gpu_info
            self._gpu_info = get_gpu_info()
            if self._gpu_badge:
                self._gpu_badge.set_text(self._gpu_info.status_label)
        except Exception as e:
            log.warning("GPU: %s", e)

    def _schedule(self):
        GLib.timeout_add_seconds(1, self._tick_clock)
        GLib.timeout_add_seconds(2, self._tick_resources)
        GLib.timeout_add_seconds(5, self._tick_training)

    def _tick_clock(self):
        if self._clock_label:
            self._clock_label.set_text(
                datetime.datetime.now().strftime("%H:%M"))
        return True

    def _tick_resources(self):
        if not self._rm: return True
        try:
            s = self._rm.get_snapshot()
            if hasattr(self._cpu_box,  "_val"):
                self._cpu_box._val.set_text(f"{s.cpu_percent:.0f}%")
            if hasattr(self._ram_box,  "_val"):
                self._ram_box._val.set_text(f"{s.ram_percent:.0f}%")
            if hasattr(self._disk_box, "_val"):
                self._disk_box._val.set_text(f"{s.disk_percent:.0f}%")
        except Exception as e:
            log.warning("resources: %s", e)
        return True

    def _tick_training(self):
        p = os.path.expanduser("~/.axonos/training_progress.json")
        if not os.path.exists(p): return True
        try:
            data = json.loads(open(p).read())
            pct  = float(data.get("progress", 0.0)) / 100.0
            if self._train_bar:
                self._train_bar.set_fraction(min(1.0, pct))
            if self._train_label:
                self._train_label.set_text(f"{int(pct*100)}%")
        except Exception:
            pass
        return True

    def set_dashboard_callback(self, cb):
        self._on_dashboard_toggle = cb

    def _on_dashboard(self, btn):
        if self._on_dashboard_toggle:
            self._on_dashboard_toggle()

    def _on_menu(self, btn):
        log.info("menu clicked")

    def _on_ws(self, btn, n):
        for b in self._ws_buttons:
            if b is not btn: b.set_active(False)

    def set_theme(self, dark):
        self._dark = dark
        self._apply_css()

    def _on_theme(self, btn):
        self._dark = not self._dark
        self._apply_css()
        if self._on_theme_toggle:
            self._on_theme_toggle()

    def get_clock_text(self):
        return datetime.datetime.now().strftime("%H:%M")
