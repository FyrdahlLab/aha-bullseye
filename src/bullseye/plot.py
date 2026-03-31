import math
from typing import Mapping, Sequence, Tuple, Union

import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib.colors import ListedColormap
import numpy as np

from .layout import BULLSEYE_SEGMENT_COUNT_ATTR, ring_bounds, validate_segment_count

DEFAULT_SEQUENTIAL_CMAP = "viridis"
DEFAULT_DIVERGING_CMAP = "coolwarm"
DEFAULT_MISSING_COLOR = (0.92, 0.92, 0.92, 1.0)
DEFAULT_LINECOLOR = "white"
DEFAULT_LINEWIDTHS = 1.0
DEFAULT_ANNOT_FONTSIZE = 7
DEFAULT_WALL_LABEL_FONTSIZE = 8


def bullseye(
    values: Sequence[Union[float, None]],
    *,
    ax=None,
    cmap: Union[str, colors.Colormap, list, None] = None,
    norm: Union[colors.Normalize, None] = None,
    vmin: Union[float, None] = None,
    vmax: Union[float, None] = None,
    center: Union[float, None] = None,
    robust: bool = False,
    annot: Union[bool, Sequence[object]] = False,
    fmt: str = ".1f",
    annot_kws: Union[Mapping[str, object], None] = None,
    show_segment_ids: bool = False,
    show_labels: Union[bool, None] = None,
    fontsize: int = DEFAULT_ANNOT_FONTSIZE,
    missing_color=DEFAULT_MISSING_COLOR,
    cbar: bool = False,
    cbar_ax=None,
    cbar_kws: Union[Mapping[str, object], None] = None,
    linecolor=DEFAULT_LINECOLOR,
    linewidths: float = DEFAULT_LINEWIDTHS,
    show_wall_labels: bool = False,
    wall_label_fontsize: int = DEFAULT_WALL_LABEL_FONTSIZE,
    figsize: Tuple[float, float] = (4.0, 4.0),
):
    validate_segment_count(len(values))
    if show_labels is not None:
        if annot is not False:
            raise ValueError("pass either annot or show_labels, not both")
        annot = show_labels

    cmap = _resolve_cmap(cmap=cmap, center=center)
    norm = _resolve_norm(
        values=values,
        norm=norm,
        vmin=vmin,
        vmax=vmax,
        center=center,
        robust=robust,
    )

    if ax is None:
        _, ax = plt.subplots(subplot_kw={"projection": "polar"}, figsize=figsize)
    segment_count = len(values)
    bounds = ring_bounds(segment_count)
    setattr(ax, BULLSEYE_SEGMENT_COUNT_ATTR, segment_count)
    ax.set_axis_off()
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(1)
    ax.set_ylim(0, 1.05)
    default_color = colors.to_rgba(missing_color)
    annotations = _resolve_annotations(values=values, annot=annot, fmt=fmt)
    text_kws = dict(annot_kws or {})

    for start_idx, end_idx, r0, r1 in bounds:
        ring_values = values[start_idx:end_idx]
        ring_segment_count = len(ring_values)
        width = 2 * math.pi / ring_segment_count

        for j, v in enumerate(ring_values):
            segment_id = start_idx + j + 1
            if _is_missing(v):
                face = default_color
            else:
                face = colors.to_rgba(cmap(norm(v)))

            is_apex_ring = ring_segment_count == 1
            edge = face if is_apex_ring else _resolve_edgecolor(face=face, linecolor=linecolor, linewidths=linewidths)
            lw = 0.0 if is_apex_ring else _resolve_linewidth(linecolor=linecolor, linewidths=linewidths)
            ax.bar(
                j * width,
                r1 - r0,
                width=width,
                bottom=r0,
                align="center",
                color=face,
                edgecolor=edge,
                linewidth=lw,
            )

            label = _format_label(
                segment_id=segment_id,
                value_text=annotations[segment_id - 1],
                show_segment_ids=show_segment_ids,
            )
            if label is None:
                continue

            theta_mid, r_mid = _label_position(
                j=j,
                width=width,
                r0=r0,
                r1=r1,
                is_apex_ring=is_apex_ring,
            )
            luminance = 0.2126 * face[0] + 0.7152 * face[1] + 0.0722 * face[2]
            draw_kws = dict(text_kws)
            draw_kws.setdefault("ha", "center")
            draw_kws.setdefault("va", "center")
            draw_kws.setdefault("multialignment", "center")
            draw_kws.setdefault("fontsize", fontsize)
            draw_kws.setdefault("color", "black" if luminance > 0.5 else "white")
            ax.text(theta_mid, r_mid, label, **draw_kws)

    if show_wall_labels:
        r = 1.15
        ax.text(0.0, r, "Anterior", ha="center", va="center", fontsize=wall_label_fontsize, clip_on=False)
        ax.text(math.pi / 2, r, "Septal", ha="center", va="center", rotation=90, fontsize=wall_label_fontsize, clip_on=False)
        ax.text(math.pi, r, "Inferior", ha="center", va="center", fontsize=wall_label_fontsize, clip_on=False)
        ax.text(3 * math.pi / 2, r, "Lateral", ha="center", va="center", rotation=90, fontsize=wall_label_fontsize, clip_on=False)

    if cbar:
        scalar_mappable = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
        scalar_mappable.set_array(_finite_values(values))
        ax.figure.colorbar(scalar_mappable, ax=ax, cax=cbar_ax, **dict(cbar_kws or {}))

    return ax


def _is_missing(value) -> bool:
    if value is None:
        return True

    try:
        return bool(np.isnan(value))
    except TypeError:
        return False


def _format_label(
    *,
    segment_id: int,
    value_text: Union[str, None],
    show_segment_ids: bool,
):
    lines = []
    if show_segment_ids:
        lines.append(str(segment_id))

    if value_text is not None:
        lines.append(value_text)

    if not lines:
        return None
    return "\n".join(lines)


def _label_position(*, j: int, width: float, r0: float, r1: float, is_apex_ring: bool):
    if is_apex_ring:
        return 0.0, 0.0
    return j * width, r0 + (r1 - r0) / 2


def _resolve_cmap(*, cmap, center: Union[float, None]):
    if cmap is None:
        cmap = DEFAULT_DIVERGING_CMAP if center is not None else DEFAULT_SEQUENTIAL_CMAP
    if isinstance(cmap, list):
        return ListedColormap(cmap)
    if isinstance(cmap, str):
        return plt.get_cmap(cmap)
    return cmap


def _resolve_norm(
    *,
    values: Sequence[Union[float, None]],
    norm,
    vmin: Union[float, None],
    vmax: Union[float, None],
    center: Union[float, None],
    robust: bool,
):
    if norm is not None:
        if any(param is not None for param in (vmin, vmax, center)) or robust:
            raise ValueError("pass either norm or vmin/vmax/center/robust, not both")
        return norm

    data_vmin, data_vmax = _infer_data_limits(values=values, robust=robust, center=center)

    if center is None:
        resolved_vmin = data_vmin if vmin is None else float(vmin)
        resolved_vmax = data_vmax if vmax is None else float(vmax)
        resolved_vmin, resolved_vmax = _expand_equal_bounds(vmin=resolved_vmin, vmax=resolved_vmax)
        return colors.Normalize(vmin=resolved_vmin, vmax=resolved_vmax)

    center = float(center)
    if vmin is None or vmax is None:
        lower = data_vmin if vmin is None else float(vmin)
        upper = data_vmax if vmax is None else float(vmax)
        span = max(abs(lower - center), abs(upper - center))
        if span == 0.0:
            span = 1.0
        resolved_vmin = center - span if vmin is None else float(vmin)
        resolved_vmax = center + span if vmax is None else float(vmax)
    else:
        resolved_vmin = float(vmin)
        resolved_vmax = float(vmax)

    resolved_vmin, resolved_vmax = _expand_equal_bounds(vmin=resolved_vmin, vmax=resolved_vmax)
    if not resolved_vmin <= center <= resolved_vmax:
        raise ValueError("center must lie between vmin and vmax")
    return colors.TwoSlopeNorm(vmin=resolved_vmin, vcenter=center, vmax=resolved_vmax)


def _infer_data_limits(
    *,
    values: Sequence[Union[float, None]],
    robust: bool,
    center: Union[float, None],
):
    finite = _finite_values(values)
    if finite.size == 0:
        if center is None:
            return 0.0, 1.0
        center = float(center)
        return center - 1.0, center + 1.0

    if robust:
        vmin, vmax = np.nanpercentile(finite, [2, 98])
    else:
        vmin, vmax = np.nanmin(finite), np.nanmax(finite)
    return float(vmin), float(vmax)


def _finite_values(values: Sequence[Union[float, None]]) -> np.ndarray:
    finite = []
    for value in values:
        if _is_missing(value):
            continue
        finite.append(float(value))
    return np.asarray(finite, dtype=float)


def _expand_equal_bounds(*, vmin: float, vmax: float):
    if vmin > vmax:
        raise ValueError("vmin must be less than or equal to vmax")
    if vmin == vmax:
        delta = 1.0 if vmin == 0.0 else abs(vmin) * 0.01
        return vmin - delta, vmax + delta
    return vmin, vmax


def _resolve_annotations(
    *,
    values: Sequence[Union[float, None]],
    annot: Union[bool, Sequence[object]],
    fmt: str,
):
    if annot is False or annot is None:
        return [None] * len(values)
    if annot is True:
        return [_format_annotation_value(value=value, fmt=fmt) for value in values]

    raw = np.asarray(annot, dtype=object).ravel()
    if raw.size != len(values):
        raise ValueError(f"annot must contain {len(values)} entries; got {raw.size}")
    return [_coerce_annotation_text(value=value, fmt=fmt) for value in raw]


def _format_annotation_value(*, value, fmt: str):
    if _is_missing(value):
        return None
    return format(float(value), fmt)


def _coerce_annotation_text(*, value, fmt: str):
    if value is None:
        return None
    if isinstance(value, str):
        return value

    try:
        if bool(np.isnan(value)):
            return None
    except TypeError:
        pass

    if isinstance(value, (int, float, np.integer, np.floating)):
        return format(float(value), fmt)
    return str(value)


def _resolve_edgecolor(*, face, linecolor, linewidths: float):
    if linewidths <= 0 or linecolor is None:
        return face
    return linecolor


def _resolve_linewidth(*, linecolor, linewidths: float):
    if linewidths <= 0 or linecolor is None:
        return 0.0
    return linewidths
