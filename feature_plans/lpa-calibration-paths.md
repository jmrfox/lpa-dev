# LPA calibration paths in one place

paninski-lab/lightning-pose-app#173 (part 1 of 2). Principle 3 in `DESIGN_PRINCIPLES.md`.

## Split

1. **Backend (branch `refactor/calibration-paths`, PR paninski-lab/lightning-pose-app#184).** No UI change.
2. **UI (follow-up).** A listing route; the File Manager label and calibration panels list what the backend returns, with a `kind` per calibration row; drop `isSessionCalibration()` / `isModelsCsv()` and the `rglob` patterns; show the backend's message when a rename is refused. `camera-calibration.service.ts` too.

## Why not `paths/` (PathUtil)

#173 proposed routing these through Karan Sikka's `paths/` package. A first attempt (2026-10-28) found that it couldn't be imported: `path_util_legacy.py` imports `SessionKey`, `FrameKey`, … from `lightning_pose.data.datatypes`, and paninski-lab/lightning-pose has never had them (only his fork did; `0c374fb` in LPA, "Add paths, project management, datatypes from core repo fork"). `for_version` also called `PathUtilLegacy` with the wrong arguments, and its session/view parsing used "`_<view>` anywhere". Making it work needed five key types defined in LPA, of which only `SessionKey` would be used, plus #177's version lookup. Decided with Jordan: drop that, and write the rule as plain functions, as #174 did with `session_view.py`. `paths/` is left as it was.

## Part 1, done

`app_server/src/litpose_app/calibration_paths.py`:
- `session_calibration_path(data_dir, session)` → `calibrations/<session>.toml`
- `project_calibration_path(data_dir)` → `calibration.toml`
- `calibration_backup_path(data_dir, session, when)` → `calibrations/backups/<session>_og-<YYYYmmdd-HHMMSS>.toml` (what bundle adjustment has always written)
- `session_calibration_files(data_dir)` → `.toml` directly in `calibrations/`, sorted ignoring case; not `backups/`
- `is_session_calibration(data_dir, path)`
- `session_calibration_filename_issue(filename)`: the one session-id rule, used by rename and import

Callers: `validate_files._validate_calibrations`, `rename_project_files` (rename, import, `_new_calibration_path`), `routes/labeler/__init__` (`get_session_level_calibration_path`, `find_calibration_file`, which lost their `config` argument), `bundle_adjust` (lookup and backup), `multiview_autolabel`. Removed from `Config`: `CALIBRATIONS_DIRNAME`, `CALIBRATION_BACKUPS_DIRNAME` (unused, and wrong) and `GLOBAL_CALIBRATION_PATH`.

Behavior change: a renamed or imported session calibration is written as `<session>.toml`. Before, `mouse1.TOML` kept its name, and validation (which lists only `.toml`) didn't show it.

## #177

Decided (option 1, recorded in the issue): today's layout is version 1. Nothing reads `schema_version` now that `paths/` stays unused, so there is no code change; the issue can close with that note or stay open until something reads the number.

## Label CSVs

`validate_files.label_csv_rels` stays the backend definition of which CSVs are label files (`findLabelFiles`, `validateProjectFiles` and the project stats use it). Part 2 lists label files from it.

## Tests

`tests/test_calibration_paths.py`, `tests/routes/test_calibration_routes.py`. Two of the three route tests fail on the old code (the lookup without `config`, the upper-case rename).
