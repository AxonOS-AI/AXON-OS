# AxonOS/platform/gui/wallpaper/neural_dark.py
# Copyright (c) 2024 Abdullah — Axon OS Project (AGPL-3.0)
# Wallpaper ①: Neural Dark — moving neural network on dark background

import math
import random
from wallpaper_engine import BaseWallpaper


class NeuralDark(BaseWallpaper):
    name      = "Neural Dark"
    dark_only = False

    def _init(self):
        self._nodes = []
        for _ in range(36):
            self._nodes.append({
                "x":  random.random(),
                "y":  random.random(),
                "vx": (random.random() - 0.5) * 0.0008,
                "vy": (random.random() - 0.5) * 0.0008,
                "pulse": random.uniform(0, math.pi * 2),
                "r": 0.004 + random.random() * 0.004,
            })

    def render(self, cr, w, h, t, dark):
        # Background
        bg = (0.02, 0.03, 0.07) if dark else (0.94, 0.95, 0.96)
        cr.set_source_rgba(*bg, 0.25)
        cr.paint()

        cyan  = (0.0, 0.83, 1.0) if dark else (0.0, 0.39, 0.78)
        purp  = (0.42, 0.24, 0.88)

        # Move nodes
        for n in self._nodes:
            n["x"] += n["vx"]
            n["y"] += n["vy"]
            if n["x"] < 0 or n["x"] > 1: n["vx"] *= -1
            if n["y"] < 0 or n["y"] > 1: n["vy"] *= -1
            n["pulse"] += 0.025

        # Connection lines
        for i, a in enumerate(self._nodes):
            for b in self._nodes[i+1:]:
                dx = (a["x"] - b["x"]) * w
                dy = (a["y"] - b["y"]) * h
                d  = math.hypot(dx, dy)
                if d < w * 0.22:
                    al = 0.14 * (1 - d / (w * 0.22))
                    cr.set_source_rgba(*cyan, al)
                    cr.set_line_width(0.5)
                    cr.move_to(a["x"]*w, a["y"]*h)
                    cr.line_to(b["x"]*w, b["y"]*h)
                    cr.stroke()

        # Lines to center
        cx, cy = w * 0.5, h * 0.5
        for n in self._nodes:
            dx = (n["x"]*w - cx)
            dy = (n["y"]*h - cy)
            d  = math.hypot(dx, dy)
            if d < w * 0.35:
                al = 0.06 * (1 - d / (w * 0.35))
                cr.set_source_rgba(*purp, al)
                cr.set_line_width(0.3)
                cr.move_to(n["x"]*w, n["y"]*h)
                cr.line_to(cx, cy)
                cr.stroke()

        # Nodes
        for n in self._nodes:
            g = 0.4 + 0.4 * math.sin(n["pulse"])
            nx, ny = n["x"]*w, n["y"]*h
            cr.set_source_rgba(*cyan, g * 0.22)
            cr.arc(nx, ny, n["r"]*w*1.8, 0, math.pi*2)
            cr.fill()
            cr.set_source_rgba(*cyan, 0.45 + g * 0.5)
            cr.arc(nx, ny, n["r"]*w, 0, math.pi*2)
            cr.fill()

        # Logo watermark
        self._logo_watermark(cr, cx, cy, min(w, h) * 0.12, dark, 0.85)
