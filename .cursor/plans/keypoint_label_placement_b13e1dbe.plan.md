---
name: Keypoint label placement
overview: Place keypoint labels in the first of four corners that does not overlap another label, and keep that corner until it no longer fits, so nearby names stop stacking on the lower-right without a layout solver.
todos:
  - id: placement-fn
    content: Add the four-corner placement function with hysteresis
    status: completed
  - id: bind-offsets
    content: Bind label top/left from that function in the keypoint container
    status: completed
  - id: test-changelog
    content: Cover nearby labels and stable corners in one spec, and note it in the changelog
    status: completed
isProject: false
---

# Dynamic keypoint label placement

Labels in [keypoint-container.component.html](lightning-pose-app/web_ui/src/app/keypoint-container/keypoint-container.component.html) are always `top`/`left` = `keypointSize / 1.15`, the lower-right of the marker. Both the Labeler and the Viewer use this component, so one change covers both.

## Placement

Add a pure function in `web_ui/src/app/keypoint-container/keypoint-label-placement.ts`. It takes the visible labels (id, text, x, y), marker size, and font size, plus the corner each id used last time.

- Estimate each box as `fontSize` tall and `0.6 * fontSize * text.length` wide. No DOM measurement.
- Try corners in order: lower-right, upper-right, lower-left, upper-left. Offsets stay relative to the marker circle and use the same tuck as today (`size / 1.15` from the circle’s top-left; the opposite sides mirror that inset).
- Walk ids in sorted order. Keep the previous corner when its box still misses every label already accepted in this pass. Otherwise take the first free corner. If every corner overlaps, keep the one with the smallest overlap.
- Treat two boxes as overlapping only when they intersect by more than a couple of pixels, so a one-pixel jitter does not flip a corner.
- Return `{ top, left }` per id, in the same coordinate space the span already uses.

Skip keypoints that are hidden (`isVisible` false) and the one being dragged. Its marker is already `display: none`, and the crosshair label follows the pointer on its own. Placement then does not run on pointer moves; it runs when a stored position, the font size, or the marker size changes.

Store the last corner per id on the component and update it from the computed that reads `keypoint.position()`, `keypointLabelFontSize()`, and `keypointSize()`. Repeating the function with the corners it just chose returns the same corners. Drop ids that are no longer shown.

Bind the span with those offsets instead of the fixed `keypointSize() / 1.15`. Keep `top`/`left`. A transform on the label would put it back on its own layer inside the zoom.

## Tests and changelog

`keypoint-label-placement.spec.ts`: two separated points both use the lower-right; two close points get different corners; running again with those corners and a tiny position change keeps the same corners.

Note the behavior in [CHANGELOG.md](lightning-pose-app/CHANGELOG.md) under `### [2.4.2.3.dev0]`.
