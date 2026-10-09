---
name: Viewer keyboard shortcuts
overview: "Make Viewer shortcuts consistent: Space always play/pause, Shift+arrow always 10 frames after using the slider, and `a` adds the current frame to the labeling queue. Log it in BUGS.md, not feature_plans."
todos:
  - id: keyboard-space-arrows
    content: Space always play/pause; blur seek slider; tabindex/mousedown on transport buttons
    status: completed
  - id: shortcut-add-frame
    content: Add `a` extractFrame shortcut, help tooltip, forward to viewer-page
    status: completed
  - id: tests-and-bugs-log
    content: Update keyboard specs and BUGS.md; fix stale bullets in lpa-viewer-frame-controls.md
    status: completed
isProject: false
---

# Viewer keyboard: Space, arrows, Add shortcut

This is a bugfix on the existing Viewer transport shortcuts (not a new feature plan). Implement on the current branch [`fix/viewer-slider-end-seek`](lightning-pose-app) (slider overshoot fix is already there). Add a second entry to [`BUGS.md`](BUGS.md).

## Intended behavior

- **Space** always play/pause on the Viewer, including after clicking a transport button or **Add**.
- **Arrows / Shift+arrows / Home / End** always the transport actions, including after dragging the time slider. Shift+arrow is ±10 frames.
- **Still leave keys alone** in text fields, open `<dialog>`s, and on the right-pane range sliders (tile size, opacity, etc.).
- **`a`** (no modifiers) adds the current frame, same as clicking **Add**. No-op when Add is disabled (no session/label file, playing, extract in flight). Same partial-views / extra-model dialogs as the button.

## Code

**Space and arrows** in [`video-player-keyboard.ts`](lightning-pose-app/web_ui/src/app/video-player/video-player-keyboard.ts):

- Drop `shouldIgnoreSpace` for buttons / popovers. Space → `togglePlay` unless text field or dialog.
- Keep `isRangeTarget` so *other* range inputs keep native arrows. After a time-slider scrub, **blur** the seek input in `onSliderChange` in [`video-player-controls.component.ts`](lightning-pose-app/web_ui/src/app/video-player/video-player-controls/video-player-controls.component.ts) so the next arrow is not eaten as a 1-frame native step.
- Transport buttons: `tabindex="-1"` and `(mousedown)="$event.preventDefault()"` so a click does not leave them focused (otherwise **Enter** would still re-click them). Do not `preventDefault` on slider mousedown (drag needs it).

**Add shortcut:** extract lives on the page, not the transport bar. Add `{ type: 'extractFrame' }` to the keyboard helper for `a` / `A`. Handle it in the controls `onDocumentKeydown` via an `extractFrame` output; forward from [`viewer-center-panel`](lightning-pose-app/web_ui/src/app/viewer/viewer-center-panel/viewer-center-panel.component.html) to [`handleExtractFramesClick()`](lightning-pose-app/web_ui/src/app/viewer/viewer-page/viewer-page.component.ts). If `isExtractFramesInteractionDisabled()` or no label file, return without calling extract.

Add a row to the keyboard help tooltip in [`video-player-controls.component.html`](lightning-pose-app/web_ui/src/app/video-player/video-player-controls/video-player-controls.component.html): `a` → Add current frame.

Correct the outdated “don’t steal Space from a focused button” / “leave arrows to the time slider” bullets in [`feature_plans/lpa-viewer-frame-controls.md`](feature_plans/lpa-viewer-frame-controls.md) so that spec matches (not a new feature-plan file).

## Tests

Replace the old specs:

- Space on a focused **button** → `togglePlay` (invert current tests in [`video-player-keyboard.spec.ts`](lightning-pose-app/web_ui/src/app/video-player/video-player-keyboard.spec.ts) and [`video-player-controls.component.spec.ts`](lightning-pose-app/web_ui/src/app/video-player/video-player-controls/video-player-controls.component.spec.ts)).
- Arrows / Shift+arrows still map with `shiftKey` even if the event target is a range (time-slider case after we blur; helper can still map them). Keep ignoring arrows on range **or** drop that test if we only rely on blur — prefer: helper still ignores generic range targets; add a spec that `onSliderChange` blurs the seek input.
- `a` → `extractFrame`; ignored in a text input and when a dialog is open.

## BUGS.md

New section (keep the slider overshoot entry). Status: fixed on this branch. Symptoms: Space re-clicks the last transport button; Shift+arrow is 1 frame after using the slider. Cause: shortcuts yielded to focused buttons and `input[type=range]`. Fix: Space always play/pause; blur seek slider on mouseup; `a` adds the current frame.

Do not commit or open a PR unless asked.

## Manual check

Click previous-frame, then Space → play/pause, not another step. Drag the slider, then Shift+arrow → 10 frames. `a` queues the current frame; play/pause still Space. Tile-size slider arrows still change tile size.