# LPA Labeler side panel layout, slider limits, skeleton wording

No issue (requested by Jordan). PR paninski-lab/lightning-pose-app#185 (branch `fix/context-reset-label-outline`, together with the context reset button and the label outline fix); the default opacity followed in PR paninski-lab/lightning-pose-app#186.

UI-only. No backend, RPC, or on-disk format changes. Stored view options (`localStorage`) keep the same keys and units.

## Behavior

- **Button order:** Save / delete, Save and next, Next and Revert sit right under the Keypoints panel, then Multiview tools, then View options. They were at the bottom of the panel. The block is `data-testid="frame-actions"`.
- **Slider limits (Labeler View options):**

| Slider | Before | Now |
|---|---|---|
| Image size | 200–1200px | 200–1600px |
| Image brightness | 0.3–1.7 | 0–2 |
| Image contrast | 0.5–1.5 | 0–2 |
| Keypoint opacity | 0–0.6 | 0–1 |

  Brightness and contrast are CSS filter multipliers; 1 is still unchanged and sits mid-slider. No number is shown under them (Jordan asked for limits only). 0–3 was tried and reverted to 0–2. The four sliders now have `aria-label`s. The Viewer's keypoint opacity slider already ran 0–1.
- **Wording:** the shared skeleton sliders (`components/skeleton-view-options/`, Labeler and Viewer) are **Skeleton thickness** and **Skeleton opacity** (were "Bone …"). The skeleton settings page says "Each pair will be connected with a line in the Labeler and the Viewer."

## Default keypoint opacity (PR paninski-lab/lightning-pose-app#186)

Labeler keypoints start at opacity 0.5 (was 0.15): `ColorService.defaultOpacity` in `infra/color.service.ts`, which only the Labeler uses. Reset returns to 0.5. A value already saved in the browser (`labeler-view-options.opacity`) is kept; a saved 0 falls back to the default because the value is read with `Number(...) || default`. The Viewer's default (`DEFAULT_OPACITY = 1.0` in `viewer-view-options.service.ts`) is unchanged.

Test: `labeler-view-options.service.spec.ts` (with nothing saved, opacity starts at 0.5 and Reset returns to 0.5; a saved 0.2 is kept).

## Show skeleton with no pairs (PR paninski-lab/lightning-pose-app#189)

`app-skeleton-view-options` has a `noPairs` input. Labeler (`labeler-center-panel`) and Viewer (`viewer-page`) set it from `skeletonPairs(projectInfo.skeleton).length === 0`. With no pairs the switch shows off and is disabled, with the hint "No skeleton pairs defined. Add them in project settings." The stored `*.showSkeleton` flag is not written, so it still applies in projects with pairs. Disabled rather than merely off, because turning it on would draw nothing.

Tests: `skeleton-view-options.component.spec.ts` (no pairs: off, disabled, no sliders, no change emitted; pairs again: the saved on shows); `labeler-center-panel.component.spec.ts` "shows Show skeleton off when the project defines no skeleton pairs". The Viewer page has no spec; it passes the same input.

## Skeleton slider numbers (PR paninski-lab/lightning-pose-app#189)

`app-skeleton-view-options` has a `showValues` input (default true). The Labeler passes false, so Skeleton thickness and Skeleton opacity show no number, matching brightness, contrast and keypoint opacity. The Viewer keeps the numbers. Test: `skeleton-view-options.component.spec.ts` "shows the thickness and opacity values unless showValues is off".

## Tests

- `labeler-center-panel.component.spec.ts` "side panel": the button block comes after the Keypoints panel and before View options; Image size, Image brightness, Image contrast and Keypoint opacity have the new limits.
- `skeleton-view-options.component.spec.ts`: slider `aria-label`s and text are Skeleton thickness / Skeleton opacity, no "Bone".
- The settings-page sentence is wording only; its test was dropped in the test trim (PR paninski-lab/lightning-pose-app#187).

## Not done

- The skeleton settings page's empty-list hint still says "Bones appear in the Labeler and Viewer once both keypoints of a pair are placed."
