---
name: Session video ignores
overview: Stop writing ignored video folders into projects.toml. Remember them in the running server until it stops, and keep the File Manager, Viewer, inference, and project stats reading that same list.
todos:
  - id: session-store
    content: Remember ignored video folders in process memory and stop writing them to projects.toml.
    status: completed
  - id: tests-docs
    content: Update getProjectInfo expectation, add the toml test, and note that the choice lasts until restart.
    status: completed
isProject: false
---

# Session-only ignored video folders

Unchecked `videos*` folders stay on disk and stay out of the app, but only until the server process stops. A browser reload keeps the choice. Restarting the app checks every folder again.

## Store

Add a process-wide dict in a small module, keyed by project key. [`setIgnoredVideoDirs`](lightning-pose-app/app_server/src/litpose_app/routes/project.py) validates folder names as it does now, then writes that dict. It no longer calls `update_project_paths`.

Remove `ignored_video_dirs` from [`ProjectPaths`](lightning-pose-app/app_server/src/litpose_app/datatypes.py). Remove the block in [`update_project_paths`](lightning-pose-app/app_server/src/litpose_app/project.py) that copies the list back into `projects.toml`. Pydantic ignores a leftover key already in an old file. The next path save drops it.

Keep the field on the `ProjectInfo` response, filled from the dict in `getProjectInfo` (default `[]`). The UI keeps reading `projectInfo.ignored_video_dirs`. Config saves already exclude that field from `project.yaml`.

## Readers

These reload the project from `projects.toml` on each request, so they must read the dict by project key:

- `_fetch_all_stats` in [`project.py`](lightning-pose-app/app_server/src/litpose_app/routes/project.py)
- session video selection in [`inference.py`](lightning-pose-app/app_server/src/litpose_app/routes/inference.py)
- `resolve_project_video` in [`videos.py`](lightning-pose-app/app_server/src/litpose_app/routes/videos.py)

`iter_project_mp4s` and `project_video_root` already take the list as an argument. [`test_ignored_video_dir_is_omitted_from_project_videos`](lightning-pose-app/app_server/tests/routes/test_videos.py) stays as it is.

## Notes and check

In the Videos Help paragraph, say an unchecked folder is left out until the app restarts. Update the `projects.toml` sentence in [feature_plans/lpa-video-management.md](feature_plans/lpa-video-management.md) and the Videos bullet in [CHANGELOG.md](lightning-pose-app/CHANGELOG.md).

Add `"ignored_video_dirs": []` to the expected object in [`test_get_project_info`](lightning-pose-app/app_server/tests/routes/test_project.py). That is the current CI failure. Add `test_set_ignored_video_dirs_is_not_written_to_projects_toml`: after `setIgnoredVideoDirs`, `getProjectInfo` returns that folder, and `projects.toml` does not contain `ignored_video_dirs`.
