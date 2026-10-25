# LPA Web UI code review tracker

> **Historical snapshot (2026-09-29).** This detailed Angular/test audit predates more
> than 11,000 lines of work now on `origin/main`, including the File Manager, project
> cache and validation, safer deletion, skeleton overlays, and new label/video behavior.
> Keep it for its review method and test notes, but re-verify every finding before acting.
> The current cross-stack tracker is
> [`lpa-global-code-review.md`](lpa-global-code-review.md).

Rolling, human-in-the-loop review of [lightning-pose-app/web_ui/](lightning-pose-app/web_ui/) (Angular app under `src/app/`). Goal: spot architectural drift, test gaps, easy-to-miss performance problems, and inconsistencies—not to rewrite working features.

Each phase reviews **source and specs together**. The suite should stay **lean**: only tests that guard problems that could actually hurt users, labels, or project data. Expect to **remove, merge, or trim** specs—not only add them. Policy: `.cursor/rules/lpa-web-ui-tests.mdc`.

**Standards to apply in every chunk:** [lightning-pose-app/AGENTS.md](lightning-pose-app/AGENTS.md) (UI + tests), [lightning-pose-app/CLAUDE.md](lightning-pose-app/CLAUDE.md) (patterns), workspace `.cursor/rules/angular-20.mdc`, `lpa-ui-components.mdc`, and `lpa-web-ui-tests.mdc`.

**Path prefix:** Unless noted otherwise, paths below are relative to `lightning-pose-app/web_ui/`.

**How to run one chunk**

1. Read the paths listed for that chunk (skim templates + services, not only `.ts`).
2. List every `*.spec.ts` in the same paths (`find lightning-pose-app/web_ui/src/app/<area> -name '*.spec.ts'`).
3. Scrutinize each `describe` / `it` with the [test review checklist](#test-review-checklist) below; log outcomes in [Test audit log](#test-audit-log).
4. Note code findings in the phase **Notes** column (or a linked issue/PR).
5. Set **Status**, **Specs**, and **Reviewed** when the chunk is done for this pass.
6. Prefer small follow-up PRs in `lightning-pose-app` (code and test deletions welcome in separate commits if easier to review).

**Status values:** `not started` · `in progress` · `done` · `deferred`

---

## Review checklist (per chunk)

Use as a consistent lens; not every item applies to every file.

| Area | Questions |
|------|-----------|
| **Signals & OnPush** | `input()` / `output()` / `computed()` used? Legacy `@Input` / getter reads that skip signal tracking? |
| **Smart vs dumb** | Do `components/` widgets avoid `RpcService` / `ProjectInfoService`? Do feature containers own RPC and pass data down? |
| **Styling** | DaisyUI first; custom CSS only where justified (Viewer transport, canvas overlays)? |
| **Tests (code)** | Specs assert user-visible behavior? Services mocked? Stale parent specs stubbing moved children? |
| **Stories** | Reusable `components/*` have `*.stories.ts`? (Storybook does not replace specs.) |
| **Accessibility** | Controls have labels / `aria-label`? Tooltips use `data-tip`? |
| **State** | Duplicated state between siblings? `localStorage` keys documented? |
| **RxJS** | Subscriptions cleaned up (`takeUntilDestroyed`)? Could this be a signal? |
| **Performance** | Heavy work in templates? Unbounded lists? Re-fetch on every CD cycle? |
| **Indirection** | New helpers that only forward to one call/property? Prefer inline code + a comment if needed (`.cursor/rules/no-useless-wrappers.mdc`). |

---

## Test review checklist

Apply to **each** `it()` in the phase’s spec files.

| Question | If “no” → action |
|----------|------------------|
| Would a failure here indicate a **real bug** users would care about? | **Remove** or narrow the test. |
| Is this rule **owned** by exactly one spec (not duplicated in parent + child)? | **Merge** into the best owner; delete the other. |
| Does it only assert `toBeTruthy()` on the component instance? | **Remove** (“should create” alone). |
| Does it lock in copy/CSS that changes often without guarding logic? | **Trim** to stable selectors (`aria-label`, outputs) or remove. |
| Is the logic pure and non-obvious (validation, math, keyboard map)? | Prefer a **helper spec** (`foo.spec.ts` next to `foo.ts`); drop redundant component tests. |
| Does it hit real RPC/router/resolver? | **Fix** mocks or delete. |

**Verdict labels** (use in audit log): `keep` · `trim` · `remove` · `merge` · `add` (missing high-risk case).

### What usually deserves a spec

- Saving or patching **project.yaml**, label CSVs, or session data (wrong shape, partial write).
- **Viewer** transport: frame/time typing, seek bounds, keyboard shortcuts documented in UI.
- **Labeler** placement/save, multiview label file selection, autolabel boundaries.
- **Validation catalogs** with many rules (e.g. skeleton pairs)—one spec file for the rules, not per-component re-tests.
- **Cross-model / cross-view** invariants (bones, predictions, keypoint visibility).

### What we often drop

- Duplicate coverage of the same rule in Settings + helper + overlay.
- Tests that only mirror the implementation line-for-line.
- Per-dialog “renders title” unless the dialog has branching submit logic worth guarding.

---

## Phases (recommended order)

Order is intentional: **foundation → shared widgets → video → Labeler/Viewer → rest**. Later phases assume familiarity with RPC, project context, and video/keypoint overlays from earlier chunks.

| Phase | Focus | Primary paths | Status | Specs | Reviewed | Notes |
|-------|--------|---------------|--------|-------|----------|-------|
| **0** | Bootstrap, routing, global styles | `src/main.ts`, `index.html`, `styles.css`, `fontfaces.css`, `src/proxy.conf.json`, `src/app/app.config.ts`, `src/app/app.routes.ts`, `src/app/app.component.*`, `global-error-handler.service.ts` | done | done | 2026-09-29 | See findings P0-1–P0-8; no `app.component.spec.ts` (OK). |
| **1** | Core services & domain types | `src/app/rpc.service.ts`, `project-info.service.ts`, `session.service.ts`, `loading.service.ts`, `toast.service.ts`, `local-storage.service.ts`, `viewport-context.service.ts`, `enabled-views-keypoints.service.ts`, `project-info.ts`, `session.model.ts`, `label-file.model.ts`, `prediction-file.ts`, `modelconf.ts`, `keypoint.ts`, `extract-frames-request.ts`, `csv-parser.service.ts` | done | done | 2026-09-29 | P1-1–P1-14; wrapper cleanup backlog W1–W5. |
| **2** | Shared components & utilities | `src/app/components/**`, `utils/**`, `infra/**`, `keypoint-container/**`, `zoomable-content.component.ts`, `types/**` | done | done | 2026-09-29 | P2-1–P2-6; skeleton specs OK; many widgets stories-only. |
| **3** | Video playback stack | `src/app/video-player/**`, `video-widget.ts`, `video-metadata.ts`, `utils/fine-video.service.ts` | done | done | 2026-09-29 | P3-1–P3-3; keep state + keyboard specs. |
| **4** | Labeler | `src/app/labeler/**` | done | done | 2026-09-29 | P4-1–P4-4; keep `labeler-page` spec pattern. |
| **5** | Viewer | `src/app/viewer/**` | done | done | 2026-09-29 | P5-1–P5-3; **no viewer specs**—rely on video-player keyboard/state. |
| **6** | Project shell & settings | `src/app/home-page/**`, `project-home-page/**`, `project-settings/**`, `label-file-picker/**`, `add-existing-project-dialog/**`, `update-project-paths-dialog/**` | done | done | 2026-09-29 | P6-1–P6-4; keep `project-skeleton` spec. |
| **7** | Models & training UI | `src/app/models-page/**`, `models-list/**`, `create-*-dialog/**`, `model-inference-dialog/**`, `run-model-inference-dialog/**`, `bundle-adjust-dialog/**` | done | done | 2026-09-29 | P7-1–P7-4; keep `model-detail` + `create-model` config tests. |
| **8** | Import, terminal, chrome | `src/app/video-import/**`, `session-import/**`, `terminal-output/**`, `loading-bar/**`, `error-dialog/**` | done | done | 2026-09-29 | P8-1–P8-3; store logic untested (add only if bugs appear). |
| **9** | Cross-cutting pass | Suite inventory, dialog notes, mock hygiene | done | done | 2026-09-29 | P9-1–P9-3; **W6** batch delete ~25 create-only specs. |

**Specs column:** same status values as **Status** (`not started` · `in progress` · `done` · `deferred`).

---

## Phase details & file inventory

### Phase 0 — Bootstrap & shell

- Entry and global CSS set DaisyUI theme and Tailwind; changes here affect every page.
- `app.routes.ts` maps product areas: home → project home → viewer / labeler / models.
- Confirm resolvers/guards (if any) and how `ProjectInfoService.fetchContext` ties to navigation.

**Reviewed 2026-09-29**

- `provideZonelessChangeDetection()` + `withComponentInputBinding()` — modern shell; no action.
- `contextResolver` on `''` and `project/:projectKey` always calls `fetchContext` (blocking RPC). Documented failure modes in [activated_route_provider_error.md](lightning-pose-app/web_ui/docs/activated_route_provider_error.md). No route-level error handler if resolver throws—users see global error dialog via `GlobalErrorHandler`.
- Settings are **not** a route; `AppComponent` opens modal from `settingsOpen` / `createProject` query params. Creation navigates to `/project/:key` on `doneCreation`.
- Navbar home uses raw `href="/"` (full reload) vs `routerLink` elsewhere—minor UX inconsistency (P0-3).
- Browser gate uses `userAgentData` Chromium/Edge only; Firefox/Safari get warning (intentional).
- No specs for `AppComponent`, `app.routes`, or `contextResolver` — acceptable; behavior worth guarding lives in Phase 1 (`project-info.service`) + Phase 6 (settings query params) if we add anything.

### Phase 1 — Core services

- **RPC boundary:** `rpc.service.ts` is the only HTTP/RPC client most features should use.
- **Project context:** `project-info.service.ts` + `projectContext()` signal vs legacy `projectInfo` getter—prefer signal reads in `computed()`.
- **Session:** `session.service.ts` and prediction/label file loading patterns used by Viewer and Labeler.

**Reviewed 2026-09-29**

- **`RpcService`:** Intentional thin HTTP boundary (`call` → `firstValueFrom(callObservable)`). Keep; not a useless wrapper.
- **`ProjectInfoService`:** `storeProjectInfo` / `reloadProjectInfo` justify extraction (cache + subjects + views). `getProjectKeyOrThrow` is duplicated in `SessionService` (same logic)—consolidate later (P1-6). Legacy `projectInfo` getter still used heavily in `session.service.ts` (P1-5). `createNewProject` refreshes list but does not reload `projectContext` (P1-7). Parallel `globalLoaded$` / `projectLoaded$` plus `toSignal` duplicates—acceptable migration surface.
- **`SessionService`:** Large RPC surface; also uses raw `HttpClient` for multipart `UploadVideo` (P1-8, OK). `loadSessions` swallows errors silently (P1-9). No spec file—OK if we add one high-value test later (session grouping), not create-only service test.
- **`ToastService`:** `showToast` → `showToast` alias only (W2). `variantToClass` switch is fine (mapping, not passthrough).
- **`LocalStorageService`:** `setHasSeenDiscordTooltip` combines signal + persistence—keep.
- **`ViewportContextService`:** `setScale` / `setTranslate` are one-line passthroughs to `.set()` (W1)—callers in `zoomable-content` can use signals directly.
- **`EnabledViewsKeypointsService`:** `setViewsShown` etc. wrap `BehaviorSubject.next`—thin but hide private subjects; keep unless we make subjects private with public signals only.
- **`mc_util`:** getter `c` only returns `m.config` (W3)—inline `m.config` in class or rename to `config` if kept for readability.
- **Domain types:** `ProjectInfo` constructor normalizes YAML shapes—good. `modelconf.ts` types are LP config mirrors—no action.

**Wrapper / cleanup backlog (fix in LPA PRs)**

| ID | Item |
|----|------|
| W1 | Remove `ViewportContextService.setScale` / `setTranslate`; use `scale.set` / `translateX.set` in `zoomable-content.component.ts`. |
| W2 | Remove `ToastService.showToast`; migrate ~15 call sites to `showAlert`. |
| W3 | Drop `mc_util` getter `c`; use `this.m.config` (or one renamed getter `config`). |
| W4 | Single `getProjectKeyFromContext()` helper or use `projectInfoService.projectContext()!.key` with one shared throw helper on `ProjectInfoService`. |
| W5 | Phase 0+1 create-only specs: `rpc`, `project-info`, `toast`, `csv-parser`, `error-dialog`, `loading` (see audit log). |
| W6 | **Batch remove** create-only component/service specs listed in Phase 9 (keep files that have real `it` blocks). |

### Phase 2 — Shared components (reviewed 2026-09-29)

- **Specs (7 files):** `skeleton-validity`, `skeleton-bones`, `skeleton-overlay`, `skeleton-view-options`, `dense-listbox`, `path-editable`, `terminal-command`. Skeleton split is correct (rules vs geometry vs paint vs view-options)—no duplicate ownership.
- **Stories without specs:** `dropdown`, `path-bar`, `path-display`, `alert-dialog`, `list-box`, etc.—OK per lean policy; Storybook is the visual contract.
- **`dense-listbox`:** Real keyboard/selection tests—**keep**; trim lone `should create` `it`.
- **`path-editable`:** Behavioral tests beyond create—**keep**; trim create `it`.
- **`utils/pair.spec.ts`:** Only `new Pair(1,2)` truthy—**remove file** or **add** `toMapKey` / `fromMapKey` round-trip (Viewer DataFrame keys depend on this)—P2-1.
- **`utils/video-utils.spec.ts`:** Misnamed FineVideoService create-only—**remove** (P2-2).
- **`infra/color.service.spec.ts`:** Create-only—**remove** (P2-3).
- **`keypoint-container` spec:** Z-order rule—**keep** (one DOM assertion, high value).
- **`zoomable-content`:** Pan/zoom logic belongs here; W1 viewport passthroughs apply.

### Phase 3 — Video stack (reviewed 2026-09-29)

- **`video-player-state.spec.ts`:** Frame step, clamp, seek—**keep** (core Viewer/Labeler transport math).
- **`video-player-keyboard.spec.ts`:** Pure `viewerPlaybackActionFromKeyboard`—**keep** (shared with Viewer toolbar).
- **`video-player-controls` spec:** Check for create-only vs interaction—trim if only create.
- **`fine-video.service`:** Create-only spec—**remove** unless we add URL-building test (P3-1).
- **`video-tile` / ffprobe:** No specs—OK; low logic in components.

### Phase 4 — Labeler (reviewed 2026-09-29)

- **`labeler-page.component.spec.ts`:** Good pattern—stub children, test extract-frames dialog inputs—**keep** as template for other pages (P4-1).
- **`labeler-center-panel.component.spec.ts`:** Create-only—**remove** (P4-2).
- **`label-file-fetcher.service.spec.ts`:** Create-only—**remove** or add one fetch/cache test when touching labeler load (P4-3).
- **`extract-frames-dialog.component.spec.ts`:** Create-only—**remove**; dialog flow covered indirectly by `labeler-page` stubs if expanded later.
- **No spec:** `image-label-widget`, `labeler-view-options.service`—OK; behavior is visual + integration-heavy.

### Phase 5 — Viewer (reviewed 2026-09-29)

- **Zero `*.spec.ts` under `viewer/`** (P5-1). Transport/keyboard covered by `video-player-*` specs; Viewer-specific gaps: multiview widget rebuild, prediction tile filtering—**defer** unless regressions appear.
- **`viewer-center-panel`:** Heavy `pureComputeWidgetModels` / prediction cache—candidate for **one** unit test with mocked DataFrame, not component create test (P5-2).
- **Reactivity:** Same `projectContext()` pattern as skeleton fix—viewer computeds already use signal reads post-skeleton PR.

### Phase 6 — Project shell (reviewed 2026-09-29)

- **`home-page.component.spec.ts`:** Create-only + `provideHttpClientTesting` but no `HttpTestingController`—still risks noise; **remove** or mock `ProjectInfoService.fetchProjects` (P6-1, ties P0-8).
- **`project-home-page`, `project-settings`, `label-file-picker`:** Create-only—**remove** (W6).
- **`project-skeleton.component.spec.ts`:** Add/remove/error paths—**keep** (settings + validity integration).
- **`add-existing-project-dialog` / `update-project-paths-dialog`:** Stories exist; no specs—OK.

### Phase 7 — Models (reviewed 2026-09-29)

- **`model-detail.component.spec.ts`:** TensorBoard copy, EKS warning, header paths—**keep**; optional trim create `it` (P7-1).
- **`create-model-dialog.component.spec.ts`:** `imgaug_3d` / multiview config patch tests—**keep** (training config risk).
- **`create-eks-model-dialog`:** Check for beyond-create tests; trim create if sole `it`.
- **`models-page`, `models-list`, rename/delete dialogs, `model-inference-dialog`, `bundle-adjust-dialog`:** Create-only—**remove** files or delete first `it` only (W6).

### Phase 8 — Import & terminal (reviewed 2026-09-29)

- **`video-import.store.ts`:** Multiview session/view grouping in `items` computed—non-trivial; **no spec** today—**add** only if import bugs recur (P8-1).
- **`video-file-table`, `session-import`, `loading-bar`, `error-dialog` component:** Create-only specs—**remove** (W6).
- **`terminal-output`:** No spec—OK (display-only).

### Phase 9 — Cross-cutting (reviewed 2026-09-29)

- **Inventory:** 46 `*.spec.ts` files; ~**28** include a `should create` / `should be created` `it`; ~**half** of those files have **no other** meaningful assertions.
- **Mock hygiene (P9-1):** Component tests that import real `HomePageComponent` + HTTP client without mocking `ProjectInfoService`/`RpcService` cause 404 console noise—fix when trimming home spec or add shared `provideProjectInfoTesting()` helper.
- **Dialogs (P9-2):** See [dialog_inconsistency_problem/](lightning-pose-app/web_ui/docs/dialog_inconsistency_problem/)—out of scope for test deletion PR.
- **Recommended PR order (P9-3):** (1) W6 delete create-only spec files, (2) W1–W4 wrapper cleanup, (3) add `pair` + `csv-parser` + optional `project-info.storeProjectInfo` tests.
- **`highlight.directive.spec.ts`:** Create-only—**remove**.
- **`storybook-recorder`:** Dev-only flag in `app.config.ts`—no test needed.

---

## Recommended PR batches (from full review)

| PR | Scope |
|----|--------|
| **A** | W6: Delete or gut create-only `*.spec.ts` (~25 files); keep behavioral specs listed as **keep** in audit log. |
| **B** | W1–W4: Wrapper removal (viewport, toast alias, `mc_util.c`, project key helper). |
| **C** | P1-5 / P1-9: `SessionService` use `projectContext()`; surface `loadSessions` errors. |
| **D** | Add 2–4 high-value tests only: `Pair` map keys, `csv-parser` fixture, optional `LoadingService` resolver spinner, optional `storeProjectInfo` signal update. |

---

## Test audit log

One row per **spec file** (or per `it` if you need granularity). Link PR when changes land.

| Spec file (under `web_ui/src/app/`) | Phase | Verdict | Rationale (one line) | PR |
|-------------------------------------|-------|---------|----------------------|-----|
| `global-error-handler.service.spec.ts` | 0 | trim | Drop `should be created`; merge into one `handleError` test that asserts `isLoading.set(false)` and `openDialog` (today only umami is asserted). | |
| `global-error-handler.service.spec.ts` | 0 | keep | `should not crash if umami is not defined` guards prod-like env. | |
| `global-error-handler.service.spec.ts` | 0 | remove | `umami.track` payload test is analytics detail, not user workflow—optional remove when trimming. | |
| `loading.service.spec.ts` | 0 | remove | Sole `should be created` test; file adds no value. | |
| `loading.service.spec.ts` | 0 | add | One test: `ResolveStart` → `isContextLoading true`, `ResolveEnd` → false (drives shell spinner)—if we keep any LoadingService spec. | |
| `rpc.service.spec.ts` | 1 | remove | Create-only; no assertion on URL/body. Optional **add**: one `HttpTestingController` test for POST `/app/v0/rpc/foo`. | |
| `project-info.service.spec.ts` | 1 | remove | Create-only; triggers no `fetchContext` behavior. **Add** later: mock RPC, assert `storeProjectInfo` updates `projectContext` signal. | |
| `toast.service.spec.ts` | 1 | remove | Create-only. Optional **add**: dismiss / duplicate-content behavior if we keep ToastService at all. | |
| `csv-parser.service.spec.ts` | 1 | remove | Create-only. **Add**: one fixture CSV for `getBodyParts` or `parsePredictionFile` (real parsing risk). | |
| `error-dialog.service.spec.ts` | 1 | remove | Create-only (Phase 1 adjacent). | |
| `modelconf.spec.ts` | 1 | keep | `mc_util.createdAt` paths are non-obvious EKS vs normal—worth keeping. | |
| `skeleton-validity.spec.ts` | 2 | keep | Canonical skeleton rules (pairs, thickness, multiview)—single owner. | |
| `skeleton-bones.spec.ts` | 2 | keep | Bone geometry / segment math. | |
| `skeleton-overlay.component.spec.ts` | 2 | keep | Paint-layer behavior tied to overlay. | |
| `skeleton-view-options.component.spec.ts` | 2 | keep | View-options + localStorage thickness. | |
| `dense-listbox.component.spec.ts` | 2 | keep | Keyboard + selection behavior. | |
| `dense-listbox.component.spec.ts` | 2 | trim | Drop lone `should create` if present. | |
| `path-editable.component.spec.ts` | 2 | keep | Edit/commit paths beyond create. | |
| `path-editable.component.spec.ts` | 2 | trim | Drop create-only `it` if redundant. | |
| `terminal-command.component.spec.ts` | 2 | keep | Copy UI + `isCopied` rendering. | |
| `terminal-command.component.spec.ts` | 2 | trim | Drop `should create`. | |
| `keypoint-container.component.spec.ts` | 2 | keep | Skeleton SVG z-order before keypoints. | |
| `pair.spec.ts` | 2 | remove | Constructor truthy only—no `toMapKey` coverage. | |
| `pair.spec.ts` | 2 | add | Round-trip `toMapKey` / parse (Viewer column keys). | PR D |
| `video-utils.spec.ts` | 2 | remove | Misnamed FineVideoService create-only. | |
| `infra/color.service.spec.ts` | 2 | remove | Create-only. | |
| `utils/daisy-form-control.directive.spec.ts` | 2 | remove | Create-only directive instance. | |
| `highlight.directive.spec.ts` | 2 | remove | Create-only. | |
| `video-player-state.spec.ts` | 3 | keep | Frame/time clamp and seek math. | |
| `video-player-keyboard.spec.ts` | 3 | keep | Pure keyboard → playback action map. | |
| `video-player-controls.component.spec.ts` | 3 | keep | Transport bar, slider max, keyboard, extract frame—high value. | |
| `video-player-controls.component.spec.ts` | 3 | trim | `creates the transport bar` is weak if only truthy—optional merge into first real test. | |
| `labeler-page.component.spec.ts` | 4 | keep | Stub children; extract-frames dialog wiring template. | |
| `labeler-center-panel.component.spec.ts` | 4 | remove | Create-only. | |
| `label-file-fetcher.service.spec.ts` | 4 | remove | Create-only. | |
| `extract-frames-dialog.component.spec.ts` | 4 | remove | Create-only. | |
| _(no files)_ | 5 | add | Optional: unit test `pureComputeWidgetModels` with mocked predictions—only if Viewer regressions. | |
| `home-page.component.spec.ts` | 6 | remove | Create-only + real HTTP risk (P0-8). | |
| `project-home-page.component.spec.ts` | 6 | remove | Create-only. | |
| `project-settings.component.spec.ts` | 6 | remove | Create-only; skeleton covered by `project-skeleton`. | |
| `project-skeleton.component.spec.ts` | 6 | keep | Add/remove bones + error paths in settings. | |
| `label-file-picker.component.spec.ts` | 6 | remove | Create-only. | |
| `model-detail.component.spec.ts` | 7 | keep | TensorBoard / EKS / header copy and paths. | |
| `model-detail.component.spec.ts` | 7 | trim | Drop `should create` if other tests cover bootstrap. | |
| `create-model-dialog.component.spec.ts` | 7 | keep | `imgaug_3d` / multiview config patch tests. | |
| `create-eks-model-dialog.component.spec.ts` | 7 | keep | Submit disabled/enabled vs model count. | |
| `create-eks-model-dialog.component.spec.ts` | 7 | trim | Drop `should create`. | |
| `models-page.component.spec.ts` | 7 | remove | Create-only. | |
| `models-list.component.spec.ts` | 7 | remove | Create-only. | |
| `model-rename-dialog.component.spec.ts` | 7 | remove | Create-only. | |
| `model-delete-dialog.component.spec.ts` | 7 | remove | Create-only. | |
| `model-inference-dialog.component.spec.ts` | 7 | remove | Create-only. | |
| `bundle-adjust-dialog.component.spec.ts` | 7 | remove | Create-only. | |
| `video-file-table.component.spec.ts` | 8 | remove | Create-only. | |
| `session-import.component.spec.ts` | 8 | remove | Create-only. | |
| `loading-bar.component.spec.ts` | 8 | remove | Create-only. | |
| `error-dialog.component.spec.ts` | 8 | remove | Create-only (service spec separate in Phase 1). | |

Example verdicts: `remove` shallow create test; `merge` duplicate skeleton rule into `skeleton-validity.spec.ts`; `keep` keyboard seek spec.

**W6 delete batch (create-only files):** ~22 files marked `remove` above (plus Phase 0–1 service specs). After PR A, suite ≈ **24** behavioral spec files.

---

## Findings log (summary — code & architecture)

| ID | Phase | Severity | Summary | Tracking |
|----|-------|----------|---------|----------|
| P0-1 | 0 | low | `loading.service.spec.ts` is create-only; remove file or replace with resolver spinner behavior test. | Test audit |
| P0-2 | 0 | low | `global-error-handler.service.spec.ts` should assert dialog + loading clear, not only Umami; drop create-only `it`. | Test audit |
| P0-3 | 0 | low | Navbar project home control uses `href="/"` (full page load) instead of `routerLink`. | |
| P0-4 | 0 | info | No `app.component.spec.ts` — OK for lean suite; query-param settings flow is the main gap if we add shell tests later (Phase 6). | |
| P0-5 | 0 | info | `navLinks` typed as `unknown[]` for `routerLink`; could be `string[]` routes. | |
| P0-6 | 0 | info | `LoadingService` router subscription not tied to `DestroyRef` (root singleton—acceptable but never torn down). | |
| P0-7 | 0 | info | `src/proxy.conf.json` proxies `/app` → `:8080` for dev; production serves same origin from FastAPI. | |
| P0-8 | 0 | med | Resolver + real routes trigger real HTTP in tests that use `provideRouter(routes)` without mocks—see activated_route doc; fix in Phase 1/9, not new AppComponent tests. | [activated_route_provider_error.md](lightning-pose-app/web_ui/docs/activated_route_provider_error.md) |
| P1-1 | 1 | low | Five Phase-1 service specs are create-only (`rpc`, `project-info`, `toast`, `csv-parser`, `error-dialog`)—remove or replace per audit log. | Test audit |
| P1-2 | 1 | low | `modelconf.spec.ts` is useful—keep. | |
| P1-3 | 1 | info | No `session.service.spec.ts`—OK for lean suite; session grouping is add candidate not boilerplate. | |
| P1-4 | 1 | med | `SessionService` + home/feature tests hit real HTTP when `ProjectInfoService` / `RpcService` not mocked (P0-8). | W5 / Phase 9 |
| P1-5 | 1 | med | `session.service.ts` reads `projectInfoService.projectInfo` in many places—not signal-tracked; same class of bug as pre-skeleton `computed()` fixes. | |
| P1-6 | 1 | low | Duplicate `getProjectKeyOrThrow` in `ProjectInfoService` and `SessionService`. | W4 |
| P1-7 | 1 | low | `createNewProject` does not refresh `projectContext` after create (only `fetchProjects`). | |
| P1-8 | 1 | info | `SessionService.uploadVideo` uses `HttpClient` multipart, not `RpcService.call`—document as intentional. | |
| P1-9 | 1 | med | `loadSessions` empty `catch` hides load failures from UI. | |
| P1-10 | 1 | low | `ToastService.showToast` is alias-only wrapper. | W2 |
| P1-11 | 1 | low | `ViewportContextService.setScale` / `setTranslate` passthroughs. | W1 |
| P1-12 | 1 | low | `mc_util` getter `c` passthrough to `m.config`. | W3 |
| P1-13 | 1 | info | `csv-parser.service.ts` has real parsing logic but no behavioral spec—gap. | Test audit |
| P1-14 | 1 | info | `enabled-views-keypoints` setters: thin but OK as subject encapsulation. | |
| P2-1 | 2 | med | `Pair` map keys used in Viewer DataFrame columns—no spec for `toMapKey` / parsing. | PR D |
| P2-2 | 2 | low | `video-utils.spec.ts` tests wrong service name; delete file. | W6 |
| P2-3 | 2 | low | `color.service.spec.ts` create-only—delete. | W6 |
| P2-4 | 2 | info | Most `components/*` rely on Storybook only—aligned with lean policy. | |
| P2-5 | 2 | info | Skeleton split across validity / bones / overlay / view-options is the right ownership model. | |
| P2-6 | 2 | low | `daisy-form-control` + `highlight` directive specs are create-only—delete. | W6 |
| P3-1 | 3 | low | No `FineVideoService` behavioral spec—OK unless URL/session bugs recur. | |
| P3-2 | 3 | info | `video-player-controls` spec is one of the strongest in the app—keep as reference. | |
| P3-3 | 3 | info | `video-tile` / ffprobe panel untested—acceptable (thin templates). | |
| P4-1 | 4 | info | `labeler-page` spec is the page-test pattern to copy (stub children, assert dialog inputs). | |
| P4-2 | 4 | low | Labeler center panel / fetcher / extract-frames specs are create-only—W6. | W6 |
| P4-3 | 4 | info | `image-label-widget` + view-options service untested—integration-heavy; defer. | |
| P4-4 | 4 | info | Labeler shares video transport specs with Viewer (Phase 3). | |
| P5-1 | 5 | info | No specs under `viewer/`—transport covered by `video-player-*`. | |
| P5-2 | 5 | low | `viewer-center-panel` widget/prediction rebuild logic is add-candidate, not boilerplate component test. | PR D (optional) |
| P5-3 | 5 | info | Viewer view-options + session import mirror Labeler patterns; stories/manual QA for now. | |
| P6-1 | 6 | med | `home-page` spec risks real HTTP without `ProjectInfoService` mock (P0-8). | W6 |
| P6-2 | 6 | low | Project home / settings / label-file-picker create-only specs—W6. | W6 |
| P6-3 | 6 | info | `project-skeleton` spec is the right place for settings skeleton UX tests. | |
| P6-4 | 6 | info | Path dialogs (`add-existing`, `update-paths`) stories-only—OK. | |
| P7-1 | 7 | info | `model-detail` + `create-model-dialog` carry real training/inference UI risk—keep. | |
| P7-2 | 7 | low | Models page/list + rename/delete/inference/bundle-adjust create-only—W6. | W6 |
| P7-3 | 7 | info | `create-eks-model-dialog` has meaningful submit-enable tests—trim create `it` only. | |
| P7-4 | 7 | info | Unified inference plan may consolidate dialogs later—not blocking test cleanup. | [unified-inference-plan](lightning-pose-app/docs/design/unified-inference-plan.md) |
| P8-1 | 8 | med | `video-import.store` multiview grouping in `items` computed has no spec—add on bug recurrence. | |
| P8-2 | 8 | low | Import/session/loading-bar/error-dialog component specs create-only—W6. | W6 |
| P8-3 | 8 | info | `terminal-output` display-only—no spec needed. | |
| P9-1 | 9 | med | ~35 spec files still contain a create `it`; ~22 files are create-only—batch delete PR A. | W6 |
| P9-2 | 9 | info | Dialog open/close inconsistency documented separately—not solved in test pass. | dialog_inconsistency_problem |
| P9-3 | 9 | info | Suggested merge order: W6 → W1–W4 → SessionService fixes → 2–4 additive tests. | Recommended PR batches |

_Add rows as reviews complete. Link PRs or GitHub issues in **Tracking**._

---

## Optional later passes

- **Accessibility audit** (keyboard-only Labeler/Viewer, focus traps in dialogs).
- **Bundle / lazy loading** (`app.routes` code splitting if introduced).
- **E2E** (if Playwright or similar is added)—out of scope for first pass.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-09-29 | Initial tracker and phase breakdown (Studio workspace copy). |
| 2026-09-29 | Paired spec review checklist, test audit log, lean-suite policy; Cursor rule `lpa-web-ui-tests.mdc`. |
| 2026-09-29 | Phase 0 review complete (bootstrap, routes, app shell, global error handler). |
| 2026-09-29 | Phase 1 review complete (core services, domain types, service specs); wrapper backlog W1–W5. |
| 2026-09-29 | Phases 2–9 complete; full test audit log; findings P2–P9; W6 batch + PR batches A–D. |
