---
name: Label and pane fixes
overview: Stop the first-paint label jump, place names from the ink plus the stroke so the gap stays even at large sizes, and clamp split panes through the public size input instead of a private field.
todos:
  - id: ink-and-first-paint
    content: Hide labels until the frame and ink box are known, and place the ink plus the 1px stroke on the tuck
    status: completed
  - id: public-pane-clamp
    content: Clamp split panes by updating the public size signal, and move the playback-bar sum into a pure function
    status: completed
  - id: tests-changelog
    content: Cover the tuck, the pane clamp, and the playback-bar sum, and note the label gap in the changelog
    status: completed
isProject: false
---

# Label flash, ink gap, and pane clamp

Three follow-ups from the branch review. The placer in [keypoint-label-placement.ts](lightning-pose-app/web_ui/src/app/keypoint-container/keypoint-label-placement.ts) stays the corner chooser. The component and the pane helper change around it.

## No jump on the first paint

Labels currently draw once with a width guess and a frame of `{ width: 0, height: 0 }` (the edge check is skipped), then snap when `afterEveryRender` and the `ResizeObserver` in [keypoint-container.component.ts](lightning-pose-app/web_ui/src/app/keypoint-container/keypoint-container.component.ts) report real numbers.

Keep each `.keypoint-label` at `visibility: hidden` until the frame `offsetWidth` and `offsetHeight` are both non-zero and that label has a measurement. Hidden labels still have layout, so they can be measured. They appear once, already in the corner they will keep.

Skip the DOM walk unless the font size or the set of label texts changed. Pointer moves do not remeasure.

## Place the ink, not the em box

`offsetWidth` is the em box. The letters sit inside it, and the 2px stroke (`paint-order: stroke fill`) paints about 1px outside the fill. That is why a larger font looks too far from the marker on one corner and overlaps it on another.

After render, for each visible label, compare the span box with a `Range` around its text. Divide the difference by the same scale (`rect.width / offsetWidth`) so the ancestor zoom does not leak into the numbers. That yields the ink inset inside the span.

Expand that ink by 1px on every side and pass that box to `placeKeypointLabels` as `w` and `h`. The tuck stays `markerSize / 1.15`. Shift the span by the inset so the ink, not the em box, sits on the returned `top` / `left`. The stroke's outer edge is the edge that clears markers and the frame.

Until a label has this measurement, leave it hidden rather than using the `0.6 * fontSize * length` guess.

## Clamp panes without `_internalSize`

In angular-split, `maxSize` is ignored when the `size` input is already larger (`normalizeMaxSize` returns Infinity), and a drag writes `_internalSize` without updating `size`. [split-pane-limit.ts](lightning-pose-app/web_ui/src/app/split-pane-limit.ts) papers over both by writing that private signal.

Stop writing `_internalSize`. `clampSplitPane` already receives the size signal. Also pass the pane's `clientWidth`. Set the size signal to the limit whenever the signal or the live width is over the limit. Setting `size` refreshes the linked signal, which is what pulls a dragged pane back. If the signal is already equal to the limit but the live width is still over it, set the signal one pixel away and then back to the limit in the same turn so the linked signal actually recomputes. Set `max` only after `size` is within it.

Move the playback-bar sum out of [viewer-page.component.ts](lightning-pose-app/web_ui/src/app/viewer/viewer-page/viewer-page.component.ts) into a pure function next to `clampSplitPane`: padding, plus each gap, plus each item's width, with the seek item replaced by 96. The component still reads the DOM and calls that function.

## Tests and changelog

Extend [keypoint-label-placement.spec.ts](lightning-pose-app/web_ui/src/app/keypoint-container/keypoint-label-placement.spec.ts) so a box that is the ink-plus-stroke size keeps its near edge on the tuck.

Add `split-pane-limit.spec.ts`: a pane already under the limit stays there; one over the limit becomes the floored limit; the limit is never negative; the playback-bar sum uses 96 for the seek item and the measured widths for the rest.

Add one sentence to the keypoint-label bullet in [CHANGELOG.md](lightning-pose-app/CHANGELOG.md) under `### [2.4.2.3.dev0]`: names stay hidden until they can be placed, and the gap follows the letters rather than the em box.
