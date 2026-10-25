#!/usr/bin/env python3
"""Download a <2GB fly-anipose subset into datasets/fly-anipose-tiny."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd
from huggingface_hub import HfApi

REPO = "paninski-lab/fly-anipose"
SESSIONS_IND = ["05272019_fly1_0_R1C24", "05272019_fly2_0_R1C14"]
SESSION_OOD = "05272019_fly5_0_R1C12"


def hf_download(dest: Path, paths: list[str]) -> None:
    paths = sorted(set(paths))
    if not paths:
        return
    subprocess.run(
        ["hf", "download", REPO, "--repo-type", "dataset", "--local-dir", str(dest), *paths],
        check=True,
    )


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    dest = root / "datasets" / "fly-anipose-tiny"

    api = HfApi()
    all_files = api.list_repo_files(REPO, repo_type="dataset")

    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)

    session_ids = SESSIONS_IND + [SESSION_OOD]
    paths: list[str] = ["README.md", "project.yaml", "config_fly-anipose.yaml"]
    paths += [f for f in all_files if f.startswith("calibrations/") and any(s in f for s in session_ids)]

    for sess in SESSIONS_IND:
        paths += [f for f in all_files if f.startswith("videos/") and sess in f and f.endswith(".mp4")]
    paths += [
        f for f in all_files if f.startswith("videos_test/") and SESSION_OOD in f and f.endswith(".mp4")
    ]

    for cam in "ABCDEF":
        paths.append(f"CollectedData_Cam-{cam}.csv")
        paths.append(f"CollectedData_Cam-{cam}_test.csv")

    hf_download(dest, paths)

    img_paths: list[str] = []

    def filter_csv(name: str, allowed: list[str]) -> None:
        p = dest / name
        df = pd.read_csv(p, header=[0, 1, 2], index_col=0)
        mask = [any(s in str(idx) for s in allowed) for idx in df.index]
        sub = df.loc[mask]
        sub.to_csv(p)
        img_paths.extend(str(i) for i in sub.index)

    for cam in "ABCDEF":
        filter_csv(f"CollectedData_Cam-{cam}.csv", SESSIONS_IND)
        filter_csv(f"CollectedData_Cam-{cam}_test.csv", [SESSION_OOD])

    labeled = sorted({p for p in img_paths if p.startswith("labeled-data/")})
    for i in range(0, len(labeled), 100):
        hf_download(dest, labeled[i : i + 100])

    config = dest / "config_fly-anipose-tiny.yaml"
    config.write_text(
        (dest / "config_fly-anipose.yaml").read_text().replace(
            "data_dir: ${LP_ROOT_PATH:}/data/fly-anipose",
            f"data_dir: {dest}",
        )
    )

    (dest / "SUBSET.md").write_text(
        f"""# fly-anipose-tiny (local subset)

From [{REPO}](https://huggingface.co/datasets/{REPO}) for Lightning Pose / LPA smoke tests (<2GB).

| Split | Sessions |
|-------|----------|
| InD (`videos/`, `CollectedData_Cam-*.csv`) | {", ".join(SESSIONS_IND)} |
| OOD (`videos_test/`, `CollectedData_*_test.csv`) | {SESSION_OOD} |

- **{len(labeled)}** labeled PNGs (only rows kept in the filtered CSVs)
- **{len([p for p in paths if p.endswith('.mp4')])}** session video clips (6 cameras × 3 sessions)

Rebuild: `bash scripts/build-fly-anipose-tiny.sh`

Train: `litpose train {dest / 'config_fly-anipose-tiny.yaml'}`
"""
    )
    cache = dest / ".cache"
    if cache.exists():
        shutil.rmtree(cache)

    subprocess.run(
        [sys.executable, str(Path(__file__).resolve().parent / "normalize_fly_anipose_session_names.py"), str(dest)],
        check=True,
    )
    print(dest)


if __name__ == "__main__":
    main()
