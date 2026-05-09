# AxonOS/platform/gui/wallpaper/deep_space.py
# Copyright (c) 2024 Abdullah — Axon OS Project (AGPL-3.0)
# Wallpaper ②: Deep Space — stars, nebulae, shooting stars

import math
import random
from wallpaper_engine import BaseWallpaper


class DeepSpace(BaseWallpaper):
    name = "Deep Space"

    def _init(self):
        self._stars = [
            {
                "x": random.random(), "y": random.random(),
                "r": 0.0005 + random.random() * 0.002,
                "pulse": random.uniform(0, math.pi*2),
                "speed": 0.008 + random.random() * 0.018,
            }
            for _ in range(200)
        ]
        self._nebulae = [
            {"x": 0.3, "y": 0.4, "col": (0.42, 0.24, 0.88), "r": 0.28},
            {"x": 0.75,"y": 0.6, "col": (0.0,  0.83, 1.0),  "r": 0.22},
            {"x": 0.15,"y": 0.7, "col": (0.31, 0.16, 0.63), "r": 0.18},
        ]
        self._shoot_x  = -0.2
        self._shoot_y  = 0.1
        self._shoot_sp = 0.005

    def render(self, cr, w, h, t, dark):
        bg = (0.01, 0.02, 0.05) if dark else (0.92, 0.94, 0.98)
        cr.set_source_rgb(*bg)
        cr.paint()

        cx, cy = w * 0.5, h * 0.5

        # Nebulae
        for nb in self._nebulae:
            nx, ny, nr = nb["x"]*w, nb["y"]*h, nb["r"]*min(w,h)
            col = nb["col"]
            pat = cr.RadialGradient if hasattr(cr, 'RadialGradient') else None
            # Manual radial
            for step in range(8):
                frac = step / 8
                alpha = 0.06 * (1 - frac) * (0.6 if dark else 0.35)
                r_step = nr * frac
                cr.set_source_rgba(*col, alpha)
                cr.arc(nx, ny, r_step, 0, math.pi*2)
                cr.fill()

        # Stars
        for s in self._stars:
            s["pulse"] += s["speed"]
            alpha = (0.2 + 0.8 * abs(math.sin(s["pulse"])))
            col = (1.0, 1.0, 1.0) if dark else (0.2, 0.3, 0.5)
            cr.set_source_rgba(*col, alpha)
            cr.arc(s["x"]*w, s["y"]*h, s["r"]*w, 0, math.pi*2)
            cr.fill()

        # Shooting star
        self._shoot_x += self._shoot_sp
        if self._shoot_x > 1.3:
            self._shoot_x = -0.2
            self._shoot_y = random.uniform(0.05, 0.4)
        tail = 0.09
        sx, sy = self._shoot_x * w, self._shoot_y * h
        for i in range(12):
            frac = i / 12
            alpha = (1 - frac) * 0.5 * (1 if dark else 0.4)
            cr.set_source_rgba(1, 1, 1, alpha)
            cr.arc(sx - tail*w*frac, sy + tail*h*0.25*frac,
                   max(0.5, (1-frac)*2.5), 0, math.pi*2)
            cr.fill()

        # Pulse rings from center
        for i in range(3):
            phase = t * 0.025 + i * math.pi * 2 / 3
            ring_r = min(w,h) * (0.08 + i*0.06 + 0.015*math.sin(phase))
            alpha  = (0.04 + 0.03*math.sin(phase)) * (1 if dark else 0.6)
            col = (0, 0.83, 1) if i % 2 == 0 else (0.42, 0.24, 0.88)
            cr.set_source_rgba(*col, alpha)
            cr.set_line_width(0.7)
            cr.arc(cx, cy, ring_r, 0, math.pi*2)
            cr.stroke()

        # Logo
        self.&, dark, 0.80)
