# axon-os/phase1_boot/splash_simulator/animation.py
# ────────────────────────────────────────────────────
# Axon OS — Animation Engine
# Manages: particles, progress bar, text fade, pulse effects.
# ────────────────────────────────────────────────────

import pygame
import math
import random
import time
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_PRIMARY, COLOR_SECONDARY,
    COLOR_BG, COLOR_TEXT, COLOR_TEXT_DIM,
    COLOR_PROGRESS_BG, COLOR_PROGRESS_FG,
    COLOR_PARTICLE,
    PARTICLE_COUNT, PARTICLE_MIN_SIZE, PARTICLE_MAX_SIZE,
    PARTICLE_SPEED_MIN, PARTICLE_SPEED_MAX,
    PROGRESS_WIDTH, PROGRESS_HEIGHT, PROGRESS_Y_OFFSET,
    PROGRESS_SPEED, PROGRESS_CORNER_R,
    LOGO_PULSE_SPEED, LOGO_PULSE_SCALE,
    BOOT_MESSAGES,
    FONT_NAME_SIZE, FONT_VERSION_SIZE, FONT_STATUS_SIZE,
    OS_NAME, OS_VERSION, OS_TAGLINE,
)


# ── Particle ──────────────────────────────────────────

class Particle:
    """A single floating ambient particle."""

    def __init__(self):
        self.reset(initial=True)

    def reset(self, initial: bool = False):
        self.x     = random.uniform(0, SCREEN_WIDTH)
        self.y     = random.uniform(0, SCREEN_HEIGHT) if initial else SCREEN_HEIGHT + 10
        self.size  = random.uniform(PARTICLE_MIN_SIZE, PARTICLE_MAX_SIZE)
        self.speed = random.uniform(PARTICLE_SPEED_MIN, PARTICLE_SPEED_MAX)
        self.alpha = random.randint(30, 120)
        self.drift = random.uniform(-0.15, 0.15)

    def update(self):
        self.y -= self.speed
        self.x += self.drift
        if self.y < -10:
            self.reset()

    def draw(self, surface: pygame.Surface):
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*COLOR_PRIMARY[:3], self.alpha),
                           (int(self.size), int(self.size)), int(self.size))
        surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))


# ── Progress Bar ─────────────────────────────────────

class ProgressBar:
    """Animated progress bar with rounded corners and glow."""

    def __init__(self, cx: int, cy: int):
        self.cx       = cx
        self.cy       = cy
        self.progress = 0.0          # 0.0 → 1.0
        self.done     = False

    def update(self):
        if self.progress < 1.0:
            self.progress = min(1.0, self.progress + PROGRESS_SPEED)
        else:
            self.done = True

    def draw(self, surface: pygame.Surface, alpha: int = 255):
        x = self.cx - PROGRESS_WIDTH // 2
        y = self.cy - PROGRESS_HEIGHT // 2
        r = PROGRESS_CORNER_R

        # Background track
        bg_surf = pygame.Surface((PROGRESS_WIDTH, PROGRESS_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(bg_surf, (*COLOR_PROGRESS_BG, alpha),
                         (0, 0, PROGRESS_WIDTH, PROGRESS_HEIGHT), border_radius=r)
        surface.blit(bg_surf, (x, y))

        # Fill
        fill_w = int(PROGRESS_WIDTH * self.progress)
        if fill_w > 0:
            fill_surf = pygame.Surface((fill_w, PROGRESS_HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(fill_surf, (*COLOR_PROGRESS_FG, alpha),
                             (0, 0, fill_w, PROGRESS_HEIGHT), border_radius=r)
            surface.blit(fill_surf, (x, y))

            # Glow at tip
            glow_x = x + fill_w
            for gw in range(8, 0, -2):
                ga = int(alpha * (gw / 10) * 0.5)
                gs = pygame.Surface((gw * 2, PROGRESS_HEIGHT + gw * 2), pygame.SRCALPHA)
                pygame.draw.ellipse(gs, (*COLOR_PRIMARY, ga), gs.get_rect())
                surface.blit(gs, (glow_x - gw, y - gw))

    @property
    def percent(self) -> int:
        return int(self.progress * 100)


# ── Boot Text ────────────────────────────────────────

class BootText:
    """Renders OS name, version, tagline, and cycling status messages."""

    def __init__(self):
        # Try a clean sans-serif font; fall back to default
        try:
            self.font_name    = pygame.font.SysFont("DejaVu Sans",    FONT_NAME_SIZE,    bold=True)
            self.font_version = pygame.font.SysFont("DejaVu Sans",    FONT_VERSION_SIZE, bold=False)
            self.font_status  = pygame.font.SysFont("DejaVu Sans Mono", FONT_STATUS_SIZE, bold=False)
        except Exception:
            self.font_name    = pygame.font.Font(None, FONT_NAME_SIZE)
            self.font_version = pygame.font.Font(None, FONT_VERSION_SIZE)
            self.font_status  = pygame.font.Font(None, FONT_STATUS_SIZE)

        self.msg_index    = 0
        self.msg_timer    = 0
        self.msg_interval = 90       # frames between messages

    def update(self):
        self.msg_timer += 1
        if self.msg_timer >= self.msg_interval:
            self.msg_timer = 0
            self.msg_index = (self.msg_index + 1) % len(BOOT_MESSAGES)

    def draw(self, surface: pygame.Surface, cx: int, name_y: int,
             status_y: int, alpha: int = 255):
        a = max(0, min(255, alpha))

        # OS Name
        name_surf = self.font_name.render(OS_NAME, True, COLOR_TEXT)
        name_surf.set_alpha(a)
        surface.blit(name_surf, (cx - name_surf.get_width() // 2, name_y))

        # Tagline
        tag_surf = self.font_version.render(OS_TAGLINE, True, COLOR_TEXT_DIM)
        tag_surf.set_alpha(a)
        surface.blit(tag_surf, (cx - tag_surf.get_width() // 2,
                                name_y + name_surf.get_height() + 6))

        # Version
        ver_surf = self.font_version.render(f"v{OS_VERSION}", True, COLOR_TEXT_DIM)
        ver_surf.set_alpha(int(a * 0.6))
        surface.blit(ver_surf, (cx - ver_surf.get_width() // 2,
                                name_y + name_surf.get_height() + 26))

        # Status message
        msg_surf = self.font_status.render(BOOT_MESSAGES[self.msg_index], True,
                                           COLOR_TEXT_DIM)
        fade     = 1.0 - (self.msg_timer / self.msg_interval)
        msg_surf.set_alpha(int(a * 0.5 * (0.5 + 0.5 * fade)))
        surface.blit(msg_surf, (cx - msg_surf.get_width() // 2, status_y))


# ── Pulse Effect ─────────────────────────────────────

class PulseEffect:
    """Expanding ring pulse around the logo."""

    def __init__(self, cx: int, cy: int):
        self.cx    = cx
        self.cy    = cy
        self.rings = []          # list of (radius, alpha)
        self.timer = 0
        self.interval = 80       # frames between new rings

    def update(self, base_radius: float):
        self.timer += 1
        if self.timer >= self.interval:
            self.timer = 0
            self.rings.append([base_radius * 1.05, 180])

        alive = []
        for ring in self.rings:
            ring[0] += 1.2        # expand
            ring[1] -= 3          # fade
            if ring[1] > 0:
                alive.append(ring)
        self.rings = alive

    def draw(self, surface: pygame.Surface, global_alpha: int = 255):
        for radius, alpha in self.rings:
            a = int(alpha * (global_alpha / 255))
            if a <= 0:
                continue
            s = pygame.Surface((int(radius * 2 + 4), int(radius * 2 + 4)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*COLOR_PRIMARY, a),
                               (int(radius) + 2, int(radius) + 2),
                               int(radius), 1)
            surface.blit(s, (self.cx - int(radius) - 2, self.cy - int(radius) - 2))
