---
name: Locate frame in Viewer
overview: Add a Labeler button under Revert changes that opens the Viewer on the video session and frame index encoded in the current labeled image.
todos:
  - id: parse-target
    content: Parse a label frame key into a Viewer session key and frame index
    status: completed
  - id: locate-button
    content: Add Locate in Viewer under Revert changes and navigate when a session matches
    status: completed
  - id: viewer-seek
    content: Seek the Viewer to the frame query after the session is ready
    status: completed
  - id: test-changelog
    content: Cover the parse in one spec, and note it in the changelog and feature plan
    status: completed
isProject: false
---

# Locate the current frame in the Viewer

The Labeler frame key is the image path with the view name already replaced by `*` (for example `labeled-data/180609_005/img082941.png` or `labeled-data/180605_000_*/img00003983.jpg`). The parent directory is the Viewer session key, and the digits in `img<digits>` are the zero-based frame index. The Viewer route is `/project/:projectKey/viewer/:sessionKey` and does not take a frame today; playback starts at 0 after ffprobe sets duration and fps in [`viewer-center-panel.component.ts`](lightning-pose-app/web_ui/src/app/viewer/viewer-center-panel/viewer-center-panel.component.ts).

## Button

In [`labeler-center-panel.component.html`](lightning-pose-app/web_ui/src/app/labeler/labeler-center-panel/labeler-center-panel.component.html), under **Revert changes**, add **Locate in Viewer** with the same full-width primary button classes. It is shown only when a frame is open. If the image name is not `img` plus digits, the button is disabled.

On click, load sessions and match `session.key` to that directory. If none matches, show a toast and stay on the Labeler. Otherwise navigate to `/project/<key>/viewer/<sessionKey>` with query param `frame` set to the index. `withComponentInputBinding` already maps that query param onto a component input.

## Viewer seek

- Parse the frame key in a small helper, `viewerTargetForLabelFrame`, next to the Labeler. It returns `{ sessionKey, frame }` or null.
- Add a `frame` input on [`viewer-page.component.ts`](lightning-pose-app/web_ui/src/app/viewer/viewer-page/viewer-page.component.ts) and pass the number into the center panel.
- After a session load has set fps and then duration, call `seekToFrame` when that input is set. `seekToFrame` no-ops until duration and fps are known, and if the `<video>` is not mounted yet it only stores the time.
- In the video tile `loadedmetadata` handler, if playback is paused, copy `VideoPlayerState` current time onto the element so the picture lands on that frame once metadata arrives.

## Test and notes

- One spec, `viewer-target.spec.ts`: a padded name (`img082941.png`) is frame 82941, a `*` session directory is kept, and a non-`img` name returns null.
- Changelog bullet under `### [2.4.2.3.dev0]`.
- Short feature note in [`feature_plans/lpa-locate-in-viewer.md`](lightning-pose-app/feature_plans/lpa-locate-in-viewer.md) naming that spec.