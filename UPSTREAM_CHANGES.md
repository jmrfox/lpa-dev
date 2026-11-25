# Upstream changes

Changes we plan to propose to libraries that LPA uses but doesn't own. Each entry says what to change, why, what LPA does meanwhile, and what LPA can remove once it's done.

| Library | Repo | Pinned in LPA |
|---|---|---|
| EKS | [paninski-lab/eks](https://github.com/paninski-lab/eks) | `ensemble-kalman-smoother==4.6.0` (`app_server/pyproject.toml`) |
| LP | [paninski-lab/lightning-pose](https://github.com/paninski-lab/lightning-pose) | editable clone in `lightning-pose/` |

Status: **Planned** (not raised yet), **Raised** (issue or PR open, link it), **Done** (released; note the version).

## EKS

### Run the smoother in 64-bit floats

**Status:** Planned.

**What:** EKS should do its Kalman filter and smoother math in 64-bit floats itself, instead of leaving it to whoever calls it. EKS could turn on JAX's 64-bit mode (`jax_enable_x64`) around the smoother, or convert the uncertainty arrays (P, Q, R) to 64-bit there. The other option is a covariance update that stays valid in 32-bit, such as the Joseph form or a square-root (Cholesky) filter.

**Why:** EKS 4.6.0 never turns on 64-bit mode, so JAX runs it in 32-bit.
- Its camera projection code asks for `jnp.float64` (`multicam_smoother.py`, `make_jax_projection_fn`), but with 64-bit mode off JAX converts that to 32-bit.
- In 32-bit, whole keypoints come back NaN when `smooth_param` is large and the ensemble members agree closely.
- This isn't specific to LPA: anyone who calls EKS with a large `smooth_param` can hit it, from Python or with `eks multicam --s`. EKS's command line and LP's docs choose `smooth_param` automatically by default, and that gave no NaNs here. A fix inside EKS covers every caller, rather than leaving each caller to turn on 64-bit.

**What we measured** (mirror-mouse-separate, session 180605_000, 30,000 frames, `smooth_param` 1000):

| Run | 32-bit | 64-bit |
|---|---|---|
| Nonlinear, 2 members | NaN for 5 of 7 keypoints on every frame | no NaNs |
| Linear, 2 members | NaN for paw2LF on every frame | no NaNs |
| Nonlinear or linear, 3 members | no NaNs | — |
| Run time, nonlinear | 9.2–11.1 s | 10.6–10.7 s |
| Run time, linear | 7.9 s | 9.4 s |
| Peak memory | — | about 15–20% higher |

- The member predictions had no NaNs.
- The NaN keypoints were those where `smooth_param × Q` (Q is the process noise EKS estimates from frame-to-frame movement) was largest relative to the ensemble variance, both in pixels².
- With automatic `smooth_param`, 32-bit gave no NaNs, but nonlinear took about 10 minutes on CPU.
- Changing the calibration made no difference: translations ×0.01, or the mirrored camera replaced with an equivalent non-mirrored one.
- Not checked: which operation first produces the NaN, and whether EKS 4.6.1 or 4.6.2 behave differently. Neither release mentions a related change.

The full investigation is in `feature_plans/lpa-eks-linear-nonlinear.md`.

**Related EKS issues:** paninski-lab/eks#62 (mostly-NaN multicam output). It was closed by paninski-lab/eks#65, released in 4.5.0 and so already in 4.6.0, which changed the single-model variance. paninski-lab/eks#86 / #87 is also single-model only.

**What LPA does meanwhile:** `run_eks.py` turns on 64-bit in its own process before importing eks (`_enable_jax_x64`; paninski-lab/lightning-pose-app#192, LPA #150). The Create EKS Model dialog also warns when an even number of members is selected.

**Once EKS does this:** raise LPA's EKS pin to that release. Keep or remove `_enable_jax_x64` in `run_eks.py` and its test `tests/test_run_eks.py`, depending on how EKS turns 64-bit on. If EKS only turns it on inside its own functions, LPA's process-wide switch does no harm, but it's no longer needed.

## LP

### OS-specific install docs

**Status:** Planned (paninski-lab/lightning-pose-app#128, label `LP change`).

**What:** Install directions per OS in LP's docs (`docs/source/installation_guide.rst`): Linux supports everything; Windows supports labeling only and should use WSL2 for full features; macOS supports labeling only.

**What LPA does meanwhile:** nothing; the docs live in LP.

### Output folder for `litpose crop`

**Status:** Planned (draft written; for paninski-lab/lightning-pose-app#209).

**What:** `litpose crop --output_dir` so crops go somewhere other than the detector's folder, and a way for `litpose train` to train on crops from that folder (a new option, or `--detector_model` accepting it).

**Why:** `crop` always writes to `<detector>/cropped_images`, `<detector>/cropped_videos` and `<detector>/image_preds/<csv>/cropped_<csv>`, and `train --detector_model` reads those fixed paths. Two pose models on one detector with different box settings write their crops to the same place, and the first pose model's `config.yaml` then points at the second's crops.

**What LPA does meanwhile:** one box setting per detector (`feature_plans/lpa-crop-and-zoom.md`, open question 1).

**What LPA can remove once done:** the one-setting lock; crops would go in each pose model's own folder.
