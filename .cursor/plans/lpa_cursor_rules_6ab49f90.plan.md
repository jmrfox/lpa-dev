---
name: LPA Cursor rules
overview: Add a concise AGENTS.md and focused Cursor rules in the LPA repo (shared conventions), plus one Studio-only rule for this Lightning Studio SSH environment. Do not open a PR unless you ask.
todos:
  - id: agents-md
    content: Add lightning-pose-app/AGENTS.md and a one-line pointer at the top of CLAUDE.md
    status: completed
  - id: lpa-rules
    content: "Add LPA .cursor/rules: lpa-safety, lpa-git, lpa-backend, lpa-frontend"
    status: completed
  - id: studio-rule
    content: Add workspace .cursor/rules/lightning-studio.mdc (not in LPA git)
    status: completed
isProject: false
---

# Cursor rules and AGENTS.md for LPA

## Split of concerns

**Committed in [lightning-pose-app](lightning-pose-app)** (on `jmrfox/dev`, not pushed to a PR unless you ask):

- [AGENTS.md](lightning-pose-app/AGENTS.md) — what every agent (Cursor, Codex, etc.) should read first: product goal, safety bar, git/release loop, how to run/test. Points at [development.md](lightning-pose-app/development.md) and [CLAUDE.md](lightning-pose-app/CLAUDE.md) instead of copying them.
- `.cursor/rules/*.mdc` — short, one-concern rules (under ~50 lines each).

**Only on this Studio** (not in the LPA git repo): [`.cursor/rules/lightning-studio.mdc`](.cursor/rules/lightning-studio.mdc) at the workspace root. Machine-specific: `cloudspace`, Node 26 PATH, honcho on 4200, test data under `LPProjects/`.

Leave [CLAUDE.md](lightning-pose-app/CLAUDE.md) in place as the stack/patterns cheat sheet. Add one line at the top pointing to `AGENTS.md` so they do not drift.

## AGENTS.md (LPA repo)

Keep it operational, not a second CLAUDE.md:

- LPA is research software for 100+ users: powerful, easy, **robust**. Prefer boring, reversible changes over cleverness.
- Filesystem is the database; never silently rewrite `project.yaml`, label CSVs, or model dirs. New on-disk formats need a numbered migration.
- Git: work on a personal branch (e.g. `jmrfox/dev`); **do not push `main`**; **do not open, merge, or close PRs unless asked**; releases are version bump + README notes via PR, then `./scripts/create_github_release.sh` from `main`.
- Dev: `honcho -f Procfile.dev start` → localhost:4200 (hot reload). `litpose run_app --host 0.0.0.0` is production-shaped (needs `./build_ui.sh`).
- Tests before calling work done: `pytest` in `app_server` (CI ignores `test_predict_wrapper.py`); `npx ng lint` / targeted `ng test` for UI you touch.
- **Propose extra tools; do not install or enable them unless asked.**

## Rules in `lightning-pose-app/.cursor/rules/`

Three always-on or glob rules — not a dump of the whole codebase:

1. **`lpa-safety.mdc`** (`alwaysApply: true`)
   - Do not break existing projects, labels, or trained models.
   - Atomic writes for labels/status (`*.tmp` then `os.replace()`).
   - Single-view fused datasets (e.g. `mirror-mouse-fused`) are **not** two-camera projects: `_top`/`_bot` in keypoint names ≠ `view_names`.
   - If a change could corrupt user data, stop and explain.

2. **`lpa-git.mdc`** (`alwaysApply: true`)
   - Personal branch + PR into `main`; no force-push; no GitHub Release/tag from a personal branch.
   - Commit only when asked; do not open PRs unless asked.
   - After merge, sync the personal branch with `main`.

3. **`lpa-backend.mdc`** (`globs: app_server/**/*.py`)
   - RPC only: `POST /app/v0/rpc/<MethodName>`; add route + Angular `RpcService.call`.
   - ruff as in `app_server/pyproject.toml`; do not “fix” the intentional `is_dir == False` in `rglob.py`.

4. **`lpa-frontend.mdc`** (`globs: web_ui/src/**/*.{ts,html}`)
   - Standalone + OnPush; signals (zoneless); no new Angular Material dialogs (native `<dialog>`).
   - No new REST clients; `RpcService` only.
   - Template `== null` for optional router inputs.

Skip a fourth always-apply “how to run” rule; that lives in AGENTS.md.

## Studio-only rule

[`.cursor/rules/lightning-studio.mdc`](.cursor/rules/lightning-studio.mdc) (`alwaysApply: true` in this workspace):

- One conda env: `cloudspace` (not `poseapp`).
- Node 26 must be on PATH for honcho (`…/.nvm/versions/node/v26.*/bin`); Studio wraps `node`/`npm` onto 22.
- Daily UI: honcho, **localhost:4200**. `run_app` needs `--host 0.0.0.0` and a UI build.
- Smoke-test data: `/teamspace/studios/this_studio/LPProjects/mirror-mouse-fused-tiny` (and the full fused set next to it). Do not commit these.

## What we will not do now

- Open a GitHub PR.
- Change git config.
- Enable extra GitHub/Cursor products.

## Extra tools (suggest only — say if you want any)

These would help a careful RSE loop; none will be added unless you opt in:

- **Branch protection on `main`** (admin): require PR + passing lint/tests.
- **Cursor Bugbot** on PRs (`/review-bugbot` skill) for regressions.
- **Security review** on PRs that touch RPC, file paths, or uploads.
- Set **git `user.name` / `user.email`** in this Studio so commits do not need env hacks.
- Later: Playwright e2e in CI (exists locally, not in GitHub Actions today).
