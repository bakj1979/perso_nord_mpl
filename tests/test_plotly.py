"""Tests for ``nord_mpl.plotly``, the Plotly counterpart of the Nord style.

Colours are checked against the matplotlib side of the package (the
``nord-dark`` stylesheet, the registered colormaps and named colours) so the
two front ends cannot drift apart. Plotly Express is exercised directly, since
it resolves template defaults differently from ``graph_objects``.
"""

import importlib
import sys
from collections.abc import Iterator, Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import pytest

import nord_mpl
import nord_mpl.plotly as nord_plotly

COLORMAP_NAMES = (
    "nord_seq",
    "nord_frost",
    "nord_aurora",
    "nord_div",
    "nord_qual",
    "nord_mono",
)


def _hex(colour: str) -> str:
    """Return a colour as a lower-case ``#rrggbb`` string.

    Args:
        colour: Any colour string matplotlib accepts, with or without ``#``.

    Returns:
        The normalised hex string.
    """
    if not colour.startswith("#") and len(colour) == 6:
        colour = f"#{colour}"
    return mcolors.to_hex(colour)


def _as_pairs(scale: Sequence[Sequence[object]]) -> list[tuple[float, str]]:
    """Normalise a Plotly colourscale to a list of ``(position, hex)`` pairs.

    Args:
        scale: Colourscale as Plotly returns it, lists or tuples.

    Returns:
        Comparable list of pairs.
    """
    return [(float(position), _hex(str(colour))) for position, colour in scale]


@pytest.fixture
def style() -> dict:
    """The rcParams of the registered ``nord-dark`` stylesheet."""
    return plt.style.library["nord-dark"]


@pytest.fixture
def template() -> go.layout.Template:
    """The registered ``nord_dark`` Plotly template."""
    return pio.templates["nord_dark"]


@pytest.fixture
def restore_default_template() -> Iterator[None]:
    """Restore Plotly's default template after a test changes it."""
    previous = pio.templates.default
    yield
    pio.templates.default = previous


def test_template_is_registered_without_becoming_default() -> None:
    assert "nord_dark" in pio.templates
    assert pio.templates.default != "nord_dark"


def test_colorway_matches_stylesheet_cycle(
    template: go.layout.Template, style: dict
) -> None:
    stylesheet_cycle = [_hex(c) for c in style["axes.prop_cycle"].by_key()["color"]]
    assert [_hex(c) for c in template.layout.colorway] == stylesheet_cycle
    assert list(nord_plotly.COLORWAY) == stylesheet_cycle


def test_backgrounds_and_text_match_stylesheet(
    template: go.layout.Template, style: dict
) -> None:
    assert _hex(template.layout.paper_bgcolor) == _hex(style["figure.facecolor"])
    assert _hex(template.layout.plot_bgcolor) == _hex(style["axes.facecolor"])
    assert _hex(template.layout.font.color) == _hex(style["text.color"])
    assert _hex(template.layout.xaxis.gridcolor) == _hex(style["grid.color"])
    assert _hex(template.layout.xaxis.linecolor) == _hex(style["axes.edgecolor"])


def test_named_colours_match_matplotlib() -> None:
    assert set(nord_plotly.COLOURS) == {f"nord{i}" for i in range(16)}
    for name, colour in nord_plotly.COLOURS.items():
        assert colour == mcolors.to_hex(name)


def test_named_colours_are_read_only() -> None:
    with pytest.raises(TypeError):
        nord_plotly.COLOURS["nord0"] = "#000000"  # type: ignore[index]


@pytest.mark.parametrize("name", COLORMAP_NAMES)
def test_colourscales_cover_unit_interval(name: str) -> None:
    for scale_name in (name, f"{name}_r"):
        positions = [p for p, _ in nord_plotly.COLORSCALES[scale_name]]
        assert positions[0] == 0.0
        assert positions[-1] == 1.0
        assert positions == sorted(positions)


def _segment_nodes(cmap: mcolors.LinearSegmentedColormap) -> list[tuple[float, str]]:
    """Return a linear colormap's anchor points as ``(position, hex)`` pairs.

    Args:
        cmap: Colormap built with ``LinearSegmentedColormap.from_list``.

    Returns:
        The anchors, read from the colormap's segment data.
    """
    channels = [cmap._segmentdata[key] for key in ("red", "green", "blue")]
    return [
        (float(red[0]), mcolors.to_hex((red[1], green[1], blue[1])))
        for red, green, blue in zip(*channels)
    ]


@pytest.mark.parametrize("name", [n for n in COLORMAP_NAMES if n != "nord_qual"])
def test_colourscales_match_matplotlib_anchors(name: str) -> None:
    for scale_name in (name, f"{name}_r"):
        expected = _segment_nodes(plt.colormaps[scale_name])
        actual = nord_plotly.COLORSCALES[scale_name]
        assert [c for _, c in actual] == [c for _, c in expected]
        assert [p for p, _ in actual] == pytest.approx([p for p, _ in expected])


def test_qualitative_scale_is_stepped_over_listed_colours() -> None:
    listed = [mcolors.to_hex(c) for c in plt.colormaps["nord_qual"].colors]
    stops = nord_plotly.COLORSCALES["nord_qual"]
    assert len(stops) == 2 * len(listed)
    assert [colour for _, colour in stops[::2]] == listed
    assert [colour for _, colour in stops[1::2]] == listed


def test_reversed_scales_mirror_forward_scales() -> None:
    for name in COLORMAP_NAMES:
        forward = nord_plotly.COLORSCALES[name]
        reverse = nord_plotly.COLORSCALES[f"{name}_r"]
        assert [c for _, c in reverse] == [c for _, c in reversed(forward)]
        assert [p for p, _ in reverse] == pytest.approx(
            [1.0 - p for p, _ in reversed(forward)]
        )


def test_express_continuous_colour_uses_nord_seq() -> None:
    fig = px.scatter(
        x=[1, 2, 3], y=[1, 2, 3], color=[0.1, 0.5, 0.9], template="nord_dark"
    )
    assert _as_pairs(fig.layout.coloraxis.colorscale) == _as_pairs(
        nord_plotly.COLORSCALES["nord_seq"]
    )


def test_express_discrete_colour_follows_colorway() -> None:
    fig = px.line(
        x=[0, 1, 0, 1, 0, 1],
        y=[0, 1, 1, 2, 2, 3],
        color=["a", "a", "b", "b", "c", "c"],
        template="nord_dark",
    )
    assert [_hex(trace.line.color) for trace in fig.data] == list(
        nord_plotly.COLORWAY[:3]
    )


def test_express_honours_template_set_as_default(
    restore_default_template: None,
) -> None:
    pio.templates.default = "nord_dark"
    fig = px.scatter(x=[1, 2, 3], y=[1, 2, 3], color=[0.1, 0.5, 0.9])
    assert _as_pairs(fig.layout.coloraxis.colorscale) == _as_pairs(
        nord_plotly.COLORSCALES["nord_seq"]
    )


@pytest.mark.parametrize("trace_type", ["heatmap", "contour", "surface", "histogram2d"])
def test_graph_objects_traces_default_to_nord_seq(
    template: go.layout.Template, trace_type: str
) -> None:
    trace_defaults = getattr(template.data, trace_type)
    assert _as_pairs(trace_defaults[0].colorscale) == _as_pairs(
        nord_plotly.COLORSCALES["nord_seq"]
    )


def test_diverging_default_is_nord_div(template: go.layout.Template) -> None:
    assert _as_pairs(template.layout.colorscale.diverging) == _as_pairs(
        nord_plotly.COLORSCALES["nord_div"]
    )


def test_missing_plotly_raises_with_install_hint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(sys.modules, "plotly", None)
    monkeypatch.delitem(sys.modules, "nord_mpl.plotly")
    with pytest.raises(ImportError, match=r"nord-mpl\[plotly\]"):
        importlib.import_module("nord_mpl.plotly")
    monkeypatch.undo()
    assert importlib.import_module("nord_mpl.plotly") is nord_plotly


def test_package_version_is_bumped() -> None:
    assert nord_mpl.__version__ == "0.4.0"
