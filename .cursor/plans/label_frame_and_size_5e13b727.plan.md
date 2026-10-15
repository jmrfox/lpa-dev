---
name: Label frame and size
overview: Keep keypoint names inside the frame, use the lower-right whenever it fits, and place each name from its real size so a larger font stays the same distance from its marker. Put the label-size slider under the labels toggle and hide it when labels are off.
todos:
  - id: placement-rules
    content: Prefer lower-right when it fits, reject corners outside the frame, and place from each label's real width and height
    status: completed
  - id: wire-size-frame
    content: Set line-height 1, measure label boxes, and pass the container frame size into the placer
    status: completed
  - id: spec-changelog
    content: Update the placement spec and the changelog bullet
    status: completed
  - id: label-size-slider
    content: Move the keypoint label size slider under the labels toggle in the Labeler and Viewer, and hide it when labels are off
    status: completed
isProject: false
---

# Label frame, default corner, and size

The placer in [keypoint-label-placement.ts](lightning-pose-app/web_ui/src/app/keypoint-container/keypoint-label-placement.ts) guesses each box as `fontSize` tall and `0.6 * fontSize * text.length` wide, and it keeps the previous corner before it considers the lower-right. The label span inherits Tailwind’s `line-height: 1.5`, so the real line box is taller than that guess. At a small font the error is a couple of pixels. At a large font the lower-right letters sit in the extra leading (too far), and an upper corner hangs into the marker (too close or overlapping). A wrong width does the same on the left corners.

## Placement rules

Change `placeKeypointLabels` so each label carries its own `w` and `h`. Drop the font-size estimate from the function.

- A corner fits only when its box misses other names and other markers, and lies inside the frame (`0 … frameWidth`, `0 … frameHeight` in keypoint coordinates). A missing frame (width or height still 0) skips the edge check.
- If the lower-right fits, use it, even when the label was in another corner last time.
- Otherwise keep the previous corner when it still fits, so a small move does not shuffle the other three corners.
- Otherwise take the first of upper-right, lower-left, upper-left that fits. If none fit, take the corner with the smallest overlap plus the least area outside the frame.
- The near edge of the box stays at today’s tuck (`markerSize / 1.15` from the circle’s top-left, opposite sides mirrored). Only the far edges move when `w` or `h` changes, so a larger name grows away from the marker instead of drifting toward it or off it.

## Wiring

In [keypoint-container.component.html](lightning-pose-app/web_ui/src/app/keypoint-container/keypoint-container.component.html), set `.keypoint-label { line-height: 1 }` so the line box matches the font size.

In [keypoint-container.component.ts](lightning-pose-app/web_ui/src/app/keypoint-container/keypoint-container.component.ts):

- Observe `#containerDiv` with a `ResizeObserver` and store `offsetWidth` / `offsetHeight`. Those are the image or video frame in the same unscaled coordinates as the keypoints. The container already clips with `overflow-hidden`.
- After render, read each visible `.keypoint-label`’s `offsetWidth` and `offsetHeight` and store them. Update only when a size changes, so this does not run on pointer moves. Until the first measurement, use height = font size and width = `0.6 * fontSize * text.length`.
- Pass the frame size and those boxes into the placer from the existing `labelOffsets` computed.

## Test and changelog

Update [keypoint-label-placement.spec.ts](lightning-pose-app/web_ui/src/app/keypoint-container/keypoint-label-placement.spec.ts), still one spec: separated names stay lower-right; a nearby name leaves the lower-right and keeps that other corner while the lower-right is still blocked; once the lower-right is free again, the name returns there; a name in the bottom-right of the frame uses the upper-left and stays inside; a wider and taller name keeps the same inner edges and grows outward.

Note the frame and size behavior on the existing keypoint-label bullet in [CHANGELOG.md](lightning-pose-app/CHANGELOG.md) under `### [2.4.2.3.dev0]`.

## Label size slider

In the Labeler and Viewer right-hand panels, **Keypoint label size** currently sits above the **Keypoint labels** toggle. Move the slider (and the Viewer’s `px` readout) to just below that toggle.

Show it only when labels are on, the same way [skeleton-view-options.component.ts](lightning-pose-app/web_ui/src/app/components/skeleton-view-options/skeleton-view-options.component.ts) wraps bone thickness and opacity in `@if (showSkeleton() && !invalid())`:

- [labeler-center-panel.component.html](lightning-pose-app/web_ui/src/app/labeler/labeler-center-panel/labeler-center-panel.component.html): `@if (viewOptions.enableKeypointLabels())` around the label-size block.
- [viewer-page.component.html](lightning-pose-app/web_ui/src/app/viewer/viewer-page/viewer-page.component.html): the same `@if`.

Leave the slider’s range, reset button, and readout as they are. Mention the order on the view-options changelog bullet. No new spec; this is the same show/hide the skeleton options already use, and [keypoint-label-placement.spec.ts](lightning-pose-app/web_ui/src/app/keypoint-container/keypoint-label-placement.spec.ts) stays the test for placement.
