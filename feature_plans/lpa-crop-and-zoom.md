# Crop and zoom (LP "cropzoom") in LPA

Status: design, not started. Issue: paninski-lab/lightning-pose-app#209.

LP reference: `lightning-pose/` at `eed0301` ("end-to-end singleview cropzoom pipeline", LP #508, released in LP 2.4.4). User guide: `docs/source/user_guide_advanced/cropzoom_pipeline.rst`. Bbox file format: `docs/source/directory_structure_reference/bounding_box_file_format.rst`.

## What crop and zoom is

For a small animal in a large arena, LP runs two ordinary models:

- a **detector** model, trained on the full frame, that finds the animal;
- a **pose** model, trained on crops around the animal.

Neither model is special. They differ only in what images they were trained on. The two models may use different backbones, image sizes and keypoints.

## How LP does it

### Training (5 commands)

```bash
litpose train config.yaml --output_dir $DET                 # 1. detector, on full frames
litpose predict $DET data/CollectedData.csv                 # 2. detector predictions on the labeled frames
litpose create_bbox $DET data/CollectedData.csv             # 3. one box per labeled frame
litpose crop $DET data/CollectedData.csv                    # 4. crop images + shift the labels
litpose train config.yaml --output_dir $POSE --detector_model $DET   # 5. pose model, on the crops
```

Where the files go (all inside the **detector's** folder):

| Step | Writes |
|---|---|
| 2 | `$DET/image_preds/CollectedData.csv/predictions.csv` |
| 3 | `$DET/image_preds/CollectedData.csv/bbox.csv` (`,x,y,h,w`, one row per labeled image, keyed by image path) |
| 4 | `$DET/cropped_images/<same relative image paths>`, `$DET/image_preds/CollectedData.csv/cropped_CollectedData.csv` (labels in crop coordinates) |

Step 5 (`cli/commands/train.py`) loads the detector and, before training, replaces in the pose config:

- `data.data_dir` → `$DET/cropped_images`
- `data.video_dir` and `eval.test_videos_directory` → `$DET/cropped_videos`
- `data.csv_file` → `$DET/image_preds/<csv>/cropped_<csv>` (each, for a list)

LP then saves that config as `$POSE/config.yaml` (`train.py`, "Save configuration in output directory"), so the pose model's config points into the detector's folder. Nothing in the pose folder names the detector.

Box size options (`cli/bbox_args.py`, shared by `create_bbox` and `predict --detector`):

- `--crop_ratio R` (default 2.0, must be > 1): box is R × the keypoint spread, per frame.
- `--crop_size N`: fixed N × N box centred on the mean of the keypoints.
- `--anchor_keypoints a,b,c`: which detector keypoints define the box (default: all).

Optional `litpose smooth_bbox` smooths boxes over time (videos).

### Inference

One command does detector → box → crop → pose → map back to full-frame coordinates, in memory:

```bash
litpose predict $POSE videos/session.mp4 --detector $DET [--crop_ratio R | --crop_size N] \
    [--anchor_keypoints a,b] [--detector_confidence_thresh T] [--batch_size B]
```

It writes `$POSE/video_preds/session.csv` (full-frame coordinates, the same format as any model) and `$POSE/video_preds/session_bbox.csv` (one box per frame).

Limits of `--detector` (`pipelines/cropzoom.py`, `cli/commands/predict.py`):

- single-view models only, both detector and pose;
- not context models (`heatmap_mhcrnn`);
- video inputs only;
- cannot be combined with `--bbox_dir`, `--overrides`, `--compile`, or a non-eager `--runtime`;
- no box smoothing;
- `--detector_confidence_thresh` (off by default): anchor keypoints below it are dropped; a frame with fewer than 2 left reuses the previous frame's box.

The older multi-command route (`predict` detector → `create_bbox` → optional `smooth_bbox` → `predict $POSE --bbox_dir`) also works, including for multiview pose models (one `<video_stem>_bbox.csv` per view). LP's roadmap lists multiview crop and zoom training as not done.

## What LPA does today

- No crop-and-zoom support. No open or closed issue mentions it.
- Training: `train_scheduler.py` runs exactly one command per model, `litpose train <config> --output_dir <model>`.
- Inference: `routes/inference.py` runs `utils/inference/predict_wrapper.py`, which calls `litpose predict <model> <videos> --skip_viz --overrides=dali.base.predict.sequence_length=<B>` and halves B on CUDA out-of-memory. `--overrides` is refused with `--detector`.
- EKS models are already a "model made from other models": `ensemble.yaml` in the model folder lists member model names, and inference runs the members first. Crop and zoom can follow the same pattern.
- Migration `004_fix_config_data_dirs` runs at startup for every project and sets every model's `data.data_dir` to the project data folder when they differ. A crop-and-zoom pose model's `data_dir` is `$DET/cropped_images`, so 004 would rewrite it.
- `validate_files.py` already accepts `_bbox` files from `litpose create_bbox`; `session.service.ts` already skips `bbox.csv` and `predictions.csv` when listing.

## Design

### On disk

A crop-and-zoom pose model is an ordinary LP model folder plus one LPA file, `cropzoom.yaml`, like `ensemble.yaml` for EKS:

```yaml
detector: <detector model name, relative to the project model folder>
crop_ratio: 2.0          # or crop_size: 256 (exactly one)
anchor_keypoints: []     # empty = all detector keypoints
detector_confidence_thresh: null
```

- The model name (not a path) is stored, as `ensemble.yaml` does, so moving the project keeps it working (design principles 4 and 7).
- Everything LP needs stays in LP's own files. `cropzoom.yaml` only tells LPA how to call LP. The `--detector` options are the same ones used to make the training crops, so the pose model sees the same kind of crop at inference that it trained on.
- This is a new file, not a change to an existing format, so no migration is needed for it. Migration 004 does need a change (below).

### Training

Create Model dialog gets a **Crop and zoom** section (single-view projects only):

- **Detector**: pick a single-view, non-context model in the project (completed, or still pending/training).
- **Box size**: ratio (default 2.0) or fixed size in pixels.
- **Anchor keypoints**: from the detector's keypoints (default all).
- **Model type** of the pose model: context models are disabled while a detector is chosen, because `--detector` inference does not support them.

`createTrainTask` writes `cropzoom.yaml` next to `config.yaml`. The scheduler, for a model with `cropzoom.yaml`:

1. Waits until the detector is COMPLETED (stays PENDING; fails with a clear message if the detector failed or was deleted).
2. Runs, in the model's log files, with `<det csv>` the detector's own label file:
   - `litpose predict $DET <det csv>`
   - `litpose create_bbox $DET <det csv> <size options>` → `$DET/image_preds/<det csv>/bbox.csv`
   - `litpose crop $DET <pose csv> --bbox_dir $DET/image_preds/<det csv>` → crops and `$DET/image_preds/<pose csv>/cropped_<pose csv>`, the path `--detector_model` reads.
   The detector is never run on the pose label file: with fewer keypoints, `litpose predict` exits 1 there (tested, below). The predict step is rerun every time so that labels added after the detector was trained get boxes (the detector label file has to be rewritten from the pose label file first, if it is a subset).
3. Runs `litpose train <config> --output_dir <model> --detector_model $DET --overrides eval.predict_vids_after_training=false`, unless the project videos were cropped too (open question 2). Without the override, training exits 1 at the end (tested, below).

A new status (for example `PREPARING_CROPS`) shows that steps 2 are running. The GPU lock is held for the whole chain.

### Inference

For a model with `cropzoom.yaml`, the inference plan:

- skips it with a clear message if the detector is missing or not completed (principle 8);
- runs `predict_wrapper.py` with `--detector $DET` and the options from `cropzoom.yaml`;
- `predict_wrapper.py` switches from `--overrides=...sequence_length=B` to LP's `--batch_size B` (LP #481, in LP 2.4.0 and later), for all models.
- `--detector` is in LP 2.4.4 and later (LP #508). LPA's `pyproject.toml` does not pin LP, so the dialog should say so on older LP, as the recommender does for 2.4.1.

The pose model's `video_preds/<video>.csv` is in full-frame coordinates, so the Viewer, EKS and everything else that reads predictions works unchanged.

An EKS model may use crop-and-zoom pose models as members; the member step is just a normal predict step with `--detector`.

### Viewer (second step)

- Draw the crop box from `<pose>/video_preds/<video>_bbox.csv` as an optional overlay. This helps users judge the detector.

### Models page

- Show "Crop and zoom, detector: <name>" on the model card and detail.
- Deleting a detector that pose models use: warn and list them (the pose models stop being able to run inference and retrain).
- Renaming a detector: update `cropzoom.yaml` in the pose models that name it (as model renames should already do for `ensemble.yaml`; check).

### Migration 004

Change 004 to leave `data_dir`/`video_dir` alone for models with `cropzoom.yaml`, or to point them at the detector's current `cropped_images`/`cropped_videos`. The second keeps the config correct when the project moves. Add a test with a crop-and-zoom model folder.

## Open questions (for Jordan)

1. **One crop setting per detector.** LP writes the crops and the cropped labels into the detector's folder. Two pose models built on one detector with different box sizes would overwrite each other's crops, and the first pose model's `config.yaml` would point at crops made with the second's settings. Options:
   - a. Allow one box setting per detector: the second pose model must use the same setting (LPA fills it in and locks it). Simplest; matches LP.
   - b. Rerun the crops each time and accept that older pose models' training data changed (only matters for retraining).
   - c. Propose upstream (`UPSTREAM_CHANGES.md`): let `litpose crop` / `train --detector_model` take an output folder, so crops live in the pose model's folder.
   Leaning a for v1, c upstream.
2. **Videos for unsupervised losses.** `train --detector_model` sets the pose model's video folder to `$DET/cropped_videos`, which is empty unless videos were cropped. Semi-supervised pose models need cropped videos (detector predict + `create_bbox` + `crop` on the project videos). v1 could allow supervised pose models only, or add those steps. With no cropped videos, training needs `eval.predict_vids_after_training=false` (tested, below).
3. **Box smoothing.** `--detector` does not smooth. Leave smoothing out of v1?
4. **Multiview.** LP supports multiview crop and zoom at inference (`--bbox_dir`) but not training (roadmap). Leave multiview out of v1?
5. **Detector keypoints.** From the lab meeting: the detector trains on a subset of keypoints. LP has no setting for that; the detector needs its own label file with only those columns. The subset route works (tested, below). Open: does LPA write that file (from the pose label file, rewritten before each pose model so new labels are included), and where (a project label file the user sees, or inside the detector's folder)? The other way to get a subset is to train on all keypoints and build the box from `--anchor_keypoints`.
6. **Pose model labeled-frame predictions.** LP's post-training predictions for the pose model are in crop coordinates (`train.py` sets `bbox_files = None` on purpose). LPA does not show them today; if it ever does, they need mapping back (`litpose remap`).

## Test on charis-bot-up (2026-11-24)

LP 2.4.4 (`eed0301`), poseapp env, RTX 4070. Project `LPProjects/charis-bot-up`: single-view bottom-up mouse, 1120×1120 frames, `CollectedData.csv` 493 frames × 8 keypoints; the mouse spans about 200 px. Everything was written to the session scratchpad; nothing in the project was changed.

Setup: LP's `config_default.yaml`, heatmap, `resnet50_animal_ap10k`, supervised, 256×256, 40 epochs, `dlc-top-down`. Detector label file `CollectedData_det.csv`: the same 493 rows, only `l_h_paw`, `r_h_paw`, `tailbase`, `tailtip` (each missing in at most 2 frames). Anchor keypoints: those four, `crop_ratio` 2.0.

| Step | Result |
|---|---|
| `litpose train config_det.yaml` (4 keypoints) | Trained, about 6 min. Median error train 7–9 px, validation 7–11 px (full frame). Exited 1 at the end only because I set `eval.test_videos_directory: null`; LPA's configs set it. |
| `litpose predict $DET CollectedData.csv` (8-keypoint file) | `predictions.csv` written, complete (493 rows, 4 keypoints), then **exit 1** in `compute_metrics_single`: `operands could not be broadcast together with shapes (493,8,2) (493,4,2)`. |
| `create_bbox $DET CollectedData.csv` + `crop $DET CollectedData.csv` on those predictions | Both exit 0. 2450 images cropped (labeled frames and their neighbors). `cropped_CollectedData.csv` has all 8 keypoints. |
| Route without the error: `create_bbox $DET CollectedData_det.csv` (training-time predictions), then `crop $DET CollectedData.csv --bbox_dir $DET/image_preds/CollectedData_det.csv` | Both exit 0. `cropped_CollectedData.csv` byte-identical to the row above. |
| `litpose train config_pose.yaml --detector_model $DET` (8 keypoints) | Trained, about 3 min. Median validation error 3–17 px (crop coordinates). Then **exit 1**: `OSError: Did not find any valid video files in $DET/cropped_videos`. Checkpoint saved, `train_status.json` left at `EVALUATING`, so LPA's scheduler would mark the model FAILED. Saved `config.yaml` has `data_dir`, `video_dir`, `csv_file`, `test_videos_directory` all inside `$DET`. |
| Same, plus `--overrides eval.predict_vids_after_training=false` | Exit 0, `train_status.json` COMPLETED. |
| `litpose predict $POSE videos/12808-short.mp4 --detector $DET --anchor_keypoints … --skip_viz` | Exit 0, 7200 frames in 34 s. `12808-short.csv` (8 keypoints, no NaNs) and `12808-short_bbox.csv` (7200 rows). Every prediction lies inside its frame's box. Frame 3000 drawn: the mouse is in the top-left corner and box and keypoints sit on it. Boxes have negative x/y near the frame edge (box reaches past the frame). |

Also seen:
- With crop ratio 2.0 on these four keypoints, training boxes were 144–1966 px (median 474); 82 of 3508 labeled points (2%) fell outside their box. The tail makes the keypoint spread large. On the video, boxes were 72–508 px (median 280).
- Each crop-and-zoom pose model's crops and labels go into the detector folder, as above (open question 1).

## Tests (to write with the change)

- Backend: `createTrainTask` writes `cropzoom.yaml`; scheduler runs the four commands in order and waits for the detector (fake `litpose`); inference plan adds `--detector` and the box options, and skips when the detector is missing; migration 004 leaves (or fixes) a crop-and-zoom model's `data_dir`.
- UI: `create-model-dialog.component.spec.ts`: choosing a detector shows box options, disables context model types, sends them in the request; hidden for multiview projects.
- One end-to-end run on a real project (single-view, small animal) before merging: detector + pose model trained through the app, Viewer shows full-frame predictions.
