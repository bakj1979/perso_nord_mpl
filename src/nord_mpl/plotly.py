"""Nord template, colourscales and named colours for Plotly.

Importing this module registers the ``nord_dark`` template in
``plotly.io.templates``. It does not make it the default:

    import plotly.io as pio
    import nord_mpl.plotly as nord

    pio.templates.default = "nord_dark"          # every figure
    fig = px.line(df, template="nord_dark")      # or one figure

Colours are taken from the matplotlib side of the package (the ``nord-dark``
stylesheet and the colormap anchors), so both front ends stay in step.

Provides:
  - COLOURS: read-only mapping ``nord0`` ... ``nord15`` to hex. Plotly only
    resolves CSS colour names, so use ``nord.COLOURS["nord11"]``.
  - COLORWAY: the 9-colour Nord cycle, as in the stylesheet.
  - COLORSCALES: the six package colormaps plus ``_r`` reverses, as Plotly
    colourscales, e.g. ``colorscale=nord.COLORSCALES["nord_div"]``.
  - TEMPLATE: the ``nord_dark`` template object.
"""

from collections.abc import Sequence
from types import MappingProxyType

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt

from nord_mpl import _LINEAR_ANCHORS, _QUALITATIVE, _nord_named

try:
    import plotly.graph_objects as go
    import plotly.io as pio
except ImportError as error:
    raise ImportError(
        "nord_mpl.plotly needs plotly: install nord-mpl[plotly]"
    ) from error

Colourscale = tuple[tuple[float, str], ...]


def _hex(colour: str) -> str:
    """Normalise an rcParams colour, which may lack the ``#``, to ``#rrggbb``.

    Args:
        colour: Colour string as read from the stylesheet.

    Returns:
        Lower-case hex colour.
    """
    if len(colour) == 6 and not colour.startswith("#"):
        colour = f"#{colour}"
    return mcolors.to_hex(colour)


def _linear_scale(anchors: Sequence[str]) -> Colourscale:
    """Spread colours evenly over [0, 1], as ``LinearSegmentedColormap.from_list``.

    Args:
        anchors: Colours in order, at least two.

    Returns:
        Plotly colourscale.
    """
    last = len(anchors) - 1
    return tuple((i / last, _hex(c)) for i, c in enumerate(anchors))


def _stepped_scale(colours: Sequence[str]) -> Colourscale:
    """Give each colour a constant band of equal width, as ``ListedColormap``.

    Args:
        colours: Colours in order.

    Returns:
        Plotly colourscale with two stops per band.
    """
    count = len(colours)
    return tuple(
        stop
        for i, c in enumerate(colours)
        for stop in ((i / count, _hex(c)), ((i + 1) / count, _hex(c)))
    )


def _reversed_scale(scale: Colourscale) -> Colourscale:
    """Mirror a colourscale about 0.5.

    Args:
        scale: Plotly colourscale.

    Returns:
        The reversed colourscale.
    """
    return tuple((1.0 - position, colour) for position, colour in reversed(scale))


def _build_colourscales() -> MappingProxyType:
    """Return every package colormap as a Plotly colourscale, with reverses.

    Returns:
        Read-only mapping from colormap name to colourscale.
    """
    forward = {name: _linear_scale(a) for name, a in _LINEAR_ANCHORS.items()}
    forward["nord_qual"] = _stepped_scale(_QUALITATIVE)
    reverses = {f"{name}_r": _reversed_scale(s) for name, s in forward.items()}
    return MappingProxyType(forward | reverses)


COLOURS = MappingProxyType({name: _hex(c) for name, c in _nord_named.items()})
COLORSCALES = _build_colourscales()

_style = plt.style.library["nord-dark"]
COLORWAY = tuple(_hex(c) for c in _style["axes.prop_cycle"].by_key()["color"])


def _build_template() -> go.layout.Template:
    """Translate the ``nord-dark`` stylesheet into a Plotly template.

    Returns:
        The ``nord_dark`` template.
    """
    background = _hex(_style["axes.facecolor"])
    edge = _hex(_style["axes.edgecolor"])
    grid = _hex(_style["grid.color"])
    tick_label = _hex(_style["xtick.labelcolor"])
    label = _hex(_style["axes.labelcolor"])
    sequential = COLORSCALES["nord_seq"]

    axis = {
        "showgrid": True,
        "gridcolor": grid,
        "showline": True,
        "linecolor": edge,
        "zeroline": True,
        "zerolinecolor": edge,
        "ticks": "outside",
        "tickcolor": edge,
        "tickfont": {"color": tick_label, "size": _style["xtick.labelsize"]},
        "title": {"font": {"color": label, "size": _style["axes.labelsize"]}},
        "automargin": True,
    }
    scene_axis = {k: v for k, v in axis.items() if k != "automargin"} | {
        "backgroundcolor": background,
        "showbackground": True,
    }
    colourbar = {
        "outlinewidth": 0,
        "tickcolor": edge,
        "tickfont": {"color": tick_label},
        "title": {"font": {"color": label}},
    }
    continuous = {"colorscale": sequential, "colorbar": colourbar}

    return go.layout.Template(
        layout={
            "colorway": COLORWAY,
            "paper_bgcolor": _hex(_style["figure.facecolor"]),
            "plot_bgcolor": background,
            "font": {
                "family": ", ".join(_style["font.sans-serif"]),
                "color": _hex(_style["text.color"]),
                "size": _style["font.size"],
            },
            "title": {
                "x": 0.0,
                "xref": "paper",
                "xanchor": "left",
                "font": {"size": _style["axes.titlesize"]},
            },
            "xaxis": axis,
            "yaxis": axis,
            "scene": {"xaxis": scene_axis, "yaxis": scene_axis, "zaxis": scene_axis},
            "polar": {
                "bgcolor": background,
                "angularaxis": {
                    "gridcolor": grid,
                    "linecolor": edge,
                    "tickcolor": edge,
                },
                "radialaxis": {"gridcolor": grid, "linecolor": edge, "tickcolor": edge},
            },
            "legend": {"bgcolor": "rgba(0,0,0,0)", "font": {"color": label}},
            "hoverlabel": {
                "bgcolor": _hex(_nord_named["nord1"]),
                "bordercolor": edge,
                "font": {"color": _hex(_nord_named["nord6"])},
            },
            "colorscale": {
                "sequential": sequential,
                "sequentialminus": sequential,
                "diverging": COLORSCALES["nord_div"],
            },
            "coloraxis": {"colorbar": colourbar},
        },
        data={
            "heatmap": [go.Heatmap(**continuous)],
            "contour": [go.Contour(**continuous)],
            "surface": [go.Surface(**continuous)],
            "histogram2d": [go.Histogram2d(**continuous)],
            "histogram2dcontour": [go.Histogram2dContour(**continuous)],
        },
    )


TEMPLATE = _build_template()
pio.templates["nord_dark"] = TEMPLATE

__all__ = ["COLORSCALES", "COLORWAY", "COLOURS", "TEMPLATE"]
