import os, sys, math, logging
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path: sys.path.insert(0, _HERE)
log = logging.getLogger("axon.side_panel")
try:
    import gi
    gi.require_version("Gtk", "4.0")
    from gi.repository import Gtk, Gdk, GLib
    import cairo
    GTK_OK = True
except Exception:
    GTK_OK = False

PANEL_W = 80
ICON_SIZE = 48
SPACING = 14
ICONS = [
    ("Dashboard", "dashboard", (0.00, 0.83, 1.00)),
    ("Terminal",  "terminal",  (0.11, 0.78, 0.46)),
    ("Files",     "files",     (0.00, 0.65, 1.00)),
    ("AI",        "ai",        (0.62, 0.24, 0.98)),
    ("Settings",  "settings",  (0.00, 0.83, 1.00)),
    ("Axon AI",   "axonai",    (1.00, 0.42, 0.78)),
]

def _draw_icon(cr, cx, cy, size, key, color):
    s = size / 44.0
    c = color
    cr.save()
    cr.translate(cx, cy)
    cr.scale(s, s)
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.set_line_join(cairo.LINE_JOIN_ROUND)
    if key == "dashboard":
        for ox, oy in [(-7,-7),(2,-7),(-7,2),(2,2)]:
            cr.rectangle(ox, oy, 8, 8)
            cr.set_source_rgba(*c, 0.15); cr.fill_preserve()
            cr.set_source_rgba(*c, 1); cr.set_line_width(1.8); cr.stroke()
    elif key == "terminal":
        cr.rectangle(-13,-12,26,22)
        cr.set_source_rgba(*c, 0.12); cr.fill_preserve()
        cr.set_source_rgba(*c, 1); cr.set_line_width(2); cr.stroke()
        cr.rectangle(-13,-12,26,5)
        cr.set_source_rgba(*c, 0.25); cr.fill()
        cr.move_to(-8,-2); cr.line_to(-2,1); cr.line_to(-8,4)
        cr.set_source_rgba(*c, 1); cr.set_line_width(2); cr.stroke()
        cr.rectangle(-1,3,7,2)
        cr.set_source_rgba(*c, 0.9); cr.fill()
    elif key == "files":
        cr.move_to(-12,-2); cr.line_to(-12,13)
        cr.line_to(12,13); cr.line_to(12,1)
        cr.line_to(4,1); cr.line_to(1,-2); cr.close_path()
        cr.set_source_rgba(*c, 0.12); cr.fill_preserve()
        cr.set_source_rgba(*c, 1); cr.set_line_width(2); cr.stroke()
        for y in [4,7,10]:
            cr.move_to(-8,y); cr.line_to(8,y)
            cr.set_source_rgba(*c, 0.5); cr.set_line_width(1); cr.stroke()
    elif key == "ai":
        left=[(-12,-7),(-12,0),(-12,7)]
        mid=[(0,-4),(0,4)]
        right=[(12,-7),(12,7)]
        for x1,y1 in left:
            for x2,y2 in mid:
                cr.move_to(x1,y1); cr.line_to(x2,y2)
                cr.set_source_rgba(*c,0.3); cr.set_line_width(1); cr.stroke()
        for x1,y1 in mid:
            for x2,y2 in right:
                cr.move_to(x1,y1); cr.line_to(x2,y2)
                cr.set_source_rgba(*c,0.3); cr.set_line_width(1); cr.stroke()
        for x,y in left+mid+right:
            cr.arc(x,y,3,0,2*math.pi)
            cr.set_source_rgba(*c,1); cr.fill()
    elif key == "settings":
        for i in range(8):
            a = i*math.pi/4
            cr.move_to(math.cos(a)*7,math.sin(a)*7)
            cr.line_to(math.cos(a)*12,math.sin(a)*12)
            cr.set_source_rgba(*c,1); cr.set_line_width(2.5); cr.stroke()
        cr.arc(0,0,6,0,2*math.pi)
        cr.set_source_rgba(*c,0.15); cr.fill_preserve()
        cr.set_source_rgba(*c,1); cr.set_line_width(2); cr.stroke()
        cr.arc(0,0,2.5,0,2*math.pi)
        cr.set_source_rgba(*c,1); cr.fill()
    elif key == "axonai":
        cr.rectangle(-9,-9,18,18)
        cr.set_source_rgba(0.02,0.03,0.09,0.92); cr.fill_preserve()
        cr.set_source_rgba(*c,1); cr.set_line_width(2); cr.stroke()
        for x in [-4,4]:
            cr.move_to(x,-9); cr.line_to(x,-13)
            cr.move_to(x,9); cr.line_to(x,13)
            cr.set_source_rgba(*c,0.8); cr.set_line_width(1.5); cr.stroke()
        for y in [-3,3]:
            cr.move_to(-9,y); cr.line_to(-13,y)
            cr.move_to(9,y); cr.line_to(13,y)
            cr.set_source_rgba(*c,0.8); cr.set_line_width(1.5); cr.stroke()
        cr.select_font_face("Courier New",cairo.FONT_SLANT_NORMAL,cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(8)
        ext = cr.text_extents("Ax")
        cr.move_to(-ext.width/2-ext.x_bearing,-ext.height/2-ext.y_bearing)
        cr.set_source_rgba(*c,1); cr.show_text("Ax")
    cr.restore()

class SidePanel:
    def __init__(self, overlay, dark=True, on_icon=None):
        self._overlay = overlay
        self._dark    = dark
        self._on_icon = on_icon
        self._visible = True
        self._offset  = 0.0
        self._target  = 0.0
        self._hovered = -1
        self._t       = 0
        self._build()

    def _build(self):
        if not GTK_OK: return
        n = len(ICONS)
        self._panel_h = n * (ICON_SIZE + SPACING) + SPACING * 2 + 20
        self._box = Gtk.Box()
        self._box.set_size_request(PANEL_W + 20, self._panel_h)
        self._box.set_valign(Gtk.Align.CENTER)
        self._box.set_halign(Gtk.Align.END)
        self._box.set_margin_end(0)
        self._box.set_margin_top(0)
        self._box.set_margin_bottom(0)
        self._area = Gtk.DrawingArea()
        self._area.set_size_request(PANEL_W + 20, self._panel_h)
        self._area.set_draw_func(self._draw)
        self._box.append(self._area)
        self._overlay.add_overlay(self._box)
        motion = Gtk.EventControllerMotion()
        motion.connect("motion", self._on_motion)
        motion.connect("leave",  self._on_leave)
        self._area.add_controller(motion)
        click = Gtk.GestureClick()
        click.connect("pressed", self._on_click)
        self._area.add_controller(click)
        GLib.timeout_add(16, self._tick)

    def _tick(self):
        self._t += 1
        diff = self._target - self._offset
        if abs(diff) > 0.5:
            self._offset += diff * 0.15
        else:
            self._offset = self._target
        off = int(self._offset)
        if off >= PANEL_W + 22:
            self._box.set_visible(False)
        else:
            self._box.set_visible(True)
            self._box.set_margin_end(off)
        self._area.queue_draw()
        return True

    def toggle(self):
        if self._visible:
            self._target  = PANEL_W + 25
            self._visible = False
        else:
            self._target  = 0
            self._visible = True

    def show(self): self._visible = True;  self._target = 0
    def hide(self): self._visible = False; self._target = PANEL_W + 25
    def set_theme(self, dark): self._dark = dark

    def _icon_y(self, idx):
        return SPACING + idx * (ICON_SIZE + SPACING)

    def _on_motion(self, ctrl, mx, my):
        old = self._hovered
        self._hovered = -1
        for i in range(len(ICONS)):
            iy = self._icon_y(i)
            if 6 <= mx <= 6+ICON_SIZE+4 and iy <= my <= iy+ICON_SIZE:
                self._hovered = i; break
        if self._hovered != old: self._area.queue_draw()

    def _on_leave(self, ctrl):
        self._hovered = -1
        self._area.queue_draw()

    def _on_click(self, gesture, n, mx, my):
        for i, (name, key, color) in enumerate(ICONS):
            iy = self._icon_y(i)
            if 6 <= mx <= 6+ICON_SIZE+4 and iy <= my <= iy+ICON_SIZE:
                if self._on_icon: self._on_icon(name, key)
                break

    def _rrect(self, cr, x, y, w, h, r):
        cr.new_sub_path()
        cr.arc(x+r,   y+r,   r, math.pi,     math.pi*1.5)
        cr.arc(x+w-r, y+r,   r, math.pi*1.5, 0)
        cr.arc(x+w-r, y+h-r, r, 0,           math.pi*0.5)
        cr.arc(x+r,   y+h-r, r, math.pi*0.5, math.pi)
        cr.close_path()

    def _draw(self, area, cr, w, h):
        dark = self._dark
        if dark:
            cr.set_source_rgba(0.02, 0.04, 0.12, 0.92)
        else:
            cr.set_source_rgba(0.95, 0.97, 1.00, 0.92)
        r = 16
        cr.new_sub_path()
        cr.arc(r+8, r, r, math.pi, math.pi*1.5)
        cr.line_to(w, 0); cr.line_to(w, h)
        cr.arc(r+8, h-r, r, math.pi*0.5, math.pi)
        cr.close_path(); cr.fill()
        bc = (0.00,0.83,1.00) if dark else (0.00,0.35,0.75)
        cr.set_source_rgba(*bc, 0.70)
        cr.set_line_width(2.0)
        cr.move_to(8, r); cr.arc(r+8, r, r, math.pi, math.pi*1.5)
        cr.move_to(8, r); cr.line_to(8, h-r)
        cr.arc(r+8, h-r, r, math.pi*0.5, math.pi)
        cr.stroke()
        for i, (name, key, base_color) in enumerate(ICONS):
            iy  = self._icon_y(i)
            cx  = 8 + ICON_SIZE/2
            cy  = iy + ICON_SIZE/2
            hov = (self._hovered == i)
            c   = base_color
            if hov:
                pulse = 0.5 + 0.5 * math.sin(self._t * 0.08)
                cr.set_source_rgba(*c, 0.20 + 0.08*pulse)
                self._rrect(cr, 6, iy-2, ICON_SIZE+4, ICON_SIZE+4, 10); cr.fill()
                cr.set_source_rgba(*c, 0.70); cr.set_line_width(1.5)
                self._rrect(cr, 6, iy-2, ICON_SIZE+4, ICON_SIZE+4, 10); cr.stroke()
            else:
                cr.set_source_rgba(*c, 0.07 if dark else 0.05)
                self._rrect(cr, 8, iy, ICON_SIZE, ICON_SIZE, 10); cr.fill()
            sz = (ICON_SIZE - 10) * (1.06 if hov else 1.0)
            _draw_icon(cr, cx, cy, sz, key, c)
            cr.select_font_face("Courier New", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            cr.set_font_size(8)
            ext = cr.text_extents(name)
            lx  = cx - ext.width/2 - ext.x_bearing
            ly  = iy + ICON_SIZE + 11
            pad = 3
            cr.set_source_rgba(0, 0, 0, 0.68)
            self._rrect(cr, lx-pad, ly-ext.height-pad, ext.width+pad*2, ext.height+pad*2, 3); cr.fill()
            cr.set_source_rgba(1, 1, 1, 0.95)
            cr.move_to(lx, ly); cr.show_text(name)
