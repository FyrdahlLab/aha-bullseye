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
bullseye(values, ax=None, cmap=None, norm=None, vmin=None, vmax=None,
         center=None, robust=False, annot=False, fmt=".1f", annot_kws=None,
         show_segment_ids=False, missing_color=..., cbar=False, cbar_ax=None,
         cbar_kws=None, linecolor="white", linewidths=1.0,
         show_wall_labels=False, figsize=(4.0, 4.0)) → ax

bullseye_outline(ax, selected_segments, color="red", linewidth=3.0)
```

`selected_segments`: 1-based AHA ids (`[2, 3, 8, 9, 14]`) or a boolean mask.
