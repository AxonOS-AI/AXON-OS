#!/usr/bin/env bash

set -e

AXON_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$AXON_DIR/.venv"
LOCAL_BIN="$HOME/.local/bin"
AXON_LINK="$LOCAL_BIN/axon"

echo "AXON OS Developer Preview setup"
echo "================================"
echo "Project directory: $AXON_DIR"
echo ""

if ! command -v python3 >/dev/null 2>&1; then
    echo "AXON Error: python3 is not installed."
    exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "[AXON] Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
else
    echo "[AXON] Virtual environment already exists."
fi

VENV_PYTHON="$VENV_DIR/bin/python"

if [ ! -x "$VENV_PYTHON" ]; then
    echo "AXON Error: virtual environment python was not created correctly."
    echo "Expected: $VENV_PYTHON"
    exit 1
fi

echo "[AXON] Skipping automatic pip upgrade to avoid unnecessary downloads."
echo "[AXON] Existing pip version:"
"$VENV_PYTHON" -m pip --version

if [ -f "$AXON_DIR/requirements.txt" ]; then
    echo "[AXON] Installing minimal Developer Preview requirements..."
    "$VENV_PYTHON" -m pip install -r "$AXON_DIR/requirements.txt"
fi

echo "[AXON] Preparing command wrapper..."
chmod +x "$AXON_DIR/axon"

mkdir -p "$LOCAL_BIN"
ln -sf "$AXON_DIR/axon" "$AXON_LINK"
chmod +x "$AXON_LINK"

echo ""
echo "AXON setup completed."
echo ""
echo "Available commands:"
echo "  axon start"
echo "  axon start --fast"
echo "  axon doctor"
echo "  axon version"
echo "  axon help"
echo ""
echo "Run:"
echo "  axon start --fast"
