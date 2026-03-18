# axon-os/phase1_boot/splash_simulator/main.py
# ─────────────────────────────────────────────
# Axon OS — Boot Splash Simulator
# Run this to preview the boot screen without installing anything.
#
# Usage:
#   pip install pygame
#   python main.py
#
# Press ESC or close the window to exit.
# ─────────────────────────────────────────────

import sys
import math
import pygame

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, FULLSCREEN,
    COLOR_BG, LOGO_SIZE,
    LOGO_PULSE_SPEED, LOGO_PULSE_SCALE,
    PROGRESS_Y_OFFSET,
    FADE_IN_DURATION, HOLD_DURATION, FADE_OUT_DURATION,
    PARTICLE_COUNT,
)
from animation import Particle, ProgressBar, BootText, PulseEffect
from logo_generator import draw_logo


# ── State Machine ─────────────────────────────
PHASE_FADE_IN  = "fade_in"
PHASE_HOLD     = "hold"
PHASE_FADE_OUT = "fade_out"
PHASE_DONE     = "done"


class BootSplash:
    def __init__(self, screen: pygame.Surface):
        self.screen    = screen
        self.cx        = SCREEN_WIDTH  // 2
        self.cy        = SCREEN_HEIGHT // 2

        # Components
        self.particles  = [Particle() for _ in range(PARTICLE_COUNT)]
        self.progress   = ProgressBar(self.cx, self.cy + PROGRESS_Y_OFFSET)
        self.boot_text  = BootText()
        self.pulse      = PulseEffect(self.cx, self.cy)

        # State
        self.phase      = PHASE_FADE_IN
        self.phase_time = 0.0
        self.global_alpha = 0
        self.pulse_t    = 0.0
        self.clock      = pygame.time.Clock()

    # ── Phase transitions ──────────────────────
    def _update_phase(self, dt: float):
        self.phase_time += dt

        if self.phase == PHASE_FADE_IN:
            self.global_alpha = int(255 * min(1.0, self.phase_time / FADE_IN_DURATION))
            if self.phase_time >= FADE_IN_DURATION:
                self.phase = PHASE_HOLD
                self.phase_time = 0.0

        elif self.phase == PHASE_HOLD:
            self.global_alpha = 255
            if self.progress.done and self.phase_time >= HOLD_DURATION:
                self.phase = PHASE_FADE_OUT
                self.phase_time = 0.0

        elif self.phase == PHASE_FADE_OUT:
            self.global_alpha = int(255 * max(0.0, 1.0 - self.phase_time / FADE_OUT_DURATION))
            if self.phase_time >= FADE_OUT_DURATION:
                self.phase = PHASE_DONE

    # ── Main update ───────────────────────────
    def update(self):
        dt = self.clock.tick(FPS) / 1000.0

        self._update_phase(dt)
        self.pulse_t += LOGO_PULSE_SPEED

        for p in self.particles:
            p.update()

        self.progress.update()
        self.boot_text.update()

        # Compute pulsing logo size
        pulse_scale = 1.0 + math.sin(self.pulse_t) * LOGO_PULSE_SCALE
        self.current_logo_size = LOGO_SIZE * pulse_scale

        # Update pulse rings using pulsed radius
        self.pulse.update(self.current_logo_size)

    # ── Draw frame ────────────────────────────
    def draw(self):
        self.screen.fill(COLOR_BG)

        # Particles (behind everything)
        for p in self.particles:
            p.draw(self.screen)

        # Pulse rings (behind logo)
        self.pulse.draw(self.screen, self.global_alpha)

        # Logo
        draw_logo(self.screen, self.cx, self.cy,
                  self.current_logo_size, self.global_alpha)

        # Progress bar
        self.progress.draw(self.screen, self.global_alpha)

        # Text — name sits below logo, status at bottom third
        name_y    = self.cy + int(LOGO_SIZE * 1.1)
        status_y  = self.cy + PROGRESS_Y_OFFSET + 24
        self.boot_text.draw(self.screen, self.cx, name_y,
                             status_y, self.global_alpha)

        pygame.display.flip()

    # ── Run loop ──────────────────────────────
    def run(self) -> bool:
        """Returns True if the user closed normally, False if they quit."""
        while self.phase != PHASE_DONE:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return False
            self.update()
            self.draw()
        return True


# ── Entry Point ───────────────────────────────

def main():
    pygame.init()

    flags = pygame.FULLSCREEN if FULLSCREEN else 0
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
    pygame.display.set_caption("Axon OS — Boot Screen")
    pygame.mouse.set_visible(False)

    splash = BootSplash(screen)
    splash.run()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
