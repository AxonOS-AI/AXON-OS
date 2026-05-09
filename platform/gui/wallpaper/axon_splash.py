# AxonOS/platform/gui/wallpaper/axon_splash.py
# Copyright (c) 2024 Abdullah -- Axon OS Project (AGPL-3.0)

import math, random
from wallpaper_engine import BaseWallpaper


class AxonSplash(BaseWallpaper):
    name = "Axon Splash"

    def _init(self):
        random.seed(42)
        self._stars = [
            {
                "x": random.random(), "y": random.random(),
                "r": 0.0003 + random.random() * 0.0015,
                "alpha": 0.3 + random.random() * 0.7,
                "pulse": random.uniform(0, math.pi * 2),
                "speed": 0.005 + random.random() * 0.015,
            }
            for _ in range(250)
        ]

    def render(self, cr, w, h, t, dark):
        # Background — deep space
        import cairo as _cairo
        grad = _cairo.LinearGradient(0, 0, 0, h)
        grad.add_color_stop_rgb(0.0, 0.01, 0.02, 0.08)
        grad.add_color_stop_rgb(0.5, 0.02, 0.03, 0.12)
        grad.add_color_stop_rgb(1.0, 0.01, 0.01, 0.06)
        cr.set_source(grad)
        cr.paint()

        cx, cy = w * 0.5, h * 0.5

        # Stars
        for s in self._stars:
            s["pulse"] += s["speed"]
            a = s["alpha"] * (0.5 + 0.5 * abs(math.sin(s["pulse"])))
            cr.set_source_rgba(1, 1, 1, a)
            cr.arc(s["x"] * w, s["y"] * h, s["r"] * w, 0, math.pi * 2)
            cr.fill()

        # Glow behind logo
        logo_y = cy * 0.72
        for ring in range(6):
            r = 120 + ring * 40
            a = 0.06 - ring * 0.008
            pulse = 0.5 + 0.5 * math.sin(t * 0.03 + ring)
            cr.set_source_rgba(0.00, 0.83, 1.00, a * pulse)
            cr.arc(cx, logo_y, r, 0, math.pi * 2)
            cr.fill()

        # Draw colorful AX logo
        self._draw_ax_logo(cr, cx, logo_y, 110, t)

        # "AXON OS" text
        cr.select_font_face("Courier New",
                            _cairo.FONT_SLANT_NORMAL,
                            _cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(min(w, h) * 0.065)

        # Gradient text effect
        text = "AXON OS"
        ext = cr.text_extents(text)
        tx = cx - ext.width / 2 - ext.x_bearing
        ty = logo_y + 130

        # Shadow
        cr.set_source_rgba(0.00, 0.83, 1.00, 0.15)
        cr.move_to(tx + 2, ty + 2)
        cr.show_text(text)

        # Main text
        cr.set_source_rgba(0.00, 0.83, 1.00, 0.95)
        cr.move_to(tx, ty)
        cr.show_text(text)

        # Subtitle
        cr.set_font_size(min(w, h) * 0.022)
        subtitle = "Initializing AI Core..."
        pulse_a = 0.5 + 0.5 * math.sin(t * 0.04)
        cr.set_source_rgba(0.70, 0.85, 1.00, 0.55 + 0.3 * pulse_a)
        ext2 = cr.text_extents(subtitle)
        cr.move_to(cx - ext2.width / 2 - ext2.x_bearing, ty + 46)
        cr.show_text(subtitle)

        # Bottom glow line
        import cairo as _cairo2
        lg = _cairo2.LinearGradient(0, h * 0.92, w, h * 0.92)
        lg.add_color_stop_rgba(0.0,  0.00, 0.83, 1.00, 0.0)
        lg.add_color_stop_rgba(0.35, 0.00, 0.83, 1.00, 0.4)
        lg.add_color_stop_rgba(0.65, 0.42, 0.24, 0.88, 0.4)
        lg.add_color_stop_rgba(1.0,  0.42, 0.24, 0.88, 0.0)
        cr.set_source(lg)
        cr.rectangle(0, h * 0.92, w, 2)
        cr.fill()

    def _draw_ax_logo(self, cr, cx, cy, size, t):
        import cairo as _cairo

        ps = size * 0.45

        # Outer glow ring animated
        for i in range(3):
            phase = t * 0.025 + i * math.pi * 2 / 3
            rr = ps * 1.3 + ps * 0.08 * math.sin(phase)
            a  = 0.08 + 0.04 * math.sin(phase)
            cr.set_source_rgba(0.00, 0.83, 1.00, a)
            cr.set_line_width(1.5)
            cr.arc(cx, cy, rr, 0, math.pi * 2)
            cr.stroke()

        # Circuit traces at corners
        corners = [
            (cx - ps, cy - ps, -1, -1),
            (cx + ps, cy - ps,  1, -1),
            (cx - ps, cy + ps, -1,  1),
            (cx + ps, cy + ps,  1,  1),
        ]
        tlen = ps * 0.7
        tgap = ps * 0.28
        colors = [
            (0.00, 0.83, 1.00),
            (1.00, 0.42, 0.78),
            (0.42, 0.78, 1.00),
            (0.78, 0.42, 1.00),
        ]
        for idx, (bx, by, dx, dy) in enumerate(corners):
            c = colors[idx]
            flash = 0.6 + 0.4 * math.sin(t * 0.06 + idx * 1.2)
            cr.set_source_rgba(*c, 0.85 * flash)
            cr.set_line_width(2.0)
            cr.move_to(bx, by + dy * tgap)
            cr.line_to(bx + dx * tlen, by + dy * tgap)
            cr.stroke()
            cr.move_to(bx + dx * tgap, by)
            cr.line_to(bx + dx * tgap, by + dy * tlen)
            cr.stroke()
            cr.arc(bx + dx * tgap, by + dy * tgap, 3.5, 0, math.pi * 2)
            cr.set_source_rgba(*c, flash)
            cr.fill()

        # Pins
        pin_colors = [(0.00,0.83,1.00),(1.00,0.42,0.78),(0.42,0.78,1.00)]
        for i, off in enumerate([-ps*0.35, 0, ps*0.35]):
            c = pin_colors[i % 3]
            flash = 0.5 + 0.5 * math.sin(t * 0.07 + off * 0.02)
            cr.set_source_rgba(*c, 0.85 * flash)
            cr.set_line_width(2.2)
            plen = ps * 0.5
            for px, py, ex, ey in [
                (cx+off, cy-ps, cx+off, cy-ps-plen),
                (cx+off, cy+ps, cx+off, cy+ps+plen),
                (cx-ps, cy+off, cx-ps-plen, cy+off),
                (cx+ps, cy+off, cx+ps+plen, cy+off),
            ]:
                cr.move_to(px, py); cr.line_to(ex, ey); cr.stroke()
                cr.arc(ex, ey, 3, 0, math.pi * 2)
                cr.set_source_rgba(*c, flash); cr.fill()
                cr.set_source_rgba(*c, 0.85 * flash)

        # Body background
        self._rrect(cr, cx-ps, cy-ps, ps*2, ps*2, ps*0.14)
        cr.set_source_rgba(0.02, 0.04, 0.10, 0.94)
        cr.fill()

        # Body border — rainbow gradient
        import cairo as _cairo3
        lg = _cairo3.LinearGradient(cx-ps, cy-ps, cx+ps, cy+ps)
        lg.add_color_stop_rgba(0.0,  0.00, 0.83, 1.00, 0.95)
        lg.add_color_stop_rgba(0.33, 1.00, 0.42, 0.78, 0.95)
        lg.add_color_stop_rgba(0.66, 0.42, 0.78, 1.00, 0.95)
        lg.add_color_stop_rgba(1.0,  0.78, 0.42, 1.00, 0.95)
        cr.set_source(lg)
        cr.set_line_width(2.8)
        self._rrect(cr, cx-ps, cy-ps, ps*2, ps*2, ps*0.14)
        cr.stroke()

        # Inner die
        die = ps * 0.62
        cr.set_source_rgba(0.42, 0.24, 0.88, 0.15)
        self._rrect(cr, cx-die, cy-die, die*2, die*2, ps*0.08)
        cr.fill()
        cr.set_source_rgba(0.42, 0.24, 0.88, 0.60)
        cr.set_line_width(1.5)
        self._rrect(cr, cx-die, cy-die, die*2, die*2, ps*0.08)
        cr.stroke()

        # AX text with gradient
        import cairo as _cairo4
        cr.select_font_face("Courier New",
                            _cairo4.FONT_SLANT_NORMAL,
                            _cairo4.FONT_WEIGHT_BOLD)
        fs = ps * 0.75
        cr.set_font_size(fs)
        ext = cr.text_extents("AX")
        tx = cx - ext.width/2 - ext.x_bearing
        ty = cy - ext.height/2 - ext.y_bearing

        # Text gradient
        tg = _cairo4.LinearGradient(tx, ty - ext.height, tx, ty)
        tg.add_color_stop_rgba(0.0, 0.00, 0.83, 1.00, 1.0)
        tg.add_color_stop_rgba(0.5, 0.78, 0.42, 1.00, 1.0)
        tg.add_color_stop_rgba(1.0, 1.00, 0.42, 0.78, 1.0)
        cr.set_source(tg)
        cr.move_to(tx, ty)
        cr.show_text("AX")
