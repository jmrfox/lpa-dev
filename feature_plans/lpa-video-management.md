# LPA video file management

Let a user import videos that are already on the server, and manage the videos already in a project: list them, flag names, check all-intra encoding, convert, and rename.

## Import session

The live **Choose videos** control is `app-session-import` (Viewer “Upload a new session”, extract frames, and run inference).

- One button. A **Server files** checkbox beside it defaults to off.
- Off: the browser file picker (the user’s machine), then `UploadVideo` and `TranscodeVideo` with `uploads://`.
- On: `app-server-video-picker` browses the server, starting at the project data directory and staying under the home directory. Chosen files skip upload and call `TranscodeVideo` with the absolute path. Output is still `<data_dir>/videos/<stem>.mp4`. The source file is not deleted.

Filename rules are shared with the Videos page via `parseVideoFilename`.

## Project settings Videos

A **Videos** tab on project settings, hidden while creating a project so the wizard still saves from Multiview.

`app-project-videos` lists files under `videos/` and `videos_test/` (`rglob` pattern `videos*/**/*`, keeping only those two folders).

- Names are checked on load. Single-view: `session.ext`. Multiview: `session_view.ext` (last `_`). A view segment that is not a configured view is flagged. Invalid characters and a missing extension are flagged the same way as import.
- **Check all-intra** uses the existing `ffprobe` RPC. Non-mp4 files are marked as needing conversion.
- **Process selected** and **Process all** convert files that are not all-intra. **Process all** checks first when status is unknown. Conversion reuses the upload ffmpeg options (`-g 1`) through `GET /app/v0/sse/TranscodeVideoInPlace`: the file must already be under that project’s `videos/` or `videos_test/`, a temp sibling is written, then the original is replaced in the same folder. Status is keyed by the full path.
- **Rename** uses `POST /app/v0/rpc/RenameVideo`. The new name stays in the same folder, must pass `parse_session_view`, and conflicts return 409. Prediction and label files are not renamed.

## Tests

- `app_server/tests/routes/test_videos.py`
  - `test_transcode_in_place_replaces_videos_test_file`: in-place transcode replaces a `videos_test` file and does not copy it into `videos/`.
  - `test_rename_video_accepts_valid_name_rejects_bad_name_and_collision`: rename accepts a valid name, rejects a bad name, and returns 409 when the target exists.
- `web_ui/src/app/session-import/session-import.component.spec.ts`: the server-files checkbox defaults off, and when it is on, Choose videos does not open the local file input.
- `web_ui/src/app/project-settings/project-videos/project-videos.component.spec.ts`: a multiview name without `_` is flagged, and `session_view.mp4` is accepted when that view is configured.
