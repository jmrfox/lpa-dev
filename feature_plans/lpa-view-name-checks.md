# LPA camera view name checks

paninski-lab/lightning-pose-app#176, with #174 on branch `fix/session-view-naming`, PR paninski-lab/lightning-pose-app#182.

## Why

Multiview names are `<session>_<view>`, split at the last `_` (LP's rule for `labeled-data/` folders and calibrations; LPA's everywhere since #174). A view name with `_` can't be read back: `mouse1_cam_top.mp4` is session `mouse1_cam`, view `top`. Karan Sikka's 2025 project spec also says view names must not contain `_`.

## Behavior

| Where | `_` in a view name | Names that differ only in case |
|---|---|---|
| New project (form) | Error under Camera view names; Save/Create disabled | Warning (views and keypoints) |
| New project (`CreateNewProject`) | 400 with the same message | Not checked |
| Existing project (form) | Warning; Save allowed, so a user isn't locked out | Warning |
| `UpdateProjectConfig` | Allowed | Not checked |
| File Manager Videos and Labeled Image Folders | Notice at the top: the message, plus "Files for those views show as Unknown view until the views are renamed in Project settings." | — |

Message (backend `session_view.view_underscore_message`, UI `utils/session-view.ts`): "View names can't contain _ (cam_top), because video and folder names are split at the last _. Use - instead (for example cam-top)."

Case message: "View names Top and top differ only in letter case. They name the same file on macOS and Windows." Keypoints: "Keypoint names Nose and nose differ only in letter case."

The Camera view names help text now describes the last-`_` rule; it used to say a view could be delimited by `_` or `-` anywhere in the name.

## Tests

`project-settings.component.spec.ts` "view and keypoint name checks"; `name-checks.spec.ts`; `file-manager/view-underscore-notice.spec.ts`; `test_project.py::test_create_rejects_underscore_view_and_update_allows_it`.

## Not done

- No migration or rename tool for projects that already have `_` in a view name.
- Case checks aren't enforced on the backend.
