# Button styles

Text buttons use the soft styles already in the dim theme. Hover stays DaisyUI's: a dark tint with light colored text at rest, and a light fill with dark text on hover.

- **Important** is `btn btn-soft btn-primary`, the same green as **Add more frames from a session**. Use it when the button opens another screen, opens a dialog, or writes data or files.
- **Normal** is `btn btn-soft btn-info`, the same blue as the Multiview tools question mark. Use it when the button only acts on the current screen. In the Labeler, **Save**, **Save and next**, **Load Calibration**, and **Refine calibration** use this blue as well. On the Models screen, **Run inference on all sessions** uses this blue too. In File Manager, every button except the green **Add** buttons uses this blue. **Delete Selected** stays red.
- **Delete** is `btn btn-soft btn-error`, the same red as the Labeler trash button. Use it when the button deletes or removes something. **Cancel task** uses this too, because it stops a running job.
- **Choice** is `btn-choice` on the Project settings page list and the model-creation page list, including **Preview YAML**. A resting page uses the dialog's `base-100` with no border. The selected page uses the darker `base-300`, and both keep light text.

The top screen selector, video transport controls, accordions, Help toggles, and icon-only buttons stay as they are. Frame-list highlights stay `bg-sky-700`.
