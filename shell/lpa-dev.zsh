# lpa-dev shell integration (zsh). Source from ~/.zshrc:
#   source /path/to/lpa-dev/shell/lpa-dev.zsh

if [[ -z "${LPA_DEV_ROOT:-}" ]]; then
  LPA_DEV_ROOT="$(cd "${${(%):-%N}:A:h}/.." && pwd)"
fi
export LPA_DEV_ROOT

_lpa_dev_bin="${LPA_DEV_ROOT}/bin/lpa-dev"

lpa-dev() {
  local subcmd="${1:-run}"
  if [[ "$subcmd" == setup ]]; then
    local node26_bin
    node26_bin="$("$_lpa_dev_bin" print-node26)"
    if [[ -z "$node26_bin" || ! -x "$node26_bin/node" ]]; then
      echo "Node 26 not found (install nvm and run: cd lightning-pose-app/web_ui && nvm install)" >&2
      return 1
    fi
    export PATH="$node26_bin:$PATH"
    unfunction node npm npx 2>/dev/null || true
    unset -f node npm npx 2>/dev/null || true
    "$_lpa_dev_bin" sync-editable
    "$_lpa_dev_bin" sync-ui
    return 0
  fi
  "$_lpa_dev_bin" "$@"
}

export PATH="${LPA_DEV_ROOT}/bin:${PATH}"
