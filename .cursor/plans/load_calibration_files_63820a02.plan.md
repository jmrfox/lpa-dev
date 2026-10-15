---
name: Load calibration files
overview: Add a Load Calibration button that copies a .toml into calibrations/, creating that folder when needed, using the same local-or-server file chooser as Import Session.
todos:
  - id: shared-chooser
    content: Extract the local-or-server file chooser and let the server browser filter by extension.
    status: completed
  - id: load-calibration
    content: Add Load Calibration, create calibrations/ when missing, and copy or upload the .toml without overwriting.
    status: completed
  - id: tests-docs
    content: Cover the new-folder copy and the 409 collision with one pytest, update the feature plan, and check the dialog in the browser.
    status: completed
isProject: false
---

# Load calibration files

The user’s computer cannot be browsed with the same in-app folder list as the server. Local files stay on the browser’s Open File control. Server files keep the existing in-app browser. Do not edit the cursor plan file, and do not commit.

## Shared chooser

Import Session already has this pattern in [session-import.component.html](lightning-pose-app/web_ui/src/app/session-import/session-import.component.html): a **Server files** checkbox (off by default), a Choose button, a hidden local file input, and [server-video-picker.component.ts](lightning-pose-app/web_ui/src/app/components/server-video-picker/server-video-picker.component.ts).

Pull that row into one reusable control, and give the server browser an extension filter plus single- or multi-select. Session import uses it for video extensions and multiple files, with the same `choose-videos` and `server-files-checkbox` test ids so [session-import.component.spec.ts](lightning-pose-app/web_ui/src/app/session-import/session-import.component.spec.ts) still passes. The unused older dialogs (`model-inference-dialog`, `video-group-import`) stay as they are.

## Camera Calibration button

On the left of the Camera Calibration button row, add **Load Calibration**, and mention it in bold in the description.

It opens a dialog on the shared chooser, limited to `.toml`, and allows more than one file. Choosing a file does not move or delete the source.

- A local file is uploaded.
- A server file is copied. The path must be a `.toml` file under the home directory.

`data_dir/calibrations/` is created when it is missing. Each file is written as `calibrations/<filename>.toml`. The name before `.toml` is the session id and uses the same character rule as rename. If that destination already exists, the request returns 409 and nothing is replaced. `calibration.toml` at the data-directory root is unchanged; this button only fills the `calibrations/` folder.

After a successful load, the panel list refreshes.

One pytest, `test_import_calibration_creates_folder_and_copies_toml`: a server `.toml` is copied into a new `calibrations/` directory, and a second import of the same name returns 409 with the first file unchanged.

Update [feature_plans/lpa-video-management.md](feature_plans/lpa-video-management.md). Then check in the browser that Load Calibration opens the chooser, the Server files checkbox switches to the in-app browser, and a local `.toml` can be chosen. Do not leave a test file in a real project.