# Lightning Pose App global code review

Persistent architecture, product-quality, and development-process review of
[`lightning-pose-app/`](lightning-pose-app/). The primary user is a neuroscientist who
wants to move safely from behavioral videos to labels, trained models, predictions,
and visual review without needing to understand Lightning Pose's internal file formats.

This is the current review tracker. The older
[`lpa-web-ui-code-review.md`](lpa-web-ui-code-review.md) remains useful as a detailed
September 2026 Angular/test audit, but it predates substantial File Manager, project
cache, validation, project-deletion, labeler, and video work.

GitHub tracking: [umbrella issue #146](https://github.com/paninski-lab/lightning-pose-app/issues/146)
and the [LP App Roadmap](https://github.com/orgs/paninski-lab/projects/1).

## Review baseline

| Item | Value |
|------|-------|
| Review started | 2026-10-20 |
| Code baseline | `origin/main` at `74e4e3a` (`2.4.2.4.dev0`) |
| Working checkout during review | `jmrfox/dev` at `a78d73e` (kept unchanged) |
| Current source size | about 9,450 backend Python lines and 29,412 frontend TS/HTML/CSS lines |
| Automated test inventory | 21 backend test files / 98 test functions; 52 Angular specs / 149 `it()` blocks; 4 Playwright specs; 25 stories |
| GitHub CI at baseline | latest `main` backend and frontend unit-test workflow passed |
| Local checks | Angular lint passed; production app build passed with a bundle warning; Storybook static build passed with size/deprecation warnings |

Before each review session, run `git fetch origin` and record the reviewed SHA. Review
`origin/main` (or an explicit PR), not whichever long-lived development branch happens
to be checked out.

## Principles

1. Protect labels, project metadata, models, and original videos before optimizing code.
2. Review complete scientist workflows, not only individual components and functions.
3. Treat actionable error messages, progress, cancellation, and recovery as product features.
4. Prefer a small number of tests around real data-loss and scientific-validity risks.
5. Extend the existing stack before adding a parallel framework or state system.
6. Promote a finding to a GitHub issue only after confirming scope, user impact, and an acceptance test.

## Status and priority

- Status: `not started`, `in progress`, `reviewed`, `deferred`, `resolved`.
- Priority: `P0` active data-loss/catastrophic bug; `P1` high user or maintainer value;
  `P2` worthwhile improvement; `P3` cleanup or watch item.

## Review chunks

Each chunk should end with: findings, tests inspected, commands run, roadmap overlap,
and the smallest sensible issue/PR boundaries.

| Chunk | Scope | Status | Output / notes |
|-------|-------|--------|----------------|
| 0 | Baseline, architecture map, reconcile old review | reviewed | Initial findings below; old UI review is historical, not current. |
| 1 | Filesystem data safety and migrations | in progress | Start with label CSV transactions and `projects.toml`; then project/model/file operations. |
| 2 | FastAPI routes, validation, errors, and Angular contracts | not started | Inventory 53 operations; decide typed-client approach after response models are complete. |
| 3 | Background work: training, inference, video jobs, locks, cancel/restart | not started | Inspect process lifecycle, state persistence, cleanup, and UI recovery. |
| 4 | Video ingest, naming, ffprobe, transcoding, multiview sessions | not started | Include open issues #68 and #87 and realistic video fixtures. |
| 5 | Label extraction, labeler, CSV/JSONL integrity, calibration | not started | Include multiview all-or-nothing behavior and keypoint/schema changes. |
| 6 | Model configuration, training, EKS, inference, scientific guardrails | not started | Include issue #54 and LP/LPA version compatibility. |
| 7 | Angular architecture, state ownership, dialogs, errors | not started | Refresh the September review against current `main`. |
| 8 | Frontend performance and packaging | in progress | Initial bundle findings below; profile lazy-route and Danfo alternatives. |
| 9 | Accessibility and novice-scientist UX | not started | Keyboard, focus, terminology, loading/empty/error states, smaller screens. |
| 10 | Tests, CI, release, and installed-wheel smoke testing | in progress | Unit CI is green; missing workflow/package gates recorded below. |
| 11 | Dependencies, security, observability, support, documentation | not started | Prefer privacy-preserving local diagnostics and low-maintenance automation. |

## Confirmed initial findings

These are review findings, not yet implementation commitments.

| ID | Priority | Finding and evidence | User / maintainer impact | Proposed next action | Status |
|----|----------|----------------------|--------------------------|----------------------|--------|
| CR-001 | P1 | The local LPA checkout was on `jmrfox/dev` at `a78d73e`, while refreshed `origin/main` was `74e4e3a`: 13 commits, 144 changed files, and about 11,788 added lines newer. | Reviews and feature branches can unknowingly start from obsolete architecture. | Add a short review/start-work preflight to `lpa-dev` (`fetch`, show divergence, do not auto-switch). Retire or clearly label long-lived branches. | confirmed |
| CR-002 | P1 | The production Angular configuration disables script optimization, disables CSS minification, and emits source maps. The measured initial build was 12.60 MB raw (12.39 MB JS) and emitted a 20.26 MB JS source map. Enabling normal production optimization in a disposable snapshot reduced the estimate to 7.22 MB raw / 1.61 MB transferred, but remained over budget. Git history shows these values came from the 2025 initial commit, before Danfo and Storybook, with no explanatory commit or issue; the initial generated README simultaneously claimed production builds were optimized. | Slower startup and parsing, especially across Lightning Studio networking; larger wheels; production ships source content unnecessarily. The original rationale may nevertheless have been easier debugging or avoidance of an early minification/runtime bug. | Before changing it, ask the original developer if possible and run optimized packaged builds through Viewer, Labeler, CSV parsing, errors/stack traces, and browser compatibility. If those pass, enable production optimization, decide deliberately whether hidden/private source maps are needed, and add a meaningful bundle budget to CI. | tracked in [#142](https://github.com/paninski-lab/lightning-pose-app/issues/142); rationale unknown |
| CR-003 | P1 | Danfo contributes about 8.28 MB of the unoptimized initial JS bundle. All feature routes use eager `component` imports, so Viewer/Labeler CSV machinery is downloaded on the project list page. | Every user pays the largest dependency cost before selecting a project or workflow. | Lazy-load non-landing routes first. Then benchmark replacing the small DataFrame use surface with typed arrays/maps plus Papa Parse, versus a dynamic Danfo import. Do not rewrite both at once. | tracked in [#142](https://github.com/paninski-lab/lightning-pose-app/issues/142) |
| CR-004 | P2 | `web_ui/angular.json` copies the entire `public/` directory to both `/` and `/static`, duplicating about 2.42 MB of images/fonts/favicon in the compiled package. | Larger wheel and Storybook output with no user value. | Determine which URL convention is canonical, remove the duplicate asset rule, and add an installed-wheel asset smoke test. | tracked in [#142](https://github.com/paninski-lab/lightning-pose-app/issues/142) |
| CR-005 | P1 | `save_mvframe` accepts each `csvPath` from the browser and reads/writes it without first proving it is an expected label file inside the selected project's data directory. `project_data_dir` is available but is used only for cache invalidation. | A stale or malformed client payload can modify an unintended CSV that the server account can access. This is a data-integrity boundary even for a local app. | Resolve and validate every target against project paths and the selected label-file inventory before reading. Add rejection tests for outside paths, symlinks, non-label CSVs, and project mismatch. | tracked in [#143](https://github.com/paninski-lab/lightning-pose-app/issues/143) |
| CR-006 | P1 | Multiview label saves stage all CSVs but commit them using sequential `os.replace()` calls, then update JSONL queues separately. A failure partway through can leave views or queues out of sync. | Partial multiview labels are scientifically misleading and difficult to diagnose later. | Design a small transaction/rollback helper with backups or a journal; inject failures after each commit in tests. Clarify what can and cannot be atomic across files. | tracked in [#144](https://github.com/paninski-lab/lightning-pose-app/issues/144) |
| CR-007 | P1 | `ProjectUtil.update_project_paths()` performs read-modify-write on `projects.toml` with a direct `wb` write and no shared lock. | A crash can truncate the registry; overlapping create/update/delete requests can lose entries. | Add a registry lock plus temp-file write, flush/fsync as appropriate, parse validation, and `os.replace()`. Add interruption and concurrent-update tests. | tracked in [#141](https://github.com/paninski-lab/lightning-pose-app/issues/141) |
| CR-008 | P1 | Four Playwright specs exist and already record screenshots/video/traces, but no GitHub workflow runs them. The publish workflow builds a wheel and lists its contents but never installs it into a clean environment or opens the packaged app. | Unit tests can pass while a complete new-project workflow or released static package is broken. | Add one deterministic CPU-only golden path in CI: start backend+UI, create project, navigate pages, delete it. Separately build/install the wheel and smoke `/`, `/app/v0/rpc/GetGlobalContext`, and one bundled asset before PyPI publication. | tracked in [#145](https://github.com/paninski-lab/lightning-pose-app/issues/145) |
| CR-009 | P2 | Storybook and `@storybook/addon-a11y` are installed and the static build passes, but stories/a11y do not run in CI and global `a11y.test` is not set. | Reusable widgets can regress visually or become keyboard/screen-reader inaccessible without a failing check. | Start Storybook accessibility checks as `todo`, fix the baseline, then set new/clean stories to `error`; keep behavioral logic in Angular specs. | confirmed |
| CR-010 | P2 | FastAPI exposes an OpenAPI schema and most endpoints use Pydantic models, but Angular's single boundary is `call(method: string, params?: any): Promise<unknown>` and callers cast responses manually. | Endpoint renames and request/response drift are discovered at runtime, often in a user's workflow. | Finish explicit request/response models, export OpenAPI in CI, and prototype a generated or checked-in TypeScript contract. Keep `RpcService` as transport, but make method names and payloads typed. | confirmed |
| CR-011 | P2 | Dependabot currently watches GitHub Actions only, despite `package-lock.json` and Python dependencies in `pyproject.toml`. Angular core is v21 while CDK/Material are v20 and `angular-eslint` is v19. | Dependency drift accumulates until upgrades become large and risky; compatibility is implicit. | Extend the existing Dependabot config to npm (`/web_ui`) and pip (`/app_server`), grouped and rate-limited. Align Angular ecosystem majors in a dedicated PR after CI coverage improves. | confirmed |
| CR-012 | P2 | Package metadata says Python `>=3.10`; user docs say 3.10–3.12; CI tests only 3.12. | A published install can resolve on a version the project does not regularly validate, and upper support is not encoded. | Decide the actual supported range, encode it consistently, and test a small Python matrix or narrow `requires-python`. | confirmed |
| CR-013 | P3 | Angular lint passes but warns that `eslint.config.js` is reparsed as ESM because `package.json` has no `"type": "module"`. The Storybook build passes but emits Node/Storybook deprecation and oversized-asset warnings. | Repeated noise hides meaningful warnings and adds small local friction. | Clean these only after the P1 build/CI work; do not make a standalone architecture project out of them. | confirmed |
| CR-014 | P3 | Open issue #95 describes blank JSONL lines breaking saves. Current `main` filters blank lines and has `test_save_mvframe_skips_blank_unlabeled_sidecar_lines`. | The roadmap overstates remaining work and can send maintainers toward an already-fixed bug. | Reproduce once on a packaged current build, link the regression test/commit, and close the issue if confirmed. | triage |

## Product opportunities to validate with users

These should become features only after short conversations or observed support cases.

| Opportunity | Why it may help a neuroscience lab | First experiment |
|-------------|-------------------------------------|------------------|
| Environment preflight / support report | Installation failures often present later as cryptic ffmpeg, CUDA, path, version, or permissions errors. | Add a read-only diagnostics view: LPA/LP/EKS versions, ffmpeg/ffprobe, OS/WSL, GPU/CUDA visibility, writable project dirs, free disk, and browser-vs-server file location. Provide a copyable redacted report. |
| Persistent task center | Training, inference, upload, and transcoding have different status mechanisms; browser/server restarts can make work look lost. | Map all task states and recovery behavior, then show one durable history with logs, cancel/retry, and a clear distinction between queued/running/failed/completed. |
| Project backup/export and restore check | The filesystem is the database; labs need confidence before upgrades, renames, or moving machines. | Define a manifest and dry-run validation first. Do not invent a new on-disk layout without a migration plan. |
| Scientific preflight at workflow boundaries | Invalid PCA choices, label schemas, incomplete multiview sessions, and incompatible project state should fail before long jobs start. | Turn issue #54 into the first rules-based preflight and reuse the same rule in UI, API validation, and tests. |
| Guided first project / demo data | New users need to understand server files versus browser uploads and the Labeler→Models→Viewer sequence. | Instrument or observe one novice session, then build the smallest checklist or demo project that addresses actual confusion. |
| Local recovery for unsaved labeling edits | A browser refresh or failed save can cost careful manual labels. | First determine whether this occurs in practice and how current save/revert works; prototype a per-frame dirty-state warning before implementing autosave. |

## Tooling recommendations

### Adopt or deepen soon

1. **FastAPI/Pydantic/OpenAPI as the contract source.** FastAPI already generates the
   schema; use it to detect drift and, after model coverage is complete, produce a typed
   Angular contract. Do not add a second backend framework.
2. **Playwright in CI.** The repo already contains sensible traces, screenshots, and a
   small create/navigate/delete flow. Make one hermetic workflow reliable before adding
   more end-to-end cases.
3. **Storybook accessibility automation.** Keep DaisyUI + Storybook. Run the existing
   stories and axe-based checks in CI, progressing from warnings to failures rather than
   attempting a visual redesign.
4. **Dependabot for npm and pip.** Extend the existing configuration; do not add Renovate
   unless Dependabot proves insufficient.
5. **Bundle stats and budgets.** Save Angular build stats as a CI artifact and fail only on
   meaningful regression thresholds after CR-002/003 are addressed.
6. **`ruff format --check`.** Ruff is already installed in CI; using its formatter adds
   consistency without another Python formatter.

### Pilot only where the risk fits

- **`pytest-cov`:** collect an informational report to find untested data-changing code;
  avoid a repository-wide percentage gate.
- **Hypothesis:** useful for path containment, filename parsing, label-table invariants,
  and transaction failure sequences. Pilot it on one pure safety boundary.
- **Python type checking:** trial Pyright or mypy on new/clean backend modules before
  imposing it on legacy path code.
- **CodeQL:** evaluate GitHub's Python/JavaScript analysis after path/file boundaries are
  covered by behavior tests. Treat findings as review input, not automatic truth.

### Not recommended now

- A database rewrite, microservices, a second Angular state framework, Angular Material
  expansion, or replacing DaisyUI.
- Sentry or another hosted telemetry service by default. Behavioral-video labs may have
  privacy constraints; improve local logs and a user-controlled redacted support bundle
  first.
- Broad snapshot/visual tests for every screen. Keep visual checks on reusable components
  and behavioral tests on workflows that protect scientific data.

## Immediate sequence

1. Complete chunk 1 around `save_mvframe` and `projects.toml`, then open narrowly scoped
   safety issues with failure-injection acceptance tests.
2. Do CR-002 and CR-004 as a low-risk build/package PR; measure before/after wheel and
   first-load sizes.
3. Do CR-003 separately: lazy-load routes, then decide whether replacing Danfo is worth
   the additional code.
4. Make one Playwright golden path and installed-wheel smoke test reliable in CI.
5. Refresh the frontend architecture/test audit against current `main` rather than
   mechanically applying the September deletion list.
6. Review the open roadmap: reproduce #95 on the current package, then prioritize #54,
   #68, and #87 by observed user frequency and data/scientific impact.

## Session log

### 2026-10-20 — baseline and first-pass architecture review

- Refreshed `origin/main`; kept the user's checked-out branch unchanged.
- Read current maintainer docs, workflows, route structure, roadmap items, and open issues.
- Confirmed latest GitHub `main` unit workflow success.
- Angular lint: passed; one ESM configuration warning.
- Angular production build: passed; initial bundle 12.60 MB raw, with an 8.28 MB Danfo
  contribution and 20.26 MB JavaScript source map.
- Disposable optimized build: 7.22 MB raw / 1.61 MB estimated transfer; still over the
  2 MB raw warning budget. No source edit was made to LPA.
- Follow-up history check: the disabled production optimization and enabled source maps
  date to the 2025 initial commit, before Danfo/Storybook, with no commit, issue, or PR
  explanation. Treat the rationale as unknown and verify optimized packaged workflows
  before proposing a change.
- Storybook static build: passed; reported duplicate/large assets and large chunks.
- Local backend suite in the Codex sandbox reached the first TestClient request and then
  stalled; interrupted after several minutes. The same SHA's GitHub backend workflow is
  green, so this is recorded as an environment discrepancy, not a code failure.
- Created CR-001 through CR-014 and started chunks 1, 8, and 10.
- Created umbrella issue #146 and scoped issues #141–#145, assigned them to `jmrfox`,
  and added all six to the LP App Roadmap with status Todo.

