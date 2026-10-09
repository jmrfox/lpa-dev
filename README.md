# lpa-dev — Lightning Studio workspace

Git snapshot of the **Lightning Studio** home directory used for Lightning Pose App development. This repo holds studio configuration, Cursor rules, helper scripts, and planning docs—not the application source trees.

## What is tracked here

- `.cursor/` — rules, skills, plans, and related Cursor project config (see `.cursor/.gitignore`)
- `bin/` — `lpa-dev`, `gitstatus`, and other studio helpers
- `feature_plans/`, `BUGS.md`, `lpa-web-ui-code-review.md`
- `project.yaml`, `.lightningignore`, `.lightning_studio/` hooks
- Shell/editor snippets: `.zshrc`, `.bashrc`, `.vimrc`, `.vscode/settings.json`, `.angular-config.json`, `.storybook/`

## What is **not** tracked

| Path | Reason |
|------|--------|
| `lightning-pose/` | [paninski-lab/lightning-pose](https://github.com/paninski-lab/lightning-pose) |
| `lightning-pose-app/` | [paninski-lab/lightning-pose-app](https://github.com/paninski-lab/lightning-pose-app) |
| `data/`, `LPProjects/` | Large local/smoke-test data |

Clone those repos beside this tree on a fresh Studio machine, then pull this repo into `$HOME` (or merge paths) as needed.

## Fresh Studio layout (sketch)

```bash
# In $HOME (/teamspace/studios/this_studio on Lightning Studio)
git clone https://github.com/jmrfox/lpa-dev.git .
# Or clone into a subdir and copy tracked files—HOME is usually this repo root.

git clone https://github.com/paninski-lab/lightning-pose.git
git clone https://github.com/paninski-lab/lightning-pose-app.git
```

Use `bin/gitstatus` or `lpa-dev gitstatus` for LP/LPA working trees; use `git status` at `$HOME` for studio config.
