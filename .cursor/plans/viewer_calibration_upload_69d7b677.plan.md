---
name: Viewer calibration upload
overview: Add an Upload a calibration file button in the Viewer that reuses the existing load dialog, hide calibration actions on single-view projects, and run the existing name and camera-group checks as soon as a file is loaded.
todos:
  - id: viewer-button
    content: Add the disabled-when-single-view Viewer button and open the existing load dialog.
    status: completed
  - id: panel-single-view
    content: Disable File Manager calibration actions on single-view projects and state that at the top of the description.
    status: completed
  - id: validate-on-load
    content: Return CameraGroup issues from the import RPCs and show them in the dialog and the panel list.
    status: completed
  - id: test-docs-browser
    content: Extend the import pytest, update the feature plan, and check both projects in the browser.
    status: completed
isProject: false
---

# Viewer calibration upload

Multiview means more than one project view (`views.length > 1`), the same rule as create-model and extract-frames. `mms1` is multiview. `mmf1` and `mmf-tiny` have no views, so they are single-view.

## Viewer button

In [viewer-page.component.html](lightning-pose-app/web_ui/src/app/viewer/viewer-page/viewer-page.component.html), under **Upload a new session**, add **Upload a calibration file** with the same full-width outline button. It is disabled when the project is single-view. It opens the existing [load-calibration-dialog.component.ts](lightning-pose-app/web_ui/src/app/file-manager/load-calibration-dialog.component.ts), mounted the same way as `app-session-import`.

## Single-view File Manager panel

In [calibration-files-panel.component.ts](lightning-pose-app/web_ui/src/app/file-manager/calibration-files-panel.component.ts), when the project is single-view, the description starts with: "This project is single-view, so camera calibration is not used." **Load Calibration**, **Validate All**, and **Rename Selected** are disabled. Refresh still lists any files already on disk.

## Validate on load

A bad filename still returns 400 and is not written. That character rule is already in `importCalibrationFile` and `importCalibrationUpload`.

After a file is written, both RPCs run the same check as **Validate All** for that one file: `CameraGroup.load`, and camera names must match the project views in order. The file stays on disk. The response includes those issues.

The dialog reports a format problem in an error toast. On the File Manager, a successful load refreshes the list and then runs the existing calibration validation, so the new row shows the result without a separate **Validate All** click. The Viewer has no list, so the toast is the result there.

## Check

Extend `test_import_calibration_creates_folder_and_copies_toml` so the copied non-camera `.toml` is still saved, the response includes a format issue, and the 409 collision still leaves the first file unchanged.

Update [feature_plans/lpa-video-management.md](feature_plans/lpa-video-management.md). In the browser, confirm the Viewer button is disabled on `mmf-tiny` and opens the chooser on `mms1`, and that the File Manager panel shows the single-view sentence with its action buttons disabled on `mmf-tiny`. Do not leave a test file in a real project.