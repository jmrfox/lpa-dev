# LPA Labeler side panel layout, slider limits, skeleton wording

No issue (requested by Jordan). PR paninski-lab/lightning-pose-app#185 (branch `fix/context-reset-label-outline`, together with the context reset button and the label outline fix).

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

## Tests

- `labeler-center-panel.component.spec.ts` "side panel": the button block comes after the Keypoints panel and before View options; Image size, Image brightness, Image contrast and Keypoint opacity have the new limits.
- `skeleton-view-options.component.spec.ts`: slider `aria-label`s and text are Skeleton thickness / Skeleton opacity, no "Bone".
- The settings-page sentence is wording only; its test was dropped in the test trim (`test/trim-low-value-specs`).

## Not done

- The skeleton settings page's empty-list hint still says "Bones appear in the Labeler and Viewer once both keypoints of a pair are placed."
