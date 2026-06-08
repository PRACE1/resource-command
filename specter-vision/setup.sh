#!/usr/bin/env bash
# =============================================================================
#   SPECTER-VISION — One-Click Setup
#   Kgosi Capital // NVIDIA A100 / H100 Server (Ubuntu 22.04+)
#
#   Usage:
#     chmod +x setup.sh && sudo ./setup.sh
#
#   What this script does:
#     1. Validates NVIDIA GPU + CUDA drivers
#     2. Installs Docker + NVIDIA Container Toolkit if missing
#     3. Creates the full model/volume directory tree
#     4. Clones and configures all required ComfyUI custom nodes
#     5. Downloads RIFE 4.7 interpolation model
#     6. Optionally downloads Wan 2.1 I2V 14B via HuggingFace CLI
#     7. Builds Docker images and starts the stack
# =============================================================================

set -euo pipefail

# ── Colours ──────────────────────────────────────────────────────────
CYAN='\033[0;36m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
RED='\033[0;31m';  BOLD='\033[1m';     RESET='\033[0m'

log_step()    { echo -e "\n${BOLD}${CYAN}▸ $*${RESET}"; }
log_success() { echo -e "  ${GREEN}✓ $*${RESET}"; }
log_info()    { echo -e "  ${YELLOW}→ $*${RESET}"; }
log_error()   { echo -e "  ${RED}✕ $*${RESET}" >&2; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MIN_VRAM_GB=20   # Wan 2.1 14B fp8 minimum

# =============================================================================
print_banner() {
cat <<'EOF'

  ╔═══════════════════════════════════════════════════════════════╗
  ║          S P E C T E R - V I S I O N   S E T U P             ║
  ║          Kgosi Capital // Private AI Video Terminal           ║
  ╚═══════════════════════════════════════════════════════════════╝

EOF
}

# =============================================================================
step_check_prerequisites() {
  log_step "Checking prerequisites"

  # Root / sudo
  if [[ "$EUID" -ne 0 ]]; then
    log_error "Run this script with sudo: sudo ./setup.sh"
    exit 1
  fi

  # NVIDIA GPU & driver
  if ! command -v nvidia-smi &>/dev/null; then
    log_error "nvidia-smi not found. Install NVIDIA drivers first:"
    log_info  "  https://docs.nvidia.com/cuda/cuda-installation-guide-linux/"
    exit 1
  fi

  GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1)
  VRAM_MB=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -d ' ')
  VRAM_GB=$(( VRAM_MB / 1024 ))

  log_success "GPU: ${GPU_NAME} (${VRAM_GB} GB VRAM)"

  if [[ "$VRAM_GB" -lt "$MIN_VRAM_GB" ]]; then
    log_error "Minimum ${MIN_VRAM_GB} GB VRAM required for Wan 2.1 14B fp8."
    log_info  "Detected: ${VRAM_GB} GB. Consider 480P 1.3B model instead."
    read -rp "  Continue anyway? [y/N] " yn
    [[ "$yn" =~ ^[Yy]$ ]] || exit 1
  fi

  # CUDA driver version
  DRIVER_VER=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1)
  log_success "CUDA driver: ${DRIVER_VER}"

  # OS
  if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    log_success "OS: ${PRETTY_NAME}"
  fi
}

# =============================================================================
step_install_docker() {
  log_step "Docker & NVIDIA Container Toolkit"

  if ! command -v docker &>/dev/null; then
    log_info "Installing Docker CE..."
    apt-get update -qq
    apt-get install -y -qq ca-certificates curl gnupg lsb-release
    curl -fsSL https://get.docker.com | sh
    usermod -aG docker "${SUDO_USER:-$USER}" || true
    log_success "Docker installed"
  else
    log_success "Docker: $(docker --version | cut -d' ' -f3 | tr -d ',')"
  fi

  # Docker Compose plugin (v2)
  if ! docker compose version &>/dev/null 2>&1; then
    log_info "Installing Docker Compose plugin..."
    apt-get install -y -qq docker-compose-plugin
    log_success "Docker Compose installed"
  else
    log_success "Docker Compose: $(docker compose version --short 2>/dev/null || echo 'ok')"
  fi

  # NVIDIA Container Toolkit
  if ! dpkg -l | grep -q nvidia-container-toolkit 2>/dev/null; then
    log_info "Installing NVIDIA Container Toolkit..."
    DISTRIBUTION=$(. /etc/os-release; echo "${ID}${VERSION_ID}")
    curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey \
      | gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
    curl -sL "https://nvidia.github.io/libnvidia-container/${DISTRIBUTION}/libnvidia-container.list" \
      | sed 's|deb https://|deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://|g' \
      | tee /etc/apt/sources.list.d/nvidia-container-toolkit.list > /dev/null
    apt-get update -qq
    apt-get install -y -qq nvidia-container-toolkit
    nvidia-ctk runtime configure --runtime=docker
    systemctl restart docker
    log_success "NVIDIA Container Toolkit installed"
  else
    log_success "NVIDIA Container Toolkit: already installed"
  fi
}

# =============================================================================
step_install_python_tools() {
  log_step "Python tools"

  if ! command -v python3 &>/dev/null; then
    apt-get install -y -qq python3 python3-pip python3-venv
  fi
  log_success "Python: $(python3 --version)"

  if ! command -v huggingface-cli &>/dev/null; then
    log_info "Installing huggingface_hub CLI (for model downloads)..."
    pip install -q --upgrade "huggingface_hub[cli]"
  fi
  log_success "huggingface-cli: ready"

  if ! command -v git &>/dev/null; then
    apt-get install -y -qq git
  fi
  log_success "git: $(git --version | cut -d' ' -f3)"

  # wget for direct file downloads
  if ! command -v wget &>/dev/null; then
    apt-get install -y -qq wget
  fi
}

# =============================================================================
step_create_structure() {
  log_step "Directory structure"

  cd "$SCRIPT_DIR"

  declare -a DIRS=(
    "volumes/models/diffusion_models"
    "volumes/models/vae"
    "volumes/models/text_encoders"
    "volumes/models/clip_vision"
    "volumes/models/controlnet"
    "volumes/models/rife"
    "volumes/models/upscale_models"
    "volumes/custom_nodes"
    "volumes/output"
    "volumes/input"
    "volumes/uploads"
    "backend/outputs"
    "backend/uploads"
  )

  for d in "${DIRS[@]}"; do
    mkdir -p "$d"
  done

  log_success "$(echo "${#DIRS[@]}" directories created under $SCRIPT_DIR)"

  # Write a .gitignore for the large volume dirs
  cat > volumes/.gitignore <<'GITIGNORE'
models/
output/
input/
uploads/
custom_nodes/
GITIGNORE
}

# =============================================================================
step_install_custom_nodes() {
  log_step "ComfyUI custom nodes"

  cd "$SCRIPT_DIR"

  # Node definitions: "name|url"
  declare -a NODES=(
    "ComfyUI-WanVideoWrapper|https://github.com/kijai/ComfyUI-WanVideoWrapper.git"
    "comfyui_controlnet_aux|https://github.com/Fannovel16/comfyui_controlnet_aux.git"
    "ComfyUI-Frame-Interpolation|https://github.com/Fannovel16/ComfyUI-Frame-Interpolation.git"
    "ComfyUI-VideoHelperSuite|https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git"
    "ComfyUI-KJNodes|https://github.com/kijai/ComfyUI-KJNodes.git"
  )

  # Temporary venv for custom node pip deps (ComfyUI will use its own venv at runtime)
  VENV_DIR="$SCRIPT_DIR/.setup_venv"
  if [[ ! -d "$VENV_DIR" ]]; then
    python3 -m venv "$VENV_DIR" --system-site-packages
  fi
  # shellcheck disable=SC1091
  source "$VENV_DIR/bin/activate"

  for entry in "${NODES[@]}"; do
    IFS='|' read -r name url <<< "$entry"
    target="volumes/custom_nodes/$name"

    if [[ -d "$target/.git" ]]; then
      log_info "Updating $name..."
      git -C "$target" pull --ff-only --quiet
    else
      log_info "Cloning $name..."
      git clone --depth=1 --quiet "$url" "$target"
    fi

    if [[ -f "$target/requirements.txt" ]]; then
      pip install -q --no-warn-script-location -r "$target/requirements.txt" 2>/dev/null || true
    fi
    log_success "$name"
  done

  deactivate
}

# =============================================================================
step_download_models() {
  log_step "Model downloads"

  cd "$SCRIPT_DIR"

  # ── RIFE 4.7 (frame interpolation) — small, always download ──────
  RIFE_PATH="volumes/models/rife/rife47.pth"
  if [[ ! -f "$RIFE_PATH" ]]; then
    log_info "Downloading RIFE 4.7 (~360 MB)..."
    wget -q --show-progress \
      "https://github.com/hzwer/Practical-RIFE/releases/download/model-4.7/rife47.pth" \
      -O "$RIFE_PATH"
    log_success "RIFE 4.7 → volumes/models/rife/rife47.pth"
  else
    log_success "RIFE 4.7: already present"
  fi

  # ── Wan 2.1 I2V 14B — large, prompt user ─────────────────────────
  WAN_DIR="volumes/models/diffusion_models/wan2.1-i2v-14b"
  if [[ ! -d "$WAN_DIR" ]]; then
    echo ""
    echo -e "  ${BOLD}Wan 2.1 I2V 14B requires ~30 GB of disk space and ~20-60 min to download.${RESET}"
    read -rp "  Download now via HuggingFace? [Y/n] " yn
    yn="${yn:-Y}"
    if [[ "$yn" =~ ^[Yy]$ ]]; then
      log_info "Downloading Wan 2.1 I2V 14B (this will take a while)..."
      huggingface-cli download \
        Wan-AI/Wan2.1-I2V-14B-480P \
        --local-dir "$WAN_DIR" \
        --exclude "*.gguf"       # skip GGUF quantizations unless needed
      log_success "Wan 2.1 I2V 14B → $WAN_DIR"
    else
      log_info "Skipped. Download manually and place in:"
      log_info "  $SCRIPT_DIR/$WAN_DIR"
    fi
  else
    log_success "Wan 2.1 I2V 14B: already present"
  fi

  # ── Print checklist for models that need manual placement ─────────
  echo ""
  echo -e "  ${BOLD}Manual model placement required:${RESET}"
  echo -e "  ┌──────────────────────────────────────────────────────────────────────┐"
  echo -e "  │  Filename                             → Place in                     │"
  echo -e "  ├──────────────────────────────────────────────────────────────────────┤"
  echo -e "  │  wan_2.1_vae.safetensors              → volumes/models/vae/           │"
  echo -e "  │  umt5_xxl_fp8_e4m3fn_scaled.safetensors → volumes/models/text_encoders/ │"
  echo -e "  │  clip_vision_h.safetensors            → volumes/models/clip_vision/   │"
  echo -e "  │  depth_anything_v2_controlnet.safetensors → volumes/models/controlnet/ │"
  echo -e "  │  controlnet_canny_wan.safetensors     → volumes/models/controlnet/    │"
  echo -e "  └──────────────────────────────────────────────────────────────────────┘"
  echo -e "  Source: https://huggingface.co/Wan-AI"
}

# =============================================================================
step_write_env() {
  log_step "Environment configuration"

  cd "$SCRIPT_DIR"

  if [[ ! -f ".env" ]]; then
    cat > .env <<'ENV'
# Specter-Vision environment
COMFYUI_URL=http://comfyui:8188
OUTPUT_DIR=/app/outputs
UPLOAD_DIR=/app/uploads
WORKFLOW_DIR=/app/workflows
ENV
    log_success ".env created"
  else
    log_success ".env already exists — skipping"
  fi
}

# =============================================================================
step_build_and_start() {
  log_step "Building and starting Docker services"

  cd "$SCRIPT_DIR"

  log_info "Building backend image (includes FFmpeg)..."
  docker compose build --quiet backend

  log_info "Pulling ComfyUI image (may take several minutes first time)..."
  docker compose pull comfyui --quiet 2>/dev/null || true

  log_info "Starting all services..."
  docker compose up -d

  # Wait for health checks
  log_info "Waiting for ComfyUI to become healthy (up to 3 min)..."
  for i in $(seq 1 36); do
    if docker compose ps comfyui 2>/dev/null | grep -q "healthy"; then
      log_success "ComfyUI is healthy"
      break
    fi
    if [[ $i -eq 36 ]]; then
      log_info "ComfyUI still starting — check 'docker compose logs comfyui'"
    fi
    sleep 5
  done
}

# =============================================================================
print_final_report() {
  echo ""
  echo -e "${BOLD}${CYAN}"
  cat <<'EOF'
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    SPECTER-VISION — DEPLOYMENT COMPLETE
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF
  echo -e "${RESET}"
  echo -e "  ${GREEN}Terminal UI${RESET}  →  http://localhost:5173"
  echo -e "  ${GREEN}API Docs   ${RESET}  →  http://localhost:8000/api/docs"
  echo -e "  ${GREEN}ComfyUI    ${RESET}  →  http://localhost:8188"
  echo ""
  echo -e "  ${YELLOW}Service management:${RESET}"
  echo -e "    docker compose logs -f       # stream all logs"
  echo -e "    docker compose down          # stop"
  echo -e "    docker compose up -d         # start"
  echo ""
  echo -e "  ${YELLOW}Next step:${RESET} Place model files listed above, then refresh the terminal."
  echo ""
}

# =============================================================================
main() {
  print_banner
  step_check_prerequisites
  step_install_docker
  step_install_python_tools
  step_create_structure
  step_install_custom_nodes
  step_download_models
  step_write_env
  step_build_and_start
  print_final_report
}

main "$@"
