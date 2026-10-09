# LPA user-defined skeleton

Let a researcher define a skeleton for a project and see its bones in the Labeler and the Viewer.

Designed against `main` at app version **2.4.2.1.dev0**. Display only. No Lightning Pose training, loss, or prediction changes.

## Answers

**Keep the definition only in `project.yaml`.** Nothing else on disk should store it.

Checked and ruled out:

- `~/.lightning-pose/projects.toml` holds this machine's data and model directories only.
- Label CSVs hold per-frame coordinates. A bone is not a label.
- Model `config.yaml` files (and `data_dir/configs/config_default*.yaml`) are Lightning Pose training configs. They copy `keypoint_names` when a model is created. They do not get a copy of the skeleton, or a later edit in Settings would leave every model with a stale copy.
- `localStorage` holds Labeler and Viewer display preferences only: show/hide, bone thickness, and bone opacity. Same idea as keypoint opacity and labels. Not the skeleton itself.

The app still has to *load* the field. `project.yaml` is parsed into `ProjectConfig` (`app_server/src/litpose_app/datatypes.py`) and returned as `ProjectInfo`. Pydantic ignores unknown keys, and `UpdateProjectConfig` rewrites the file from that model. A `skeleton` key typed into the yaml by hand, with no field on `ProjectConfig` and `ProjectInfo`, disappears the next time Settings saves keypoints or views. So the field lives in those two models and in the frontend `ProjectInfo` class. That is the same document, not a second copy.

No `schema_version` bump and no migration. Projects without the key have no bones. An empty list is the same thing.

**No Lightning Pose repo changes.** There is no skeleton in lightning-pose 2.4.2. Training reads `data.keypoint_names` and losses (PCA, temporal, multiview reprojection). `generate_labeled_video` in `lightning_pose/utils/predictions.py` draws a circle per keypoint and never a line. Bones in the app do not require that exporter to change. Saved labeled mp4s from Lightning Pose stay without bones.

## On-disk shape

In `<data_dir>/project.yaml`, next to `keypoint_names`:

```yaml
skeleton:
  - [nose, neck]
  - [neck, tail_base]
```

An unordered list of pairs. Each pair is two keypoint names. `[nose, neck]` and `[neck, nose]` are the same bone. List order does not matter. Omit the key, or use `[]`, when there is no skeleton.

People will hand-edit this file. Names match `keypoint_names` exactly, including case. The app must load a bad definition without crashing, show what is wrong, and refuse to draw it. `UpdateProjectConfig` still rejects an invalid skeleton and does not write it. A missing key or `[]` is valid and means no bones.

`getProjectInfo` loads `project.yaml` through `ProjectConfig.model_validate`. A strict pair type would reject the whole file, and the home page would show that project as failed, so the user could not open Settings to read the error. Keep `skeleton` as the raw YAML value on `ProjectConfig` and `ProjectInfo`. The shared check decides validity after load. Only a save that sends `skeleton` is rejected.

### Validity

One shared check, used by the Skeleton page and by the Labeler and Viewer. A definition is invalid when any of these is true:

- A pair is not exactly two names.
- A name is not in `keypoint_names` (including after a keypoint is renamed or removed).
- Both names in a pair are the same keypoint.
- The same undirected pair appears twice. `[nose, neck]` and `[neck, nose]` are the same pair. A keypoint may appear in more than one pair.
- The value is some other shape than a list of pairs (a string, a map, a nested list).

The check returns a short explanation per problem, naming the pair or the name. Several problems can be true at once; show each explanation. A valid definition produces no message.

## Settings

Add a **Skeleton** tab on project settings, after Keypoints. Same tab in the create-project wizard, so a new `project.yaml` can include it. The wizard still saves from the last tab; an empty skeleton is valid and the key is omitted.

`app-project-skeleton` lives in `web_ui/src/app/project-settings/project-skeleton/`. It is presentational: `keypointNames` and `skeleton` come in through `input()` / `model()`, and it does not inject `RpcService` or `ProjectInfoService`. The settings page keeps owning the form and the save, the same way it owns the keypoints textarea.

UI, DaisyUI only:

- Two `select`s of the project's keypoint names, plus an Add button.
- A list of current pairs, including pairs loaded from a hand-edited `project.yaml`. Each row has the two names and a remove button.
- When the definition is invalid, a red error (`text-error`) above the list. One line per problem, from the shared check: same keypoint twice, a name that is not in the project, a repeated pair, or another bad shape. A valid skeleton shows no status message.
- Adding a pair that would make the definition invalid does not change the list; the same red error explains why.
- Empty state, only when the list is empty and valid: short note that bones appear in the Labeler and Viewer once both keypoints of a pair are placed.

Create sends `skeleton` only when the user added at least one pair. Edit sends it when the Skeleton form is dirty, including `[]` after the last pair is removed, so a cleared skeleton is actually cleared. Other tabs stay patch-only and do not resend it.

## Drawing

Stack, front to back, on each Labeler image and each Viewer tile:

1. Keypoint dots and their labels (and the placement crosshair).
2. Skeleton bones.
3. The image or video.

Bones are SVG lines in `app-keypoint-container`, the overlay the Labeler (`app-image-label-widget`) and the Viewer (`app-viewer-center-panel`) already mount on top of the picture. The skeleton `svg` is the first child of that container, before the keypoint nodes. Those nodes include the labels, so both dots and labels paint in front of the lines. The picture stays behind the container. `pointer-events: none` on the svg, so bones never take a click.

Keypoint positions there are already display pixels (`getTransform` uses `position().x` / `position().y`). A line between those two points sits in the same box, so zoom on `app-zoomable-content` scales bones with the dots. No second coordinate system.

`app-skeleton-overlay` in `web_ui/src/app/components/` is the presentational piece: an `svg` of `line`s from a list of segments (`x1`, `y1`, `x2`, `y2`). Stroke is `#3b82f6` (Tailwind blue-500), not the keypoint color (`ColorService` green-500, or the per-model Viewer colors). Thickness and opacity come from the view-option sliders below, not from the keypoint size or opacity controls. Round caps. No custom CSS beyond what an SVG overlay needs.

A small pure helper (next to the overlay) turns a valid skeleton plus the keypoints on that tile into segments. Callers do not call it when the shared check fails, so this helper does not re-check the rules.

- Draw a bone only when both endpoints are on that same tile.
- A non-finite `x` or `y` is a missing end. Clearing a label (NaN) drops every bone that used it.
- Labeler: each keypoint `id` is the keypoint name. The position signal updates on pointerup, when the parent replaces the keypoint. During placement or a drag the dot is hidden and `crosshairPosition` is the live point, so that end of the bone follows the crosshair until pointerup. Temporal context unmounts `app-keypoint-container`, so bones are absent there, same as the keypoints.
- Viewer: match on `ViewerKeypoint.name`, not `id`. Ids are `${name}-${modelKey}` so several models can share a name. Group by `modelKey` and draw one bone per model. Do not connect model A's nose to model B's tail. Skip an endpoint whose `isVisible` is false (below the likelihood threshold, or otherwise hidden), or whose name is unchecked in the keypoint list (`keypointsShown` omits it from the tile). Every model's bones use the same blue. Two models draw two bones; they are not merged.

### Multiview

The same skeleton is applied independently inside each camera view. A bone may connect two keypoints on one view's image. It may not run from a keypoint in one view to a keypoint in another. There is no cross-view pair in the definition: pairs are keypoint names, and each view's overlay only sees that view's points. Do not draw a line between tiles.

## View options

In the right-hand View options of the Labeler and the Viewer, a **Show skeleton** row patterned on Keypoint labels. DaisyUI `toggle`. The icon is a bone drawn as a small inline SVG. The Material Icons font has no bone ligature, so a `material-icons` name would show the word "bone". Default on. The switch, the invalid-definition message, and the two sliders are one presentational component, used by both pages, so this behavior is implemented and tested once.

Thickness and opacity sliders sit **under** that switch. They follow the keypoint size and opacity rows on that same panel (label, `range range-xs`, reset button, current value), with their own signals:

- `showSkeleton`, `skeletonThickness`, `skeletonOpacity` on `LabelerViewOptionsService` and `ViewerViewOptionsService`.
- Persisted separately (`labeler-view-options.skeletonThickness`, and the viewer equivalents). Not written to `project.yaml`.
- Thickness is a pixel stroke width: default 2, range 0–5, step 0.05. Opacity is a stroke opacity: default 1, range 0–1, step 0.05. Reset returns those defaults. Neither reads or writes the keypoint sliders. The Labeler keypoint opacity slider caps at 0.6; the bone opacity slider does not.

When the switch is off, do not render bones, and hide the two sliders. When it is on, render bones and show the sliders.

When `project.yaml` has a skeleton and the shared check says it is invalid, disable the switch, show it off, and put a red `text-error` message beside it telling the user the skeleton definition is invalid. Leave the sliders hidden. Draw nothing, even if the stored switch is on. A missing or empty skeleton is valid: the switch works, and an empty list simply draws nothing.

`app-keypoint-container` takes the segments (or the skeleton plus a show flag), thickness, and opacity as inputs. The Labeler and Viewer parents pass them. The container does not load the project itself.

## Tests

Each spec below covers a behavior the others do not. Do not add a second spec that repeats the same rule through another component. Storybook for `app-skeleton-overlay` is for looking at the stroke. It is not a test.

- `web_ui/src/app/components/skeleton-overlay/skeleton-validity.spec.ts`: the rule catalog. A self-pair, an unknown name, a repeated undirected pair, and a bad shape each return an explanation that names the pair or the name. A valid list, including two pairs that share a keypoint, a missing key, and `[]` return no explanation.
- `web_ui/src/app/project-settings/project-skeleton/project-skeleton.component.spec.ts`: the page shows that explanation in red and does not emit the bad pair. Add emits a second pair that reuses a keypoint; remove emits the shorter list.
- `web_ui/src/app/components/skeleton-overlay/skeleton-bones.spec.ts`: where a line is allowed. Both ends on one tile produce one segment. A missing end, or an end that is present but not visible, produces none. Two models on one tile do not connect across `modelKey`. Points on two views do not connect across views.
- `web_ui/src/app/components/skeleton-overlay/skeleton-overlay.component.spec.ts`: the line is blue and uses the thickness and opacity inputs. This spec does not decide whether a segment should exist.
- `web_ui/src/app/keypoint-container/keypoint-container.component.spec.ts`: the skeleton svg comes before the keypoint nodes, so the dots and labels paint in front of the bones.
- The shared view-options component spec: switch off hides the thickness and opacity sliders; switch on shows them. An invalid skeleton disables the switch, shows the red message beside it, and hides the sliders.
- `app_server/tests/routes/test_project.py`
  - `test_update_project_config_round_trips_skeleton`: a valid skeleton is written to `project.yaml` and returned by `getProjectInfo`.
  - `test_update_project_config_rejects_bad_skeleton`: one invalid body is refused and the file is unchanged. This does not repeat the rule catalog.
  - `test_project_without_skeleton_loads`: a `project.yaml` with no `skeleton` key still loads, and saving an unrelated field does not invent or drop bones.

## Out of scope

- Lightning Pose labeled-video export, losses, or model configs.
- Per-bone color or thickness in the yaml. Color is the hardcoded blue; thickness and opacity are view options.
- A skeleton that differs by camera view, or a bone drawn from one view to another.
- Importing a DeepLabCut skeleton.
- Drawing bones in any screen other than the Labeler and the Viewer.
