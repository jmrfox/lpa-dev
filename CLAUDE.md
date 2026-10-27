# lpa-dev — workspace for Lightning Pose App development

Jordan's personal workspace repo (`jmrfox/lpa-dev`). It holds plans, logs, rules, and helper scripts. App source lives in two sibling clones that this repo ignores:

| Name | Path | Repo | Notes |
|------|------|------|-------|
| **LP** | `lightning-pose/` | paninski-lab/lightning-pose | Library developed by others. Read it; do not change it unless asked. |
| **LPA** | `lightning-pose-app/` | paninski-lab/lightning-pose-app | Lab-owned; Jordan is lead RSE. Every change: branch from `origin/main` → PR → merge. |
| **lpa-dev** | `.` | jmrfox/lpa-dev | Work on `main`, no PRs. After a requested change, commit and push only the files it touched. |

"lpa" means **lightning-pose-app**. "Commit and push lpa" is the LPA clone, not this repo. Jordan says "lpa-dev" explicitly to mean this repo.

## Routine

Pick a GitHub issue in LPA (`gh issue list` from `lightning-pose-app/`) → branch → change + tests → version/CHANGELOG/README per `lpa-git` rule → PR → merge. One PR may close several related issues. Log bug fixes in `BUGS.md` and features in `feature_plans/` here.

## Agents

Claude Code is the primary agent. Cursor is used afterwards to review Claude's changes. Both read the same rules:

- Canonical rules: `.cursor/rules/*.mdc`. Each `.claude/rules/*.md` is a symlink to one of them. Edit the `.mdc` file; a new rule needs a matching symlink.
- Scoped rules carry both `globs:` (Cursor) and `paths:` (Claude). Keep them identical.
- `.cursor/plans/` holds past Cursor plan-mode notes. They are history, not instructions.

## Workspace docs

- `DESIGN_PRINCIPLES.md` — how LPA names, places and resolves project files; read before changing file layout or path code
- `feature_plans/` — feature designs (one `.md` each)
- `BUGS.md` — bug log with status and covering test
- `lpa-code-reviews/` — code-review trackers for LPA
- `bin/lpa-dev`, `shell/lpa-dev.zsh` — dev helpers (`lpa-dev setup`, `run`, `test`, `gitstatus`)

## LPA project instructions

`lightning-pose-app/CLAUDE.md` (stack and patterns) loads when you work in that tree. Its workflow rules:

@lightning-pose-app/AGENTS.md
