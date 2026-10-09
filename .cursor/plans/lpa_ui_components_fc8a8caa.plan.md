---
name: LPA UI components
overview: Document a shared UI standard for Lightning Pose App (DaisyUI classes plus Storybook stories for reusable widgets), and bring the Viewer video controls onto that standard where they still use custom controls.
todos:
  - id: contributing
    content: Add a UI components section to lightning-pose-app/CONTRIBUTING.md
    status: completed
  - id: cursor-rule
    content: Add .cursor/rules/lpa-ui-components.mdc scoped to web_ui templates and styles
    status: completed
  - id: video-controls
    content: Use DaisyUI range (and input if it stays compact) on video controls; add a Storybook story
    status: completed
  - id: verify
    content: Check the Viewer control bar and the new story in the browser
    status: completed
isProject: false
---

# LPA Storybook and DaisyUI workflow

Storybook and DaisyUI are already installed in the app. The gap is the written standard, and a few Viewer controls that bypass DaisyUI.

## What is already in place

- DaisyUI 5 is the theme in [`lightning-pose-app/web_ui/src/styles.css`](lightning-pose-app/web_ui/src/styles.css) (`dim` default). Storybook loads that stylesheet through the Angular build target in [`lightning-pose-app/web_ui/angular.json`](lightning-pose-app/web_ui/angular.json).
- Reusable widgets live in [`lightning-pose-app/web_ui/src/app/components/`](lightning-pose-app/web_ui/src/app/components/) and already have stories (dropdown, alert dialog, path inputs, and others). Run with `cd web_ui && npm run storybook` (port 6006).
- Viewer transport buttons, tooltips, and the speed menu already use DaisyUI (`btn btn-ghost`, `tooltip`, `menu`) and the shared [`dropdown`](lightning-pose-app/web_ui/src/app/components/dropdown/dropdown.component.ts). The seek bar (`timestamp-slider`) and frame/time fields (`jump-field`) in [`video-player-controls.component.html`](lightning-pose-app/web_ui/src/app/video-player/video-player-controls/video-player-controls.component.html) are custom CSS, and that component has no story.

Do not wrap every Daisy button in a new Angular component. The existing pattern is: DaisyUI classes in templates for buttons, inputs, menus, and tooltips; an Angular component under `components/` only when the widget has reused behavior (dropdown, dialog, path field).

## Contributor docs

Add a **UI components** section to [`lightning-pose-app/CONTRIBUTING.md`](lightning-pose-app/CONTRIBUTING.md) (not the Lightning Pose library guide):

- Use DaisyUI component classes from the app theme before custom CSS.
- Put a widget in `web_ui/src/app/components/` when it is reused or has its own behavior. Keep feature-only UI next to the feature (for example `video-player/`).
- Add a `*.stories.ts` next to each component under `components/`, and for a distinct feature surface when it is practical to render it alone.
- How to start Storybook (`npm run storybook` from `web_ui`, Node 26).

## Cursor rule

Add [`.cursor/rules/lpa-ui-components.mdc`](.cursor/rules/lpa-ui-components.mdc) with `alwaysApply: false` and globs for `lightning-pose-app/web_ui/**/*.{html,css,ts}`. Same standard as the contributing section, aimed at future UI edits in this studio: DaisyUI first, shared widgets in `components/` with a story, no one-off button wrappers.

## Video controls subproject

In [`video-player-controls`](lightning-pose-app/web_ui/src/app/video-player/video-player-controls/video-player-controls.component.html):

- Restyle the seek `<input type="range">` with DaisyUI `range` (size that matches the bar). Drop `.timestamp-slider` rules that only duplicated range styling.
- Restyle the frame and time fields with DaisyUI `input` only if they stay compact, monospace, and inline. If Daisy’s input padding blows up the bar, keep the small custom fields and say so in the contributing note as an allowed exception.
- Leave play/step/speed/shortcut buttons on the existing Daisy classes and `app-dropdown`.
- Add `video-player-controls.stories.ts` that provides `VideoPlayerState` with a short fake duration so play, frame step, speed, and seek can be tried without a video file.

Verify in the running app (Viewer video bar: play, step, shift-step, seek, frame/time jump, speed menu, shortcut tooltip) and in Storybook. This is app code, so it belongs on a short-lived branch from `origin/main`. Do not commit or open a PR unless asked.
