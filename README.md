# lpa-dev — Lightning Studio + WSL workspace

Git snapshot of the **Lightning Studio** home directory used for Lightning Pose App development, also used as the **Cursor workspace root on WSL**. This repo holds studio configuration, Cursor rules, helper scripts, and planning docs—not the application source trees.

## What is tracked here

- `.cursor/` — rules, skills, plans, and related Cursor project config (see `.cursor/.gitignore`)
- `bin/` — `lpa-dev`, `gitstatus`, `lpa-stop`
- `shell/` — `lpa-dev.zsh` (zsh `setup` function and PATH)
- `scripts/` — `wsl-one-time-setup.sh` (WSL toolchain bootstrap)
- `feature_plans/`, `BUGS.md`, `lpa-web-ui-code-review.md`
- `project.yaml`, `.lightningignore`, `.lightning_studio/` hooks
- Editor snippets: `.vscode/settings.json`, `.angular-config.json`, `.storybook/`

## What is **not** tracked

| Path | Reason |
|------|--------|
| `lightning-pose/` | [paninski-lab/lightning-pose](https://github.com/paninski-lab/lightning-pose) |
| `lightning-pose-app/` | [paninski-lab/lightning-pose-app](https://github.com/paninski-lab/lightning-pose-app) |
| `data/`, `LPProjects/` | Large local/smoke-test data |
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

## Fresh clone

```bash
git clone https://github.com/jmrfox/lpa-dev.git lpa-dev
cd lpa-dev
git clone https://github.com/paninski-lab/lightning-pose.git
git clone https://github.com/paninski-lab/lightning-pose-app.git
```

On Studio you may instead `git clone …/lpa-dev.git .` into `$HOME`.

## WSL one-time setup

Prerequisites: [Miniforge](https://github.com/conda-forge/miniforge) (or conda), `auto_activate_base` false if you prefer, and **GitHub CLI** (`sudo apt install gh` on Ubuntu/WSL).

```bash
bash scripts/wsl-one-time-setup.sh
```

That installs **zsh**, **lsof**, **ffmpeg**, creates conda env **`poseapp`** (Python 3.11), editable **lightning-pose** + **lightning-pose-app** `[dev]`, **pre-commit** hooks, and **Node 26** via nvm.

Then add to `~/.zshrc`:

```bash
source /home/jordan/repos/lpa-dev/shell/lpa-dev.zsh   # adjust path
```

New terminal:

```bash
conda activate poseapp
lpa-dev setup
lpa-dev status
```

- **UI tests** (`lpa-dev test`): install Chromium or Google Chrome; set `CHROME_BIN` if auto-detection fails.
- **GitHub**: `gh auth login` and `gh auth setup-git` as **jmrfox**.
- **Smoke data** (optional): copy `LPProjects/mirror-mouse-fused-tiny` from Studio into `lpa-dev/LPProjects/`.

## Lightning Studio one-time setup

- Conda env **`cloudspace`** (do not create `poseapp` on Studio).
- Clone LP/LPA beside this repo if not already present.
- Node 26 under `lpa-dev/.nvm` (or Studio `~/.nvm`); use `lpa-dev setup` in zsh after sourcing `shell/lpa-dev.zsh`.
- Optional: `on_start.sh` for `nvm use 26` after Studio restarts.

## Daily workflow

```bash
conda activate poseapp          # WSL; Studio: cloudspace
lpa-dev setup                   # each new zsh terminal
lpa-dev run                     # honcho → http://localhost:4200
lpa-dev gitstatus               # LP + LPA only
git status                      # lpa-dev config repo
```

Before switching machines: `git pull` in **all three** repos; run `lpa-dev setup` after dependency changes.
