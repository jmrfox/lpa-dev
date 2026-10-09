# LPA Viewer frame controls

Expand the Viewer transport bar so researchers can inspect pose predictions frame-by-frame, play at slower-than-real-time speeds, and drive playback from the keyboard.

UI-only. No backend, RPC, or on-disk format changes.

## Current state

The bar lives in `app-video-player-controls`, mounted at the bottom of `app-viewer-center-panel`. Left → right today:

1. Play / pause
2. Current time (`toFixed(5)` seconds)
3. Current frame (`Math.round(time * fps)`)
4. Time slider
5. Total duration (`Ns`)

Playback is owned by `VideoPlayerState` (`web_ui/src/app/video-player/video-player-state.ts`):

- `isPlaying` / `currentTime` BehaviorSubjects, plus `duration` and `fps` signals.
- Play starts every registered `<video>` and syncs `currentTime` from the primary player on animation frames.
- Seek only runs while paused (`onSeek`).
- There is **no** frame-step API, **no** `playbackRate`, and **no** keyboard handling.
- Controls are Viewer-only (not used by the labeler).

Frame index is already load-bearing: keypoints, likelihood tooltips, and “extract current frame” all read `currentFrameSignal`. Keep that 0-based `round(time * fps)` definition.

## Target control bar (left → right)

```
[ |< ] [ ‹ ] [ ▶/❚❚ ] [ › ] [ 1x ▾ ]  ———slider———  f 142   3.47 / 12.00 s  [⌨]
```

| Control | Role |
|---|---|
| Go to start | Seek to t = 0 |
| Previous frame | Pause (if needed), seek one frame back |
| Play / pause | Unchanged toggle |
| Next frame | Pause (if needed), seek one frame forward |
| Play speed | Compact button showing the current rate; menu opens **upward** |
| Slider | Unchanged range input (`min=0`, `max=duration`, `step=1/fps`) |
| Frame number | Integer frame index (read-only) |
| Time | `current / total` in seconds |
| Keyboard help | `keyboard` icon; hover lists all shortcuts |

Do not add a go-to-end **button**. End-of-video remains keyboard-only (`End`).

### Buttons

Icon-only, `btn btn-ghost btn-sm`, Material icons already used in the Viewer:

- Go to start: `skip_previous`
- Previous frame: `chevron_left`
- Play / pause: `play_arrow` / `pause` (existing)
- Next frame: `chevron_right`

Each control gets `aria-label` plus a short DaisyUI `tooltip` (name only, no shortcut list). Tooltips open upward (`tooltip-top`) and stack above the sessions pane (the split area must allow horizontal overflow; DaisyUI’s default tooltip `z-index: 2` is not enough).

A `keyboard` icon on the **far right** of the bar shows every shortcut in one hover tooltip (`tooltip-top tooltip-end`, HTML `tooltip-content` table).

Disable transport when there is no loaded session (`duration() === 0`), same as a useless slider today.

### Play speed menu

Rates (fractions of real time; nothing faster than 1x). Labels use `1/n`, not single-character fractions:

| Label | `HTMLMediaElement.playbackRate` |
|---|---|
| `1x` | `1` |
| `1/2x` | `0.5` |
| `1/4x` | `0.25` |
| `1/8x` | `0.125` |
| `1/16x` | `0.0625` |

Default: `1x`. Not persisted (reset with `VideoPlayerState.reset()`). Changing speed while playing applies immediately.

Implementation: existing `app-dropdown` with host class `dropdown-top` (already supported). Do **not** use `app-select` — it always opens downward and is too large for a dense bar. Trigger is a compact button whose label is the current rate (`1x`). Menu is a short `ul.menu` with the five options; selecting one closes the popover.

### Time and frame display

Replace the three separate numeric spans with:

- **Frame:** `f {{ currentFrame() }}` (or equivalent), monospace, tooltip `Frame`.
- **Time:** `{{ current }} / {{ total }} s`, both with **two** decimal places (e.g. `3.47 / 12.00 s`). Drop the current five-decimal current-time field; it is too wide for the bar and finer than a 30 fps frame (~33 ms).

Keep `font-family: monospace` and a stable min-width so the slider does not jitter as digits change.

### Frame-step / go-to-start behavior

These are inspection controls, not YouTube-style continuous transport:

- **Previous / next frame:** if playing, pause first, then seek. Time = `clamp(frame + delta, 0, lastFrame) / fps`.
  - Button / `←` `→`: `delta = ±1`.
  - Keyboard `Shift+←` / `Shift+→` **or Shift+click** on the chevrons: `delta = ±10`. No extra buttons.
- **Go to start:** pause, then seek to `0`.
- **Go to end (`End` key):** pause, then seek to `lastFrame / fps`.
- `lastFrame` = `max(0, round(duration * fps) - 1)` so we do not land on a phantom frame at `t === duration`.
- Clamp all seeks to `[0, duration]` (a 10-frame jump near either end just stops at the first or last frame).
- **Display sync:** keypoints and the frame readout update when a video `seeked` fires for that frame. Key hold still coalesces the *next* seek to the latest requested frame, but the overlay is published for each completed seek so it does not sit on an old frame while the picture has already moved. Slider scrub stays immediate.

If the video is not all-intra, existing Viewer warning still applies; this feature does not try to make GOP videos frame-accurate.

## Keyboard

Listen on `document:keydown` from `VideoPlayerControlsComponent` (via the component `host` object — do not add `@HostListener`). The controls component is only mounted on the Viewer page, so shortcuts are naturally scoped there.

### Map

| Key | Action |
|---|---|
| `Space` | Play / pause |
| `ArrowLeft` | Previous frame |
| `ArrowRight` | Next frame |
| `Shift+ArrowLeft` | Jump back 10 frames |
| `Shift+ArrowRight` | Jump forward 10 frames |
| `Home` | Go to start |
| `End` | Go to last frame |
| `-` or Numpad `-` | Slower (`1x` → `1/2x` → `1/4x` → `1/8x` → `1/16x`, clamp, no wrap) |
| `=` / `+` or Numpad `+` | Faster (`1/16x` → … → `1x`, clamp, no wrap) |
| `a` | Add current frame to the labeling queue |

`=` is the unshifted sibling of `-` on US keyboards; `+` is the same key with Shift. Handle both `Equal` and `+`.

### When **not** to handle

Ignore the event (do not `preventDefault`) when any of these is true:

1. `ctrl` / `meta` / `alt` is down (leave browser / OS chords alone). Shift is allowed for `+` and for `Shift+Arrow` 10-frame jumps.
2. A `<dialog open>` is showing (modals, extract-frames errors, upload).
3. Focus is in an editable field: text `input`, `textarea`, `select`, or `contenteditable`.
4. **Arrows / Home / End** and the target is a right-pane `input[type=range]` (tile size, opacity, etc.). The time slider blurs on mouseup so it does not steal those keys after a scrub.

Space always play/pauses on the Viewer (including after clicking a transport button). Do not leave Space to native button activation.

When we do handle a key: `preventDefault()` (especially Space, which otherwise scrolls the page).

## State and files

Keep logic in `VideoPlayerState` so tiles stay dumb and the controls stay thin.

### `video-player-state.ts`

Add:

- `playbackRate` signal, default `1`.
- `stepFrame(delta: number)` (`±1` from buttons/arrows, `±10` from `Shift+Arrow`), `seekToStart()`, `seekToEnd()`, `setPlaybackRate(rate)`, `nudgePlaybackRate(direction: -1 | 1)`, `toggleIsPlaying()`.
- Apply `video.playbackRate` to every registered element when the rate changes, when a player registers, and in `onPlay` (in case the element was recreated).
- `reset()` also restores `playbackRate` to `1` and pauses.

Seek helpers should set `isPlaying` to false when stepping / jumping, then push `currentTime` so the existing paused `onSeek` effect updates all `<video>` elements.

### `video-player-controls`

Rewrite the template to the new order. Wire buttons to the state methods. Add the upward speed dropdown. Add the keydown host handler.

### `video-tile`

No playback API changes required if `VideoPlayerState` writes `el.playbackRate` on the native element. Optional: set `playbackRate` in `onLoadedMetadata` as a backstop if the element resets.

## Tests

There are no video-player unit tests today. Add a focused spec rather than a full Playwright suite:

- `video-player-state.spec.ts`: step forward/back clamps at 0 and last frame; `stepFrame(10)` / `stepFrame(-10)` clamp at the ends; go to start/end; rate nudge clamps at 1/16 and 1; `reset()` restores 1x and time 0.
- `video-player-controls.component.spec.ts` (or a small keyboard helper spec): Space toggles play; Left/Right step by 1; Shift+Left/Right step by 10; keys ignored inside a text input and when a button is focused (Space).

Manual (Studio, fused-mouse smoke project):

- Layout at the bottom of the Viewer with a session loaded; speed menu opens **up**, not off-screen.
- Multi-view session: frame step and slow-mo stay in sync across tiles.
- Play at 1/16x through 1x; keypoints still track the frame index.
- Keyboard works after clicking the video area; Space does not scroll; Space on “Add current frame” still clicks that button; Shift+Arrow jumps 10 frames and clamps at the ends.
- Slider scrub still pauses and seeks.

Frontend check: `npx ng lint` and targeted `ng test` for the new specs.

## Out of scope

- Speeds faster than 1x, reverse play, loop.
- Go-to-end button.
- Editable frame / time jump field. Done in [lpa-viewer-goto-frame-time.md](lpa-viewer-goto-frame-time.md).
- Persisting speed in `localStorage`.
- Labeler frame navigation (different widget).
- Fixing frame accuracy on non-all-intra videos.

## Follow-ups (not this feature)

- Type a frame number and jump. Done in [lpa-viewer-goto-frame-time.md](lpa-viewer-goto-frame-time.md).
