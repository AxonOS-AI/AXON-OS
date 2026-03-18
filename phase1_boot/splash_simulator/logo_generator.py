# axon-os/phase1_boot/splash_simulator/logo_generator.py
# ────────────────────────────────────────────────────────
# Axon OS — Logo Generator
# Draws the Axon OS logo as a pygame Surface.
# No external image files required — the logo is generated in code.
# ────────────────────────────────────────────────────────

import pygame
import math
from config import (
    COLOR_PRIMARY, COLOR_SECONDARY, COLOR_BG,
    LOGO_SIZE
)


def _hex_points(cx: float, cy: float, radius: float) -> list[tuple[float, float]]:
    """Return 6 points of a regular hexagon centered at (cx, cy)."""
    points = []
    for i in range(6):
        angle = math.radians(60 * i - 30)
        points.append((cx + radius * math.cos(angle),
                        cy + radius * math.sin(angle)))
    return points


def draw_logo(surface: pygame.Surface, cx: int, cy: int,
              size: float, alpha: int = 255) -> None:
    """
    Render the Axon OS logo onto `surface` at position (cx, cy).

    Design concept:
      ┌──────────────────────────────────────────────┐
      │   Outer hexagon ring  (cyan)                 │
      │     Inner tri-node network  (violet → cyan)  │
      │       Center dot with glow  (cyan)            │
      └──────────────────────────────────────────────┘
    """
    logo_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
    lx, ly = size, size                     # local center

    r_outer  = size * 0.90
    r_mid    = size * 0.60
    r_inner  = size * 0.22
    r_dot    = size * 0.10
    lw_outer = max(2, int(size * 0.030))
    lw_inner = max(1, int(size * 0.022))

    # ── Outer hexagon ─────────────────────────────
    outer_pts = _hex_points(lx, ly, r_outer)
    pygame.draw.polygon(logo_surf, (*COLOR_PRIMARY, alpha), outer_pts, lw_outer)

    # ── Mid hexagon (rotated 30°) ──────────────────
    mid_pts = []
    for i in range(6):
        angle = math.radians(60 * i)
        mid_pts.append((lx + r_mid * math.cos(angle),
                         ly + r_mid * math.sin(angle)))
    pygame.draw.polygon(logo_surf, (*COLOR_SECONDARY, alpha), mid_pts, lw_inner)

    # ── Connecting lines: mid vertices → center ───
    for pt in mid_pts[::2]:
        pygame.draw.line(logo_surf, (*COLOR_PRIMARY, int(alpha * 0.55)),
                         (int(lx), int(ly)), (int(pt[0]), int(pt[1])), lw_inner)

    # ── Triangle inside (every other mid vertex) ──
    tri_pts = [mid_pts[0], mid_pts[2], mid_pts[4]]
    pygame.draw.polygon(logo_surf, (*COLOR_PRIMARY, int(alpha * 0.35)), tri_pts, lw_inner)

    # ── Node dots on mid vertices ──────────────────
    node_r = max(3, int(size * 0.045))
    for pt in mid_pts:
        pygame.draw.circle(logo_surf, (*COLOR_PRIMARY, alpha),
                           (int(pt[0]), int(pt[1])), node_r)

    # ── Inner circle ──────────────────────────────
    pygame.draw.circle(logo_surf, (*COLOR_SECONDARY, alpha),
                       (int(lx), int(ly)), int(r_inner), lw_inner)

    # ── Center glow ───────────────────────────────
    for glow_r in range(int(r_dot * 2.5), 0, -1):
        a = int(alpha * (glow_r / (r_dot * 2.5)) * 0.6)
        pygame.draw.circle(logo_surf, (*COLOR_PRIMARY, a),
                           (int(lx), int(ly)), glow_r)

    # ── Center dot ────────────────────────────────
    pygame.draw.circle(logo_surf, (*COLOR_PRIMARY, alpha),
                       (int(lx), int(ly)), int(r_dot))

    # Blit onto target surface centered at (cx, cy)
    surface.blit(logo_surf, (cx - size, cy - size))


def generate_logo_png(output_path: str, size: int = 256) -> None:
    """
    Save the Axon OS logo as a PNG file.
    Useful for generating assets for Plymouth theme.
    """
    pygame.init()
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    draw_logo(surf, size // 2, size // 2, size * 0.45)
    pygame.image.save(surf, output_path)
    print(f"Logo saved → {output_path}")
