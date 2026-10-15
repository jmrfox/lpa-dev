---
name: File manager panel polish
overview: Tighten File Manager copy and button layout, check video names on refresh, and add Rename Selected on every panel plus Add Video and a Process All confirmation.
todos:
  - id: copy-layout
    content: Remove the page blurb, retitle panels, write full-sentence descriptions, and split each button row into global and selected groups.
    status: completed
  - id: videos-actions
    content: Drop video Validate and the Name column, add Check Selected Encoding, Process All confirmation, and Add Video via session import.
    status: completed
  - id: rename-panels
    content: "Add row selection and Rename Selected: label file RPC, labeled-folder RPC that rewrites CSV paths, and the existing model rename dialog."
    status: completed
  - id: tests-docs
    content: Cover CSV path rewrite with one pytest, extend the videos spec for inline name errors, and update the feature plan.
    status: completed
isProject: false
---

# File Manager panel polish

UI work stays in [lightning-pose-app/web_ui/src/app/file-manager](lightning-pose-app/web_ui/src/app/file-manager). Update [feature_plans/lpa-video-management.md](feature_plans/lpa-video-management.md) to match. Do not edit the existing cursor plan file, and do not commit.

## Copy and layout

Remove the paragraph under the File Manager title in [file-manager-page.component.html](lightning-pose-app/web_ui/src/app/file-manager/file-manager-page.component.html).

Titles: **Label Data (CSV)**, **Videos**, **Labeled Image Folders**, **Models**.

Each description is complete sentences and starts with “This panel shows…”. Videos text says names are checked on refresh, and that Process replaces a file with an all-intra copy in the same folder because all-intra encoding is optimal for analysis.

Each button row is two groups in one `flex justify-between` line. Left group is global. Right group needs a selected row.

- Label Data, Labeled Image Folders, Models: left **Refresh**, **Validate All**; right **Rename Selected**.
- Videos: left **Refresh**, **Add Video**, **Check All Encodings**, **Process All**; right **Rename Selected**, **Check Selected Encoding**, **Process Selected**.
- All buttons stay `btn btn-sm btn-primary`. File-specific buttons stay disabled until a row is selected.

## Videos list

In [project-videos.component.html](lightning-pose-app/web_ui/src/app/file-manager/project-videos/project-videos.component.html) and its component:

- Remove the Validate button and `validateFiles()`. Names are already set in `toRow()` during refresh. Drop the **Name** column and show `nameError` / `nameWarning` under the filename.
- Rename **Check all-intra** to **Check All Encodings**. Add **Check Selected Encoding**, which runs the existing single-file `ffprobe` path on the selected row.
- **Process All** opens the existing alert dialog: processing every video may take a long time, with **No** and **Yes**. Yes runs the current `processAll()` loop.
- **Add Video** uses the Viewer pattern: `@if (importOpen()) { <app-session-import (done)="onImportDone()" /> }`. On close, refresh the video list. Imported files land in `videos/` and show up under the existing `videos*` listing.
- **Rename Selected** keeps the current `RenameVideo` dialog.

Extend the existing nested-file spec in [project-videos.component.spec.ts](lightning-pose-app/web_ui/src/app/file-manager/project-videos/project-videos.component.spec.ts) so `clip.mp4` shows the multiview filename error in the table after refresh, with no Validate button.

## Rename on the other panels

[file-check-table.component.ts](lightning-pose-app/web_ui/src/app/file-manager/file-check-table.component.ts) gets a selected path and a row click, with the same highlight the video table uses.

- **Label Data (CSV):** new `POST /app/v0/rpc/renameLabelFile`. The file stays in its current directory, the new name must pass `_label_filename_issue`, and a collision returns 409. CSV contents are not rewritten. Dialog matches the video rename dialog.
- **Labeled Image Folders:** new `POST /app/v0/rpc/renameLabeledDataFolder`. A folder’s new name must pass `_session_stem_issue`. After the folder rename, label CSVs under the data directory (the same files Validate All checks, excluding the model directory) get their index paths updated from `labeled-data/<old>/` to `labeled-data/<new>/`. The rewrite is a text edit of the first field after the three header rows, so numbers and headers stay as stored. A name like `old_extra` is not treated as `old`. If writing a CSV fails, restore the original CSV text and move the folder back. A loose file in `labeled-data/` can be renamed in place, and only CSV rows whose index equals that exact path are updated.
- **Models:** reuse [model-rename-dialog.component.ts](lightning-pose-app/web_ui/src/app/models-page/model-rename-dialog/model-rename-dialog.component.ts) and `renameModel`. That RPC moves the directory to `model_dir/<new name>`, which is the Models page behavior (a nested folder is renamed at the top of the model directory).

Register the new router beside `validate_files.router` in [main.py](lightning-pose-app/app_server/src/litpose_app/main.py).

One pytest, `test_rename_labeled_data_folder_rewrites_csv_paths`: a valid folder rename updates `labeled-data/old/img0001.png` and leaves `labeled-data/old_extra/...` and the three header lines unchanged; a bad new name is rejected and nothing moves.

After the UI changes, check the File Manager in the browser: button groups, inline video name errors, Process All confirmation, and Add Video opening Import Session.