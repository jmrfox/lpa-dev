# Create Model: more options, recommended settings, project default config (LPA #190)

Branch: `feat/create-model-options` in `lightning-pose-app`.

## Decisions (Jordan, 2026-11-03)

- Project default config: the fixed path `configs/default.yaml` (no `project.yaml` field, so no `schema_version` question, #177).
- Include LP's recommender (`litpose recommend`) in #190, not a separate issue.
- Bundled defaults: match LP 2.4.4's `scripts/configs/config_default*.yaml`, but keep 256×256 images.
- The "write the default config" action goes in the dialog's General tab.

## What the user sees

- **General tab:** says whether the form builds on `configs/default.yaml` or on LPA's built-in default. Without the file, **Create project default config** writes LPA's default there (never overwriting; the backend returns 409 if it exists).
- **Data tab:** **Random seeds**: Data split (as before) and Model (`training.rng_seed_model_pt`, new).
- **Training tab:**
  - **Recommended settings** at the top (see below).
  - **Image size** (height, width; multiples of 128, LP's rule).
  - **Learning rate**. It starts at the base config's rate, or 5e-5 for a ViT backbone on a single-view project, the old hidden patch. Once the user types a rate (or takes LP's), a backbone change leaves it alone.
  - **Augmentation** adds DLC-LR. In LP, `dlc-lr` is `dlc` plus a random 0°/180° rotation, not a flip.
  - **Advanced** (collapsed): **Optimizer**, **Heatmap loss**, **Early stopping** with patience, and **Horizontal flip** (single-view only).
- Horizontal flip is hidden for multiview projects: LP raises for multiview models. It's disabled with a tooltip naming the unpaired keypoints when a `_left` keypoint has no `_right` partner or the other way round (`hflip.ts`, LP's `datasets.py` rule).
- Every new field starts from the base config (`applyBaseConfigDefaults`).

## Recommended settings

- `POST /app/v0/rpc/recommendModelConfig` (`routes/configs.py`) runs `scripts/recommend_config.py` with the app's Python. A separate process is used because `get_gpu_info` starts CUDA, which would keep GPU memory in the app server.
- The script:
  1. Calls LP's `analyze_dataset` on the first view's CSV.
  2. Replaces `csv_paths` and `view_names` with the chosen label file's. On its own, LP's directory discovery only finds `CollectedData[_<view>].csv`.
  3. Replaces `video_dir` and `has_videos` with the dialog's videos folder.
  4. Calls `get_gpu_info` and `recommend`, and prints JSON.
- The route checks that every CSV and the videos folder are inside the data directory. A script failure becomes a 400 with the last stderr line. The recommender needs LP 2.4.1 or newer (#489); older LP gets a message saying so.
- The dialog fills: multiview transformer on/off, model type (semi-supervised when LP picks losses, keeping a Context choice), backbone, image size, both batch sizes, epochs, optimizer, learning rate, augmentation, and the temporal/Pose PCA switches. It then lists LP's reason for each field.
- Single-view projects get a **Top-down view of a freely moving animal** checkbox (LP's `--top_down_freely_moving` question).
- Tried on mirror-mouse-separate through the app: multiview transformer, vits_dino, 256×256, batch 16, 300 epochs, AdamW 5e-5, `dlc`, no losses; about 2 s.

## Built-in defaults vs LP 2.4.4

Taken from LP:
- `log_weight` 11.0 (was 10.7)
- `imgaug_hflip: false`
- early stopping keys in the multiview default
- `test_videos_directory: ${data.video_dir}`

Kept (LPA's, on purpose):
- `image_resize_dims` 256×256 (LP: null)
- multiview DALI batch sizes 24/48/24 (Karan Sikka, #44)
- multiview `supervised_reprojection_heatmap_mse.log_weight: null` (Matt Whiteway, #102)
- `imgaug_3d: false`, `camera_params_file: null`, no `bbox_file`
- no `hydra:` block: LPA loads configs with `OmegaConf.to_container(resolve=True)`, and `${now:...}` is a Hydra-only resolver

New projects get `configs/default.yaml` (single-view or multiview default) instead of `configs/config_default.yaml` and `configs/config_default_multiview.yaml`, which nothing read. An existing `configs/default.yaml` is kept. Old copies in existing projects are left alone.

## Tests

- `create-model-dialog.component.spec.ts`:
  - "learning rate"
  - "training options (#190)"
  - "project default config (#190)"
  - "recommended settings (#190)"
- `app_server/tests/routes/test_model_configs.py`: bundled defaults, `writeDefaultModelConfig`, CreateNewProject keeping an existing file, the recommend route and the script (with a stand-in recommender; CI has no LP).
- `app_server/tests/routes/test_project.py`: a new project gets `configs/default.yaml`.
- Full backend suite (186) and full UI suite (283) pass; `ng lint` clean. The dialog was not tried in the browser.

## Not done

- **"Save as project default"** (optional in #190): write the current form values into `configs/default.yaml`.
- **Settings LP's recommender doesn't cover** (heatmap loss, early stopping, hflip): they keep their values when **Use recommended settings** is pressed.
