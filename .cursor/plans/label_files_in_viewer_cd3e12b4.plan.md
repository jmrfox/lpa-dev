---
name: Label files in viewer
overview: Show a label CSV in the Viewer and Labeler when File Manager would not mark it Invalid, after treating a pandas suffix on the scorer (`rick.1`) as the same scorer (`rick`).
todos:
  - id: share-label-check
    content: Strip a trailing pandas suffix from the scorer in the shared header check, then return findLabelFiles paths that File Manager would not mark Invalid.
    status: completed
  - id: update-test
    content: Update test_find_label_files_logic for a rick/rick.1 scorer row and a rejected bad header.
    status: completed
  - id: browser-check
    content: Confirm the mms1 Viewer label picker lists CollectedData without rewriting project CSVs.
    status: completed
isProject: false
---

# Label files in the Viewer

[find_label_files.py](lightning-pose-app/app_server/src/litpose_app/routes/labeler/find_label_files.py) is unchanged from `origin/main`. The Viewer label picker and the Labeler **Label file** dropdown both read `findLabelFiles` through `allLabelFiles`.

`CollectedData_top.csv` and `CollectedData_bot.csv` are normal label files. Pandas has rewritten the repeated scorer as `rick,rick.1,rick.2,...`. The bodypart row is still `paw1LH,paw1LH,...` and the coords row is still `x,y,...`. Do not rewrite the scorer row.

## Scorer suffix

Before pairing coordinates, strip one trailing pandas duplicate-column suffix from the scorer only: `rick.1` and `rick.12` count as `rick`. A scorer with no suffix is unchanged. Then require each `(scorer, bodypart)` pair to have both `x` and `y`.

Put that normalization in the header check shared with File Manager, [_label_header_issue](lightning-pose-app/app_server/src/litpose_app/routes/validate_files.py), so both screens use the same rule. Today that function ignores the scorer entirely; after this change it still accepts these files, and it still rejects a bodypart that has only one coordinate once the suffix is removed.

## One list

Make `findLabelFiles` return the relative paths from `_validate_labels` whose `issues` list is empty. That is the same set File Manager lists, minus files it would mark **Invalid**. A keypoint mismatch is a warning, so those files still appear. A bad name, a bad header, or a missing frame image does not.

The search stays outside the model directory and `data_dir/models`, and it includes nested CSVs, matching the File Manager panel.

## Check

Update `test_find_label_files_logic` so an accepted file is one File Manager would mark OK, including a `rick` / `rick.1` scorer row, and a file with a bad header is omitted. In the browser, open the Viewer label picker on `mms1` and confirm `CollectedData` is listed. Do not rewrite the project CSVs.
