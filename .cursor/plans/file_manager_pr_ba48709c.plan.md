---
name: File Manager PR
overview: Add an explicit project-or-session choice to the calibration dialog, confirm before replacing an existing calibration file, then open the pull request.
todos:
  - id: calibration-choice
    content: Let the calibration dialog write either calibration.toml or a session file, state the project-file rename, and confirm before overwrite.
    status: completed
  - id: open-pr
    content: Update the changelog and feature plan, then open the lpa-file-manager pull request into main.
    status: completed
isProject: false
---

# Calibration choice, then the pull request

The global file is the existing `calibration.toml` in the project data directory (`GLOBAL_CALIBRATION_PATH` in [config.py](lightning-pose-app/app_server/src/litpose_app/config.py)). Session files stay in `calibrations/<session>.toml`. Label and model copies still refuse to replace an existing file.

## Dialog

In [load-calibration-dialog.component.ts](lightning-pose-app/web_ui/src/app/file-manager/load-calibration-dialog.component.ts), above the file chooser, two options:

- **Project file:** one `.toml` is written to `calibration.toml` in the data directory. The chooser allows one file. The source name does not matter. While this option is selected, the dialog states: "The file will be renamed to `calibration.toml`." That sentence stays visible before **Load**, including when the chosen file already has that name.
- **Session file:** the current behavior. One or more `.toml` files are written to `calibrations/<filename>`. The name before `.toml` is the session id. This option starts selected.

The same dialog is used by File Manager **Add Calibration** and Labeler **Load Calibration**.

## Overwrite

If the destination already exists, do not write it yet. Ask: "This will overwrite `calibration.toml`. Are you sure?" or "This will overwrite `calibrations/<name>.toml`. Are you sure?" **Yes** replaces that file. **No** leaves it unchanged. Other chosen session files still proceed. **Yes** and **No** use the existing blue dialog buttons.

The server keeps the current 409 when `overwrite` is absent or false, so a second copy without confirmation still leaves the file unchanged. `overwrite: true` on `importCalibrationFile` and `importCalibrationUpload` replaces that one destination. Write to a temp file in the same folder, then replace, so a failed copy does not erase the old file. A project-file request does not create `calibrations/`.

## Notes and check

Update the Camera Calibration paragraph in [feature_plans/lpa-video-management.md](feature_plans/lpa-video-management.md) and the calibration bullet in [CHANGELOG.md](lightning-pose-app/CHANGELOG.md).

Extend [test_rename_project_files.py](lightning-pose-app/app_server/tests/routes/test_rename_project_files.py). The existing `test_import_calibration_creates_folder_and_copies_toml` still guards a session copy that returns 409 and does not change the first file. Add `test_import_calibration_project_file_and_overwrite`: a project-file copy lands at `calibration.toml`, a second copy without overwrite returns 409, and a copy with overwrite replaces the contents.

Then open the pull request into `main` from `lpa-file-manager`. On `mms1`, choose the project file and cancel the overwrite prompt, then add a session file.
