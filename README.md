# lpa-dev — Lightning Pose App dev workspace

Git snapshot of the **Lightning Studio** home directory used for Lightning Pose App development, also used as the **Cursor workspace root on WSL**. This repo holds studio configuration, Cursor rules, helper scripts, and planning docs—not the application source trees.

## What is tracked here

- `CLAUDE.md` — Claude Code entry point (primary agent)
- `.cursor/` — rules (canonical for both agents), plans, and related Cursor project config
- `.claude/rules/` — symlinks to `.cursor/rules/*.mdc` so Claude Code loads the same rules
- `bin/` — `lpa-dev`, `lpa-dev-init` (one-time machine setup), `gitstatus`, `lpa-stop`
- `shell/` — `lpa-dev.sh` (bash/zsh `setup` function and PATH; `lpa-dev.zsh` forwards to it)
- `scripts/` — `fit_mirror_mouse_calibration.py` (a calibration.toml for mirror-mouse-separate, fitted to its labels, for testing nonlinear EKS)
- `feature_plans/`, `BUGS.md`, `lpa-code-reviews/`
- `project.yaml`, `.lightningignore`, `.lightning_studio/` hooks
- Editor snippets: `.vscode/settings.json`, `.angular-config.json`, `.storybook/`

## What is **not** tracked

| Path | Reason |
|------|--------|
| `lightning-pose/` | [paninski-lab/lightning-pose](https://github.com/paninski-lab/lightning-pose) |
| `lightning-pose-app/` | [paninski-lab/lightning-pose-app](https://github.com/paninski-lab/lightning-pose-app) |
| `data/`, `LPProjects/` | Large local data, including small test projects |
| `.lightning_studio/.studiorc` | Lightning Studio machine config (see `.lightning_studio/README.md`) |

## Layout (both machines)

```text
lpa-dev/                    # this repo (workspace root)
  bin/lpa-dev
  lightning-pose/           # separate git clone
  lightning-pose-app/       # separate git clone
  LPProjects/               # optional; gitignored
```

| Machine | Typical `lpa-dev` path |
|---------|-------------------------|
| Lightning Studio | `$HOME` = `/teamspace/studios/this_studio` |
| WSL | e.g. `/home/jordan/repos/lpa-dev` |

`bin/lpa-dev` resolves `lightning-pose-app` relative to the repo root (override with `LPA_ROOT` / `LPA_DEV_ROOT` if needed).

## New machine

Prerequisites: git, curl, and conda ([Miniforge](https://conda-forge.org/download/)).
On HPC/Jetstream, `module load miniforge` first.

```bash
git clone https://github.com/jmrfox/lpa-dev.git lpa-dev
cd lpa-dev
bin/lpa-dev-init --dry-run    # see what it would do; changes nothing
bin/lpa-dev-init              # asks, then does it
```

`lpa-dev init` (same script) works on WSL, plain Linux, Jetstream, and Lightning Studio.
It checks each step and skips what is done, so rerun it after anything fails.
`--check` prints status only.

| Step | Notes |
|------|-------|
| Clone LP and LPA | Only if missing. Existing clones are never pulled or reset. |
| apt: zsh, lsof, ffmpeg, git, curl | Missing ones only. Asks separately before sudo (`--apt` to skip the question). |
| Conda env `poseapp` (Python 3.11) | In your user env dir. Never `conda init`, never base. On Studio it uses `cloudspace` and never creates an env. `--env NAME` or `LPA_CONDA_ENV` to change. |
| torch | CPU build when no NVIDIA GPU is visible, else the default CUDA build. Never replaces an installed torch. `--torch cpu\|cuda\|skip`. |
| Editable installs | `lightning-pose`, then `lightning-pose-app/app_server[dev]`, into that env's python only. |
| pre-commit, nvm, Node, `npm ci` | nvm is installed with `PROFILE=/dev/null`, so it edits no shell files. Node version from `web_ui/.nvmrc`. |
| Shell startup file | Adds `source …/shell/lpa-dev.sh` to `~/.bashrc` or `~/.zshrc`. Asks separately (`--edit-rc`). |

It stops before installing if free disk looks too small: about 10 GB with CPU torch,
18 GB with CUDA torch. On a small machine, `--skip-lp` installs the app without torch and
lightning-pose (about 3 GB). The app and its tests run, but training and `litpose` do not.

**Small root disk (e.g. Jetstream m3.small, 20 GB):** attach a volume and put the env there:

```bash
bin/lpa-dev-init --env /media/volume/<name>/poseapp
```

The env's package cache and pip's temp files go on the volume too. The choice is saved in
`.lpa-dev.local` (gitignored), so `lpa-dev setup` and later `init` runs use it.

Afterwards:

- **GitHub**: `gh auth login` and `gh auth setup-git` as **jmrfox**.
- **UI tests** (`lpa-dev test`): install Chromium or Google Chrome; set `CHROME_BIN` if auto-detection fails.
- **Small test project** (optional): copy `LPProjects/mirror-mouse-fused-tiny` from Studio into `lpa-dev/LPProjects/`.

## Lightning Studio one-time setup

- Conda env **`cloudspace`** (do not create `poseapp` on Studio).
- Clone LP/LPA beside this repo if not already present.
- Node 26 under `lpa-dev/.nvm` (or Studio `~/.nvm`); use `lpa-dev setup` after sourcing `shell/lpa-dev.sh`.
- Optional: `on_start.sh` for `nvm use 26` after Studio restarts.

## Daily workflow

```bash
lpa-dev setup                   # each new terminal: activates poseapp (Studio: cloudspace), Node 26
lpa-dev run                     # honcho → http://localhost:4200
lpa-dev gitstatus               # LP + LPA only
git status                      # lpa-dev config repo
```

Before switching machines: `git pull` in **all three** repos; run `lpa-dev setup` after dependency changes, and `lpa-dev init` if a step is new.
