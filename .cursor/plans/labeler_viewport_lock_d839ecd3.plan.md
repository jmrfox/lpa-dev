---
name: Labeler viewport lock
overview: Keep the Labeler inside the viewport the same way the Viewer already does, so a large frame or a long right-hand panel scrolls in place instead of stretching the page.
todos:
  - id: labeler-host
    content: "Add min-height: 0 and overflow: hidden to the Labeler page host"
    status: completed
  - id: split-areas
    content: "Set min-height: 0 on app-labeler split areas and the center-panel host"
    status: completed
  - id: verify
    content: Confirm center and right-panel scroll in the browser, and note it in CHANGELOG.md
    status: completed
isProject: false
---

# Labeler viewport lock

The Viewer already stops its split from growing with its content. The Labeler does not, and the new image-size slider makes that visible: a 900px frame or a long View Options list can stretch the page.

## Cause

[`labeler-page.component.html`](lightning-pose-app/web_ui/src/app/labeler/labeler-page.component.html) host is only `flex-grow: 1; display: flex`. A flex item’s default minimum height is the height of its content, so `h-full` on the nested split never becomes a real cap.

The Viewer host in [`viewer-page.component.html`](lightning-pose-app/web_ui/src/app/viewer/viewer-page/viewer-page.component.html) already sets `min-height: 0` and `overflow: hidden`. [`styles.css`](lightning-pose-app/web_ui/src/styles.css) sets `min-height: 0` on `app-viewer as-split-area`. There is no matching rule for `app-labeler`.

The center panel used to be capped with `h-[90vh]`. It is now `h-full` inside a nested `as-split` ([`labeler-center-panel.component.html`](lightning-pose-app/web_ui/src/app/labeler/labeler-center-panel/labeler-center-panel.component.html)).

## Changes

- In the Labeler page host style, add `min-height: 0` and `overflow: hidden`, matching the Viewer host.
- In [`styles.css`](lightning-pose-app/web_ui/src/styles.css), add `app-labeler as-split-area { min-height: 0; }` next to the Viewer rule. That covers both the page split and the center-panel split, since both areas are inside `app-labeler`.
- In [`labeler-center-panel.component.css`](lightning-pose-app/web_ui/src/app/labeler/labeler-center-panel/labeler-center-panel.component.css), add `min-height: 0` to `:host` so the nested panel can shrink inside the page split area. It already has `height: 100%` and `min-width: 0`.

No change to image-size storage, slider labels, or button colors. Those match the Viewer.

## Check

In the Labeler, set Image size to 900. The frame scrolls inside the center column and the page itself does not grow. Open View Options so the right panel is taller than the screen. That panel scrolls, and the left frame list stays put.

Add one short clause to the existing Labeler bullet in [`CHANGELOG.md`](lightning-pose-app/CHANGELOG.md) under `[2.4.2.3.dev0]`: a large frame or a long side panel scrolls in place.
