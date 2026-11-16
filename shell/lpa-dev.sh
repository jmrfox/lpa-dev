# lpa-dev shell integration for bash and zsh. Source it from ~/.bashrc or ~/.zshrc:
#   source /path/to/lpa-dev/shell/lpa-dev.sh
# `lpa-dev init` offers to add that line for you.

if [ -z "${LPA_DEV_ROOT:-}" ]; then
  if [ -n "${ZSH_VERSION:-}" ]; then
    eval '_lpa_dev_src="${(%):-%x}"'
  else
    _lpa_dev_src="${BASH_SOURCE[0]}"
  fi
  LPA_DEV_ROOT="$(cd "$(dirname "$_lpa_dev_src")/.." && pwd)"
  unset _lpa_dev_src
fi
export LPA_DEV_ROOT

_lpa_dev_bin="${LPA_DEV_ROOT}/bin/lpa-dev"

# Conda env for this machine: LPA_CONDA_ENV, else the one lpa-dev init saved in
# .lpa-dev.local (a name or a path), else cloudspace on Lightning Studio, else poseapp.
_lpa_dev_env_name() {
  local saved=""
  if [ -f "$LPA_DEV_ROOT/.lpa-dev.local" ]; then
    saved="$(sed -n 's/^LPA_CONDA_ENV=//p' "$LPA_DEV_ROOT/.lpa-dev.local" | tail -1)"
  fi
  if [ -n "${LPA_CONDA_ENV:-}" ]; then
    echo "$LPA_CONDA_ENV"
  elif [ -n "$saved" ]; then
    echo "$saved"
  elif [ -d /teamspace/studios/this_studio ]; then
    echo cloudspace
  else
    echo poseapp
  fi
}

# Activate the env in this shell. Loads the miniforge environment module when
# conda is missing and the module exists (HPC/Jetstream). Never runs `conda init`.
_lpa_dev_activate() {
  local env_name
  env_name="$(_lpa_dev_env_name)"
  # CONDA_DEFAULT_ENV is the name, or the full path for an env activated by path.
  [ "${CONDA_DEFAULT_ENV:-}" = "$env_name" ] && return 0
  if ! command -v conda >/dev/null 2>&1 && type module >/dev/null 2>&1; then
    module load miniforge >/dev/null 2>&1 && echo "Loaded module miniforge"
  fi
  if ! command -v conda >/dev/null 2>&1; then
    echo "conda not found; activate $env_name yourself, or run lpa-dev init." >&2
    return 1
  fi
  # `conda activate` needs the shell hook; load it without editing any rc file.
  if ! type conda 2>/dev/null | grep -q function; then
    local base
    base="$(conda info --base 2>/dev/null)"
    # shellcheck source=/dev/null
    [ -f "$base/etc/profile.d/conda.sh" ] && . "$base/etc/profile.d/conda.sh"
  fi
  conda activate "$env_name" || {
    echo "Could not activate conda env $env_name (run lpa-dev init)." >&2
    return 1
  }
  echo "Activated conda env $env_name"
}

lpa-dev() {
  local subcmd="${1:-run}"
  if [ "$subcmd" = setup ]; then
    local node_bin
    _lpa_dev_activate || return 1
    node_bin="$("$_lpa_dev_bin" print-node26)"
    if [ -z "$node_bin" ] || [ ! -x "$node_bin/node" ]; then
      echo "Node 26 not found. Run: lpa-dev init" >&2
      return 1
    fi
    export PATH="$node_bin:$PATH"
    # Lightning Studio defines node/npm/npx as shell functions that pin Node 22.
    unset -f node npm npx 2>/dev/null || true
    "$_lpa_dev_bin" sync-editable || return 1
    "$_lpa_dev_bin" sync-ui || return 1
    return 0
  fi
  if [ "$subcmd" = init ]; then
    shift
    "${LPA_DEV_ROOT}/bin/lpa-dev-init" "$@"
    return
  fi
  "$_lpa_dev_bin" "$@"
}

case ":${PATH}:" in
  *":${LPA_DEV_ROOT}/bin:"*) ;;
  *) export PATH="${LPA_DEV_ROOT}/bin:${PATH}" ;;
esac
