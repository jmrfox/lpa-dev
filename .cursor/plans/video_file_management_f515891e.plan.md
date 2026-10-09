---
name: Video file management
overview: Add a server-filesystem option to the existing Import session “Choose videos” button, and add a Project settings Videos page that lists project videos, checks names and all-intra encoding, converts with the existing ffmpeg pipeline, and renames files.
todos:
  - id: branch-and-plan
    content: Create lpa-video-management from origin/main and write feature_plans/lpa-video-management.md
    status: completed
  - id: server-picker
    content: Add Server files checkbox and server-video-picker; extend VideoImportStore to transcode absolute paths without upload
    status: completed
  - id: videos-tab
    content: Add setup-hidden Videos settings tab that lists videos/ and videos_test, flags names, and checks all-intra via ffprobe
    status: completed
  - id: in-place-and-rename
    content: Add in-place all-intra transcode and RenameVideo, with process-selected, process-all, and rename on the Videos page
    status: completed
  - id: tests
    content: Cover in-place transcode, rename, checkbox default, and filename flagging
    status: completed
isProject: false
---

# Video file management

Work happens on a new branch `lpa-video-management` cut from `origin/main` in [lightning-pose-app](lightning-pose-app). Current checkout is `feature/ui-storybook-daisy` (two commits ahead of main, docs only). Do not commit or push unless asked.

Write the design in [feature_plans/lpa-video-management.md](feature_plans/lpa-video-management.md) and name the tests below there.

## 1. Server files checkbox on Import session

The live “Choose videos” control is [session-import.component.html](lightning-pose-app/web_ui/src/app/session-import/session-import.component.html), opened from Viewer “Upload a new session”, extract-frames, and run inference. Leave the unwired copy in `model-inference-dialog` alone.

- Keep one **Choose videos** button. Add a DaisyUI checkbox beside it, default unchecked, labeled **Server files**.
- Unchecked: today’s hidden `<input type="file">` (the user’s machine).
- Checked: the button opens a server browser instead of the browser file dialog.

New `app-server-video-picker` under `web_ui/src/app/components/server-video-picker/`, built from the existing path bar and dense listbox. Do not extend `app-directory-viewer`: it only navigates folders, groups multiview names, and is Storybook-only. Start in the project data directory and keep navigation inside the server home directory. Multi-select video files, then add them to the existing import table (`app-video-file-table`).

Extend [video-import.store.ts](lightning-pose-app/web_ui/src/app/video-import/video-import.store.ts) so each item is either a local `File` or a server path:

- Local files: `UploadVideo` into `~/.lightning-pose/uploads`, then `TranscodeVideo` with `uploads://<filename>` (unchanged).
- Server paths: skip upload and call the existing `GET /app/v0/sse/TranscodeVideo` with the absolute path. That already writes `<data_dir>/videos/<stem>.mp4` and does not delete the source. Filename rules stay the same (`session.ext` or `session_view.ext`).

```mermaid
flowchart LR
  choose[Choose videos]
  choose -->|checkbox off| local[Browser file picker]
  choose -->|checkbox on| server[Server video picker]
  local --> upload[UploadVideo]
  upload --> transcode[TranscodeVideo]
  server --> transcode
  transcode --> videosDir["data_dir/videos"]
```

## 2. Project settings Videos page

Add a **Videos** tab to [project-settings.component.ts](lightning-pose-app/web_ui/src/app/project-settings/project-settings.component.ts) only when `setupMode` is false. Create-project still ends on Multiview, so Save stays on the last wizard tab. The tab is not part of the project form and does not change Save.

New `app-project-videos` next to settings (`project-settings/project-videos/`). It lists video files under `videos/` and `videos_test/` via the existing `rglob` (`videos*/**/*`), which is how the Viewer already finds both training and OOD clips.

Columns: folder, filename, name check, all-intra.

**Names (automatic).** Extract the import filename parser from `VideoImportStore.toItem` into a shared function so the page and import use one rule, matching backend `parse_session_view` in [videos.py](lightning-pose-app/app_server/src/litpose_app/routes/videos.py):

- Single-view: `session.ext`
- Multiview: `session_view.ext` (split on the last `_`). Flag the row when the view segment is not one of the project’s views.
- Invalid characters or a missing extension are flagged the same way as import.

**All-intra (button).** **Check all-intra** calls the existing `ffprobe` RPC (`is_all_intra` from the first 60 frames) for each `.mp4`. Other extensions show as needing conversion. No new check endpoint.

**Convert.** **Process selected** and **Process all** (every listed file that is not all-intra; check first when status is unknown). Reuse `_start_transcode_background` and `FFMPEG_OPTIONS` (`-g 1` all-intra). Do not call today’s `TranscodeVideo` unchanged: it always writes into `videos/`, treats an existing output as already done, and ffmpeg cannot read and write the same path. Add an in-place path that:

- accepts only a file already under that project’s `videos/` or `videos_test/`
- writes a temp sibling, then replaces the original in the same folder
- streams the same SSE `VideoTaskStatus` progress
- keys status by full path so `videos/foo.mp4` and `videos_test/foo.mp4` do not share one status

Import from the server still lands new files in `videos/` only. In-place conversion is what keeps an OOD clip in `videos_test/`.

**Rename.** Select a row, **Rename**, confirm in the existing alert dialog. New RPC `RenameVideo`: same folder only, validate with `parse_session_view`, 409 if the target exists. Video file only; prediction and label files that still use the old name are out of scope.

## Tests

- `app_server/tests/routes/test_videos.py`: in-place transcode replaces a `videos_test` file and does not copy it into `videos/`; rename accepts a valid name, rejects a bad name, and returns 409 on collision.
- `session-import.component.spec.ts`: the server-files checkbox defaults off, and when it is on, Choose videos does not open the local file input.
- `project-videos.component.spec.ts`: a multiview name without `_` is flagged, and `session_view.mp4` is accepted when that view is configured.
