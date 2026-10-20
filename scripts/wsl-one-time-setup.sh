#!/usr/bin/env bash
# One-time WSL toolchain for lpa-dev. Run from bash (not zsh required for this script):
#   bash /path/to/lpa-dev/scripts/wsl-one-time-setup.sh
set -euo pipefail

LPA_DEV_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LP_ROOT="${LPA_DEV_ROOT}/lightning-pose"
LPA_ROOT="${LPA_DEV_ROOT}/lightning-pose-app"

echo "lpa-dev root: ${LPA_DEV_ROOT}"

if ! command -v sudo >/dev/null 2>&1; then
  echo "sudo not found; install zsh and lsof yourself if needed." >&2
else
  sudo apt-get update
  sudo apt-get install -y zsh lsof ffmpeg gh
fi

if [[ -f "${HOME}/miniforge3/etc/profile.d/conda.sh" ]]; then
  # shellcheck source=/dev/null
  source "${HOME}/miniforge3/etc/profile.d/conda.sh"
elif [[ -f "${HOME}/mambaforge/etc/profile.d/conda.sh" ]]; then
  # shellcheck source=/dev/null
  source "${HOME}/mambaforge/etc/profile.d/conda.sh"
else
  echo "conda not found (expected ~/miniforge3). Install Miniforge first." >&2
  exit 1
fi

echo "Checking conda env poseapp…"
if ! conda env list | awk '{print $1}' | grep -qx poseapp; then
  echo "Creating poseapp (python 3.11)…"
  conda create -n poseapp python=3.11 -y
else
  echo "poseapp already exists."
fi

if [[ ! -d "${LP_ROOT}" ]]; then
  echo "Missing clone: ${LP_ROOT}" >&2
  exit 1
fi
if [[ ! -d "${LPA_ROOT}/app_server" ]]; then
  echo "Missing clone: ${LPA_ROOT}/app_server" >&2
  exit 1
fi

# conda run captures stdout/stderr by default — looks hung during long pip installs.
echo "Installing lightning-pose (editable). First run can take 10+ minutes (torch, etc.); pip output follows…"
conda run -s -n poseapp pip install -e "${LP_ROOT}"

echo "Installing lightning-pose-app (editable)…"
conda run -s -n poseapp pip install -e "${LPA_ROOT}/app_server[dev]"

echo "Installing pre-commit hooks…"
conda run -s -n poseapp bash -lc "cd '${LPA_ROOT}' && pre-commit install"

echo "Setting up Node $(cat "${LPA_ROOT}/web_ui/.nvmrc") via nvm…"
if [[ ! -d "${HOME}/.nvm" ]]; then
  curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
fi
# shellcheck source=/dev/null
export NVM_DIR="${HOME}/.nvm"
source "${NVM_DIR}/nvm.sh"
nvm install "$(cat "${LPA_ROOT}/web_ui/.nvmrc")"
nvm use "$(cat "${LPA_ROOT}/web_ui/.nvmrc")"

echo ""
echo "Next steps:"
echo "  1. Add to ~/.zshrc:  source ${LPA_DEV_ROOT}/shell/lpa-dev.zsh"
echo "  2. conda activate poseapp   (or: conda config --set auto_activate_base false)"
echo "  3. zsh -l && lpa-dev setup && lpa-dev status"
echo "  4. gh auth login   (if not already jmrfox)"
echo "  5. Optional smoke data: copy LPProjects/mirror-mouse-fused-tiny from Studio"
