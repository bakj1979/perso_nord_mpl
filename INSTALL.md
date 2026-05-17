# Install — nord-mpl

## 1. Place the package

Extract the tarball so you end up with this layout:

```
~/Documents/Python/python_code/python_projects_perso/perso_nord_mpl/
├── pyproject.toml
├── README.md
├── LICENSE
├── .gitignore
└── src/
    └── nord_mpl/
        ├── __init__.py
        └── data/
            ├── arctic_dark_custom.json
            └── nord-dark.mplstyle
```

Note: the **project folder** is `perso_nord_mpl` (matches the `perso_*`
naming convention) but the **Python import name** is `nord_mpl` (governed
by `src/nord_mpl/`, not the outer folder). So in code you still write
`import nord_mpl`.

## 2. Remove the legacy hand-placed files

The old `nord_mpl/` directory and `.pth` file in site-packages will conflict
with the new pip-installed package. Remove them:

```bash
SP="$HOME/miniforge3/envs/port-env/lib/python3.14/site-packages"
rm -rf "$SP/nord_mpl"
rm -f  "$SP/nord-mpl.pth"
```

You can also delete the loose files from `~/.matplotlib/` since the package
now ships its own copies (the package's mplstyle path is registered with
matplotlib at import time, and the JSON is loaded via `importlib.resources`):

```bash
# Optional cleanup
rm -f ~/.matplotlib/arctic_dark_custom.json
rm -f ~/.matplotlib/stylelib/nord-dark.mplstyle
```

If you'd rather keep them as backups, leave them — they won't conflict.

## 3. Install (editable)

From any terminal where `port-env` is the active conda env:

```bash
conda activate port-env
pip install -e ~/Documents/Python/python_code/python_projects_perso/perso_nord_mpl
```

The `-e` flag means "editable": pip installs a link to the source tree, so
any edits to `src/nord_mpl/__init__.py` are picked up after a kernel restart
without needing to reinstall.

## 4. Verify

Restart any running Jupyter kernels, then in a notebook:

```python
import matplotlib.pyplot as plt
import nord_mpl

# Colormaps
print([c for c in plt.colormaps() if "nord" in c])
# Expected: 12 entries (6 cmaps + their _r reverses)

# Named colours
print("nord11" in plt.matplotlib.colors._colors_full_map)
# Expected: True

# Style
print("nord-dark" in plt.style.available)
# Expected: True

# Aquarel theme
from nord_mpl import load_nord_theme
theme = load_nord_theme()
theme.apply()
```

## 5. Install in additional envs

For any other conda env (existing or new):

```bash
conda activate <other-env>
pip install -e ~/Documents/Python/python_code/python_projects_perso/perso_nord_mpl
```

One-liner; survives env rebuilds (the source tree is outside any env).

## 6. Set up the GitHub repo (optional)

```bash
cd ~/Documents/Python/python_code/python_projects_perso/perso_nord_mpl
git init
git add .
git commit -m "Initial commit: nord-mpl package"
gh repo create bakj1979/perso_nord_mpl --private --source=. --push
```
