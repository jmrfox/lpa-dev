# LPA Labeler temporal context controls

paninski-lab/lightning-pose-app#148, on branch `fix/labeler-context-frames` together with the #161 fix (context slots built the way LP builds them). PR: paninski-lab/lightning-pose-app#167.

UI-only. No backend, RPC, or on-disk format changes.

## Before

**Temporal context** in View options had only **Show** / **Stop**. Show cycled the five context frames (−2 … +2 and back) every 300 ms, and keypoints were hidden the whole time. You could not pause on a frame or step through them.

## Now

```
[ ‹ ] [ ▶/❚❚ ] [ › ]   ● ● ● ● ●
Showing: current
```

| Control | Behavior |
|---|---|
| Previous / Next context frame | Pause, move one slot. Disabled at −2 / +2. |
| Play / Pause | Plays −2 … +2 and back from the visible slot; Pause holds the visible slot. |
| Dots | Pause on that slot. `aria-pressed` marks the visible one. |
| Label | `Showing: −2`, `−1`, `current`, `+1`, `+2`. When the slot shows a substitute: `Showing: current in place of +2 (not found)`, `Showing: −1 in place of −2 (before the video starts)`. |

- Keypoints show when paused on the current frame (slot 2) and are hidden while playing or on another slot, since they belong to the current frame only.
- Opening another frame returns to the current frame, paused. The widget's list of failed images is cleared when the frame changes, so reopening a frame tries its images again.
- The controls are disabled, with a tip on hover, in two cases. Playback stops and the current frame is shown.
  - The file name has no frame number: "The image file name has no frame number."
  - The frame's own image fails to load (missing, or a file type the files route refuses): "This frame's image could not be loaded." Checked first, so it is not reported as missing context.
  - None of the frames around the current one load (every slot except the current frame fails), for example frames imported without their neighbors: "Context frames were not found." The widget reports this as `contextFramesMissing`; the center panel reads it from the primary widget. The end of a video is not this case, since the earlier frames still load.
- Near the edges of a video a slot shows the frame LP uses: frame 0 for slots before the start, the current frame for a frame that does not exist (past the end). See the #161 entry in `BUGS.md`.

## Code

- `labeler/temporal-context.ts`: `contextImgPaths` (#161), plus `stepContextSlot`, `playContextSlot`, `CONTEXT_SLOT_LABELS`.
- `labeler/labeler-view-options.service.ts`: `isPlayingTemporalContext` and `temporalContextIndex` signals; `isShowingTemporalContext` is now computed (playing, or not on slot 2). Methods `playTemporalContext`, `pauseTemporalContext`, `toggleTemporalContextPlayback`, `stepTemporalContext`, `jumpToTemporalContextSlot`, `resetTemporalContext`.
- `labeler/image-label-widget/`: `contextFramesMissing` (computed from the images that failed to load).
- `labeler/labeler-center-panel/`: the controls and `temporalContextUnavailableReason`; `ngOnChanges` resets context on a new frame, and an effect resets it when context becomes unavailable.

## Tests

- `temporal-context.spec.ts` "context slot stepping": step stops at the ends; play runs `[0, 1, 2, 3, 4, 3, 2, 1, 0, 1]`; play continues from the paused slot; slot labels.
- `labeler-center-panel.component.spec.ts` "temporal context": opens on the current frame; Previous / Next step and stop at the ends; clicking a dot jumps; Play advances and Pause holds (fake clock); a new frame returns to the current frame; no frame number, or `contextFramesMissing`, disables every control and sets the matching tip; playback stops when the context frames are not found.
- `image-label-widget.component.spec.ts`: keypoints shown only when paused on the current frame; the chosen slot's image is shown; past the end of the video, slots 3 and 4 show the current frame; `contextFramesMissing` is true only when every frame but the current one fails (frame 42, frame 0), and false at the end of a video or with no frame number.

## Not done

- Image formats beyond `.png` / `.jpg`, a Labeler refresh button, and frame-name checks are separate issues.

- No keyboard shortcuts for context stepping.
