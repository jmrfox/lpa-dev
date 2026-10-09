---
name: Viewer goto frame time
overview: Add editable frame and time fields on the Viewer transport bar so researchers can type a jump target. Frame values are floored and clamped; time is rounded to the displayed 0.01 s. Rename the current branch to cover this plus the slider and keyboard fixes, and document when related changes share one PR.
todos:
  - id: rename-branch-and-docs
    content: Rename branch to viewer-transport-controls; document one-branch-per-change with a same-area exception
    status: completed
  - id: write-feature-plan
    content: Write feature_plans/lpa-viewer-goto-frame-time.md; point the old plan follow-up at it
    status: completed
  - id: implement-fields
    content: Public seek helper + editable frame/time fields with floor/0.01 rounding and clamp
    status: completed
  - id: add-tests
    content: Unit tests for parse/clamp/escape
    status: completed
isProject: false
---

# Editable Viewer frame and time

New feature (not a bugfix), on the same branch as the slider-overshoot and keyboard-shortcut fixes because they all touch the Viewer transport bar.

## Branch rename

Rename local `fix/viewer-slider-end-seek` to **`viewer-transport-controls`** (`git branch -m`). It has not been pushed. Update the “fixed on …” lines in [`BUGS.md`](BUGS.md) to that name.

## Docs (same branch; they travel with the code)

One short-lived branch per feature or per bugfix bundle, from `origin/main`, then a PR into `main`. Combining is fine when the changes touch the same part of the code (this transport-bar set). Do not mix unrelated areas into one PR.

Say that in:

- [`CONTRIBUTING.md`](lightning-pose-app/CONTRIBUTING.md) Pull requests section (after the `feature/…` or `fix/…` sentence).
- [`AGENTS.md`](lightning-pose-app/AGENTS.md) Git bullet that points at CONTRIBUTING.
- [`.cursor/rules/lpa-git.mdc`](.cursor/rules/lpa-git.mdc) Features and bugfixes list.

Write [`feature_plans/lpa-viewer-goto-frame-time.md`](feature_plans/lpa-viewer-goto-frame-time.md). Mark the old “editable frame / time” out-of-scope / follow-up lines in [`feature_plans/lpa-viewer-frame-controls.md`](feature_plans/lpa-viewer-frame-controls.md) as done / superseded.

## UI

Replace the read-only spans in [`video-player-controls.component.html`](lightning-pose-app/web_ui/src/app/video-player/video-player-controls/video-player-controls.component.html) with compact fields that still look like the current monospace readout:

- Frame: label `f` plus an input showing the integer frame index (select-all on focus).
- Time: editable current time, then read-only ` / {{ duration }} s` (duration stays display-only). Same two-decimal format as today.

Use `type="text"` + `inputmode="numeric"` / `decimal` (no number spinners). Disable both when there is no video. Keep existing tooltips (`Frame`, and add `Time` on the current-time field).

Commit on **Enter** or **blur**. **Escape** reverts and blurs. While the field is focused, do not overwrite the draft from playback. Existing Viewer shortcuts already ignore text inputs ([`isTextEntryTarget`](lightning-pose-app/web_ui/src/app/video-player/video-player-keyboard.ts)).

## Parsing

Shared constant `TIME_DISPLAY_DECIMALS = 2` (matches `toFixed(2)` / 0.01 s). If the display precision ever changes, rounding follows it.

- **Frame:** `Math.floor(Number(raw))`, then clamp to `[0, lastFrame]`. Non-numeric / empty → revert, no seek.
- **Time:** parse as seconds, `Math.round(t * 10^decimals) / 10^decimals`, clamp to `[0, lastFrame / fps]`. Then jump with `seekToFrame(Math.round(time * fps))` so overlay/video use the same seeked-gated path as frame-step. Non-numeric / empty → revert.

Pause if playing (same as other seeks).

## Files

- [`video-player-controls.component.ts`](lightning-pose-app/web_ui/src/app/video-player/video-player-controls/video-player-controls.component.ts) / [`.html`](lightning-pose-app/web_ui/src/app/video-player/video-player-controls/video-player-controls.component.html) / [`.css`](lightning-pose-app/web_ui/src/app/video-player/video-player-controls/video-player-controls.component.css): draft state, parse/commit helpers, stable min-widths so the slider does not jitter.
- Optional one-liner on [`seekToFrame`](lightning-pose-app/web_ui/src/app/video-player/video-player-state.ts) — prefer calling the existing public `stepFrame`/`seekToStart`/`seekToEnd` is not enough; add a small public `seekToFrame` (it is private today) or a `seekToTime` wrapper so the controls do not reach into private seek machinery.

## Tests

In [`video-player-controls.component.spec.ts`](lightning-pose-app/web_ui/src/app/video-player/video-player-controls/video-player-controls.component.spec.ts) (and state spec if `seekToFrame` is made public):

- Frame `128.9` → frame 128; `10000` → last frame; empty → unchanged.
- Time `1.234` → 1.23 s then the corresponding frame; below 0 / above duration → clamped.
- Escape restores the previous readout.

## Manual

On `test_vid_with_fr`: type a burned-in frame index and Enter; picture / `f N` / Add target match. Type a time to two decimals. Invalid input reverts. Shortcuts still work after clicking the video; arrows inside the fields move the caret, not the playhead.

Do not commit or open a PR unless asked. Do not push the renamed branch unless asked.