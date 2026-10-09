---
name: LPA scripts/build layout
overview: Move the two root build scripts into `scripts/build/`, and rename the two “release” scripts so a wheel build is distinct from publishing a GitHub Release. Do not copy LP’s `buildbot/` folder.
todos:
  - id: move-scripts
    content: git mv build_ui.sh and build_release.sh (as build_wheel.sh) into scripts/build/; rename create_github_release.sh to publish_github_release.sh; fix REPO_ROOT and calls
    status: completed
  - id: update-callers
    content: Update development.md, AGENTS.md if present, and script comments; optionally point publish.yml at build_ui.sh
    status: completed
  - id: open-pr
    content: "Branch scripts-build-reorganize from origin/main, push, open PR; note follow-ups on #113/#114"
    status: completed
isProject: false
---

# Reorganize LPA build scripts

## What LP actually does

[lightning-pose/scripts/](lightning-pose/scripts/) is grouped by **purpose** (`converters/`, `hyper-sweep/`, `inference-timing/`). [lightning-pose/scripts/buildbot/](lightning-pose/scripts/buildbot/) is **not** a generic build directory. It is a small set of SSH/SLURM helpers that a GitHub self-hosted runner uses to run tests on axon (`ssh axon 'sh buildbot/build_srun.sh <PR>'`). LPA already builds and tests on GitHub Actions ([.github/workflows/publish.yml](lightning-pose-app/.github/workflows/publish.yml), tests, lint). Copying `buildbot/` would add cluster-specific machinery we do not need.

The useful LP pattern: keep repo-root tooling under `scripts/<purpose>/`.

## Target layout (move only, no root wrappers)

`build_release.sh` and `create_github_release.sh` both say “release.” Split the names by **artifact vs publish**:

- **build_wheel** — compile the Angular UI and produce `app_server/dist/*.whl` (local package build; does not tag or talk to GitHub)
- **publish_github_release** — tag `vX.Y.Z.W` and create the GitHub Release (that event is what triggers PyPI via [publish.yml](lightning-pose-app/.github/workflows/publish.yml))

```
scripts/
  build/
    build_ui.sh                 # was ./build_ui.sh
    build_wheel.sh              # was ./build_release.sh
  publish_github_release.sh     # was ./scripts/create_github_release.sh
```

Leave [app_server/src/litpose_app/scripts/run_eks.py](lightning-pose-app/app_server/src/litpose_app/scripts/run_eks.py) alone. That is runtime app code, not repo tooling.

A one-file publish script does not need `scripts/release/` yet.

## Script internals

Both scripts already `cd` relative to `$0`. After the move, resolve **repo root** as two levels up, then use paths from there:

- [build_ui.sh](lightning-pose-app/build_ui.sh): `cd "$REPO_ROOT/web_ui"`; output still `app_server/src/litpose_app/ngdist/ng_app` with `--deploy-url="/static/"`.
- [build_release.sh](lightning-pose-app/build_release.sh) → `scripts/build/build_wheel.sh`: `cd "$REPO_ROOT"`, call `scripts/build/build_ui.sh`, then `python -m build` in `app_server`.
- [create_github_release.sh](lightning-pose-app/scripts/create_github_release.sh) → `scripts/publish_github_release.sh`: keep the same guards (`main`, clean tree, version from pyproject). Update its header comment and usage line.

Callers (after the move):

```bash
./scripts/build/build_ui.sh
./scripts/build/build_wheel.sh
./scripts/publish_github_release.sh
```

## Docs and CI in the same PR

Update in-repo mentions on the branch:

- [development.md](lightning-pose-app/development.md) production-release commands (`sh build_ui.sh`, `./build_release.sh`, `./scripts/create_github_release.sh`)
- [AGENTS.md](lightning-pose-app/AGENTS.md) `./build_ui.sh` and `create_github_release.sh` lines (this file is currently only on `jmrfox/agents-md` / PR #114 — if this reorg branches from `origin/main`, those lines are not there yet; see below)

**Optional, recommended in the same PR:** have [publish.yml](lightning-pose-app/.github/workflows/publish.yml) call `./scripts/build/build_ui.sh` instead of duplicating the `ng build` flags. Keep Node setup + `npm ci` in the workflow; only replace the “Build Angular app” step. Wheel build can stay as `python -m build` in `app_server`, or call `build_wheel.sh` after `pip install build`. Prefer calling `build_ui.sh` only (smaller change) unless you want CI to use the full wheel script.

Do **not** add root shims (`./build_ui.sh` → new path).

Studio-only [.cursor/rules/lightning-studio.mdc](.cursor/rules/lightning-studio.mdc) also mentions `./build_ui.sh`; update that locally, not in the LPA PR.

## Git / PR

New branch from `origin/main`: `scripts-build-reorganize`. `git mv` (with the new names), fix internals, update docs that exist on `main`.

Open PRs that will land stale paths/names:

- [#113](https://github.com/paninski-lab/lightning-pose-app/pull/113) adds [development.md](lightning-pose-app/development.md) and [scripts/create_github_release.sh](lightning-pose-app/scripts/create_github_release.sh)
- [#114](https://github.com/paninski-lab/lightning-pose-app/pull/114) adds [AGENTS.md](lightning-pose-app/AGENTS.md) with `./build_ui.sh` and `create_github_release.sh`

After this PR exists, add a small follow-up commit on those branches (or rebase them onto the merged move) so they do not reintroduce root scripts.

## Out of scope

- No axon/buildbot, Makefile, or extra README under `scripts/build/`
- No move of Python package layout (`app_server/` / `web_ui/`)
- No version bump or release
