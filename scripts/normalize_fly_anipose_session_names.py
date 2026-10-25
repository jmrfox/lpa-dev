#!/usr/bin/env python3
"""Rename fly-anipose paths to <session>_<view> (view = Cam-A … Cam-F only)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Hub names: …_Cam-A_rot-ccw-0.06_sec → …_Cam-A
_MOTION_SUFFIX = re.compile(r"^(?P<prefix>.+_(?:rot|str))-(?:ccw|cw)-[\d.]+_sec$")
_STIM_SUFFIX = re.compile(r"_(?:rot|str)$")


def shorten_stem(stem: str) -> str:
    m = _MOTION_SUFFIX.match(stem)
    if m:
        stem = m.group("prefix")
    return _STIM_SUFFIX.sub("", stem)


def build_mapping(root: Path) -> dict[str, str]:
    mapping: dict[str, str] = {}

    ld = root / "labeled-data"
    if ld.is_dir():
        for d in ld.iterdir():
            if d.is_dir():
                new = shorten_stem(d.name)
                if new != d.name:
                    mapping[d.name] = new

    for sub in ("videos", "videos_test"):
        vd = root / sub
        if vd.is_dir():
            for f in vd.glob("*.mp4"):
                new_stem = shorten_stem(f.stem)
                if new_stem != f.stem:
                    mapping[f.stem] = new_stem

    cal = root / "calibrations"
    if cal.is_dir():
        for f in cal.glob("*.toml"):
            new_stem = shorten_stem(f.stem)
            if new_stem != f.stem:
                mapping[f.stem] = new_stem

    return mapping


def apply_mapping(root: Path, mapping: dict[str, str]) -> None:
    if not mapping:
        print(f"{root}: nothing to rename")
        return

    # Rename labeled-data folders (deepest paths only).
    ld = root / "labeled-data"
    for old, new in sorted(mapping.items(), key=lambda x: -len(x[0])):
        src = ld / old
        if src.is_dir():
            dst = ld / new
            if dst.exists():
                raise SystemExit(f"target already exists: {dst}")
            src.rename(dst)

    for sub in ("videos", "videos_test"):
        vd = root / sub
        if not vd.is_dir():
            continue
        for old, new in mapping.items():
            src = vd / f"{old}.mp4"
            if src.is_file():
                dst = vd / f"{new}.mp4"
                if dst.exists():
                    raise SystemExit(f"target already exists: {dst}")
                src.rename(dst)

    cal = root / "calibrations"
    if cal.is_dir():
        for old, new in mapping.items():
            src = cal / f"{old}.toml"
            if src.is_file():
                dst = cal / f"{new}.toml"
                if dst.exists():
                    raise SystemExit(f"target already exists: {dst}")
                src.rename(dst)

    # Update text files (longest keys first).
    pairs = sorted(mapping.items(), key=lambda x: -len(x[0]))
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".csv", ".yaml", ".yml", ".md", ".toml", ".json"}:
            continue
        text = path.read_text()
        new_text = text
        for old, new in pairs:
            new_text = new_text.replace(old, new)
        if new_text != text:
            path.write_text(new_text)

    print(f"{root}: renamed {len(mapping)} session/view stems")


def main() -> None:
    repo = Path(__file__).resolve().parents[1]
    targets = [repo / "LPProjects" / "fly-anipose-tiny", repo / "datasets" / "fly-anipose-tiny"]
    if len(sys.argv) > 1:
        targets = [Path(p).resolve() for p in sys.argv[1:]]

    for root in targets:
        if not root.is_dir():
            continue
        mapping = build_mapping(root)
        apply_mapping(root, mapping)


if __name__ == "__main__":
    main()
