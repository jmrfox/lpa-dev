# LPA Viewer go to frame / time

Let researchers type a frame index or a time on the Viewer transport bar and jump there.

UI-only. Same seek path as frame-step (`seekToFrame`, published on `seeked`).

## UI

Replace the read-only frame and current-time readouts with compact monospace fields:

- Frame: `f` plus an input showing the integer index. Tooltip `Frame`. Select-all on focus.
- Time: editable current time, then read-only ` / {duration} s`. Tooltip `Time` on the current-time field. Duration stays display-only. Two decimal places, same as today.

`type="text"` with `inputmode="numeric"` / `decimal` (no number spinners). Disabled when there is no video.

Commit on Enter or blur. Escape reverts the draft and blurs. While a field is focused, playback does not overwrite the draft. Viewer shortcuts already ignore text inputs, so arrows move the caret.

## Parsing

`TIME_DISPLAY_DECIMALS = 2` (0.01 s). If the display precision changes, rounding follows it.

- **Frame:** `Math.floor`, then clamp to `[0, lastFrame]`. Empty or non-numeric reverts; no seek.
- **Time:** parse seconds, round to `TIME_DISPLAY_DECIMALS`, clamp to `[0, lastFrame / fps]`, then `seekToFrame(round(time * fps))`. Empty or non-numeric reverts; no seek.

Seeking pauses playback.

## Out of scope

- Editing the duration.
- Labeler frame jump (different widget).
