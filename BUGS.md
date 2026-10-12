# Bug Fixes

This is a log for tracking bugs.

## File Manager Validate All reorders the list (fixed)

**Status:** Fixed in 2.4.2.2.

**Symptoms:** **Validate All** on a File Manager panel rearranged the rows. **Refresh** put them back in the list's usual order.

**Cause:** Refresh builds the rows in the panel's order. Validate All replaced those rows with `validateProjectFiles` results, which follow directory order (case-insensitive on some panels, glob order for label CSVs).

**Fix:** Validation updates the checks but keeps paths that are already on screen in that order. A path only in the validation response is added after those rows.

**Tests:** `file-listing.spec.ts` (validation results follow the on-screen order, and a newly reported path is appended).

## Delete project can erase a parent directory (fixed)

**Status:** Fixed on `fix/safe-project-delete`.

**Symptoms:** On the project list, Delete → Permanently delete files removed the Lightning Studio workspace (down to the home directory) instead of one project directory.

**Cause:** `deleteProject` called `shutil.rmtree` on `data_dir` and `model_dir` from `projects.toml` with no checks. An external `model_dir` does not need `project.yaml`, so a parent path (studio root, home, or another project) was deleted after the project folder.

**Fix:** Permanent delete resolves both paths and refuses `/`-level parents: home, the server working directory, `~/.lightning-pose`, a path that contains the data directory, a path that contains another registered project, and a model directory that contains any `project.yaml`. The same protected-root check runs when creating, registering, or updating paths. The dialog asks for the project key (the tile name) before sending `removeFiles`, and the server requires that same `confirmProjectKey`. Unregister without deleting files is unchanged. A rejected delete leaves the registry and the disk alone and keeps the dialog open.

**Tests:** `app_server/tests/test_project_deletion.py` (protected roots and a model directory that contains another project — the helper raises and does not return those paths). `app_server/tests/routes/test_project_delete.py` (missing or wrong confirm name, missing `project.yaml`, separate model directory, ancestor model directory, model directory containing another project or a nested `project.yaml`). `project-delete-dialog.component.spec.ts` (permanent delete stays disabled until the project key is typed; unregister does not require it; a rejected delete leaves the dialog open).

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
