---
name: Fix project info test
overview: The getProjectInfo response now includes ignored_video_dirs, and the existing equality check in test_get_project_info does not. Update that assertion so CI matches the field the app already returns.
todos:
  - id: update-assertion
    content: "Expect ignored_video_dirs: [] in test_get_project_info and rerun that test."
    status: pending
isProject: false
---

# Fix the getProjectInfo assertion

`getProjectInfo` returns [`ProjectInfo`](lightning-pose-app/app_server/src/litpose_app/routes/project.py), which includes `ignored_video_dirs: list[str] = []`. That list is the File Manager setting for `videos*` folders left on disk but skipped by the app. A new project has none, so the response correctly adds `"ignored_video_dirs": []`.

[`test_get_project_info`](lightning-pose-app/app_server/tests/routes/test_project.py) still expects the old object and fails because the left side has that extra key.

Add `"ignored_video_dirs": []` to the expected dict in that test. Do not drop the field from the response. Then run `pytest app_server/tests/routes/test_project.py::test_get_project_info`.
