#!/bin/bash
# =============================================================================
# Axon Platform - Environment Setup Script
# =============================================================================
# Usage: bash setup_env.sh [--skip-update] [--cpu-only] [--venv]
# =============================================================================

set -euo pipefail

# ─────────────────────────────────────────────
# ANSI Colors
# ─────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

log_info()    { echo -e "${CYAN}[INFO]${RESET}  $*"; }
log_success() { echo -e "${GREEN}[OK]${RESET}    $*"; }
log_warn()    { echo -e "${YELLOW}[WARN]${RESET}  $*"; }
log_error()   { echo -e "${RED}[ERROR]${RESET} $*" >&2; }
log_section() {
  echo -e "\n${BOLD}${CYAN}══════════════════════════════════════════${RESET}"
  echo -e "${BOLD}${CYAN}  $*${RESET}"
  echo -e "${BOLD}${CYAN}══════════════════════════════════════════${RESET}"
}

# ─────────────────────────────────────────────
# Argument Parsing
# ─────────────────────────────────────────────
SKIP_UPDATE=false
CPU_ONLY=false
USE_VENV=false
VENV_PATH="${HOME}/axon-venv"

for arg in "$@"; do
  case $arg in
    --skip-update) SKIP_UPDATE=true ;;
    --cpu-only)    CPU_ONLY=true ;;
    --venv)        USE_VENV=true ;;
    --help)
      echo "Usage: bash setup_env.sh [OPTIONS]"
      echo "  --skip-update   Skip apt update & upgrade"
      echo "  --cpu-only      Install CPU-only PyTorch (no CUDA)"
      echo "  --venv          Use virtual environment (safer)"
      echo "  --help          Show this help"
      exit 0
      ;;
    *) log_warn "Unknown argument: $arg (ignored)" ;;
  esac
done

# ─────────────────────────────────────────────
# Sudo Check
# ─────────────────────────────────────────────
if [[ "$EUID" -ne 0 ]]; then
  log_warn "Not running as root. Sudo will be used where required."
  SUDO="sudo"
else
  SUDO=""
fi

# ─────────────────────────────────────────────
# Detect PEP 668 (externally-managed Python)
# Ubuntu 22.04+ blocks pip system-wide installs
# ─────────────────────────────────────────────
EXTERNALLY_MANAGED=false
if find /usr/lib/python3* -maxdepth 1 -name "EXTERNALLY-MANAGED" 2>/dev/null | grep -q .; then
  EXTERNALLY_MANAGED=true
fi

# pip_install() — wrapper يضيف --break-system-packages تلقائياً
pip_install() {
  if [[ "$EXTERNALLY_MANAGED" == true && "$USE_VENV" == false ]]; then
    pip3 install --break-system-packages "$@"
  elif [[ "$USE_VENV" == true ]]; then
    "${VENV_PATH}/bin/pip" install "$@"
  else
    pip3 install "$@"
  fi
}

# python_run() — wrapper يشغّل Python من venv أو النظام
python_run() {
  if [[ "$USE_VENV" == true ]]; then
    "${VENV_PATH}/bin/python" "$@"
  else
    python3 "$@"
  fi
}

command_exists() { command -v "$1" &>/dev/null; }

# ─────────────────────────────────────────────
# إظهار وضع التثبيت
# ─────────────────────────────────────────────
if [[ "$EXTERNALLY_MANAGED" == true ]]; then
  log_warn "Detected externally-managed Python (PEP 668 / Ubuntu 22.04+)."
  if [[ "$USE_VENV" == true ]]; then
    log_info "Mode: Virtual environment → ${VENV_PATH}"
  else
    log_warn "Mode: --break-system-packages (use --venv for safer install)"
  fi
fi

# =============================================================================
# STEP 1 — System Update
# =============================================================================
log_section "Step 1 · System Update & Upgrade"

if [[ "$SKIP_UPDATE" == true ]]; then
  log_warn "Skipping system update (--skip-update flag)."
else
  log_info "Running apt update..."
  $SUDO apt update

  log_info "Running apt upgrade..."
  $SUDO apt upgrade -y

  log_info "Installing prerequisites..."
  $SUDO apt install -y \
    curl wget gnupg lsb-release ca-certificates \
    software-properties-common apt-transport-https \
    build-essential git

  log_success "System updated successfully."
fi

# =============================================================================
# STEP 2 — Python3 & pip
# =============================================================================
log_section "Step 2 · Python3 & pip"

if command_exists python3; then
  log_info "Python3 already installed: $(python3 --version)"
else
  log_info "Installing Python3..."
  $SUDO apt install -y python3 python3-dev
  log_success "Python3 installed."
fi

if command_exists pip3; then
  log_info "pip3 already installed: $(pip3 --version)"
else
  log_info "Installing pip3..."
  $SUDO apt install -y python3-pip
  log_success "pip3 installed."
fi

# ── Virtual Environment Setup ──────────────────
if [[ "$USE_VENV" == true ]]; then
  log_info "Installing python3-venv..."
  $SUDO apt install -y python3-venv python3-full

  if [[ ! -d "${VENV_PATH}" ]]; then
    log_info "Creating venv at: ${VENV_PATH}"
    python3 -m venv "${VENV_PATH}"
    log_success "Virtual environment created."
  else
    log_info "Virtual environment already exists: ${VENV_PATH}"
  fi

  log_info "Upgrading pip inside venv..."
  "${VENV_PATH}/bin/pip" install --upgrade pip
  log_success "Venv pip upgraded: $(${VENV_PATH}/bin/pip --version)"

  if ! grep -q "${VENV_PATH}/bin/activate" ~/.bashrc 2>/dev/null; then
    echo "" >> ~/.bashrc
    echo "# Axon Platform venv" >> ~/.bashrc
    echo "source ${VENV_PATH}/bin/activate" >> ~/.bashrc
    log_info "Added venv activation to ~/.bashrc"
  fi
else
  # ── Upgrade system pip ──────────────────────
  log_info "Upgrading pip..."
  pip_install --upgrade pip
  log_success "pip upgraded: $(pip3 --version)"

  # symlink python → python3
  if ! command_exists python && command_exists python3; then
    log_info "Creating symlink: python → python3"
    $SUDO ln -sf "$(command -v python3)" /usr/local/bin/python
  fi
fi

# =============================================================================
# STEP 3 — Node.js & npm
# =============================================================================
log_section "Step 3 · Node.js & npm"

if command_exists node; then
  log_info "Node.js already installed: $(node --version) | npm: $(npm --version)"
else
  log_info "Adding NodeSource LTS repository..."
  curl -fsSL https://deb.nodesource.com/setup_lts.x | $SUDO -E bash -
  $SUDO apt install -y nodejs
  log_success "Node.js $(node --version) and npm $(npm --version) installed."
fi

# =============================================================================
# STEP 4 — Docker
# =============================================================================
log_section "Step 4 · Docker"

if command_exists docker; then
  log_info "Docker already installed: $(docker --version)"
else
  log_info "Adding Docker GPG key and repository..."
  $SUDO install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
    | $SUDO gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  $SUDO chmod a+r /etc/apt/keyrings/docker.gpg

  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
    https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
    | $SUDO tee /etc/apt/sources.list.d/docker.list > /dev/null

  $SUDO apt update
  $SUDO apt install -y \
    docker-ce docker-ce-cli containerd.io \
    docker-buildx-plugin docker-compose-plugin

  if [[ -n "${SUDO_USER:-}" ]]; then
    log_info "Adding '${SUDO_USER}' to docker group..."
    $SUDO usermod -aG docker "${SUDO_USER}"
    log_warn "Log out and back in for docker group to take effect."
  fi

  $SUDO systemctl enable docker
  $SUDO systemctl start docker
  log_success "Docker $(docker --version) installed and started."
fi

# =============================================================================
# STEP 5 — AI / ML Libraries
# =============================================================================
log_section "Step 5 · AI / ML Libraries (GPU Support)"

# 5a. PyTorch
log_info "Installing PyTorch..."
if [[ "$CPU_ONLY" == true ]]; then
  log_warn "CPU-only mode — skipping CUDA."
  pip_install torch torchvision torchaudio \
    --index-url https://download.pytorch.org/whl/cpu
else
  log_info "Installing PyTorch with CUDA 11.8..."
  pip_install torch torchvision torchaudio \
    --index-url https://download.pytorch.org/whl/cu118
fi
log_success "PyTorch installed: $(python_run -c 'import torch; print(torch.__version__)' 2>/dev/null || echo 'check failed')"

# 5b. TensorFlow
log_info "Installing TensorFlow..."
pip_install tensorflow
log_success "TensorFlow installed: $(python_run -c 'import tensorflow as tf; print(tf.__version__)' 2>/dev/null || echo 'check failed')"

# 5c. Additional AI libraries
log_info "Installing supporting AI/ML libraries..."
pip_install \
  numpy \
  pandas \
  scikit-learn \
  matplotlib \
  seaborn \
  jupyter \
  transformers \
  accelerate \
  datasets \
  onnx \
  onnxruntime

log_success "All AI/ML libraries installed."

# =============================================================================
# STEP 6 — GPU Detection
# =============================================================================
log_section "Step 6 · GPU Detection"

if command_exists nvidia-smi; then
  log_info "NVIDIA GPU detected:"
  nvidia-smi --query-gpu=name,driver_version,memory.total \
    --format=csv,noheader 2>/dev/null || true
  CUDA_OK=$(python_run -c "import torch; print(torch.cuda.is_available())" 2>/dev/null || echo "unknown")
  log_info "PyTorch CUDA available: ${CUDA_OK}"
elif command_exists rocm-smi; then
  log_info "AMD ROCm GPU detected:"
  rocm-smi 2>/dev/null || true
else
  log_warn "No GPU detected. Running in CPU mode."
fi

# =============================================================================
# SUMMARY
# =============================================================================
log_section "Setup Complete ✓"

echo -e "${BOLD}Installed Components:${RESET}"
echo -e "  ${GREEN}✔${RESET}  Python3    : $(python3 --version 2>/dev/null)"
echo -e "  ${GREEN}✔${RESET}  pip3       : $(pip3 --version 2>/dev/null | cut -d' ' -f1-2)"
echo -e "  ${GREEN}✔${RESET}  Node.js    : $(node --version 2>/dev/null)"
echo -e "  ${GREEN}✔${RESET}  npm        : $(npm --version 2>/dev/null)"
echo -e "  ${GREEN}✔${RESET}  Docker     : $(docker --version 2>/dev/null | cut -d',' -f1)"
echo -e "  ${GREEN}✔${RESET}  PyTorch    : $(python_run -c 'import torch; print(torch.__version__)' 2>/dev/null || echo 'not verified')"
echo -e "  ${GREEN}✔${RESET}  TensorFlow : $(python_run -c 'import tensorflow as tf; print(tf.__version__)' 2>/dev/null || echo 'not verified')"

if [[ "$USE_VENV" == true ]]; then
  echo ""
  log_info "Venv path: ${VENV_PATH}"
  log_warn "Activate with: source ${VENV_PATH}/bin/activate"
fi

echo ""
log_info "Axon Platform environment is ready. 🚀"
