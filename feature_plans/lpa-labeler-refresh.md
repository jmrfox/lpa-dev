# Labeler Refresh button (LPA #165)

Branch: `feat/labeler-refresh` in `lightning-pose-app`.

## What the user sees

- A refresh button (icon only, `aria-label="Refresh label data and images"`) next to the label file picker. It is shown with or without a label file selected, because it also reloads the list of label files.
- It reloads the label file list, then the selected label file's CSVs and unlabeled queue, then the images.
- The open label file and frame stay open. A labeled frame keeps its view; an unlabeled frame opens on its first view, as it does when opened normally.
- If any loaded frame has unsaved keypoint edits (`mvf(frame).hasRevertibleEdits`, the check Revert uses), a dialog asks first: **Cancel** keeps the edits, **Discard and refresh** reloads. Edits live in the loaded frames, not only the open one, so every frame is checked.
- If the open frame or label file is gone after the reload, it is closed and a warning toast says so.
- Nothing is written to disk.

## How

- `LabelerPageComponent.refresh()` (`labeler-page.component.ts`):
  - sets `isRefreshing`; while it is set, `selectedLabelFile` and `selectedFrame` read as none, the same way `isIniting` and `isLoading` already do
  - calls `SessionService.loadLabelFiles()`, then `LabelFileFetcher.loadLabelFileData()`
  - a key Refresh found missing is kept in `goneLabelFileKey` / `goneFrameKey` and reads as none until the URL moves off it, so the page never throws "not found" for it, whatever the router's timing
- Images: `ImageLabelWidgetComponent` has an `imageReload` input (page → center panel → widget). At 0 the URLs are unchanged; after a Refresh it is appended as `?reload=N`, so the browser loads the images again. Images stay cacheable otherwise. The failed-image set resets when it changes, so failed images are retried.
- Label CSVs and `.unlabeled.jsonl` are already served with `Cache-Control: no-cache` (`main.py`, `read_file`), so they reload fresh. No backend change.

## Tests

- `labeler-page.component.spec.ts` "Refresh": reloads label files and labels (a new frame appears), keeps the open frame and bumps `imageReload`; with unsaved edits it asks first, Cancel keeps them, Discard reloads; a removed frame (navigates to the label file, warning) and a removed label file (navigates to none, warning) are closed without an error.
- `image-label-widget.component.spec.ts` "loads the images again, and retries failed ones, after the Labeler is refreshed".
- `labeler-center-panel.component.spec.ts` "keeps the open view when the frame is replaced by a reloaded copy (Refresh)". This guards existing center panel behavior that Refresh relies on; it passes without the Refresh change.
- Full UI suite: 261 passed. Not tried in the browser.
