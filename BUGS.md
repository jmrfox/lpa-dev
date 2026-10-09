# Bug Fixes

This is a log for tracking bugs.

## Viewer time slider overshoots start/end (fixed)

**Status:** Fixed on `viewer-transport-controls`.

**Symptoms:** Dragging the Viewer time slider quickly past either end leaves the native thumb at the start or end, but the video, `f N`, and “Add current frame N” stay on a nearby frame. Moving the pointer slowly toward the same end makes the error smaller.

**Cause:** Slider `input` events were passed through RxJS `throttleTime` with the default `{ leading: true, trailing: false }`. A rapid burst dropped the last values (including `min`/`max`). The native range input still showed the clamped thumb. Paused `onSeek` copied the stale `currentTime` onto `<video>`. After the pointer leaves the track, no further `input` events fire, so the dropped terminal value was never applied. `change` (mouseup) was not handled.

**Fix:** Trailing rAF throttle, immediate commit on `change`, and clamp the slider `max` to last-frame time (`lastFrame / fps`) rather than `duration`.

**Tests:** `video-player-controls.component.spec.ts` (slider max is last-frame time, `change` at min/max, burst of `input` then `change`).

## Viewer Space / Shift+arrow follow last-clicked control (fixed)

**Status:** Fixed on `viewer-transport-controls`.

**Symptoms:** Clicking a transport-bar button (e.g. previous fram ) then pressing Space activated that button again instead of play/pause. After dragging the time slider, Shift+arrow stepped one frame like a plain arrow, not 10 frames. Shift+click on the chevrons still jumped 10 frames.

**Cause:** Viewer shortcuts yielded to the focused control: Space was left to native button activation, and arrows/Home/End were left to a focused `input[type=range]`. The time slider kept focus after a scrub, so native range stepping (one `step` = one frame) ran instead of `stepFrame(±10)`.

**Fix:** Space always toggles play/pause (except text fields and open dialogs). The time slider blurs on mouseup so later arrows hit the shortcut handler. Transport buttons use `tabindex="-1"` and `mousedown` `preventDefault` so they do not stay focused. `a` adds the current frame to the labeling queue (no-op when Add is disabled).

**Tests:** `video-player-controls.component.spec.ts` (Space while a button is focused, Shift+click steps of 10, slider blurs on `change`, `a` emits extract). Shortcut mapping: `video-player-keyboard.spec.ts`.
