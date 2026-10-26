# LPA image formats for labeled frames

paninski-lab/lightning-pose-app#164, branch `fix/image-formats`, PR paninski-lab/lightning-pose-app#171.

## Problem

LP opens labeled frames with PIL (`lightning_pose/data/datasets.py`), so it trains on any format Pillow reads. LPA only showed lowercase `.png` and `.jpg`: the files route allowlist and the File Manager frame regexes compared `Path.suffix` with case. Frames named `.JPG`, `.PNG` or `.jpeg` (common in imported DLC projects) trained fine but were broken images in the Labeler and "Unexpected file" in File Manager.

## Formats

One backend list, `app_server/src/litpose_app/image_formats.py`, used by the files route and validation. Matched in any letter case. (`paths/path_util_legacy.py` has its own png|jpg pattern but is unused and imports types that exist only in a fork of LP, so it was left alone.)

| Group | Extensions | App behavior |
|---|---|---|
| Browser and LP (Pillow 13, Chrome) | `.jpg .jpeg .jfif .png .apng .bmp .gif .webp .avif` | Served with an explicit content type (no `mimetypes` guess); accepted by validation |
| LP only | `.tif .tiff .ppm .pgm .pbm .pnm .tga .jp2 .j2k` | Route refuses with the can't-show message; validation accepts them as frames and warns once per format; Labeler shows the message in place of the image and as the temporal context tip |

Message: "<FORMAT> frames train in Lightning Pose but cannot be shown in the browser. Convert them to PNG to label or review them here." The frontend copy is `web_ui/src/app/image-formats.ts`; keep the two lists in step.

Other suffixes are still refused by the files route (it serves any absolute path, so the allowlist stays).

## Cache

Validation results in `.project-cache` now store `FILE_CHECK_RULES` (2) in their context. Results saved before this change don't match, so File Manager checks again instead of showing an old "Unexpected file". Video probes are not affected.

## Tests

See the CHANGELOG entry under `2.4.2.4.dev0`: `test_read_file.py`, `test_image_formats.py`, `test_validate_project_files.py`, `image-formats.spec.ts`, `image-label-widget.component.spec.ts` "frame image message", `labeler-center-panel.component.spec.ts`.

## Not done

- No conversion tool for TIFF frames.
- HEIC is read by neither Pillow (without a plugin) nor Chrome, so it is not listed.
