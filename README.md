# nord-mpl

Nord colour palette for matplotlib — colormaps, named colours, an mplstyle, and an aquarel theme.

Personal package by Jeffrey Scott Baker.

## Install

Editable install from local clone:

```bash
pip install -e ~/repos/quant/perso/perso_nord_mpl
```

See [INSTALL.md](INSTALL.md) for uv projects and verification.

## What it does

On `import nord_mpl`, the package automatically registers:

- **16 named colours**: `nord0` through `nord15`, accessible anywhere matplotlib accepts a colour string (e.g. `color="nord11"`).
- **6 colormaps** plus their `_r` reversed variants: `nord_seq`, `nord_frost`, `nord_aurora`, `nord_div`, `nord_qual`, `nord_mono`.
- **1 stylesheet**: `nord-dark`, usable via `plt.style.use("nord-dark")`.

It also exposes three functions:

- **`load_nord_theme()`**: returns an aquarel `Theme` configured with the full 9-colour Nord cycle (extends aquarel's built-in 6-colour `arctic_dark`).
- **`show()`**: finalises the current figure's layout and displays it. One call in place of `fig.tight_layout()`, `theme.apply_transforms()` and `plt.show()`.
- **`finalise_layout(theme)`**: the layout step of `show()` on its own, for when the figure is saved rather than displayed.

## Use

```python
import nord_mpl  # auto-registers everything
import matplotlib.pyplot as plt

# Option 1: stylesheet
plt.style.use("nord-dark")
plt.plot([1, 2, 3], color="nord11")
data = [[0, 1], [2, 3]]
plt.imshow(data, cmap="nord_seq")

# Option 2: aquarel theme
from nord_mpl import load_nord_theme, show
theme = load_nord_theme()
theme.apply()                    # once, after import
fig, ax = plt.subplots()
ax.plot([1, 2, 3])
show()                           # in place of plt.show(), for every figure
```

`show()` uses the packaged Nord theme's transforms. If you have customised
the theme's transforms, pass it: `show(theme)`.

To save a figure instead of displaying it, finalise the layout yourself:

```python
import matplotlib.pyplot as plt
from nord_mpl import finalise_layout, load_nord_theme

theme = load_nord_theme()
theme.apply()                    # once, after import
fig, ax = plt.subplots()
ax.plot([1, 2, 3])
finalise_layout(theme)           # immediately before every save
fig.savefig("figure.png")
```

### Why `finalise_layout`

The theme carries two transforms that need opposite positions relative to
`fig.tight_layout()`. `offset` pushes spines and labels outward, so the layout
has to be computed after it or labels on neighbouring panels can collide.
`trim` cuts each spine to the major ticks present when it is called, so it has
to run after the layout, which can change them. `theme.apply_transforms()`
applies both at once, so neither order of `tight_layout()` and
`apply_transforms()` is right. `finalise_layout` applies `offset`, then
`tight_layout()`, then `trim`.

It acts on the current figure and does not support constrained layout.

## Reserved colormaps

`magma` is reserved for heatmaps in the QuantForge plotting conventions and
should not be aliased or overridden.

## License

MIT
