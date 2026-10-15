---
name: Wrap up UI tweaks
overview: The branch matches the requested UI work. Ellipsize clipped side-list names, and make the Labeler Keypoints and Multiview tools panels collapsible accordions.
todos:
  - id: ellipsis-names
    content: Ellipsize Labeler frame names and Viewer session names, with the full path on hover.
    status: completed
  - id: labeler-accordions
    content: Make Labeler Keypoints and Multiview tools collapsible accordions, with the help icon beside the Multiview tools title.
    status: completed
isProject: false
---

# Wrap up UI tweaks

## Review

`feature/ui-tweaks` has three pushed commits (`b8d143c`, `e761b17`, `c32a938`). The working tree, not yet committed, holds the follow-ups: Labeler tile header (info, view name, file name, close), aspect-ratio tile height, square bottom corners, 1200px size cap, and vertical-only side panels.

That later work matches what was asked. The Labeler close control returns to the frame list for the same label file (`handleCloseFrame` in [labeler-page.component.ts](lightning-pose-app/web_ui/src/app/labeler/labeler-page.component.ts); covered by `labeler-page.component.spec.ts`). Tile height uses [fitted-media-height.ts](lightning-pose-app/web_ui/src/app/fitted-media-height.ts) from video metadata in the Viewer and from the loaded image in the Labeler. The filmstrip stays 120×120 via `!h-[120px]`. The center frame and the filmstrip still scroll sideways on purpose.

No code fix is needed for the label-size slider max (10 in the Labeler, 8 in the Viewer). That difference was already there.

## Docs

[CHANGELOG.md](lightning-pose-app/CHANGELOG.md) under `### [2.4.2.3.dev0]` already describes the working tree, including replacing the pushed sentence that said the frame had the same shadow as a video tile. README, DEV, and AGENTS do not describe these screens. `BUGS.md` (studio root, not in this repo) already records the blank-sidecar save bug. Add one changelog bullet for the new accordions. No other doc edits.

## Cleanup

Side lists still use `w-fit` and `text-nowrap`, so hiding the horizontal bar cuts the name off with no ellipsis.

- Labeler frame lists in [labeler-page.component.html](lightning-pose-app/web_ui/src/app/labeler/labeler-page.component.html): make each row `min-w-0` and `truncate`, and put the full path on `title`.
- Viewer session list in [viewer-sessions-panel.component.html](lightning-pose-app/web_ui/src/app/viewer/viewer-left-panel/viewer-sessions-panel.component.html): same treatment for the session path.

Leave the other changelog bullets as they are. Do not commit or push.

## Labeler accordions

In [labeler-center-panel.component.html](lightning-pose-app/web_ui/src/app/labeler/labeler-center-panel/labeler-center-panel.component.html), turn the Keypoints panel and the Multiview tools panel into the same checkbox accordion as View options (`.app-accordion-toggle`, `.app-accordion-title`, `.app-accordion-icon`, `.app-accordion-content` in [styles.css](lightning-pose-app/web_ui/src/styles.css)). Use ids `app-accordion-keypoints` and `app-accordion-multiview`. Start both **open** (`checked`) so the lists and tools stay visible until collapsed. Keep the keypoint list’s `max-h-100` scroll inside the accordion body.

Multiview tools header becomes `Multiview tools`, then the existing help button, then the `+`/`-` on the right. The help button stays a dialog opener (`multiview_info.showModal()`), placed in the title group rather than `justify-between` against the title. Stop that click from also toggling the accordion. Leave the dialog outside the collapsing body so help still opens when the panel is closed.
