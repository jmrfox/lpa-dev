#!/usr/bin/env bash
# Quick checks after WSL setup. Exit 1 on any failure.
set -euo pipefail

LPA_DEV_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LPA_ROOT="${LPA_DEV_ROOT}/lightning-pose-app"
FAIL=0

check() {
  if eval "$2"; then
    echo "OK  $1"
  else
    echo "FAIL $1"
    FAIL=1
  fi
}

check "zsh" "command -v zsh >/dev/null"
check "lsof" "command -v lsof >/dev/null"
check "ffmpeg" "command -v ffmpeg >/dev/null"
check "conda poseapp" "source \"${HOME}/miniforge3/etc/profile.d/conda.sh\" 2>/dev/null && conda env list | awk '{print \$1}' | grep -qx poseapp"
check "litpose in poseapp" "conda run -n poseapp litpose --help >/dev/null 2>&1"
check "honcho in poseapp" "conda run -n poseapp honcho --version >/dev/null 2>&1"
check "node 26" "export NVM_DIR=\"${HOME}/.nvm\" && [ -s \"\$NVM_DIR/nvm.sh\" ] && . \"\$NVM_DIR/nvm.sh\" && node -v | grep -q '^v26\.'"
check "lpa-dev print-node26" "zsh -fc \"source '${LPA_DEV_ROOT}/shell/lpa-dev.zsh' && lpa-dev print-node26\" | grep -q node"
check "gh auth" "gh auth status -h github.com 2>&1 | grep -q 'Logged in'"

if [[ -e "${LPA_DEV_ROOT}/.lightning_studio/.studiorc" ]]; then
  if [[ -L "${LPA_DEV_ROOT}/.lightning_studio/.studiorc" ]] && [[ ! -e "${LPA_DEV_ROOT}/.lightning_studio/.studiorc" ]]; then
    echo "WARN broken .lightning_studio/.studiorc symlink — safe to: rm .lightning_studio/.studiorc"
  fi
fi

if [[ -x "${LPA_DEV_ROOT}/bin/lpa-dev" ]]; then
  if zsh -fc "source '${LPA_DEV_ROOT}/shell/lpa-dev.zsh' && lpa-dev sync-ui" 2>/dev/null; then
    echo "OK  lpa-dev sync-ui"
  else
    echo "FAIL lpa-dev sync-ui (run lpa-dev setup after conda activate poseapp)"
    FAIL=1
  fi
fi

exit "$FAIL"
