---
name: Standard button styles
overview: "Standardize text buttons with the soft styles already in the app: primary for important actions, info for on-screen actions, and error for delete. In-page selectors use the existing dark theme colors. No new palette."
todos:
  - id: css-classes
    content: Add only the choice-selector rule, using the existing base colors. Important, normal, and delete stay Daisy soft classes.
    status: completed
  - id: sweep-buttons
    content: Apply btn-soft btn-primary, btn-info, and btn-error to text buttons, and btn-choice to the settings and create-model page lists.
    status: completed
  - id: note-and-check
    content: Write the feature-plan note and check the labeler, File Manager, and settings selector on mms1.
    status: completed
isProject: false
---

# Standard button styles

Use the soft buttons already in the theme. Do not add new greens, blues, or reds. DaisyUI's hover stays as it is: a dark tint with light colored text at rest, and on hover a light fill with dark text.

- **Important:** `btn btn-soft btn-primary`, the same classes as **Add more frames from a session** in [labeler-page.component.html](lightning-pose-app/web_ui/src/app/labeler/labeler-page.component.html). Theme primary is the light green. Use this when a text button opens another screen, opens a dialog, or writes data or files.
- **Normal:** `btn btn-soft btn-info`. Theme info is the light blue already used by the Multiview tools question-mark button. Same soft hover as primary. Use this when a text button only acts on the current screen. This replaces one-off `bg-sky-700` fills on those buttons. Frame-list highlights stay `bg-sky-700`.
- **Delete:** `btn btn-soft btn-error`, the same classes as the labeler trash button in [labeler-center-panel.component.html](lightning-pose-app/web_ui/src/app/labeler/labeler-center-panel/labeler-center-panel.component.html). Dark red fill and red text at rest; they swap on hover. The icon-only trash button already has this and stays as it is.
- **Choice:** settings and create-model page lists. Dark background, light text, and a darker background while `menu-active`. Use the existing `base-300` and `base-100` colors in [styles.css](lightning-pose-app/web_ui/src/styles.css). No new hue.

Size classes (`btn-sm`, `w-full`) stay on each button. Disabled buttons keep Daisy's disabled state. Do not override it with a custom mix.

## What changes

- **Labeler:** **Save** and **Save and next** become important. **Next** and **Revert changes** become normal. **Load Calibration**, **Add more frames**, and the new-label-file button are important. **Project keypoints**, **Show**, and **Stop** are normal. Dialog **Cancel** and **Close** are normal. A confirm that writes is important. A confirm that deletes is delete.
- **File Manager:** **Load**, **Add Video**, **Rename**, and **Process** are important. **Refresh**, **Validate**, and **Check encoding** are normal. **Delete Selected** is delete.
- **Home and Models:** **New project**, **Add existing**, **New model**, and **Run inference** are important. Dialog confirms that write are important. **Cancel** and **Close** are normal. A confirm that deletes is delete. The model-rename **Cancel** button is currently `btn-error`; it becomes normal.
- **Settings and create-model:** the left-hand page list uses `btn-choice`. **Next** and **Save** in those footers are important. **Back** is normal.

## Left as they are

The top screen selector in [app.component.html](lightning-pose-app/web_ui/src/app/app.component.html), video transport controls, accordions, Help toggles, and icon-only buttons (close, trash, info, keypoint clear). Storybook samples are not part of the app sweep.

No new unit spec. Note the three Daisy pairs and the choice rule in [feature_plans/lpa-button-styles.md](feature_plans/lpa-button-styles.md).

## Check

On `mms1`, **Save** and **Save and next** match **Add more frames from a session**, including the hover swap. **Next** and **Revert changes** use the same soft treatment in blue. The trash icon is unchanged. On File Manager, **Load** is the soft green and **Refresh** is the soft blue. In Project settings, the selected page is darker than the other pages and both stay light text. Open **Load Calibration** and cancel it.
