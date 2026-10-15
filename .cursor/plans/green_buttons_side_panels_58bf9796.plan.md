---
name: Green buttons side panels
overview: On `feature/ui-tweaks`, switch every blue button to the green button style, and give Labeler and Viewer a user-resizable right panel that holds the existing controls while the center stays the media and its bottom controls.
todos:
  - id: green-buttons
    content: Replace btn-info with btn-primary on every button
    status: completed
  - id: labeler-split
    content: Make the Labeler right controls a resizable split area
    status: completed
  - id: viewer-split
    content: Move Viewer accordions into a resizable right split area; keep videos and transport in the center
    status: completed
  - id: changelog
    content: Note the UI tweaks in CHANGELOG 2.4.2.3.dev0
    status: completed
isProject: false
---

# Green buttons and resizable right panels

Branch is `feature/ui-tweaks` from `main`. Blue buttons are DaisyUI `btn-info`. Green buttons are already `btn-primary` (New Project, Save).

## Buttons

Replace `btn-info` with `btn-primary` on every `btn` in `web_ui/src`. That covers Labeler actions (Save, Next, Load Calibration, and the rest), File Manager actions that are blue today, and dialog buttons that are blue today, including Cancel, Back, Close, and OK. Those will look the same green as Save. Red (`btn-error`) stays. Status text such as `text-info` stays.

The Discord link in [`app.component.html`](lightning-pose-app/web_ui/src/app/app.component.html) uses `btn-info` only until it has been seen. That pulse becomes green too.

## Labeler right panel

Today the page split is only left | center ([`labeler-page.component.html`](lightning-pose-app/web_ui/src/app/labeler/labeler-page.component.html)). The right column lives inside the center as a CSS grid (`grid-cols-[2fr_minmax(260px,_1fr)]` in [`labeler-center-panel.component.html`](lightning-pose-app/web_ui/src/app/labeler/labeler-center-panel/labeler-center-panel.component.html)), so it grows with the window but has no drag handle.

Turn that center component into a nested `as-split` (same `angular-split` the left pane already uses):

- Left area (`size="*"`): the frame image and the multiview filmstrip. Fill the area (`h-full`), not the current `h-[90vh]`.
- Right area (`size="320"`, `unit="pixel"`): the existing Keypoints, Multiview tools, view options, and frame actions, unchanged. The area scrolls vertically (`overflow-y-auto`). Buttons and lists already use `w-full`; keep them stretching to the dragged width (`min-w-0 w-full`).

Import `SplitComponent` and `SplitAreaComponent` on the center panel. Do not move the controls up to the page component; they depend on that component's state.

## Viewer right panel

Today one split area holds both the video and a fixed `w-60` column of accordions ([`viewer-page.component.html`](lightning-pose-app/web_ui/src/app/viewer/viewer-page/viewer-page.component.html)). The video tiles and the transport bar are already stacked in [`viewer-center-panel.component.html`](lightning-pose-app/web_ui/src/app/viewer/viewer-center-panel/viewer-center-panel.component.html) (tiles on top, `app-video-player-controls` at the bottom).

Add a third `as-split-area` on the existing page split:

- Left stays the sessions list (`size="280"`).
- Center (`size="*"`) is only `app-viewer-center-panel`: video tiles and the controls bar at the bottom.
- Right (`size="280"`, `unit="pixel"`) is the current accordion column (Views, models, likelihood, view options, extract frames). Drop `w-60`. The area is `h-full overflow-y-auto`, and each panel is full width of that area. Range sliders use `flex-1 min-w-0` so they grow and shrink with the drag handle.

## Check

No new unit test: this is color and layout. In the running app, confirm a blue Labeler button and a blue File Manager button are green, drag the Labeler and Viewer right gutters, and confirm Viewer videos stay in the center with the transport bar along the bottom of that center region.

Add a short `### [2.4.2.3.dev0]` note in [`CHANGELOG.md`](lightning-pose-app/CHANGELOG.md) on this branch. The bugfix branch already has its own unreleased section; this note only covers the button color and the two panels.
