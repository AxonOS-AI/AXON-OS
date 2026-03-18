#!/usr/bin/env bash
# axon-os/phase1_boot/scripts/install_theme.sh
# ──────────────────────────────────────────────
# Axon OS — Plymouth Theme Installer
# Run as root on Ubuntu 20.04 / 22.04 / 24.04
# ──────────────────────────────────────────────

set -e

THEME_NAME="axon"
THEME_DIR="/usr/share/plymouth/themes/${THEME_NAME}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLYMOUTH_SRC="${SCRIPT_DIR}/../plymouth"
SIMULATOR_SRC="${SCRIPT_DIR}/../splash_simulator"

# ── Color output ──────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()    { echo -e "${CYAN}[Axon]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC}   $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
fail()    { echo -e "${RED}[FAIL]${NC} $1"; exit 1; }

# ── Check root ────────────────────────────────
if [[ $EUID -ne 0 ]]; then
    fail "This script must be run as root. Use: sudo ./install_theme.sh"
fi

# ── Check Plymouth is installed ──────────────
if ! command -v plymouth &>/dev/null; then
    info "Plymouth not found. Installing..."
    apt-get install -y plymouth plymouth-themes || fail "Failed to install Plymouth"
fi

success "Plymouth is available."

# ── Generate logo PNG via Python ─────────────
info "Generating Axon OS logo PNG..."

if command -v python3 &>/dev/null; then
    # Generate using the splash simulator's logo generator
    python3 - <<EOF
import sys, os
sys.path.insert(0, "${SIMULATOR_SRC}")
try:
    import pygame
    import logo_generator
    os.makedirs("${PLYMOUTH_SRC}/assets", exist_ok=True)
    logo_generator.generate_logo_png("${PLYMOUTH_SRC}/assets/axon_logo.png", 256)
    print("Logo generated successfully.")
except ImportError:
    print("pygame not available — using placeholder logo.")
    # Create a minimal fallback using PIL if available
    try:
        from PIL import Image, ImageDraw
        img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse([28, 28, 228, 228], outline=(0, 210, 255, 255), width=4)
        img.save("${PLYMOUTH_SRC}/assets/axon_logo.png")
        print("Fallback logo generated with PIL.")
    except ImportError:
        print("No image library available. Logo will be missing from boot screen.")
EOF
else
    warn "Python3 not found. Logo file may be missing."
fi

# ── Copy theme files ──────────────────────────
info "Installing theme to ${THEME_DIR}..."

mkdir -p "${THEME_DIR}/assets"
cp "${PLYMOUTH_SRC}/axon.plymouth" "${THEME_DIR}/"
cp "${PLYMOUTH_SRC}/axon.script"   "${THEME_DIR}/"

if [[ -f "${PLYMOUTH_SRC}/assets/axon_logo.png" ]]; then
    cp "${PLYMOUTH_SRC}/assets/axon_logo.png" "${THEME_DIR}/assets/"
    success "Logo copied."
else
    warn "Logo PNG not found — boot screen will show text only."
fi

success "Theme files installed."

# ── Set as default Plymouth theme ─────────────
info "Setting Axon as default Plymouth theme..."

if update-alternatives --list default.plymouth &>/dev/null; then
    update-alternatives --install \
        /usr/share/plymouth/themes/default.plymouth \
        default.plymouth \
        "${THEME_DIR}/axon.plymouth" 100

    update-alternatives --set default.plymouth \
        "${THEME_DIR}/axon.plymouth"
else
    # Fallback: set directly via plymouth config
    if command -v plymouth-set-default-theme &>/dev/null; then
        plymouth-set-default-theme axon
    else
        warn "Could not set default theme automatically. Set manually with:"
        warn "  sudo plymouth-set-default-theme axon"
    fi
fi

# ── Rebuild initramfs ─────────────────────────
info "Rebuilding initramfs (this may take a moment)..."
update-initramfs -u 2>&1 | tail -3

echo ""
echo -e "${GREEN}══════════════════════════════════════════${NC}"
echo -e "${GREEN}  Axon OS Boot Theme Installed Successfully${NC}"
echo -e "${GREEN}══════════════════════════════════════════${NC}"
echo ""
echo "Reboot your system to see the Axon OS boot screen."
echo ""
echo "To revert to Ubuntu default:"
echo "  sudo plymouth-set-default-theme ubuntu-logo"
echo "  sudo update-initramfs -u"
echo ""
