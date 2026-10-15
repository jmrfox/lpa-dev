---
name: Minor bugfix pass
overview: On `fix/minor-bugfixes-tweaks`, fix the five issues that are local checks or UI warnings. Leave CSV migration and the other open issues for later branches.
todos:
  - id: scroll-folders
    content: "#91: scroll the path-editable folder dropdown"
    status: completed
  - id: one-view
    content: "#85: reject exactly one camera view in settings and create/update"
    status: completed
  - id: env-warnings
    content: "#129 and #69: navbar warnings for missing ffmpeg and native Windows via GetGlobalContext"
    status: completed
  - id: keypoint-mismatch
    content: "#105: warn on keypoint rename and refuse label saves that do not match CSV columns"
    status: completed
  - id: notes
    content: Update BUGS.md and CHANGELOG 2.4.2.3.dev0
    status: completed
isProject: false
---

# Simple bugfix pass

Branch is already `fix/minor-bugfixes-tweaks` from `main` (`34b45c4`). Include these five. Do not convert label CSVs, and do not start the other open issues.

## Include

### [#91](https://github.com/paninski-lab/lightning-pose-app/issues/91) — folder list cannot scroll

Add Existing Project uses [`path-editable.component.ts`](lightning-pose-app/web_ui/src/app/components/path-editable/path-editable.component.ts). The subdirectory dropdown has no max height, and the popover in [`dropdown.component.ts`](lightning-pose-app/web_ui/src/app/components/dropdown/dropdown.component.ts) uses `overflow: visible`, so a long folder list runs off the screen.

Cap that list (`max-h` plus `overflow-y-auto`) so the user can scroll to a folder. Same control is used anywhere a path is edited, which is the right place for the fix.

### [#85](https://github.com/paninski-lab/lightning-pose-app/issues/85) — one camera view is not a multiview project

Blank views already mean single-view ([`project-settings.component.html`](lightning-pose-app/web_ui/src/app/project-settings/project-settings.component.html)). Exactly one name is invalid and is accepted today because [`isMultiviewFormValid()`](lightning-pose-app/web_ui/src/app/project-settings/project-settings.component.ts) only checks an empty validator, and [`CreateNewProject` / `UpdateProjectConfig`](lightning-pose-app/app_server/src/litpose_app/routes/project.py) write `view_names` as given.

- Settings: if the parsed list has length 1, show an error and block Next and Save. Zero or two-or-more stays valid.
- Server: reject create and update when the resulting `view_names` has length 1 (`HTTP 400`). Do not reject loading an existing project that already has one view, so those projects still open.

### [#129](https://github.com/paninski-lab/lightning-pose-app/issues/129) — missing ffmpeg

Viewer open goes through [`ffprobe.py`](lightning-pose-app/app_server/src/litpose_app/routes/ffprobe.py), which already errors if the binary is missing, but only after a video fails. [`check_dependencies()`](lightning-pose-app/app_server/src/litpose_app/tasks/transcode_fine.py) already uses `shutil.which`.

Add `ffmpegAvailable` (ffmpeg and ffprobe both on `PATH`) to [`GetGlobalContext`](lightning-pose-app/app_server/src/litpose_app/routes/config_root.py) and [`GlobalContext`](lightning-pose-app/web_ui/src/app/project-info.service.ts). Show a persistent warning in the navbar slot that already warns about non-Chrome ([`app.component.html`](lightning-pose-app/web_ui/src/app/app.component.html)). A toast would disappear while videos keep failing.

### [#69](https://github.com/paninski-lab/lightning-pose-app/issues/69) — native Windows

Jordan’s note: labeling on native Windows is fine; training and the rest belong in WSL. `sys.platform == "win32"` is native Windows (WSL reports Linux).

Add `nativeWindows` on the same global context and a second navbar warning: labeling works; use WSL for training, inference, and video processing. Do not refuse to start the app.

### [#105](https://github.com/paninski-lab/lightning-pose-app/issues/105) — renamed keypoints save silently

[`_modify_df`](lightning-pose-app/app_server/src/litpose_app/routes/labeler/save_mvframe.py) keeps only CSV columns whose bodypart is in the names being saved. After a rename, that filter is empty and Save and next writes nothing. File Manager already warns on mismatch via [`_keypoint_warning`](lightning-pose-app/app_server/src/litpose_app/routes/validate_files.py); the Labeler does not.

- Keypoints tab: when the name list differs from the saved project, say that existing label CSVs still use the old columns and must be recreated. Still allow the settings save.
- `save_mvframe`: if a changed keypoint name is not a column in that CSV, return an error (the app error dialog already shows RPC failures) and do not write the file.

Out of scope: rewriting or migrating `CollectedData.csv` to new names.

## Tests and notes

- `test_project.py`: create/update with one view name is rejected; zero and two are accepted.
- `project-settings.component.spec.ts`: one view name blocks Next (the current spec only checks that the component creates).
- A small `save_mvframe` test: a keypoint name absent from the CSV columns raises and does not write.
- `GetGlobalContext` test: the two new flags are present. Navbar copy does not need its own spec.
- Log each fix in [`BUGS.md`](BUGS.md) and add a `### [2.4.2.3.dev0]` section in [`CHANGELOG.md`](lightning-pose-app/CHANGELOG.md).

## Leave for later

- [#95](https://github.com/paninski-lab/lightning-pose-app/issues/95) blank `.unlabeled.jsonl` after the queue drains (save path, not a one-line check).
- [#89](https://github.com/paninski-lab/lightning-pose-app/issues/89), [#87](https://github.com/paninski-lab/lightning-pose-app/issues/87), [#71](https://github.com/paninski-lab/lightning-pose-app/issues/71): extract-frames rules and upload behavior.
- [#70](https://github.com/paninski-lab/lightning-pose-app/issues/70): toast position is small, but it is a global toast placement choice, not one of these five.
- [#68](https://github.com/paninski-lab/lightning-pose-app/issues/68) HDR upload, [#54](https://github.com/paninski-lab/lightning-pose-app/issues/54) pose PCA loss, [#128](https://github.com/paninski-lab/lightning-pose-app/issues/128) install docs.
