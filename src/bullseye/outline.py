import math
from typing import Sequence, Union

import numpy as np

from .layout import infer_segment_count, ring_bounds

DEFAULT_OUTLINE_COLOR = "red"
DEFAULT_OUTLINE_LINEWIDTH = 3.0


def bullseye_outline(
    ax,
    selected_segments: Sequence[Union[int, bool]],
    *,
    color: str = DEFAULT_OUTLINE_COLOR,
    linewidth: float = DEFAULT_OUTLINE_LINEWIDTH,
):
    """Draw a closed outline around selected AHA segments."""
    segment_count = infer_segment_count(ax)
    selected = _normalize_selected_segments(selected_segments, segment_count)
    if selected.size == 0:
        return

    invalid = np.unique(selected[(selected < 1) | (selected > segment_count)])
    if invalid.size:
        raise ValueError(
            f"selected_segments must be between 1 and {segment_count}; got {invalid.tolist()}"
        )

    # Pad one extra column past 2π so contours close across the 0/2π seam.
    thetas = np.linspace(0.0, 2.0 * math.pi, 721)
    radii_base = np.linspace(0.0, 1.0, 240)
    radii = np.concatenate([radii_base, [1.0 + 1e-3]])
    Theta, R = np.meshgrid(thetas, radii)

    seg_index = np.zeros_like(Theta, dtype=np.int16)

    def assign(mask, nseg: int, base: int):
        if not np.any(mask):
            return
        width = 2.0 * math.pi / float(nseg)
        theta_eps = 1e-9
        j = np.round((Theta[mask] - theta_eps) / width).astype(int) % nseg
        seg_index[mask] = base + j

    for start_idx, end_idx, r0, r1 in ring_bounds(segment_count):
        if r0 == 0.0:
            mask = R <= r1
        else:
            mask = (R > r0) & (R <= r1)
        assign(mask, end_idx - start_idx, start_idx + 1)

    filled = np.isin(seg_index, selected).astype(float)
    filled[R > 1.0] = 0.0
    return ax.contour(
        Theta, R, filled, levels=[0.5], colors=[color], linewidths=[linewidth], zorder=10
    )


def _normalize_selected_segments(selected_segments, segment_count: int) -> np.ndarray:
    raw = np.asarray(selected_segments)
    if raw.dtype.kind == "b":
        flat_mask = raw.ravel()
        if flat_mask.size != segment_count:
            raise ValueError(
                f"boolean selected_segments mask must contain {segment_count} entries; got {flat_mask.size}"
            )
        return np.flatnonzero(flat_mask).astype(np.int16) + 1

    return np.asarray(selected_segments, dtype=np.int16).ravel()
