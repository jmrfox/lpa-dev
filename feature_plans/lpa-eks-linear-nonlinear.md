# EKS: linear for every project, nonlinear with calibration (LPA #150)

Merged in PR paninski-lab/lightning-pose-app#192 (branch `feat/eks-linear-nonlinear`), 2026-11-02.

## What the user sees

- **Models → Create → EKS ensemble model** shows in every project. It was hidden in single-view projects by an `@if (views.length)` gate on the Models page (added in #81, v2.3.0.0).
- The **Create EKS Model** dialog has a **Smoother** choice: **Linear** (default) or **Nonlinear (uses camera calibration)**.
- Nonlinear is disabled, with a tag beside it, when:
  - the project has fewer than two views: "Needs a multiview project"
  - the project is multiview but has no `calibration.toml` and no `calibrations/*.toml`: "Needs camera calibration"
- Single-view projects don't show **Quantile keep PCA**; the single-camera smoother has no such setting.

## On disk

- `ensemble.yaml` gains `smoother: linear | nonlinear`. A file without it (created before this change) is linear. No migration: the key is new and has a default.
- Nonlinear EKS writes its 3D estimates to `<eks model>/video_preds_3d/<session>.csv`. It isn't in `video_preds/` because the File Manager check expects only `<session>_<view>.csv` files there, and the Viewer reads every CSV under `video_preds/`.

## Backend

- `createEksModel` takes `smoother` and returns 400 for nonlinear when the project has fewer than two views or no calibration file (`calibration_paths.project_has_calibrations`).
- `run_eks.py`:
  - fewer than two `--camera_names` runs `fit_eks_singlecam`, saving under the input file's name (`<session>.csv`, or `<session>_<view>.csv` for a one-view project)
  - `--calibration` is passed to `fit_eks_multicam`, which makes it nonlinear
  - `--save_3d_dir` saves the 3D output under the session name
- Inference (`routes/inference.py`):
  - The plan resolves each nonlinear EKS session's calibration with `calibration_paths.calibration_for_session`: `calibrations/<session>.toml`, else `calibration.toml` (LP's order).
  - A session with neither is skipped, not run as linear. Its member models still run.
  - Before running, the calibration's camera names must equal the project views in order, as LP requires (`lightning_pose/data/datasets.py`, `_load_camgroup`). EKS 4.6.0 takes the cameras in file order without checking names, so a mismatch would pair views with the wrong cameras. The check reuses File Manager's `calibration_file_issues`. A mismatched session fails with an error in the log and task; other sessions still run.
  - At the end of the task, the log lists the skipped sessions under each EKS model name, and the task's final message says how many were skipped. The task still completes; skipped sessions are not counted as errors.

## 64-bit EKS and the even-member warning

The first real run (mirror-mouse-separate, 2 members, nonlinear, `smooth_param` 1000) gave NaN for 5 of 7 keypoints on every frame; linear gave NaN for paw2LF. The member predictions had no NaNs.

- Cause: EKS 4.6.0 runs in JAX's default 32-bit floats. Its process noise is `s × Q`, with Q from the frame-to-frame movement of the triangulated points. At s=1000 this was 5,000–43,000× the ensemble variance (two members agree to about 0.25 px). The filter computes a small uncertainty as the difference of two large numbers, and 32-bit has too few digits for that.
- Not the calibration: rescaling it ×0.01, removing the mirrored (negative fy) camera, and checking its accuracy (0.6–1.8 px median reprojection error) did not change or predict the NaNs.
- With 64-bit (`jax_enable_x64`), s=1000 gave no NaNs, linear or nonlinear, at about the same run time (nonlinear 10.6–10.7 s vs 9.2–11.1 s; linear 9.4 s vs 7.9 s on 30,000 frames) and about 15–20% more memory. Automatic `s` (EKS's default) also gave no NaNs but took about 10 minutes for nonlinear on CPU.
- With 3 members, 32-bit at s=1000 gave no NaNs: the ensemble variance roughly doubled.
- Change: `run_eks.py` turns on 64-bit before importing eks. The dialog shows "EKS works best with an *odd* number of ensemble members" for an even count; Create is still allowed.
- The 1000 default stays (it came with #80). EKS paninski-lab/eks#62 reported mostly-NaN multicam output; its fix (eks#65, in 4.5.0) changed the single-model variance and doesn't cover this.

## Tests

- `app_server/tests/routes/test_eks.py`: the CLI gets `--calibration` with the session file when present, and the project file otherwise. Also covers single-view creation, the nonlinear refusals, single-view input files, the skipped-session list, and a session calibration with cameras in another order (that session fails, the other runs).
- `web_ui/.../create-eks-model-dialog.component.spec.ts`: Nonlinear is disabled with the right reason, and Create sends `smoother`. 2 members show the odd-number warning, 1 or 3 don't, and Create stays enabled.
- `app_server/tests/test_run_eks.py`: multiview and single-view EKS are called with JAX 64-bit on.
- `run_eks.py` was run by hand with eks 4.6.0 on made-up predictions, for single-view, one-view, linear and nonlinear (3D file written). That run isn't in CI.

## Open

- Renaming a session doesn't rename `video_preds_3d/<session>.csv`. Prediction CSVs in `video_preds/` aren't renamed either, so this matches today's behavior; left for a separate change.
