# AxonOS/platform/gui/themes/colors.py
# ─────────────────────────────────────────────────────────────────
# Copyright (c) 2024 Abdullah — Axon OS Project (AGPL-3.0)
# Purpose: Central color constants for all Axon OS UI components.
#          Import this file in any GUI module to stay consistent.
# Usage:   from platform.gui.themes.colors import AxonColors, theme
# ─────────────────────────────────────────────────────────────────


class AxonDark:
    """Dark theme color palette."""

    # ── Backgrounds ───────────────────────────────────────────────
    BG_PRIMARY      = "#050812"   # deepest background
    BG_SECONDARY    = "#0A0E1A"   # surface / panels
    BG_TERTIARY     = "#111827"   # cards / bars
    BG_HOVER        = "#1a2035"   # hover state
    BG_ACTIVE       = "#0d1828"   # active / pressed

    # ── Accent — Cyan (primary) ───────────────────────────────────
    CYAN            = "#00D4FF"   # primary accent
    CYAN_DIM        = "#00A8CC"   # dimmed accent
    CYAN_GLOW       = "#00D4FF44" # glow / shadow
    CYAN_BG         = "#00D4FF12" # subtle background tint
    CYAN_BORDER     = "#00D4FF30" # border with accent

    # ── Accent — Purple (secondary) ───────────────────────────────
    PURPLE          = "#6C3CE1"   # secondary accent
    PURPLE_DIM      = "#5230B0"   # dimmed
    PURPLE_BG       = "#6C3CE115" # subtle background tint

    # ── Text ──────────────────────────────────────────────────────
    TEXT_PRIMARY    = "#E8EDF5"   # main readable text
    TEXT_SECONDARY  = "#8899BB"   # muted / labels
    TEXT_HINT       = "#4A6080"   # hints / disabled
    TEXT_ACCENT     = "#00D4FF"   # highlighted text

    # ── Status Colors ─────────────────────────────────────────────
    STATUS_OK       = "#1D9E75"   # green — success
    STATUS_WARN     = "#EF9F27"   # amber — warning
    STATUS_ERROR    = "#E24B4A"   # red   — error
    STATUS_INFO     = "#378ADD"   # blue  — info

    # ── Borders ───────────────────────────────────────────────────
    BORDER_DEFAULT  = "#1E2D40"   # default border
    BORDER_HOVER    = "#2A4060"   # hover border
    BORDER_ACCENT   = "#00D4FF50" # accent border

    # ── Taskbar ───────────────────────────────────────────────────
    TASKBAR_BG      = "#111827"
    TASKBAR_ITEM_BG = "#0A0E1A"
    TASKBAR_ACTIVE  = "#00D4FF22"

    # ── Terminal / Monospace ──────────────────────────────────────
    FONT_MONO       = "Courier New, Monospace"
    FONT_SANS       = "Ubuntu, Sans"
    FONT_SIZE_SM    = 9
    FONT_SIZE_MD    = 11
    FONT_SIZE_LG    = 14
    FONT_SIZE_XL    = 18
    FONT_SIZE_XXL   = 22


class AxonLight:
    """Light theme color palette."""

    # ── Backgrounds ───────────────────────────────────────────────
    BG_PRIMARY      = "#F0F2F5"
    BG_SECONDARY    = "#FFFFFF"
    BG_TERTIARY     = "#E8EDF5"
    BG_HOVER        = "#DDE5F0"
    BG_ACTIVE       = "#C8D8EE"

    # ── Accent — Blue (primary) ───────────────────────────────────
    CYAN            = "#0064C8"
    CYAN_DIM        = "#0050A0"
    CYAN_GLOW       = "#0064C844"
    CYAN_BG         = "#0064C812"
    CYAN_BORDER     = "#0064C830"

    # ── Accent — Purple (secondary) ───────────────────────────────
    PURPLE          = "#5230B0"
    PURPLE_DIM      = "#3D2280"
    PURPLE_BG       = "#5230B015"

    # ── Text ──────────────────────────────────────────────────────
    TEXT_PRIMARY    = "#0F172A"
    TEXT_SECONDARY  = "#3A4A6A"
    TEXT_HINT       = "#6A7A9A"
    TEXT_ACCENT     = "#0064C8"

    # ── Status Colors ─────────────────────────────────────────────
    STATUS_OK       = "#15803D"
    STATUS_WARN     = "#B45309"
    STATUS_ERROR    = "#B91C1C"
    STATUS_INFO     = "#1D4ED8"

    # ── Borders ───────────────────────────────────────────────────
    BORDER_DEFAULT  = "#CBD5E1"
    BORDER_HOVER    = "#94A3B8"
    BORDER_ACCENT   = "#0064C850"

    # ── Taskbar ───────────────────────────────────────────────────
    TASKBAR_BG      = "#FFFFFF"
    TASKBAR_ITEM_BG = "#F0F2F5"
    TASKBAR_ACTIVE  = "#0064C822"

    # ── Fonts (same as dark) ──────────────────────────────────────
    FONT_MONO       = "Courier New, Monospace"
    FONT_SANS       = "Ubuntu, Sans"
    FONT_SIZE_SM    = 9
    FONT_SIZE_MD    = 11
    FONT_SIZE_LG    = 14
    FONT_SIZE_XL    = 18
    FONT_SIZE_XXL   = 22


# ── Active theme pointer ──────────────────────────────────────────

import os

def _load_saved_theme() -> str:
    """Read saved theme preference from disk."""
    path = os.path.expanduser("~/.axonos/theme.txt")
    if os.path.exists(path):
        return open(path).read().strip().lower()
    return "dark"

def save_theme(name: str) -> None:
    """Save theme preference to disk."""
    path = os.path.expanduser("~/.axonos/theme.txt")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(name.strip().lower())

def get_theme():
    """Return the active theme class (AxonDark or AxonLight)."""
    name = _load_saved_theme()
    if name == "light":
        return AxonLight
    return AxonDark

def toggle_theme() -> str:
    """Toggle between dark and light, return new theme name."""
    current = _load_saved_theme()
    new = "light" if current == "dark" else "dark"
    save_theme(new)
    return new

# ── Convenience alias ─────────────────────────────────────────────
# Usage: from colors import C
# Then:  C.CYAN, C.BG_PRIMARY, etc.

C = get_theme()

# ── GTK CSS variable mapping ──────────────────────────────────────
# Maps AxonOS color names to GTK CSS variable names

GTK_VAR_MAP = {
    "bg_primary":     "@bg_color",
    "bg_secondary":   "@base_color",
    "text_primary":   "@text_color",
    "text_secondary": "@insensitive_fg_color",
    "accent":         "@theme_selected_bg_color",
    "border":         "@borders",
}

# ── RGB helpers ───────────────────────────────────────────────────

def hex_to_rgb(hex_color: str) -> tuple:
    """Convert '#RRGGBB' to (R, G, B) integers."""
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def hex_to_rgba(hex_color: str, alpha: float = 1.0) -> tuple:
    """Convert '#RRGGBB' to (R, G, B, A) floats for GTK."""
    r, g, b = hex_to_rgb(hex_color)
    return (r / 255, g / 255, b / 255, alpha)

def hex_to_rgba_str(hex_color: str, alpha: float = 1.0) -> str:
    """Return 'rgba(R, G, B, A)' CSS string."""
    r, g, b = hex_to_rgb(hex_color)
    return f"rgba({r}, {g}, {b}, {alpha})"


# ── CLI test ──────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Axon OS Color System ===")
    t = get_theme()
    name = _load_saved_theme()
    print(f"Active theme: {name}")
    print(f"Primary BG:   {t.BG_PRIMARY}")
    print(f"Accent Cyan:  {t.CYAN}")
    print(f"Text Primary: {t.TEXT_PRIMARY}")
    print(f"Status OK:    {t.STATUS_OK}")
    r, g, b = hex_to_rgb(t.CYAN)
    print(f"Cyan RGB:     ({r}, {g}, {b})")
    print(f"Cyan RGBA:    {hex_to_rgba_str(t.CYAN, 0.8)}")
