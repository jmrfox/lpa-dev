# Bug Fixes

This is a log for tracking bugs.

## Labeler shows the wrong image near the start of a video (fixed)

**Status:** Fixed on `fix/labeler-context-frames` (paninski-lab/lightning-pose-app#161, PR paninski-lab/lightning-pose-app#167).

**Symptoms:** For a frame at video index 0 or 1, the Labeler showed frame 2 under that frame's keypoints, so labels could be placed on the wrong picture. An image whose file name had no digits (for example imported `frame_a.png`) showed no image at all.

**Cause:** The widget built the context list by skipping indices below 0, then always showed slot 2 as the current frame. Slot 2 is only the current frame when both earlier frames exist. A name with no trailing digits gave an empty list.

**Fix:** `labeler/temporal-context.ts:contextImgPaths` builds the five slots the way LP's `get_context_img_paths` does: indices floored at 0, the first run of digits in the file name, every copy of it replaced. A slot whose image fails to load shows the current frame, as LP's dataset does for a missing file. A name with no digits shows just the current image, and the temporal context controls are disabled.

**Tests:** `temporal-context.spec.ts` (frame 0 → `[0, 0, 0, 1, 2]`, frame 1 → `[0, 0, 1, 2, 3]`, no digits, digits in two places, padding); `image-label-widget.component.spec.ts` (frames 0 and 1 show their own image, no-digit name shows the image, failed slot shows the current frame); `labeler-center-panel.component.spec.ts` (controls disabled with a tip for a no-digit name); the last frame of a video shows the current frame in slots +1 and +2.

## Label files other than CollectedData.csv cannot be used (fixed)

**Status:** Fixed on `feature/usable-label-csvs`.

**Symptoms:** A label CSV with any name other than `CollectedData.csv` or `CollectedData_test.csv` (or `CollectedData_<view>.csv` / `CollectedData_<view>_test.csv` on a project with views) was marked Invalid in File Manager and did not appear in the Labeler or Viewer. `CollectedData copy.csv` is one case. Add Label File and Rename refused those names.

**Cause:** Validation treated the CollectedData filename as a hard issue. `findLabelFiles` omits every file that has an issue, so a readable table with another name was hidden from the rest of the app.

**Fix:** Any `.csv` directly in the data directory can be a label file. The file is Invalid, and hidden, only when it cannot be read as a label table. A missing frame, an unusual index path, an incomplete bodypart, or a keypoint mismatch is a warning and the file stays usable. `Config.LABEL_CSV_SCOPE` can include subfolders; the default is the data-directory root.

**Tests:** `test_validate_label_csv_hides_only_unusable_files` (a readable root CSV with a missing image stays in the label picker, a file that is not a label table does not, and a CSV in a subdirectory is not listed).

## Saving a labeled frame fails when the unlabeled list is blank (fixed)

**Status:** Fixed on `feature/ui-tweaks`.

**Symptoms:** In the Labeler, moving a keypoint on a labeled frame and saving shows `Error: [object Object]`. The keypoint file may already have been written.

**Cause:** `CollectedData.unlabeled.jsonl` can be a single newline (an empty labeling queue). Removing the frame from that file parsed every line as JSON, including the blank line, so the save returned 500. The Labeler then threw `new Error` on the HTTP error object, which prints as `[object Object]`.

**Fix:** Blank lines are skipped, the same way frames are added to the queue. A failed save reports the HTTP error message.

**Tests:** `test_save_mvframe_skips_blank_unlabeled_sidecar_lines` (a newline-only sidecar does not fail the save, and a blank line plus a queued frame still removes that frame).

## Folder list in the path picker cannot scroll (fixed)

**Status:** Fixed on `fix/minor-bugfixes-tweaks`.

**Symptoms:** Add Existing Project (and any path field) listed subfolders in a dropdown that grew past the bottom of the screen, so later folders could not be chosen.

**Cause:** The path dropdown had no maximum height, and the popover did not scroll.

**Fix:** The subdirectory list is capped and scrolls.

**Tests:** None. This is layout only.

## Exactly one camera view is accepted as multiview (fixed)

**Status:** Fixed on `fix/minor-bugfixes-tweaks`.

**Symptoms:** A project could be saved with a single camera view name. Multiview behavior then did not match a real multiview project or a single-view project.

**Cause:** Blank views already meant single-view, but one name was written to `view_names` with no check.

**Fix:** Create and update reject exactly one view. The Multiview step shows an error and disables Save while that list has one name, so a project that already has one view must clear it or add a second view before Settings will save. Opening the project is unchanged, and an update that does not send views is still accepted.

**Tests:** `test_create_and_update_reject_exactly_one_camera_view` (create and update reject one name; zero and two are saved). `project-settings.component.spec.ts` (one camera view disables Save and two names allow it).

## Missing ffmpeg fails only when a video is opened (fixed)

**Status:** Fixed on `fix/minor-bugfixes-tweaks`.

**Symptoms:** With ffmpeg absent, an existing project still loaded and videos failed later in the Viewer.

**Cause:** ffmpeg was checked only when a transcode or ffprobe ran.

**Fix:** Startup context reports whether both ffmpeg and ffprobe are on PATH. The top bar keeps a warning when either is missing.

**Tests:** `test_get_global_context_reports_ffmpeg_and_windows`.

## Native Windows fails at video upload with ffmpeg code 8 (fixed)

**Status:** Fixed on `fix/minor-bugfixes-tweaks`.

**Symptoms:** Video upload on native Windows failed with ffmpeg error code 8 because a Windows path was passed through. The app gave no advance warning.

**Cause:** The app started the same way on native Windows and on WSL.

**Fix:** On native Windows (`win32`; WSL stays Linux) the top bar says labeling works and training, inference, and video processing should run in WSL. The app still starts.

**Tests:** `test_get_global_context_reports_ffmpeg_and_windows`.

## Renamed keypoints look saved but are not written (fixed)

**Status:** Fixed on `fix/minor-bugfixes-tweaks`.

**Symptoms:** After keypoint names changed in Project settings, the Labeler showed the new names. Save and next did not say that the CSV still had the old columns, so training later failed on a shape mismatch.

**Cause:** The label save kept only CSV columns whose names were in the save request. A renamed keypoint matched nothing and the file was left unchanged.

**Fix:** The Keypoints tab warns when the list differs from the saved project and says existing label files must be recreated. The settings save is still allowed. A label save that names a keypoint missing from that CSV returns an error and does not write the file.

**Tests:** `test_save_mvframe_rejects_keypoint_missing_from_columns` (a keypoint that is not a CSV column is rejected and the file bytes stay the same).

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
