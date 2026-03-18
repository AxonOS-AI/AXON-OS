# axon-os/phase1_boot/splash_simulator/config.py
# ─────────────────────────────────────────────
# Axon OS — Boot Splash Configuration
# All visual and timing settings are centralized here.
# ─────────────────────────────────────────────

# ── Window ────────────────────────────────────
SCREEN_WIDTH  = 1920
SCREEN_HEIGHT = 1080
FPS           = 60
FULLSCREEN    = False          # Set True for real boot experience

# ── Identity ──────────────────────────────────
OS_NAME       = "Axon OS"
OS_VERSION    = "1.0.0"
OS_TAGLINE    = "Intelligence Layer"

# ── Color Palette ─────────────────────────────
COLOR_BG           = (5,   8,  18)       # Deep space black
COLOR_PRIMARY      = (0,  210, 255)      # Electric cyan
COLOR_SECONDARY    = (80,  40, 200)      # Deep violet
COLOR_TEXT         = (200, 220, 255)     # Soft blue-white
COLOR_TEXT_DIM     = (80,  100, 140)     # Dimmed text
COLOR_PROGRESS_BG  = (20,  28,  50)      # Progress bar background
COLOR_PROGRESS_FG  = (0,  210, 255)      # Progress bar fill
COLOR_GLOW         = (0,  180, 255, 60)  # Glow effect (RGBA)
COLOR_PARTICLE     = (0,  210, 255, 120) # Particle color (RGBA)

# ── Logo ──────────────────────────────────────
LOGO_SIZE          = 160       # Logo diameter in pixels
LOGO_PULSE_SPEED   = 0.03      # Pulse animation speed
LOGO_PULSE_SCALE   = 0.06      # Pulse scale range

# ── Progress Bar ──────────────────────────────
PROGRESS_WIDTH     = 320
PROGRESS_HEIGHT    = 3
PROGRESS_Y_OFFSET  = 140       # Distance below logo center
PROGRESS_SPEED     = 0.008     # How fast progress fills (0.0 → 1.0 per frame)
PROGRESS_CORNER_R  = 2         # Corner radius

# ── Text ──────────────────────────────────────
FONT_NAME_SIZE     = 42        # OS name font size
FONT_VERSION_SIZE  = 16        # Version text font size
FONT_STATUS_SIZE   = 14        # Status message font size

# ── Particles ─────────────────────────────────
PARTICLE_COUNT     = 55        # Number of floating particles
PARTICLE_MIN_SIZE  = 1
PARTICLE_MAX_SIZE  = 3
PARTICLE_SPEED_MIN = 0.2
PARTICLE_SPEED_MAX = 0.8

# ── Boot Messages ─────────────────────────────
BOOT_MESSAGES = [
    "Initializing Axon Platform Layer...",
    "Loading AI runtime environment...",
    "Mounting system components...",
    "Starting platform services...",
    "Connecting to base system...",
    "Axon OS ready.",
]

# ── Timing (seconds) ──────────────────────────
FADE_IN_DURATION   = 1.2
HOLD_DURATION      = 4.0
FADE_OUT_DURATION  = 0.8
