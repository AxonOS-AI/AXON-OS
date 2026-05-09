# AxonOS/platform/gui/wallpaper/cyber_grid.py
# Copyright (c) 2024 Abdullah — Axon OS Project (AGPL-3.0)
# Wallpaper ③: Cyber Grid — perspective grid with scan line

import math
import random
from wallpaper_engine import BaseWallpaper


class CyberGrid(BaseWallpaper):
    name = "Cyber Grid"

    def _init(self):
        self._scan_y = 0.0

    def render(self, cr, w, h, t, dark):
        bg = (0.01, 0.03, 0.06) if dark else (0.92, 0.94, 0.97)
        cr.set_source_rgb(*bg)
        cr.paint()

        cyan = (0.0, 0.83, 1.0) if dark else (0.0, 0.39, 0.78)
        purp = (0.42, 0.24, 0.88)
        cx, cy_screen = w * 0.5, h * 0.5
        hy = h * 0.58    # horizon y

        # Floor grid — perspective lines
        grid_lines = 20
        for i in range(grid_lines + 1):
            x = w * (i / grid_lines)
            alpha = (0.04 + 0.02*math.sin(t*0.014 + i*0.3)) * (1 if dark else 0.7)
            cr.set_source_rgba(*cyan, alpha)
            cr.set_line_width(0.4)
            cr.move_to(x, h)
            cr.line_to(cx, hy)
            cr.stroke()

        # Moving horizontal lines (floor)
        speed = ((t * 0.9) % 45) / 45
        for i in range(12):
            prog  = (i / 12 + speed) % 1.0
            y     = hy + (h - hy) * prog
            scale = 0.05 + 0.95 * prog
            alpha = (0.04 + 0.04*prog) * min(1.0, prog*5) * (1 if dark else 0.7)
            cr.set_source_rgba(*cyan, alpha)
            cr.set_line_width(0.4)
            cr.move_to(cx - cx*scale, y)
            cr.line_to(cx + cx*scale, y)
            cr.stroke()

        # Horizon glow
        for step in range(6):
            gy = hy - 4 + step * 1.5
            alpha = (0.12 - step*0.018) * (1 if dark else 0.5)
            cr.set_source_rgba(*cyan, alpha)
            cr.set_line_width(0.8)
            cr.move_to(0, gy)
            cr.line_to(w, gy)
            cr.stroke()

        # Ceiling grid
        for i in range(grid_lines + 1):
            x = w * (i / grid_lines)
            alpha = (0.018 + 0.01*math.sin(t*0.014 + i*0.3)) * (1 if dark else 0.4)
            cr.set_source_rgba(*purp, alpha)
            cr.set_line_width(0.3)
            cr.move_to(x, 0)
            cr.line_to(cx, hy)
            cr.stroke()

        # Scan line
        self._scan_y = ((t * 1.1) % (h + 40)) / (h + 40)
        sy = self._scan_y * (h + 40) - 20
        for step in range(8):
            gy    = sy - 16 + step * 4
            alpha = (0.07 - step*0.008) * (1 if dark else 0.5)
            cr.set_source_rgba(*cyan, alpha)
            cr.rectangle(0, gy, w, 4)
            cr.fill()

        # Logo
        self._logo_watermark(cr, cx, hy*0.55, min(w,h)*0.28, dark, 0.85)
