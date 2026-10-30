#!/usr/bin/env python3
"""Write a calibration.toml for mirror-mouse-separate, fitted to its labeled frames.

The dataset ships without a calibration. This makes one good enough to test
nonlinear EKS: the two cameras agree with where the labeled keypoints appear in
both views. It is not a real calibration: the scale is arbitrary and the
bottom camera's tilt is traded off against its image centre.

Usage (poseapp env):
    python scripts/fit_mirror_mouse_calibration.py LPProjects/mirror-mouse-separate

Views: ``top`` is a side camera; ``bot`` is the same camera seen through a 45°
mirror, so its image is mirrored. No ordinary camera produces a mirrored
image, so ``bot`` gets a negative fy. EKS (``make_jax_projection_fn``) and
aniposelib both read fx and fy separately, so that works there.

World axes: X forward (towards the nose), Y the mouse's left, Z up; the mouse is
near the origin.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
from aniposelib.cameras import Camera, CameraGroup
from scipy.optimize import least_squares
from scipy.sparse import lil_matrix

VIEWS = ("top", "bot")
DISTANCE = 500.0  # starting camera distance from the mouse
FIELD_WIDTH = 150.0  # starting guess for the width each image covers, same units


def load_labels(data_dir: Path) -> tuple[np.ndarray, dict[str, tuple[int, int]]]:
    """Keypoints labeled in both views, shape (2, n, 2), and each view's (width, height)."""
    per_view, index, sizes = [], None, {}
    for view in VIEWS:
        frames = []
        for suffix in ("", "_test"):
            csv = data_dir / f"CollectedData_{view}{suffix}.csv"
            if csv.is_file():
                frames.append(pd.read_csv(csv, header=[0, 1, 2], index_col=0))
        df = pd.concat(frames)
        h, w = cv2.imread(str(data_dir / df.index[0])).shape[:2]
        sizes[view] = (w, h)
        rows = [i.replace(f"_{view}/", "_*/") for i in df.index]
        if index is not None and rows != index:
            raise SystemExit(f"{view} labels don't list the same frames as {VIEWS[0]}")
        index = rows
        per_view.append(df.to_numpy(dtype=float).reshape(-1, 2))
    p2d = np.stack(per_view)
    both = ~np.isnan(p2d).any(axis=(0, 2))
    print(f"{len(index)} labeled frames, {both.sum()} keypoints labeled in both views")
    return p2d[:, both], sizes


def intrinsics(f: float, cx: float, cy: float, mirrored: bool) -> np.ndarray:
    return np.array([[f, 0, cx], [0, -f if mirrored else f, cy], [0, 0, 1]])


class Model:
    """Camera numbers and their projections.

    The top camera's pose is fixed; with the bottom camera's depth also fixed
    this pins the scale. Fitted camera numbers (11):
    f, cx, cy (top) | rvec (3), tx, ty (bot) | f, cx, cy (bot).
    """

    def __init__(self, sizes: dict[str, tuple[int, int]]):
        self.sizes = sizes
        # Rows of R are the camera's x, y, z axes in world coordinates.
        r_top = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]], float)  # on the right, looking left
        self.rvec_top = cv2.Rodrigues(r_top)[0].ravel()
        self.tvec_top = -r_top @ np.array([0, -DISTANCE, 0])
        # Bottom: below, looking up (identity rotation), centred under the mouse.
        self.tz_bot = DISTANCE
        f0 = sizes["top"][0] * DISTANCE / FIELD_WIDTH
        (wt, ht), (wb, hb) = sizes["top"], sizes["bot"]
        self.start = np.array([f0, wt / 2, ht / 2, 0, 0, 0, 0, 0, f0, wb / 2, hb / 2], float)

    def cameras(self, c: np.ndarray) -> list[tuple[np.ndarray, np.ndarray, np.ndarray]]:
        """(rvec, tvec, K) for top and bot."""
        top = (self.rvec_top, self.tvec_top, intrinsics(*c[0:3], mirrored=False))
        bot = (c[3:6], np.array([c[6], c[7], self.tz_bot]), intrinsics(*c[8:11], mirrored=True))
        return [top, bot]

    def residuals(self, c: np.ndarray, pts: np.ndarray, p2d: np.ndarray) -> np.ndarray:
        """Projected minus labeled pixel positions, both views, flattened."""
        out = [
            cv2.projectPoints(pts.reshape(-1, 3), r, t, k, np.zeros(5))[0].reshape(-1, 2) - obs
            for (r, t, k), obs in zip(self.cameras(c), p2d)
        ]
        return np.concatenate(out).ravel()

    def group(self, c: np.ndarray) -> CameraGroup:
        return CameraGroup([
            Camera(name=v, size=self.sizes[v], matrix=k, rvec=r, tvec=t, dist=np.zeros(5))
            for v, (r, t, k) in zip(VIEWS, self.cameras(c))
        ])


def point_sparsity(n: int) -> lil_matrix:
    """Each keypoint's 3D position affects only its own 4 residuals."""
    jac = lil_matrix((4 * n, 3 * n), dtype=int)
    for view in range(2):
        for i in range(n):
            row = 2 * (view * n + i)
            jac[row: row + 2, 3 * i: 3 * i + 3] = 1
    return jac


def pixel_errors(model: Model, c: np.ndarray, pts: np.ndarray, p2d: np.ndarray) -> np.ndarray:
    return np.linalg.norm(model.residuals(c, pts, p2d).reshape(2, -1, 2), axis=2)


def fit(model: Model, p2d: np.ndarray, rounds: int) -> np.ndarray:
    """Alternate: fit the cameras with points fixed, then the points with cameras fixed.

    A joint fit of cameras and points together stalled at the starting cameras.
    """
    n = p2d.shape[1]
    sparsity = point_sparsity(n)
    cams = model.start.copy()
    pts = model.group(cams).triangulate(p2d, fast=True).ravel()
    err = pixel_errors(model, cams, pts, p2d)
    print(f"start:    median {np.median(err):.2f} px, 90th percentile {np.percentile(err, 90):.2f} px")
    for round_ in range(rounds):
        cams = least_squares(
            lambda c: model.residuals(c, pts, p2d), cams, loss="huber", f_scale=3.0
        ).x
        pts = model.group(cams).triangulate(p2d, fast=True).ravel()
        pts = least_squares(
            lambda q: model.residuals(cams, q, p2d), pts,
            jac_sparsity=sparsity, loss="huber", f_scale=3.0,
        ).x
        err = pixel_errors(model, cams, pts, p2d)
        print(
            f"round {round_ + 1:2d}: median {np.median(err):.2f} px, "
            f"90th percentile {np.percentile(err, 90):.2f} px"
        )
    return cams


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("data_dir", type=Path, help="Project data directory")
    parser.add_argument("--rounds", type=int, default=10)
    parser.add_argument("--out", type=Path, help="Default: <data_dir>/calibration.toml")
    args = parser.parse_args()

    p2d, sizes = load_labels(args.data_dir)
    model = Model(sizes)
    group = model.group(fit(model, p2d, args.rounds))

    # Check the way EKS uses it: aniposelib triangulation, then projection.
    p3d = group.triangulate(p2d, fast=True)
    err = np.linalg.norm(group.project(p3d).reshape(2, -1, 2) - p2d, axis=2)
    print(f"aniposelib triangulate + project: median {np.median(err):.2f} px, "
          f"90th percentile {np.percentile(err, 90):.2f} px")

    out = args.out or args.data_dir / "calibration.toml"
    group.dump(str(out))
    print("wrote", out)


if __name__ == "__main__":
    main()
