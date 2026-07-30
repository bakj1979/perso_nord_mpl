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

It also exposes one function:

- **`load_nord_theme()`**: returns an aquarel `Theme` configured with the full 9-colour Nord cycle (extends aquarel's built-in 6-colour `arctic_dark`).

## Use

```python
import nord_mpl  # auto-registers everything
import matplotlib.pyplot as plt

# Option 1: stylesheet
plt.style.use("nord-dark")
plt.plot([1, 2, 3], color="nord11")
plt.imshow(data, cmap="nord_seq")

# Option 2: aquarel theme
from nord_mpl import load_nord_theme
theme = load_nord_theme()
theme.apply()
```

## Reserved colormaps

`magma` is reserved for heatmaps in the QuantForge plotting conventions and
should not be aliased or overridden.

## License

MIT
