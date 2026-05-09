# AxonOS/platform/gui/wallpaper/neural_light.py
# Copyright (c) 2024 Abdullah — Axon OS Project (AGPL-3.0)
# Wallpaper ⑤: Neural Light — neural network on white/light background

import math
import random
from wallpaper_engine import BaseWallpaper


class NeuralLight(BaseWallpaper):
    name = "Neural Light"

    def _init(self):
        self._nodes = [
            {
                "x":  random.random(),
                "y":  random.random(),
                "vx": (random.random()-0.5)*0.0007,
                "vy": (random.random()-0.5)*0.0007,
                "pulse": random.uniform(0, math.pi*2),
                "r": 0.003 + random.random()*0.004,
            }
            for _ in range(32)
        ]

    def render(self, cr, w, h, t, dark):
        # Always light regardless of system theme
        cr.set_source_rgba(0.94, 0.95, 0.97, 0.25)
        cr.paint()

        blue = (0.0, 0.39, 0.78)
        purp = (0.32, 0.19, 0.69)
        cx, cy = w*0.5, h*0.5

        for n in self._nodes:
            n["x"] += n["vx"]
            n["y"] += n["vy"]
            if n["x"] < 0 or n["x"] > 1: n["vx"] *= -1
            if n["y"] < 0 or n["y"] > 1: n["vy"] *= -1
            n["pulse"] += 0.022

        # Connections
        for i, a in enumerate(self._nodes):
            for b in self._nodes[i+1:]:
                dx = (a["x"]-b["x"])*w
                dy = (a["y"]-b["y"])*h
                d  = math.hypot(dx, dy)
                if d < w*0.20:
                    alpha = 0.12*(1-d/(w*0.20))
                    cr.set_source_rgba(*blue, alpha)
                    cr.set_line_width(0.5)
                    cr.move_to(a["x"]*w, a["y"]*h)
                    cr.line_to(b["x"]*w, b["y"]*h)
                    cr.stroke()

        # Center lines
        for n in self._nodes:
            dx = n["x"]*w - cx
            dy = n["y"]*h - cy
            d  = math.hypot(dx, dy)
            if d < w*0.30:
                alpha = 0.05*(1-d/(w*0.30))
                cr.set_source_rgba(*purp, alpha)
                cr.set_line_width(0.3)
                cr.move_to(n["x"]*w, n["y"]*h)
                cr.line_to(cx, cy)
                cr.stroke()

        # Nodes
        for n in self._nodes:
            g  = 0.4 + 0.4*math.sin(n["pulse"])
            nx, ny = n["x"]*w, n["y"]*h
            cr.set_source_rgba(*blue, g*0.18)
            cr.arc(nx, ny, n["r"]*w*1.8, 0, math.pi*2)
            cr.fill()
            cr.set_source_rgba(*blue, 0.40 + g*0.45)
            cr.arc(nx, ny, n["r"]*w, 0, math.pi*2)
            cr.fill()

        self._logo_watermark(cr, cx, cy, min(w,h)*0.28, dark, 0.85)
        # Logo (always light mode)
        self.&, False, 0.85)
