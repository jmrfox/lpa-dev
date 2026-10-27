# Bug Fixes

This is a log for tracking bugs.

## Extracted frame paths saved with \ on Windows (fixed)

**Status:** Fixed on `fix/frame-paths-posix` (paninski-lab/lightning-pose-app#175; PR paninski-lab/lightning-pose-app#179).

**Symptoms:** On Windows, Extract Frames wrote `labeled-data\sess1_cam1\img00000042.png` into `CollectedData_<view>.unlabeled.jsonl`. Found by reading the code, not a user report; not reproduced on a Windows machine (tests use `PureWindowsPath`). Expected effects: the same frame queued twice (once per separator), a labeled `\` entry left in the queue after saving, and image URLs with `\` on another OS.

**Cause:** `_update_unlabeled_files` used `str(path.relative_to(data_dir))`, which uses the OS separator. The queue's add path and the save's queue removal compared strings exactly.

**Fix:** Write with `.as_posix()`. Read queue paths with `/` everywhere: `queue_frame_path` in `utils/mv_label_file.py` (a validator on `LabelingQueueEntry`, used by the add path), the save's queue removal in `save_mvframe.py`, and the Labeler's loader (`label-file-fetcher.service.ts`). No migration; existing `\` entries are read as `/` and written back with `/` the next time the add path rewrites the file.

**Tests:** `test_extract_frames.py::test_extracted_frame_is_queued_with_forward_slashes`; `test_save_mvframe.py::test_queue_with_backslash_and_slash_entries_counts_the_frame_once`, `test_queue_entry_reads_backslashes_as_slashes`; `label-file-fetcher.service.spec.ts`. The three backend tests fail on the old code.

## Training fails below 250 epochs; schedule doesn't follow Epochs (fixed)

**Status:** Fixed on `fix/model-dialog-schedule-pca` (paninski-lab/lightning-pose-app#172; PR paninski-lab/lightning-pose-app#178).

**Symptoms:** A model created with fewer than 250 epochs stopped at the start of training: `all training.lr_scheduler_params.multisteplr.milestones must be <= training.max_epochs (100)`. Longer or shorter runs kept the 300-epoch schedule (unfreeze at 20, learning-rate drops at 150/200/250).

**Cause:** The dialog's Epochs field wrote only `min_epochs` / `max_epochs`. LP validates milestones against `max_epochs` (`ModelConfig._validate_training`). LP's own `recommender.py` also writes the fixed 20 / [150, 200, 250], so there was no LP rule to copy.

**Fix:** `epoch-schedule.ts` reads the epoch-counted settings from the base config the dialog uses (project `configs/default.yaml`, else LPA's default) and scales them by epochs ÷ its `max_epochs`: `unfreezing_epoch`, `multisteplr` milestones, and, when present, `patch_mask.init_epoch` / `final_epoch` and `callbacks.anneal_weight.freeze_until_epoch` (the last three go beyond the issue; same reasoning: at 50 epochs the default freeze of 60 would keep the unsupervised losses off for the whole run). Whole epochs; unfreezing ≥ 1; milestones increasing, after unfreezing, `<= max_epochs`. Step-based base configs are left alone and Epochs is disabled, because writing `max_epochs` into them fails LP's steps-vs-epochs check. The schedule is shown under Epochs.

**Tests:** `epoch-schedule.spec.ts`; `create-model-dialog.component.spec.ts` "epochs scale the schedule". Also checked with LP's `ModelConfig._validate_training` on `config_default.yaml` (script, not a spec): scaled 5, 50, 100 and 600 epochs pass; unscaled 100 fails with the error above.

## Pose PCA can be chosen without enough labeled frames (fixed)

**Status:** Fixed on `fix/model-dialog-schedule-pca` (paninski-lab/lightning-pose-app#54; PR paninski-lab/lightning-pose-app#178).

**Symptoms:** A semi-supervised single-view model with Pose PCA and few labeled frames failed in training with `cannot fit PCA with N samples < D observation dimensions`.

**Cause:** LP fits Pose PCA on the training split and needs at least 2 × keypoints training frames (`lightning_pose/utils/pca.py`). The dialog didn't check.

**Fix:** New `countLabeledFrames` RPC counts the CSV rows as LP's `parse_label_csv` reads them. `pose-pca.ts` copies LP's `split_sizes_from_probabilities` to get the training count, rather than the issue's `ceil(2K / 0.95)` (which is off by one at some sizes: 17 keypoints need 35 frames, not 36). With too few, the Pose PCA checkbox is unchecked and disabled with a tip naming both numbers; the user's choice comes back when it becomes available. The tip opens to the right; centered below, the dialog edge cut it off. Multiview PCA isn't offered by the dialog, so it isn't checked.

**Tests:** `pose-pca.spec.ts`; `create-model-dialog.component.spec.ts` "Pose PCA needs enough frames"; `test_count_labeled_frames.py`.

## Small keypoint labels show black spiky shapes when zoomed (fixed)

**Status:** Fixed on `fix/keypoint-markers` (PR paninski-lab/lightning-pose-app#170; found in review, no issue).

**Symptoms:** Zoomed in, a 1–4px keypoint name sat on a large black shape with spikes instead of a thin outline.

**Cause:** The outline was `-webkit-text-stroke: 2px` at every label size. On a small label the stroke is as thick as the letters, and Chrome draws text strokes with sharp (mitered) corners that cannot be rounded on page text.

**Fix:** The stroke is `0.25em` (2px at the default 8px), and placement pads by half of it (`labelStrokePad`). The edit-mode crosshair name (SVG text) uses round joins.

**Tests:** `keypoint-container.component.spec.ts` "label outline"; `keypoint-label-placement.spec.ts` `labelStrokePad`. Before/after screenshot at 40× zoom in headless Chromium.

## Keypoint labels can sit nearer a neighbor's marker than their own (fixed)

**Status:** Fixed on `fix/keypoint-markers` (paninski-lab/lightning-pose-app#154, option 1; PR paninski-lab/lightning-pose-app#170). Crowded spots where every corner is worse remain.

**Symptoms:** With two keypoints close together, a name could sit closer to the other keypoint's marker, so the wrong point could be read or corrected.

**Cause:** `placeKeypointLabels` only avoided overlap (with other names and markers) and leaving the frame. A name could be next to another marker without overlapping it.

**Fix:** A corner whose label box is nearer another marker's center than its own marker's center (by more than 0.5px) is not "clear". In the fallback, such a corner costs as much as the label's whole area, so it is used only when every corner is worse. Markers stay one color for now; per-keypoint colors (#154 option 3) would need a palette and a Viewer decision (Viewer colors mean model today).

**Tests:** `keypoint-label-placement.spec.ts` "nearer another marker". Real-data check (script, not a spec): fly-anipose-tiny, 8,820 names, marker size 10 and font 8: names nearer another marker 17.4% → 8.6%.

## Keypoint markers shift, turn capsule-shaped, or have an off-center cross (fixed)

**Status:** Fixed on `fix/keypoint-markers` (paninski-lab/lightning-pose-app#169, PR paninski-lab/lightning-pose-app#170).

**Symptoms:** Zoomed in, a marker moved slightly when Keypoint size changed, some markers were capsules, and the cross was not at the marker's center.

**Cause:** Markers were HTML `div`s (`rounded-full`) positioned with `left`/`top` inside the zoom's CSS `scale()`. The browser snaps an HTML box's edges to whole CSS pixels before the scale, so a fractional position moved by up to half a pixel times the zoom, width and height could snap to different values (capsule), and the cross SVG inside followed the snapped box. The drag offset was also taken from the snapped box (`event.offsetX`).

**Fix:** Markers, the selected ring and the cross are drawn in one SVG layer in image coordinates (`keypoint-container.component.html`). The divs stay as invisible hit targets, tooltip anchors and label anchors. The drag offset is pointer position minus the keypoint's true position (`toLocal`). Pixel convention checked: LP builds heatmaps by scaling coordinates directly (`data/heatmaps.py`), and LPA saves clicks in the same coordinates it draws, so no half-pixel shift was added.

**Tests:** `keypoint-container.component.spec.ts` "markers" (geometry at sizes 5 and 10 for a fractional position, cross center, selected ring, click selects, exact drag, Viewer shadow).

## Multiview label saves can be left half-written (fixed)

**Status:** Fixed on `fix/recoverable-label-saves` (paninski-lab/lightning-pose-app#144, with #141; PR paninski-lab/lightning-pose-app#168).

**Symptoms:** None seen in use. If a save failed partway (disk full, permission error, a file locked by another program), earlier views could already hold the new labels while later views and the labeling queues kept the old state. Separately, a Labeler save and Extract Frames could each overwrite the other's change to `*.unlabeled.jsonl`, and a crash while writing `projects.toml` could empty the project list.

**Cause:** `save_mvframe` committed CSVs with sequential `os.replace()` calls and updated sidecars afterwards, with no rollback. Extract Frames' sidecar update did not share the save's lock. `_write_projects_toml` wrote in place.

**Fix:** `utils/file_transaction.py`: `replace_files` backs up every target, replaces them in order, and restores them from the backups if any replace fails; if a restore fails it raises `CommitRollbackError` naming each file and its kept backup. A save stages and reads back each CSV and sidecar, then commits all of them in one `replace_files`. `label_files_lock` (threading) is held by both the save and `add_to_unlabeled_sidecar_files`. `write_atomic` writes `projects.toml` through a temp file (resolving a symlink first). A process killed mid-commit is not recovered automatically; the `.bak` and `.tmp` files next to the label files hold both versions.

**Tests:** `test_file_transaction.py`; `test_save_mvframe.py` (`test_save_mvframe_failed_replace_restores_every_file` for each CSV and sidecar boundary, `test_save_mvframe_unrestorable_failure_names_files_and_keeps_backups`, `test_save_mvframe_rejected_view_leaves_no_temp_files`, `test_save_mvframe_deletes_the_last_labeled_frame`, `test_extract_frames_queue_update_waits_for_a_save`); `test_project.py` (`test_write_projects_toml_failure_keeps_old_registry`, `test_write_projects_toml_keeps_symlink`).

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
