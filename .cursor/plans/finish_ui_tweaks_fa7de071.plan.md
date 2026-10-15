---
name: Finish UI tweaks
overview: Finish the branch with Viewer and Labeler layout tweaks, including toasts that sit above the playback bar, update the changelog, then commit and push. Do not open a pull request.
todos:
  - id: hide-views
    content: Hide the Viewer Views accordion on single-view projects
    status: completed
  - id: tile-header
    content: "Reorder the video tile header: info icon, view name when multiview, then file name"
    status: completed
  - id: image-box
    content: Give the Labeler image the same shadow box as a video tile
    status: completed
  - id: toast-above-controls
    content: On the Viewer, place toasts just above the video controls
    status: completed
  - id: docs-pr
    content: Update the changelog, then commit and push. Do not open a pull request.
    status: completed
isProject: false
---

# Finish UI tweaks

The branch `feature/ui-tweaks` already has the green buttons, resizable panels, view options, sharp markers, keypoint label placement, pane limits, and the blank-sidecar save fix. Nothing in that set needs another code change. A few layout tweaks are still missing, then the changelog, then commit and push. Do not open a pull request.

## Viewer

Single-view is the check already on the Viewer page: more than one camera name in project info ([`isMultiview`](lightning-pose-app/web_ui/src/app/viewer/viewer-page/viewer-page.component.ts)). Wrap the Views accordion in [`viewer-page.component.html`](lightning-pose-app/web_ui/src/app/viewer/viewer-page/viewer-page.component.html) (the `app-accordion-viewer-views` panel) in `@if (isMultiview())`. Keypoints and Models stay. The view checkboxes stay selected from startup, so hiding the list does not turn the video off.

The tile header in [`viewer-center-panel.component.html`](lightning-pose-app/web_ui/src/app/viewer/viewer-center-panel/viewer-center-panel.component.html) is the view id (`w.id`), then the info icon. Change the left side to: the info icon (still only when metadata is loaded), then the view name only when the project is multiview, then the video file name. The file name is the last segment of `sessionView.videoPath`, set on the widget when it is built. The close button stays on the right. A single-view tile often has the id `unknown`, so that name stays off.

Toasts are a fixed bar on `document.body` with DaisyUI `toast-bottom`, so they cover the playback bar. While the Viewer is open, measure [`app-video-player-controls`](lightning-pose-app/web_ui/src/app/viewer/viewer-center-panel/viewer-center-panel.component.html) and set the toast container's bottom offset to that height plus a small gap. Clear the offset when the Viewer is destroyed so other screens keep toasts at the bottom of the window.

## Labeler

Video tiles sit in `shadow-lg shadow-black/20 bg-base-200` inside the zoomed content ([`video-tile.component.html`](lightning-pose-app/web_ui/src/app/video-player/video-tile/video-tile.component.html)). Put those classes on the image wrapper in [`image-label-widget.component.html`](lightning-pose-app/web_ui/src/app/labeler/image-label-widget/image-label-widget.component.html) so the box hugs the picture and zooms with it. The filmstrip already clips overflow, so the shadow shows on the main image.

## Docs and commit

Add short changelog bullets under `### [2.4.2.3.dev0]` for the hidden Views list, the tile header, the labeled-image box, and Viewer toasts sitting above the playback bar. No new spec: this is layout.

Commit the working tree on `feature/ui-tweaks` (do not squash the two commits already on the branch) and push. Do not open a pull request.
