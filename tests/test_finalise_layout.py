"""Tests for ``nord_mpl.finalise_layout`` and its wrapper ``nord_mpl.show``.

The Nord theme carries two aquarel transforms that need opposite positions
relative to ``Figure.tight_layout()``: ``offset`` moves labels, so the layout
must follow it; ``trim`` reads tick positions, so it must follow the layout.
Each behaviour is tested alongside a companion showing that the naive call
order fails on the same figure, so the tests cannot pass vacuously.

All figures use synthetic data and the Agg backend. ``plt.show`` is replaced
in the ``show`` tests, since Agg cannot display a figure.
"""

import copy
from collections.abc import Iterator

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pytest
from aquarel import Theme
from matplotlib.figure import Figure
from matplotlib.text import Text

import nord_mpl


@pytest.fixture
def theme() -> Iterator[Theme]:
    """Nord theme applied inside an rc context, with figures closed afterwards."""
    with matplotlib.rc_context():
        nord_theme = nord_mpl.load_nord_theme()
        nord_theme.apply()
        yield nord_theme
        plt.close("all")


def _twin_axis_figure() -> tuple[Figure, Text, Text]:
    """Two panels whose facing y labels sit either side of the gutter.

    Returns:
        The figure, the left panel's twin-axis y label, and the right panel's
        y label.
    """
    x = np.linspace(0.0, 0.8, 9)
    fig, (left, right) = plt.subplots(1, 2, figsize=(9, 4.5))
    left.plot(x, 75.0 + 30.0 * x)
    left.set(xlabel="share", ylabel="left axis")
    twin = left.twinx()
    twin.plot(x, 2700.0 + 1300.0 * x)
    twin.set_ylabel("twin axis")
    right.plot(x, 8000.0 + 200.0 * x)
    right.set(xlabel="share", ylabel="right axis")
    return fig, twin.yaxis.label, right.yaxis.label


def _narrow_axes_figure() -> Figure:
    """One panel squeezed to a sliver, so that the layout changes its ticks.

    The axes start a twentieth of the figure wide. ``tight_layout`` then
    widens them roughly tenfold, and the tick locator picks more ticks.
    """
    fig, ax = plt.subplots()
    fig.subplots_adjust(left=0.45, right=0.50)
    ax.plot(np.linspace(0.0, 0.8, 9), np.linspace(0.0, 1.0, 9))
    return fig


def _overlap(fig: Figure, first: Text, second: Text) -> bool:
    """Whether the drawn bounding boxes of two texts intersect."""
    fig.canvas.draw()
    a, b = first.get_window_extent(), second.get_window_extent()
    return min(a.x1, b.x1) > max(a.x0, b.x0) and min(a.y1, b.y1) > max(a.y0, b.y0)


def _x_spine_ends_on_drawn_ticks(fig: Figure) -> bool:
    """Whether every bottom spine spans exactly its first to last drawn tick."""
    fig.canvas.draw()
    for ax in fig.axes:
        lower, upper = sorted(ax.get_xlim())
        ticks = np.asarray(ax.xaxis.get_majorticklocs())
        drawn = ticks[(ticks >= lower) & (ticks <= upper)]
        bounds = ax.spines["bottom"].get_bounds()
        if bounds is None or not np.allclose(bounds, (drawn[0], drawn[-1])):
            return False
    return True


def test_layout_accounts_for_spine_offset(theme: Theme) -> None:
    fig, twin_label, right_label = _twin_axis_figure()

    nord_mpl.finalise_layout(theme)

    assert not _overlap(fig, twin_label, right_label)


def test_layout_before_transforms_collides(theme: Theme) -> None:
    """Companion: the naive order puts the facing labels on top of each other."""
    fig, twin_label, right_label = _twin_axis_figure()

    fig.tight_layout()
    theme.apply_transforms()

    assert _overlap(fig, twin_label, right_label)


def test_trimmed_spines_end_on_drawn_ticks(theme: Theme) -> None:
    fig = _narrow_axes_figure()

    nord_mpl.finalise_layout(theme)

    assert _x_spine_ends_on_drawn_ticks(fig)


def test_transforms_before_layout_leaves_stale_trim(theme: Theme) -> None:
    """Companion: trimming first leaves the spine on ticks the layout replaced."""
    fig = _narrow_axes_figure()

    theme.apply_transforms()
    fig.tight_layout()

    assert not _x_spine_ends_on_drawn_ticks(fig)


def test_theme_without_transforms_still_gets_layout(theme: Theme) -> None:
    theme.transforms = {}
    fig, ax = plt.subplots()
    ax.set(xlabel="x", ylabel="y")
    position_before = ax.get_position().bounds

    nord_mpl.finalise_layout(theme)

    assert not np.allclose(ax.get_position().bounds, position_before)
    assert ax.spines["bottom"].get_bounds() is None
    assert fig is plt.gcf()


def test_theme_transforms_are_not_modified(theme: Theme) -> None:
    transforms_before = copy.deepcopy(theme.transforms)
    plt.subplots()

    nord_mpl.finalise_layout(theme)

    assert theme.transforms == transforms_before


def test_show_finalises_layout_before_displaying(
    theme: Theme, monkeypatch: pytest.MonkeyPatch
) -> None:
    fig = _narrow_axes_figure()
    trimmed_at_display: list[bool] = []
    monkeypatch.setattr(
        plt,
        "show",
        lambda: trimmed_at_display.append(_x_spine_ends_on_drawn_ticks(fig)),
    )

    nord_mpl.show(theme)

    assert trimmed_at_display == [True]


def test_show_without_theme_uses_packaged_transforms(
    theme: Theme, monkeypatch: pytest.MonkeyPatch
) -> None:
    fig, twin_label, right_label = _twin_axis_figure()
    monkeypatch.setattr(plt, "show", lambda: None)

    nord_mpl.show()

    assert not _overlap(fig, twin_label, right_label)
    assert fig.axes[0].spines["bottom"].get_bounds() is not None


def test_show_with_explicit_theme_uses_that_theme(
    theme: Theme, monkeypatch: pytest.MonkeyPatch
) -> None:
    theme.transforms = {}
    _, ax = plt.subplots()
    monkeypatch.setattr(plt, "show", lambda: None)

    nord_mpl.show(theme)

    assert ax.spines["bottom"].get_bounds() is None
