---
name: Safe model deletion
overview: Bring the project-deletion checks from main onto this branch and use them so deleting a model requires the typed model path and refuses any directory outside that model folder.
todos:
  - id: merge-main
    content: Merge origin/main so project_deletion.py is on this branch, keeping the file-manager changes.
    status: completed
  - id: model-delete-checks
    content: Require a typed model path and fail closed before rmtree in deleteModel.
    status: completed
  - id: delete-ui
    content: Use the typed-path dialog on the Models page and add Delete Selected in File Manager.
    status: completed
  - id: test-docs-browser
    content: Add the delete pytest, update the feature plan, and cancel the dialog in the browser.
    status: completed
isProject: false
---

# Safe model deletion

This branch is one commit behind `origin/main` (`26dd786`), which added [project_deletion.py](lightning-pose-app/app_server/src/litpose_app/project_deletion.py). Merge that commit first so model deletion can call the same path checks. Expect conflicts in [project.py](lightning-pose-app/app_server/src/litpose_app/routes/project.py) and [project-info.service.ts](lightning-pose-app/web_ui/src/app/project-info.service.ts); keep both the file-manager video-dir changes and the typed project-key delete.

## Server

`deleteModel` in [models.py](lightning-pose-app/app_server/src/litpose_app/routes/models.py) currently `assert`s a string prefix and then calls `shutil.rmtree`. Replace that with a helper next to `paths_to_delete` that:

- Resolves the project model directory and the requested relative path.
- Refuses an empty path, an absolute path, `..`, the model directory itself, or any path that is not a directory strictly inside the model directory.
- Uses `reject_forbidden_root` so the target cannot be or contain home, the server working directory, or the app system directory.
- Refuses a folder that contains `project.yaml` or another registered project path.

The request gains `confirmModelPath`. It must equal `modelRelativePath` exactly, or the RPC returns 400 and nothing is removed. A matching confirm deletes only the resolved model folder.

## Dialogs

The Models page dialog in [model-delete-dialog.component.html](lightning-pose-app/web_ui/src/app/models-page/model-delete-dialog/model-delete-dialog.component.html) asks the user to type the model path, the same way project deletion asks for the project name. **Delete Permanently** stays disabled until the typed text matches `modelRelativePath`. The RPC receives that text. A server error is shown in the toast and the dialog stays open.

The File Manager Models panel gets **Delete Selected** beside **Rename Selected**, enabled when a row is selected. It opens that same dialog. Mention **Delete Selected** in bold in the panel description.

## Check

One pytest, `test_delete_model_requires_typed_path_and_stays_inside_model_dir`: a wrong confirmation leaves the folder, a path outside the model directory is refused, and the matching confirmation removes only that model folder.

Update [feature_plans/lpa-video-management.md](feature_plans/lpa-video-management.md). In the browser, on a project that has a model, open Delete Selected, confirm the button stays disabled until the path is typed, then cancel. Do not delete a real model.