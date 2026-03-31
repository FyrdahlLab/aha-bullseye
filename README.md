# aha-bullseye

AHA 16/17-segment bullseye plots on matplotlib.

```bash
pip install -e .
```

## Usage

```python
import numpy as np
import matplotlib.pyplot as plt
from bullseye import bullseye, bullseye_outline

values = np.random.uniform(500, 1500, size=17)

ax = bullseye(values, cmap="viridis", annot=True, fmt=".0f", show_segment_ids=True, cbar=True)
bullseye_outline(ax, [2, 3, 8, 9, 14], color="red", linewidth=3.0)
plt.show()
```

Segments follow AHA order: 1-6 basal, 7-12 mid, 13-16 apical, 17 apex. Passing 16 values omit the apex. Returns `ax`, access the figure as `ax.figure`.

## Subplots

```python
fig, axes = plt.subplots(1, 2, figsize=(8, 4), subplot_kw={"projection": "polar"})

bullseye(baseline, ax=axes[0], vmin=650, vmax=1950, annot=True)
bullseye(follow_up, ax=axes[1], vmin=650, vmax=1950, annot=True)
```

## API

```
bullseye(values, ...) → ax

    Draw an AHA 16- or 17-segment bullseye plot.

    Parameters
    ----------
    values : sequence of float or None
        Per-segment values in AHA order (length 16 or 17).
        None/NaN entries are drawn with missing_color.
    ax : polar Axes, optional
        Axes to plot on. Created if not provided.
    cmap : str, list, or Colormap, optional
        Colormap name, Colormap instance, or list of colors
        (e.g. ["#ccc", "red"]). Defaults to "viridis", or
        "coolwarm" when center is set.
    norm : Normalize, optional
        Custom normalization. Mutually exclusive with
        vmin/vmax/center/robust.
    vmin, vmax : float, optional
        Color scale limits. Inferred from data if not set.
    center : float, optional
        Midpoint for diverging colormaps. Enables TwoSlopeNorm.
    robust : bool, default False
        Use 2nd–98th percentile for color limits.
    annot : bool or sequence, default False
        True to label segments with values. A sequence provides
        custom per-segment labels.
    fmt : str, default ".1f"
        Format string for numeric annotations.
    annot_kws : dict, optional
        Extra keywords forwarded to ax.text.
    show_segment_ids : bool, default False
        Show 1-based AHA segment numbers.
    fontsize : int, default 7
        Font size for annotations and segment IDs.
    missing_color : color, default (0.92, 0.92, 0.92, 1.0)
        Fill color for None/NaN segments.
    cbar : bool, default False
        Add a colorbar.
    cbar_ax : Axes, optional
        Pre-existing axes for the colorbar.
    cbar_kws : dict, optional
        Extra keywords forwarded to figure.colorbar.
    linecolor : color, default "white"
        Color of lines between segments.
    linewidths : float, default 1.0
        Width of lines between segments. 0 to hide.
    show_wall_labels : bool, default False
        Show Anterior/Septal/Inferior/Lateral labels.
    wall_label_fontsize : int, default 8
        Font size for wall labels.
    figsize : (float, float), default (4.0, 4.0)
        Figure size in inches. Only used when ax is None.

    Returns
    -------
    ax : polar Axes


bullseye_outline(ax, selected_segments, ...) → QuadContourSet

    Draw a closed outline around selected AHA segments.

    Parameters
    ----------
    ax : polar Axes
        Axes returned by bullseye().
    selected_segments : sequence of int or bool
        1-based AHA IDs (e.g. [2, 3, 8, 9, 14]) or a boolean
        mask of length 16/17.
    color : str, default "red"
        Outline color.
    linewidth : float, default 3.0
        Outline width.

    Returns
    -------
    contour : QuadContourSet or None
```
