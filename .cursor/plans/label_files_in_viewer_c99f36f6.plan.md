---
name: Label files in viewer
overview: Show a label CSV in the Viewer and Labeler only when File Manager would mark it OK or Check, including files whose scorer names were uniquified to rick, rick.1.
todos:
  - id: share-label-check
    content: Return findLabelFiles paths that File Manager would not mark Invalid, using the bodypart header check.
    status: pending
  - id: update-test
    content: Update test_find_label_files_logic for a uniquified scorer header and a rejected bad header.
    status: pending
  - id: browser-check
    content: Confirm the mms1 Viewer label picker lists CollectedData without rewriting project CSVs.
    status: pending
isProject: false
---

# Label files in the Viewer

This is not from this branch. [find_label_files.py](lightning-pose-app/app_server/src/litpose_app/routes/labeler/find_label_files.py) is unchanged from `origin/main`. The Viewer label picker and the Labeler **Label file** dropdown both read `findLabelFiles` through `allLabelFiles`.

`CollectedData_bot.csv` is a normal label file. Its scorer row is `rick,rick.1,rick.2,...` because a CSV cannot keep duplicate column names after a pandas save: the repeated scorer `rick` is rewritten as `rick`, `rick.1`, `rick.2`. The bodypart row is still `paw1LH,paw1LH,...` and the coords row is still `x,y,...`. The scorer text is who labeled the column. Pairing is by bodypart and `x`/`y`, which is already how frame save works in [save_mvframe.py](lightning-pose-app/app_server/src/litpose_app/routes/labeler/save_mvframe.py). Files that still say `rick,rick,rick` were never rewritten that way. Do not rewrite the scorer row.

`findLabelFiles` rejects a file unless each scorer-and-bodypart pair has both `x` and `y`. After uniquifying, `paw1LH` under `rick` has only `x` and `paw1LH` under `rick.1` has only `y`, so every column fails and the dropdown is empty. File Manager already accepts this in `_label_header_issue`: each bodypart needs `x` and `y`, and the scorer strings may differ.

## One list

Make `findLabelFiles` return the relative paths from `_validate_labels` whose `issues` list is empty. That is the same set File Manager lists, minus files it would mark **Invalid**. A keypoint mismatch is a warning, so those files still appear. A bad name, a bad header, or a missing frame image does not.

The search stays outside the model directory and `data_dir/models`, and it includes nested CSVs, matching the File Manager panel.

## Check

Update `test_find_label_files_logic` so an accepted file is one File Manager would mark OK, including a `rick` / `rick.1` header, and a file with a bad header is omitted. In the browser, open the Viewer label picker on `mms1` and confirm `CollectedData` is listed. Do not rewrite the project CSVs.