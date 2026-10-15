---
name: Video dirs and calibration
overview: Let a project ignore some videos* folders without deleting them, add a Camera Calibration panel under Models, and bold button names in every File Manager description.
todos:
  - id: bold-names
    content: Bold button names in every File Manager panel description.
    status: completed
  - id: video-dirs
    content: Add the videos* folder checklist, persist ignored folders, and skip them in listing, Viewer, stats, and inference.
    status: completed
  - id: calibration-panel
    content: Add the Camera Calibration panel under Models, with Validate All and session-file rename.
    status: completed
  - id: tests-docs
    content: Add the ignored-folder and calibration pytest, update the feature plan, and check the page in the browser.
    status: completed
isProject: false
---

# Video folders and camera calibration

Work stays on the File Manager in [lightning-pose-app](lightning-pose-app). Update [feature_plans/lpa-video-management.md](feature_plans/lpa-video-management.md). Do not edit the cursor plan file, and do not commit.

## Bold button names

In every panel description, wrap the control names in `<strong>`: **Refresh**, **Validate All**, **Rename Selected**, **Add Video**, **Check All Encodings**, **Check Selected Encoding**, **Process Selected**, and **Process All**.

## Video folders

Between the Videos description and the button row in [project-videos.component.html](lightning-pose-app/web_ui/src/app/file-manager/project-videos/project-videos.component.html), list every direct child of the data directory whose name starts with `videos`. Each row is a checkbox plus the folder name.

Checked means the app uses that folder. Unchecked means the folder stays on disk and the app ignores it. Nothing is deleted. The default is the current rule: every such folder is used, including nested files (`videos*/**/*.mp4`, not only one level down). The editor does not add folders that do not start with `videos`.

Store the unchecked names as `ignored_video_dirs` on that project in `projects.toml`, on [ProjectPaths](lightning-pose-app/app_server/src/litpose_app/datatypes.py). A toggle calls a small RPC and then refreshes project info. [update_project_paths](lightning-pose-app/app_server/src/litpose_app/project.py) must keep this list when it rewrites a project entry.

Ignored folders stay visible in the checkbox list. They drop out of:

- the file table in this panel
- Viewer sessions ([session.service.ts](lightning-pose-app/web_ui/src/app/session.service.ts) filters the `videos*/**/*.mp4` glob)
- `iter_project_mp4s` and `project_video_root` in [project_videos.py](lightning-pose-app/app_server/src/litpose_app/paths/project_videos.py), so stats, inference, rename, and in-place processing skip them

The Viewer tooltip gets one clause that folders unchecked in File Manager are skipped.

One pytest, `test_ignored_video_dir_is_omitted_from_project_videos`: a nested mp4 under an ignored `videos*` folder is absent from `iter_project_mp4s`, and `project_video_root` rejects it; a sibling `videos` folder is still included.

## Camera calibration panel

Add a fifth panel under Models: **Camera Calibration**.

This panel shows the files Lightning Pose discovers for multiview calibration, as described in the [camera calibration docs](https://lightning-pose.readthedocs.io/en/latest/source/directory_structure_reference/camera_calibration_file_format.html#automatic-calibration-discovery): `calibration.toml` at the data directory, then `calibrations/<session>.toml`. The session id is the labeled-data folder name before the last `_`. Files under `calibrations/backups/` are not listed.

Same button row as the other file panels: **Refresh** and **Validate All** on the left, **Rename Selected** on the right. **Validate All** loads each file with `CameraGroup.load`. When the project has views, the camera names must match those views in order, and the number of `[cam_N]` sections must match. **Rename Selected** renames a file inside `calibrations/` so the new stem is the session id. `calibration.toml` stays under that name, so its rename action stays disabled.

Register the check as sector `calibration` on `validateProjectFiles`, and add `POST /app/v0/rpc/renameCalibrationFile` beside the other rename route.

One pytest, `test_validate_calibration_toml_flags_missing_camera_field`: a `calibrations/<session>.toml` that `CameraGroup` cannot load is reported, and a file whose cameras match the project views is not.

After the UI changes, check File Manager in the browser: the folder checkboxes, an ignored folder disappearing from the video table, the calibration panel under Models, and bold button names in the descriptions.