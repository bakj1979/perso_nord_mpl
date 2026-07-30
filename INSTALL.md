# Install — nord-mpl

The project folder is `perso_nord_mpl` (matching the `perso_*` convention) but
the Python import name is `nord_mpl`, governed by `src/nord_mpl/` rather than
the outer folder. In code you always write `import nord_mpl`.

## 1. Clone

```bash
git clone https://github.com/bakj1979/perso_nord_mpl.git ~/repos/quant/perso/perso_nord_mpl
```

Expected layout:

```
~/repos/quant/perso/perso_nord_mpl/
├── pyproject.toml
├── README.md
├── INSTALL.md
├── LICENSE
├── .gitignore
└── src/
    └── nord_mpl/
        ├── __init__.py
        └── data/
            ├── arctic_dark_custom.json
            └── nord-dark.mplstyle
```

If the target folder already exists, GitHub Desktop will refuse to clone into
it — it only clones into empty directories. Use **Add → Add Existing
Repository** and point it at the existing path instead.

## 2. Install

**conda env** (editable — edits to the source tree are picked up after a kernel
restart, no reinstall):

```bash
conda activate port-env
pip install -e ~/repos/quant/perso/perso_nord_mpl
```

**uv project** (install from git):

```bash
uv add "nord-mpl @ git+https://github.com/bakj1979/perso_nord_mpl"
```

To develop against the local tree from inside a uv project instead:

```bash
uv add --editable ~/repos/quant/perso/perso_nord_mpl
```

Repeat per env. The source tree lives outside every env, so it survives env
rebuilds.

## 3. Verify

Restart any running Jupyter kernels first, then:

```python
import matplotlib as mpl
import matplotlib.pyplot as plt
import nord_mpl

# Colormaps — expect 12 (6 cmaps plus their _r reverses)
print(sorted(c for c in plt.colormaps if "nord" in c))

# Named colours
print(mpl.colors.to_hex("nord11"))          # -> #bf616a

# Stylesheet
print("nord-dark" in plt.style.available)   # -> True
plt.style.use("nord-dark")

# Aquarel theme
theme = nord_mpl.load_nord_theme()
theme.apply()
```

## 4. Compatibility

Requires Python >= 3.10, matplotlib >= 3.6, aquarel >= 0.0.6.

Verified against matplotlib 3.10.8 and 3.11.1 (with aquarel 0.0.7). matplotlib
3.11 relocated `matplotlib.style.core`; the original 0.1.0 import path relied on
it and fails under 3.11 with `AttributeError: module 'matplotlib.style' has no
attribute 'core'`. The stylesheet is now registered through
`matplotlib.style.library` directly, which works across the whole supported
range.
