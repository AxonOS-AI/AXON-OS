# AxonOS/platform/gui/wallpaper/aurora_wave.py
# Copyright (c) 2024 Abdullah — Axon OS Project (AGPL-3.0)
# Wallpaper ④: Aurora Wave — polar aurora with particle field

import math
import random
from wallpaper_engine import BaseWallpaper


class AuroraWave(BaseWallpaper):
    name = "Aurora Wave"

    def _init(self):
        self._particles = [
            {
                "x":   random.random(),
                "y":   0.3 + random.random() * 0.5,
                "vx":  (random.random() - 0.5) * 0.0005,
                "vy":  (random.random() - 0.5) * 0.0003,
                "size": 0.002 + random.random() * 0.003,
                "hue":  160 + random.random() * 80,
            }
            for _ in range(80)
        ]
        self._stars = [
            {"x": random.random(), "y": random.random() * 0.45,
             "r": 0.0004 + random.random()*0.001,
             "pulse": random.uniform(0, math.pi*2),
             "speed": 0.008 + random.random()*0.018}
            for _ in range(120)
        ]

    def _hsl_to_rgb(self, h, s, l):
        h /= 360
        if s == 0:
            return l, l, l
        def hue2rgb(p, q, t):
            if t < 0: t += 1
            if t > 1: t -= 1
            if t < 1/6: return p + (q-p)*6*t
            if t < 1/2: return q
            if t < 2/3: return p + (q-p)*(2/3-t)*6
            return p
        q = l*(1+s) if l < 0.5 else l+s-l*s
        p = 2*l - q
        return hue2rgb(p,q,h+1/3), hue2rgb(p,q,h), hue2rgb(p,q,h-1/3)

    def render(self, cr, w, h, t, dark):
        bg = (0.01, 0.02, 0.06) if dark else (0.92, 0.95, 0.98)
        cr.set_source_rgb(*bg)
        cr.paint()

        # Stars (upper portion)
        for s in self._stars:
            s["pulse"] += s["speed"]
            alpha = (0.15 + 0.7*abs(math.sin(s["pulse"]))) * (1 if dark else 0.4)
            col = (1,1,1) if dark else (0.3,0.4,0.6)
            cr.set_source_rgba(*col, alpha)
            cr.arc(s["x"]*w, s["y"]*h, s["r"]*w, 0, math.pi*2)
            cr.fill()

        # Aurora wave bands
        for layer in range(6):
            phase  = t * 0.012 + layer * 0.85
            y_base = h * (0.32 + layer * 0.055)
            hue    = 165 + layer * 16
            r, g, b = self._hsl_to_rgb(hue, 1.0, 0.85)
            alpha  = (0.08 + 0.04*math.sin(phase)) * (1 if dark else 0.5)

            cr.move_to(0, h)
            for x_step in range(w + 1):
                frac = x_step / w
                y = (y_base
                     + math.sin(frac * 6 + phase) * h * 0.04
                     + math.sin(frac * 11 + phase * 1.3) * h * 0.02)
                if x_step == 0:
                    cr.move_to(x_step, y)
                else:
                    cr.line_to(x_step, y)
            cr.line_to(w, h)
            cr.line_to(0, h)
            cr.close_path()
            cr.set_source_rgba(r, g, b, alpha)
            cr.fill()

        # Particles
        for p in self._particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            if p["x"] < 0: p["x"] = 1.0
            if p["x"] > 1: p["x"] = 0.0
            if p["y"] < 0.2 or p["y"] > 0.9: p["vy"] *= -1

            r, g, b = self._hsl_to_rgb(p["hue"], 1.0, 0.65)
            alpha   = 0.18 * (1 if dark else 0.5)
            cr.set_source_rgba(r, g, b, alpha)
            cr.arc(p["x"]*w, p["y"]*h, p["size"]*w, 0, math.pi*2)
            cr.fill()

        self._logo_watermark(cr, cx, cy, min(w,h)*0.28, dark, 0.85)
        # Logo
        cx, cy = w*0.5, h*0.5
        self.&, dark, 0.80)
