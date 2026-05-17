"""Nord colormaps, named colours, and aquarel theme for matplotlib.

Auto-registers on import:
  - 16 named colours: nord0 ... nord15
  - 6 colormaps (plus _r reverses): nord_seq, nord_frost, nord_aurora,
    nord_div, nord_qual, nord_mono
  - 1 mplstyle: 'nord-dark' (use via plt.style.use('nord-dark'))

Provides:
  - load_nord_theme(): returns aquarel Theme with the 9-colour Nord cycle
"""
from importlib.resources import files
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# ── Named colours ─────────────────────────────────────────────────────
_nord_named = {
    # Polar Night
    "nord0": "#2e3440", "nord1": "#3b4252",
    "nord2": "#434c5e", "nord3": "#4c566a",
    # Snow Storm
    "nord4": "#d8dee9", "nord5": "#e5e9f0", "nord6": "#eceff4",
    # Frost
    "nord7": "#8fbcbb", "nord8": "#88c0d0",
    "nord9": "#81a1c1", "nord10": "#5e81ac",
    # Aurora
    "nord11": "#bf616a", "nord12": "#d08770", "nord13": "#ebcb8b",
    "nord14": "#a3be8c", "nord15": "#b48ead",
}
mcolors._colors_full_map.update(_nord_named)

# ── Colormaps ─────────────────────────────────────────────────────────
_FROST = ["#8fbcbb", "#88c0d0", "#81a1c1", "#5e81ac"]
_AURORA = ["#bf616a", "#d08770", "#ebcb8b", "#a3be8c", "#b48ead"]
_POLAR_NIGHT = ["#2e3440", "#3b4252", "#434c5e", "#4c566a"]
_SNOW_STORM = ["#d8dee9", "#e5e9f0", "#eceff4"]

_cmaps = {
    "nord_frost": mcolors.LinearSegmentedColormap.from_list(
        "nord_frost", list(reversed(_FROST))
    ),
    "nord_seq": mcolors.LinearSegmentedColormap.from_list(
        "nord_seq",
        ["#5e81ac", "#81a1c1", "#88c0d0", "#8fbcbb",
         "#a3be8c", "#ebcb8b", "#d08770", "#bf616a"],
    ),
    "nord_aurora": mcolors.LinearSegmentedColormap.from_list(
        "nord_aurora", _AURORA
    ),
    "nord_div": mcolors.LinearSegmentedColormap.from_list(
        "nord_div",
        ["#5e81ac", "#81a1c1", "#88c0d0",
         "#eceff4",
         "#ebcb8b", "#d08770", "#bf616a"],
    ),
    "nord_qual": mcolors.ListedColormap(_FROST + _AURORA, name="nord_qual"),
    "nord_mono": mcolors.LinearSegmentedColormap.from_list(
        "nord_mono", _POLAR_NIGHT + _SNOW_STORM
    ),
}

for _cmap in _cmaps.values():
    try:
        plt.colormaps.register(_cmap)
        plt.colormaps.register(_cmap.reversed())
    except ValueError:
        # already registered (e.g. on module reload)
        pass

# ── Stylesheet ────────────────────────────────────────────────────────
# Register the package's data directory so plt.style.use('nord-dark') works.
_style_dir = files("nord_mpl") / "data"
plt.style.core.USER_LIBRARY_PATHS.append(str(_style_dir))
plt.style.core.reload_library()


# ── Aquarel theme loader ──────────────────────────────────────────────
def load_nord_theme():
    """Return the customised aquarel Theme with the full 9-colour Nord cycle.

    Usage:
        from nord_mpl import load_nord_theme
        theme = load_nord_theme()
        theme.apply()
    """
    from aquarel import Theme
    json_path = files("nord_mpl") / "data" / "arctic_dark_custom.json"
    return Theme.from_file(str(json_path))


__all__ = ["load_nord_theme"]
__version__ = "0.1.0"
