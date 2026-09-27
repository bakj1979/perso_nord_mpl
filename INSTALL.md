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
├── src/
│   └── nord_mpl/
│       ├── __init__.py
│       └── data/
│           ├── arctic_dark_custom.json
│           └── nord-dark.mplstyle
└── tests/
    └── test_finalise_layout.py
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

**uv project** (install from git, pinned to a tag):

```bash
uv add "nord-mpl @ git+https://github.com/bakj1979/perso_nord_mpl@v0.2.0"
```

Pin the tag. Without `@v0.2.0` the install tracks the default branch, so two
environments built a week apart can end up on different commits — which is
exactly how an env can silently land on 0.1.0 and break under matplotlib 3.11.
uv records the resolved commit SHA in `direct_url.json`, so a pinned install
stays reproducible even if the tag is later moved.

To develop against the local tree from inside a uv project instead:

```bash
uv add --editable ~/repos/quant/perso/perso_nord_mpl
```

**plain venv, or any repo not managed by uv** — use `uv pip install`, not
`uv add`:

```bash
uv pip install --python .venv/bin/python \
    "nord-mpl @ git+https://github.com/bakj1979/perso_nord_mpl@v0.2.0"
```

`uv add` is for uv-managed projects: it writes a static `project.dependencies`
entry into `pyproject.toml`, then locks and syncs. Against a `pyproject.toml`
that declares `dynamic = ["dependencies"]` it fails outright, because PEP 621
forbids a field being both static and dynamic:

```
configuration error: You cannot provide a value for `project.dependencies`
and list it under `project.dynamic` at the same time
```

The failure is about the target repo, not the package being added — `uv add`
anything fails there identically. uv rolls its own edit back afterwards, so
`pyproject.toml` looks untouched and the cause is easy to misread as a problem
with the package. `uv pip install` sidesteps all of it by installing into the
environment without touching project metadata.

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

# Layout helper (0.2.0 and later)
fig, ax = plt.subplots()
ax.plot([1, 2, 3])
nord_mpl.finalise_layout(theme)
```

To run the test suite without installing pytest into a shared env, from the
repo root:

```bash
uv run --no-project --with pytest --with-editable . pytest
```

`--no-project` stops uv creating a `.venv` and a `uv.lock` inside the repo.

## 4. Compatibility

Requires Python >= 3.10, matplotlib >= 3.6, aquarel >= 0.0.6.

Version 0.1.1 is verified against matplotlib 3.6.3, 3.7.2, 3.8.4, 3.10.8 and
3.11.1, on Python 3.11 and 3.14, with aquarel 0.0.7. Every run escalated
`DeprecationWarning`, `FutureWarning` and `MatplotlibDeprecationWarning` to
errors, and checked import, the twelve colormaps, the `nord0`–`nord15` named
colours, `plt.style.use("nord-dark")`, and the aquarel theme through
`apply_transforms()` to a rendered figure. 3.6.3 is the declared floor, so the
supported range is tested at both ends rather than only in the middle.

Version 0.2.0 adds `finalise_layout` and leaves the import-time registration
untouched. Its test suite (`tests/test_finalise_layout.py`) was run on two
combinations: Python 3.14.5 with matplotlib 3.11.2, aquarel 0.0.7 and numpy
2.5.3; and the declared floor, Python 3.11.15 with matplotlib 3.6.3, aquarel
0.0.6 and numpy 1.26.4. The 0.1.1 matrix above was not re-run for 0.2.0.
`finalise_layout` rests on `pyplot.gcf`, `Figure.tight_layout` and the
module-level functions in `aquarel.transforms`, whose names match the keys of
`Theme.transforms`.

Use 0.1.1 or later on matplotlib >= 3.11. matplotlib 3.11 relocated
`matplotlib.style.core`; the original 0.1.0 import path relied on it and fails
under 3.11 with `AttributeError: module 'matplotlib.style' has no attribute
'core'`. The stylesheet is now registered through `matplotlib.style.library`
directly. `matplotlib.style.USER_LIBRARY_PATHS` would have been the terser
swap, but it only exists from 3.11, and using it would have silently dropped
3.10 and below.

The breadth of that range is the point, not an accident. One version has to
serve both a current conda base and an older pinned notebook repo without a
per-environment fork. `port-env` (Python 3.14, matplotlib 3.11.1, numpy 2.4.6)
and the FMNM notebooks (Python 3.11, matplotlib 3.7.2, numpy 1.25.1) both run
0.1.1 unmodified. `rc_params_from_file`, `style.library` and `style.available`
are public and stable across the whole `>=3.6` range, which is what makes that
possible; keep any future stylesheet change on those three.

Two environment notes when testing against older matplotlib in a fresh venv.
Constrain `numpy<2`: matplotlib gained numpy 2 support in 3.9, and earlier
releases were compiled against the numpy 1.x ABI, so they abort with
`numpy.core.multiarray failed to import` if numpy 2 is resolved. Expect
`PyparsingDeprecationWarning` raised from inside
`matplotlib._fontconfig_pattern` on 3.6 and 3.8 against a modern pyparsing;
that is matplotlib's own noise, not this package's, and it surfaces only if you
escalate warnings to errors.
