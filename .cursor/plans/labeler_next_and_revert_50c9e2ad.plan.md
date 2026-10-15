---
name: Labeler next and revert
overview: Add Next and Revert changes under Save and next, make both remove-frame buttons red trash cans, and add Load Calibration inside Multiview tools.
todos:
  - id: buttons
    content: Add right-aligned Next and Revert changes under Save and next.
    status: completed
  - id: next-frame
    content: Navigate to the next frame in the combined list without saving.
    status: completed
  - id: revert-edits
    content: Restore saved keypoints on labeled frames and clear unlabeled frames, refreshing the image widgets.
    status: completed
  - id: remove-buttons
    content: Use the red trash icon for both remove-frame buttons, keeping the two tooltips.
    status: completed
  - id: load-calibration
    content: Add Load Calibration in Multiview tools, reusing the File Manager dialog, and refresh calibration status after a copy.
    status: completed
  - id: tests-and-plan
    content: Add the frame-model spec, the next-frame page case, and the feature plan note.
    status: completed
  - id: browser-check
    content: On mms1, check Next, Revert, both trash buttons, and cancel Load Calibration without writing.
    status: completed
isProject: false
---

# Labeler Next and Revert

Add two buttons in the right-hand column of [labeler-center-panel.component.html](lightning-pose-app/web_ui/src/app/labeler/labeler-center-panel/labeler-center-panel.component.html), in a right-aligned row directly under **Save and next**. Labels: **Next →** and **Revert changes ↫**. Use the default `btn` style so they stay distinct from the sky save buttons. **Save** and **Save and next** stay as they are, including advancing to the next view before the next frame.

## Next

**Next** does not save and does not discard edits. It selects the next `MVFrame` in `labelFileData`, the same order as today: labeled frames, then remaining frames ([label-file-fetcher.service.ts](lightning-pose-app/web_ui/src/app/labeler/label-file-fetcher.service.ts) returns `mvf.concat(unl)`). The last labeled frame therefore continues into the first remaining frame. On the last frame, the button is inactive (`hasNextFrame` is already computed in [labeler-page.component.ts](lightning-pose-app/web_ui/src/app/labeler/labeler-page.component.ts)). It does not switch views inside the current frame.

The center panel emits `nextFrame`. The page navigates with the same query params **Save and next** uses (`labelFileKey`, `frameKey`). In-memory edits stay on that frame object, which is the current behavior when you pick another frame in the list.

## Revert changes

Active only when this frame has edits. Inactive while saving, and after a revert.

- Labeled frame (`originalKeypoints` is set): copy those saved points back onto every view. The saved copy itself is not reused as the live array, so a later drag cannot overwrite it.
- Unlabeled frame (`originalKeypoints` is null): set every keypoint on every view to `NaN`. The frame stays in **Remaining frames to label** because it is still unsaved. Points that came from the unlabeled sidecar are cleared too.

Put this on `MVFUtils` in [frame.model.ts](lightning-pose-app/web_ui/src/app/labeler/frame.model.ts) as `hasRevertibleEdits` and `revertEdits()`. Do not change the existing `hasChanges` getter. **Save** uses that getter, and it is true for every unlabeled frame because `originalKeypoints` is null. Revert uses the narrower check: any non-`NaN` point on an unlabeled frame, or `hasChanges` on a labeled frame.

After revert, replace each view's `keypoints` array and bump the existing `cacheBuster`. The image widget caches markers by that array ([image-label-widget.component.ts](lightning-pose-app/web_ui/src/app/labeler/image-label-widget/image-label-widget.component.ts)), and OnPush will not redraw the main view or the filmstrip when the `FrameView` object is the same. Pass `cacheBuster` into both `app-image-label-widget`s as a revision input so they read the new points.

## Test and note

One spec, `frame.model.spec.ts`: `reverts labeled frames to saved keypoints and clears unlabeled frames`. It checks a labeled frame returns to the saved coordinates, the saved copy stays independent, an unlabeled frame becomes all `NaN` with `originalKeypoints` still null, and a cleared unlabeled frame is no longer revertible.

Add one case to the existing advance tests in [labeler-page.component.spec.ts](lightning-pose-app/web_ui/src/app/labeler/labeler-page.component.spec.ts): **Next** from the last labeled frame opens the first remaining frame and leaves the edited points on the frame you left.

Write that behavior in [feature_plans/lpa-labeler-next-revert.md](feature_plans/lpa-labeler-next-revert.md) and name that frame-model spec. Mention the shared trash button and **Load Calibration** there too. No extra spec for those two: the copy behavior is already covered by the File Manager calibration import.

## Remove-frame buttons

In [labeler-center-panel.component.html](lightning-pose-app/web_ui/src/app/labeler/labeler-center-panel/labeler-center-panel.component.html), the labeled-frame control is `btn btn-error btn-soft` with the `delete` icon. The remaining-frame control is `btn btn-soft` with the `cancel` icon. Use the red trash button for both. Keep the tooltips: "Remove frame from label file" and "Remove frame from labeling queue".

## Load calibration

At the bottom of the **Multiview tools** panel, add a full-width **Load Calibration** button. It stays enabled when no calibration file is present. The other two buttons in that panel stay disabled until a calibration exists.

Reuse [load-calibration-dialog.component.ts](lightning-pose-app/web_ui/src/app/file-manager/load-calibration-dialog.component.ts) the same way the File Manager does: mount it while a signal is set, and close it on `done`. The dialog copies `.toml` files into `calibrations/`. The name before `.toml` is the session id. An existing file is left unchanged. Cancel writes nothing.

When a file was copied, call `checkIfHasCameraCalibrationFiles()` again so the status line, **Project keypoints to all views**, and **Refine calibration** update for the current session.

## Check

On `mms1` in the labeler, move a point on a labeled frame, confirm **Revert changes** turns on and restores the saved point, then confirm **Next** changes frame with no save toast. Open a remaining frame, place a point, revert, and confirm the points are gone and the frame is still in that list. On that remaining frame, the remove button is a red trash can. Open **Load Calibration** and cancel it so nothing is written.