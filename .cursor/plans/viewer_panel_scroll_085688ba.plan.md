---
name: Viewer panel scroll
overview: Keep the Viewer playback bar at the bottom of the center column, and let the right-hand panel scroll inside the viewport the way the Labeler panel already does.
todos:
  - id: viewer-scroll
    content: Constrain the Viewer split to the viewport and scroll only the right panel
    status: completed
  - id: center-tooltips
    content: Keep transport tooltips overflowing the center area only
    status: completed
isProject: false
---

# Viewer right panel scroll and playback bar

The right panel does not scroll, and the playback bar sits under that panel, because the right split area is allowed to grow the page.

[`styles.css`](lightning-pose-app/web_ui/src/styles.css) sets `overflow: visible` on `app-viewer as-split-area:last-of-type`. That used to be the center column, so transport tooltips could paint over the sessions list. After the three-column split, `:last-of-type` is the right panel. A grid item with visible overflow uses its content as a minimum height, so the accordions stretch the whole Viewer past the viewport. The center column stretches with it, and [`app-video-player-controls`](lightning-pose-app/web_ui/src/app/viewer/viewer-center-panel/viewer-center-panel.component.html) ends up at the bottom of that tall column, under the right-hand controls.

The Labeler right panel scrolls because it lives in a nested split whose height is already limited to the page.

## Changes

- In [`viewer-page.component.html`](lightning-pose-app/web_ui/src/app/viewer/viewer-page/viewer-page.component.html), set the host to `min-height: 0` and `overflow: hidden` so the split stays inside `main` and cannot grow with the accordions.
- In [`styles.css`](lightning-pose-app/web_ui/src/styles.css), stop applying `overflow: visible` to the last split area. Give every Viewer split area `min-height: 0` so content cannot stretch the row. Keep `overflow: visible` only on the center area (a class on that `as-split-area`) so the playback tooltips can still extend upward and toward the sessions list.
- Leave the right area on the split's normal overflow. Its inner wrapper stays `h-full overflow-y-auto`, so a vertical scrollbar appears when Views, models, and the other sections are taller than the screen.
- Do not move the playback bar. It already follows the video tiles inside the center panel. Once that panel is viewport height, the bar stays at the bottom of the center column no matter how tall the right panel's contents are.
