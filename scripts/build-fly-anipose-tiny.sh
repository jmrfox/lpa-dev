#!/usr/bin/env bash
set -euo pipefail
source "${HOME}/miniforge3/etc/profile.d/conda.sh"
conda run -n poseapp python3 "$(cd "$(dirname "$0")/.." && pwd)/scripts/build_fly_anipose_tiny.py"
du -sh "$(cd "$(dirname "$0")/.." && pwd)/datasets/fly-anipose-tiny"
