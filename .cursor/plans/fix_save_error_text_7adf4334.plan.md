---
name: Fix save error text
overview: "The bugfix branch is correct aside from one display bug: a Labeler save failure still hides the server’s explanation, including the new “keypoint is not a column” error."
todos:
  - id: rethrow-save-error
    content: Rethrow the original Labeler save error so the dialog shows the server detail.
    status: completed
isProject: false
---

# Fix save error text

## Review

`fix/minor-bugfixes-tweaks` vs `main` is the 2.4.2.3 bugfix set, plus the merge of UI tweaks. Those fixes match [BUGS.md](BUGS.md): scrolling path list, reject exactly one camera view, ffmpeg/Windows navbar warnings, and refusing a label save whose keypoint is not a CSV column. The merge kept both `save_mvframe` tests. No further change is needed in project settings, the path dropdown, or the changelog.

## Fix

A failed Labeler save is wrapped before the error dialog sees it:

```387:389:lightning-pose-app/web_ui/src/app/labeler/labeler-center-panel/labeler-center-panel.component.ts
      .catch((error) => {
        this.isSaving.set(false);
        throw new Error(error?.message ?? String(error));
      });
```

`error.message` on an HTTP failure is Angular’s generic line (`Http failure response for ...`). The dialog in [error-dialog.component.html](lightning-pose-app/web_ui/src/app/error-dialog/error-dialog.component.html) already prints `data.error.detail` and the status when it receives the original HTTP error. The wrapper drops both, so the new 400 (“These keypoints are not columns in the label file…”) never appears.

Rethrow the original error after clearing `isSaving`. The dialog then shows the status and the server detail. No new spec: the dialog already covers that shape.
