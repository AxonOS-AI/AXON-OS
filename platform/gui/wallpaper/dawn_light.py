# AxonOS/platform/gui/wallpaper/dawn_light.py
# Copyright (c) 2024 Abdullah — Axon OS Project (AGPL-3.0)
# Wallpaper ⑥: Dawn Light — warm sunrise with soft geometric grid

import math
import random
from wallpaper_engine import BaseWallpaper


class DawnLight(BaseWallpaper):
    name = "Dawn Light"

    def _init(self):
        self._circles = [
            {"x": 0.22, "y": 0.30, "r": 0.30, "col": (1.0, 0.72, 0.42), "spd": 0.008},
            {"x": 0.80, "y": 0.62, "r": 0.22, "col": (0.60, 0.72, 1.0), "spd": 0.012},
            {"x": 0.50, "y": 0.80, "r": 0.20, "col": (0.70, 0.86, 1.0), "spd": 0.006},
        ]
        self._floaters = [
            {
                "x": random.random(),
                "y": random.random(),
                "vx": (random.random()-0.5)*0.0004,
                "vy": (random.random()-0.5)*0.0003,
                "r":  0.002 + random.random()*0.003,
                "col": random.choice([
                    (1.0, 0.72, 0.42),
                    (0.60, 0.72, 1.0),
                    (0.50, 0.80, 0.90),
                ]),
                "pulse": random.uniform(0, math.pi*2),
            }
            for _ in range(40)
        ]

    def render(self, cr, w, h, t, dark):
        # Gradient background (always light)
        cr.set_source_rgba(0.98, 0.96, 0.94, 0.25)
        cr.paint()

        # Soft glowing circles
        for c in self._circles:
            nx, ny = c["x"]*w, c["y"]*h
            nr = c["r"]*min(w, h) + 10*math.sin(t*c["spd"])
            col = c["col"]
            for step in range(10):
                frac  = step / 10
                alpha = 0.10 * (1-frac) * 0.8
                cr.set_source_rgba(*col, alpha)
                cr.arc(nx, ny, nr*frac, 0, math.pi*2)
                cr.fill()

        # Soft grid
        gs = 45
        for x in range(0, w+gs, gs):
            alpha = 0.03 + 0.015*math.sin(t*0.01 + x*0.03)
            cr.set_source_rgba(0.0, 0.39, 0.78, alpha)
            cr.set_line_width(0.3)
            cr.move_to(x, 0)
            cr.line_to(x, h)
            cr.stroke()
        for y in range(0, h+gs, gs):
            alpha = 0.03 + 0.015*math.sin(t*0.01 + y*0.03)
            cr.set_source_rgba(0.0, 0.39, 0.78, alpha)
            cr.move_to(0, y)
            cr.line_to(w, y)
            cr.stroke()

        # Floating particles
        for p in self._floaters:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            if p["x"] < 0 or p["x"] > 1: p["vx"] *= -1
            if p["y"] < 0 or p["y"] > 1: p["vy"] *= -1
            p["pulse"] += 0.02
            g = 0.3 + 0.4*math.sin(p["pulse"])
            cr.set_source_rgba(*p["col"], g*0.25)
            cr.arc(p["x"]*w, p["y"]*h, p["r"]*w, 0, math.pi*2)
            cr.fill()

        self._logo_watermark(cr, cx, cy, min(w,h)*0.28, dark, 0.85)
        # Logo (light mode)
        cx, cy = w*0.5, h*0.5
        self.&, False, 0.80)
