---
name: File Manager panel help
overview: Move File Manager descriptions into Help, title the video-directory list, disable single-view calibration, and add Load buttons for label CSVs and a whole model directory.
todos:
  - id: help-accordions
    content: Move each panel description into a collapsed Help accordion, with a bullet per button.
    status: completed
  - id: video-dir-title
    content: Add the Video directories (videos*/) heading above the folder list.
    status: completed
  - id: single-view-calibration
    content: Show the single-view sentence under the calibration title and disable the rest of that panel.
    status: completed
  - id: load-label-and-model
    content: Add Load Label File and Load Model, copying into the data directory or model directory without overwrite.
    status: completed
  - id: browser-check
    content: Check Help and the video heading on mms1, the disabled calibration panel on mmf-tiny, and cancel both load dialogs without writing.
    status: completed
isProject: false
---

# File Manager panel help

Each panel keeps its title, then a collapsed **Help** accordion, then the existing button row and list. Reuse the checkbox accordion in [styles.css](lightning-pose-app/web_ui/src/styles.css) (`app-accordion-toggle`, `app-accordion-title`, `app-accordion-icon`, `app-accordion-content`). It starts closed. The label is **Help**. Give each panel its own checkbox id so five panels on one page do not share a `for`.

Inside Help, keep the current explanation as a few sentences, then a bullet list with one item per button on that panel, in the same order as the button row. Button names stay bold. **Refresh** gets a bullet on every panel: it reloads that panel's list.

- [label-files-panel.component.ts](lightning-pose-app/web_ui/src/app/file-manager/label-files-panel.component.ts): Refresh, Load Label File, Validate All, Rename Selected.
- [project-videos.component.html](lightning-pose-app/web_ui/src/app/file-manager/project-videos/project-videos.component.html): Refresh, Add Video, Check All Encodings, Process All, Rename Selected, Check Selected Encoding, Process Selected.
- [labeled-data-panel.component.ts](lightning-pose-app/web_ui/src/app/file-manager/labeled-data-panel.component.ts): Refresh, Validate All, Rename Selected.
- [model-files-panel.component.ts](lightning-pose-app/web_ui/src/app/file-manager/model-files-panel.component.ts): Refresh, Load Model, Validate All, Rename Selected, Delete Selected.
- [calibration-files-panel.component.ts](lightning-pose-app/web_ui/src/app/file-manager/calibration-files-panel.component.ts): Refresh, Load Calibration, Validate All, Rename Selected.

## Video directories

In the Videos panel, put this heading above the folder checkboxes, including when the list is empty: **Video directories (`videos*/`)**.

## Single-view calibration

On a project with fewer than two views, show this sentence directly under the **Camera Calibration** title, outside Help: "This project is single-view, so camera calibration is not used."

Everything below that sentence is disabled: Help, every button including Refresh, and the file table. The list may still load, but it cannot be used. Multiview projects stay as they are, and the sentence is absent.

Update the File Manager section of [feature_plans/lpa-video-management.md](feature_plans/lpa-video-management.md) to match: descriptions live under Help, the videos directory list has that heading, and a single-view calibration panel is disabled with the sentence under the title.

## Load label files and models

**Load Label File** sits with Refresh on the Label Data panel. **Load Model** sits with Refresh on the Models panel. Each opens a dialog that reuses [file-source-chooser.component.ts](lightning-pose-app/web_ui/src/app/components/file-source-chooser/file-source-chooser.component.ts): Server files starts off. Off uses the browser picker. On uses the in-app browser. The source is copied, not moved.

Label files are `.csv` files, and more than one can be chosen. Each file is written at the data-directory root under its own filename. The name must already pass the CollectedData rule (`CollectedData.csv`, `CollectedData_test.csv`, or `CollectedData_<view>.csv` / `CollectedData_<view>_test.csv`). A bad name returns 400 and is not written. If that filename already exists, the request returns 409 and the existing file is left unchanged. After a file is written, the same header and index check as **Validate All** runs. The file stays on disk, and the dialog reports any problems. The panel then refreshes.

A model is one directory. The local picker selects a folder. The server browser selects a folder under the home directory. The copy lands at `model_dir/<folder name>`, and the folder name must pass the existing model-name rule. The destination must not already exist (409, nothing replaced). The source must not be the destination or sit inside it. After the copy, the same model check as **Validate All** runs. The folder stays on disk, and the dialog reports any problems. The panel then refreshes.

One pytest, `test_import_label_and_model_copy_without_overwrite`, covers a label CSV written at the data-directory root, a 409 when that name exists, a model folder copied under the model directory, and a 409 when that folder name exists.

Update [feature_plans/lpa-video-management.md](feature_plans/lpa-video-management.md) for Help, the video-directory heading, the disabled single-view calibration panel, and these two load buttons.

## Check

In the browser, on `mms1` open Help on Videos and confirm the directory heading and the button bullets. Open **Load Label File** and **Load Model**, then cancel both so nothing is written. On `mmf-tiny`, confirm the single-view sentence sits under the calibration title and the buttons do not respond.
