---
name: Sidecar save blank line
overview: Saving a labeled frame fails because the unlabeled sidecar is a lone newline and the save path parses every line as JSON. Skip blank lines the same way the add path already does, and show the real HTTP error instead of `[object Object]`.
todos:
  - id: skip-blank-lines
    content: Skip blank lines when removing a frame from the unlabeled sidecar
    status: completed
  - id: save-error-text
    content: Throw the HTTP error message from the Labeler save catch
    status: completed
  - id: test-and-log
    content: Add the sidecar pytest and note the fix in BUGS.md and the changelog
    status: completed
isProject: false
---

# Fix labeled-frame save on a blank sidecar

Saving a moved keypoint posts `save_mvframe`. The CSV write finishes, then [`remove_from_unlabeled_sidecar_files`](lightning-pose-app/app_server/src/litpose_app/routes/labeler/save_mvframe.py) reads each view’s `*.unlabeled.jsonl`. For this project that file is [`LPProjects/mirror-mouse-fused/CollectedData.unlabeled.jsonl`](LPProjects/mirror-mouse-fused/CollectedData.unlabeled.jsonl): one byte, `0x0a`. `splitlines()` yields `""`, and `json.loads("")` raises `JSONDecodeError: Expecting value: line 1 column 1 (char 0)`, which becomes the 500.

The add path in [`mv_label_file.py`](lightning-pose-app/app_server/src/litpose_app/utils/mv_label_file.py) already skips those lines (`if line.strip()`). An empty queue is written as `"\n".join([]) + "\n"`, which is exactly this file. The remove path does not skip them:

```200:205:lightning-pose-app/app_server/src/litpose_app/routes/labeler/save_mvframe.py
        lines = [
            json.loads(line) for line in unlabeled_sidecar_file.read_text().splitlines()
        ]
        filtered_lines = [
            line for line in lines if line.get("frame_path") != vr.indexToChange
        ]
```

The console line comes from the Labeler save catch, the only caller of `saveMVFrame`. `HttpClient` rejects with an `HttpErrorResponse`, and `throw new Error(error)` stringifies that object:

```376:378:lightning-pose-app/web_ui/src/app/labeler/labeler-center-panel/labeler-center-panel.component.ts
      .catch((error) => {
        this.isSaving.set(false);
        throw new Error(error);
      });
```

## Changes

- In `remove_task`, parse only non-blank lines, matching `add_task`. A newline-only sidecar then has nothing to remove, so the save returns successfully and the CSV change stays. A sidecar that mixes a blank line with a real `frame_path` still drops that frame.
- In the Labeler save `.catch`, throw `new Error` with a string (`error.message`, or `String(error)`), so a later failure is not printed as `[object Object]`.
- One pytest, `test_save_mvframe_skips_blank_unlabeled_sidecar_lines`, calling `remove_from_unlabeled_sidecar_files`: a newline-only sidecar does not raise, and a blank line plus a matching `frame_path` removes that entry.
- Note the bug in [`BUGS.md`](BUGS.md) and add a short bullet under `### [2.4.2.3.dev0]` in [`CHANGELOG.md`](lightning-pose-app/CHANGELOG.md).

The existing newline file does not need a manual rewrite. After this, saving the same frame again completes.