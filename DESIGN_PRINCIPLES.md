# LPA design principles

How we decide where files live, how they're named, and which code is allowed to know about it. Written 2026-10-27. Update it when we decide something new.

**Sources:**
- `LP Project Spec v1.pdf` (kept in the lpa-dev folder, not committed), the directory spec Karan Sikka wrote in Oct–Nov 2025. Its status line says "Conceptually approved, investigating changes to LP code required". Most of its v1 layout was never built. We treat it as a source of ideas, not as rules.
- Karan's note on the path layers (quoted under principle 3).
- Our own rules: `.cursor/rules/lpa-research-software.mdc` and the "align with LP" rule.

Each principle below says whether it's **in place**, **adopted** (we follow it from now on, even where the code doesn't yet), or **open** (needs a decision).

---

## 1. LP decides what the files mean

LPA reads and writes the files LP trains on. When LPA and LP disagree about a name, a location or a format, LPA changes. Read the LP code (`lightning-pose/`) before designing anything that touches project files, and cite the LP file in the issue or PR.

The spec planned a v1 layout that needed LP changes first: a `PathResolver` in LP, key types (`SessionKey`, `LabelFileKey`), and datasets that take keys instead of paths. These were only ever written in Karan's LP fork. They aren't in paninski-lab/lightning-pose. So **v1 is not the target layout**. Today's layout (what LP reads now) is.

*Status: in place.*

## 2. Write the convention, read what's there

LPA always **writes** files in the standard layout and naming. It **reads** what the user actually has, and flags anything unusual instead of refusing it. The spec says "must" and "not allowed" in many places. We keep its conventions as what LPA writes and recommends, and drop the requirement that projects match them before LPA will open them.

Examples:
- Video names: the File Manager flags a name that doesn't parse as `session_view`. It doesn't hide the file.
- Labeled frames: LPA shows any image format LP's Pillow can read (#164). The spec allowed `.png` only.
- Validation reports problems. It blocks only when continuing would lose data or LP is certain to fail (see `lpa-research-software.mdc`).

The spec's ban on "searching the filesystem and fuzzy matching" inside a project is the strict version of this. We don't search to *guess* what a file is. Each kind of file has one rule for its name. But we do list what's on disk, and show the files that don't match.

*Status: in place.*

## 3. Naming rules live in one place, at the top

Karan's note:

> High-level entities like multiview label files (MVLabelFile) and multiview videos (Session) are represented by data structures that contain both their high-level identifiers (SessionKey) and explicit filepaths. Only the topmost layers of the application (the UI and other entry points) are responsible for resolving these explicit paths based on schema rules and conventions. Lower layers, including the backend, operate on explicit filepath references as much as possible.

What that means for us:
- Objects passed around in memory (`Session`, `MVLabelFile`) carry the key **and** the full path of each per-view file.
- The UI and the entry points (RPC routes, CLI commands) turn keys into paths. Code below them opens the paths it's given and doesn't rebuild filenames.
- Each naming rule is written **once**. On the backend that place is `app_server/src/litpose_app/paths/`: one `ResourceUtil` per kind of file, with `get_path` (key → path) and `parse_path` (path → key). It matches the spec's `PathResolver`, kept inside LPA.
- The UI doesn't copy a backend rule (a glob pattern, a folder name, a character set). It asks the backend for the list, or for a check.

Where we are: `paths/` exists but nothing calls it, and most of its methods are unfinished. The File Manager and several routes write the rules out themselves. Fixing that for label CSVs and calibrations is paninski-lab/lightning-pose-app#173. The session/view split is one rule, the last `_`, in `session_view.py` and `utils/session-view.ts` (paninski-lab/lightning-pose-app#174). The same applies to the other kinds of file afterwards.

*Status: adopted, partly in place.*

## 4. Nothing machine-specific inside the project

A project folder can be copied to another machine, a cluster, a portable drive or a cloud bucket, and still work there.
- Absolute paths belong only in `~/.lightning-pose/projects.toml`, which belongs to one machine. A project is referred to by its key from that file, not by its path.
- Paths stored in project files are relative and always use `/`, on Windows too. Convert to the OS form only when opening the file. (This is what LP does for image paths in label CSVs.)
- LP writes `data.data_dir` / `data.video_dir` into each model's `config.yaml`, which breaks this. Migration `004_fix_config_data_dirs` rewrites them when a project moves. LPA doesn't use those values to find files.

The spec goes further: store keys, not even relative paths, in files. That only applies to new file formats we design. Existing LP formats (label CSV index of image paths, `config.yaml`) stay as LP defines them.

*Status: adopted.*

## 5. Keys are stable, and their names are safe

Session names, view names, keypoint names, label file names and model names show up inside other files and filenames (calibrations, model configs, EKS configs). Renaming one means updating every place that refers to it, so:
- Treat a key as permanent once other files use it. The rename tools must update every reference, or say clearly which ones they didn't update.
- Characters: letters, digits, `-`, `_`, `.`. This is the rule in `validate_files._NAME_RE` and the calibration rename. The spec also allowed spaces. We don't, because spaces in filenames cause trouble in shell commands and cluster scripts.
- **A view name must not contain `_`.** A video is `<session>_<view>`, split at the last `_`. LPA doesn't check this when a project is created yet.
- Two keys that differ only in letter case (`Mouse1`, `mouse1`) are the same file on macOS and Windows. Warn about it.
- Keep names well under 255 characters. The spec suggests about 100.

*Status: adopted. New projects refuse `_` in view names; existing ones warn. Names that differ only in case warn (paninski-lab/lightning-pose-app#176).*

## 6. Layout changes go through a version and a migration

The project's layout version is stored in its config. A change to the layout gets a numbered migration in `app_server/src/litpose_app/migrations/`, and is never done as a silent rewrite (see `AGENTS.md`). A migration must leave the user's labels, models and videos readable by LP.

*Status: in place for migrations. Today's layout is version 1, which is what `CreateNewProject` and migration 003 already write; 0 or a missing field means a project written before the field existed, with the same layout. The spec's layout, if ever built, would be version 2. `PathUtil.for_version(1)` still raises until paninski-lab/lightning-pose-app#177 lands.*

## 7. A model folder is enough to run inference

Copying `models/<name>/` to another machine should be enough to run `litpose predict` there. Inference never depends on paths recorded at training time.

*Status: adopted (it's LP's job; LPA must not break it).*

## 8. Missing files are expected

Users delete old sessions, move videos, and copy projects without their models. A key that points to a missing file must not crash a page or block the rest of the project. Show which file is missing, and keep everything else working. (The spec accepted "a cryptic error" here. We want a clear one.)

*Status: adopted.*

## 9. Labeling works on Windows and macOS

Training and inference need Linux (NVIDIA DALI). Labeling, the Viewer and the File Manager should work on any OS, and must never write OS-specific paths into the project (see 4).

*Status: adopted.*

## 10. One simple naming rule, no guessing

Video files are `<session>_<view>.<ext>`, with the view after the last `_`. The spec considered parsing other naming schemes ("search for the view name and strip it") and rejected it as too hard to explain. We agree: the user should be able to predict how LPA reads a filename. When names don't fit, LPA flags them and offers a rename (File Manager). It doesn't guess.

*Status: in place.*

---

## Parts of the spec we are not taking (for now)

These are the spec's v1 layout changes. None are in LP. Each would need an LP change, a migration and a reason that's worth that cost. Keep them as a reference for any future layout version.

| Spec v1 | Today |
|---|---|
| `project.toml` | `project.yaml` |
| Calibrations: `calibrations/default.toml` for the project | `calibration.toml` in the data dir (what LP reads) |
| Calibration backups: `calibrations/backups/<session>_<time_ns>.toml` (the `PathResolver` section says `calibration_backups/<session>.<time_ns>.toml`, so the spec contradicts itself) | `calibrations/backups/<session>_og-<YYYYmmdd-HHMMSS>.toml` (#173) |
| One `videos/` folder | Any `videos*/` folder, nested allowed, with folders you can turn off |
| Frames in `labeled-data/frames/<session>_<view>/frame_<8 digits>.png`, `selected_frames.txt` required | `labeled-data/<session>_<view>/`, any image name LP accepts |
| Label CSVs in `labeled-data/labels/` | Data dir root (`LABEL_CSV_SCOPE`) |
| Labeling queue `labeled-data/labeling-queue/<key>.csv` | `<label file>.unlabeled.jsonl` next to the CSV (migration 001) |
| Flat models folder, `video-preds/<name>` without `.mp4`, `ensemble.txt` | LP's current output layout, `ensemble.yaml` |
| `misc/` folder for user files | Not needed. LPA ignores files it doesn't know. |
| `project_key` in model config, no `data_dir` | LP config as is (see 4) |

## Open questions

1. **Inference on videos outside the project.** The spec left this open. LPA's inference uses videos inside the project. If we allow outside videos, where do the predictions go, and how does the Viewer find them?
2. **`paths/` types.** `paths/` imports `SessionKey` and the other keys from `lightning_pose.data.datatypes`, which only had them in Karan's fork. Define them in LPA, or ask for them in LP?
