# Labeler next, revert, and calibration load

The actions stack in one column: **Save** beside the trash button, then **Save and next**, **Next →**, and **Revert changes ↫**. All four use the normal blue.

- **Next →** opens the next frame in the combined list (labeled frames, then remaining frames) and does not save. Edits stay on the frame you left. The button is inactive on the last frame. It does not switch views inside the current frame.
- **Revert changes ↫** is active only when this frame has edits. On a labeled frame it restores the saved keypoints. On a remaining frame it clears every point, including sidecar predictions, and leaves the frame in **Remaining frames to label**.

Both remove-frame buttons are the red trash icon. The tooltip still says whether the frame leaves the label file or the labeling queue.

**Load Calibration** sits at the top of **Multiview tools**, then **Refine calibration**, then **Project keypoints to all views**. It uses the File Manager dialog. It copies `.toml` files into `calibrations/`. The name before `.toml` is the session id. An existing file is left unchanged. After a copy, the calibration status for the current session is checked again.

`frame.model.spec.ts` (`reverts labeled frames to saved keypoints and clears unlabeled frames`) guards a labeled restore that does not alias the saved copy, and an unlabeled clear that stays unsaved. `labeler-page.component.spec.ts` (`next frame follows the combined list without saving`) guards moving from the last labeled frame into the first remaining frame without discarding the edit.
