"""Chart builders for the dashboard."""

import numpy as np
import plotly.graph_objects as go
from dash import dcc
from scipy import stats

CHART_COLORS = {
    "text": "#111827",
    "muted": "#6b7280",
    "grid": "#e5e7eb",
    "accent": "#636efa",
    "accent_soft": "rgba(99, 110, 250, 0.14)",
    "reference": "#374151",
    "surface": "#ffffff",
}


def hex_to_rgba(hex_color: str, alpha: float) -> str:
    hex_color = hex_color.lstrip("#")
    r, g, b = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r}, {g}, {b}, {alpha})"


def apply_card_figure_style(fig: go.Figure) -> go.Figure:
    """Apply common dashboard-card styling to a Plotly figure."""
    fig.update_layout(
        template="plotly_white",
        autosize=True,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=CHART_COLORS["surface"],
        font={
            "family": (
                "Inter, system-ui, -apple-system, BlinkMacSystemFont, "
                "'Segoe UI', sans-serif"
            ),
            "size": 12,
            "color": CHART_COLORS["text"],
        },
        margin={
            "t": 12,
            "r": 18,
            "b": 42,
            "l": 54,
        },
        hovermode="x unified",
        showlegend=False,
        modebar_remove=[
            "zoom",
            "zoomIn",
            "zoomOut",
            "pan",
            "select2d",
            "lasso2d",
            "autoScale2d",
        ],
        hoverlabel={
            "bgcolor": hex_to_rgba("#333333", 0.1),
            "bordercolor": hex_to_rgba("#333333", 0.5),
        },
    )

    fig.update_xaxes(
        showline=False,
        showgrid=False,
        zeroline=False,
        ticks="outside",
        tickcolor=CHART_COLORS["grid"],
        tickfont={"color": CHART_COLORS["muted"], "size": 11},
        title_font={"color": CHART_COLORS["muted"], "size": 14},
        automargin=True,
    )

    fig.update_yaxes(
        showline=False,
        showgrid=True,
        gridcolor=CHART_COLORS["grid"],
        gridwidth=1,
        zeroline=False,
        ticks="outside",
        tickcolor=CHART_COLORS["grid"],
        tickfont={"color": CHART_COLORS["muted"], "size": 11},
        title_font={"color": CHART_COLORS["muted"], "size": 14},
        automargin=True,
    )

    return fig


def build_mc_paths_plot(p5: np.ndarray, p50: np.ndarray, p95: np.ndarray) -> dcc.Graph:
    fig = go.Figure()
    x = np.arange(len(p5)) + 1

    # Upper boundary of the band.
    # This trace is invisible but needed as the first edge.
    fig.add_trace(
        go.Scatter(
            x=x,
            y=p95,
            mode="lines",
            line={"width": 0, "shape": "hv"},
            showlegend=False,
            hoverinfo="skip",
        ),
    )

    # Lower boundary of the band.
    # fill="tonexty" fills the area to the previous trace, i.e. p95.
    fig.add_trace(
        go.Scatter(
            x=x,
            y=p5,
            mode="lines",
            line={"width": 0, "shape": "hv"},
            fill="tonexty",
            fillcolor=hex_to_rgba(CHART_COLORS["accent"], 0.2),
            name="5th–95th percentile",
            hoverinfo="skip",
        ),
    )

    # Median line.
    fig.add_trace(
        go.Scatter(
            x=x,
            y=p50,
            mode="lines",
            name="Median",
            line={
                "color": CHART_COLORS["accent"],
                "width": 3,
                "shape": "hv",
            },
            hovertemplate=(
                "<b>Median: %{y:,.0f} kr</b>"
                "<extra></extra>"
            ),
        ),
    )

    fig.add_hline(y=0, line_color="black", line_width=1)

    fig.update_xaxes(title_text="Months")
    fig.update_yaxes(title_text="Advantage of <br>immediate withdrawal (kr)")

    fig = apply_card_figure_style(fig)
    return dcc.Graph(
        className="card-graph",
        figure=fig,
        mathjax=True,
        responsive=True,
        config={
            "responsive": True,
            "displaylogo": False,
        },
    )

def build_final_income_plot(immediate: np.ndarray, deferred: np.ndarray) -> dcc.Graph:
    fig = go.Figure()
    fig.add_histogram(
        x=immediate / 1000,
        name="Immediate",
    )
    fig.add_histogram(
        x=deferred / 1000,
        name="Deferred",
    )

    fig.update_layout(barmode="overlay")
    fig.update_traces(
        opacity=0.75,
        histnorm="probability",
        hovertemplate=(
            "<b>Value: %{x:,.0f} tkr<br></b>"
            "<extra></extra>"
        ),
    )

    fig.update_xaxes(title_text="Final net income (tkr)")

    fig.update_yaxes(
        title_text="Density",
    )

    fig = apply_card_figure_style(fig)
    return dcc.Graph(
        className="card-graph",
        figure=fig,
        mathjax=True,
        responsive=True,
        config={
            "responsive": True,
            "displaylogo": False,
        },
    )


def build_final_advantage_plot(arr: np.ndarray) -> dcc.Graph:
    # Calculate cumulative histogram
    x = np.sort(arr) * 1e-3
    y = np.arange(1, len(x) + 1) / len(x)

    fig = go.Figure()
    fig.add_scatter(
        x=x,
        y=y,
        mode="lines",
        line={
            "color": "#636efa",
            "width": 3,
            "shape": "hv",  # step-like empirical CDF
        },
        fill="tozeroy",
        fillcolor="rgba(99, 110, 250, 0.14)",
        hovertemplate=(
            "<b>Value: %{x:,.1f} tkr<br>"
            "Density: %{y:.0%}</b>"
            "<extra></extra>"
        ),
    )

    idx = np.argmin(np.abs(x))
    y0 = round(100 * y[idx])
    fig.add_vline(
        x=0,
        line_width=1,
        line_dash="dash",
        line_color=CHART_COLORS["reference"],
        annotation_text=f"0 kr, {y0} %",
        annotation_position="top",
        annotation_font={
            "size": 11,
            "color": CHART_COLORS["muted"],
        },
    )

    fig.update_xaxes(title_text="Δ income (tkr)<br>Immediate salary →")

    fig.update_yaxes(
        title_text="Density",
        tickformat=".0%",
    )

    fig = apply_card_figure_style(fig)
    return dcc.Graph(
        className="card-graph",
        figure=fig,
        mathjax=True,
        responsive=True,
        config={
            "responsive": True,
            "displaylogo": False,
        },
    )


def build_return_dist_plot(mean: float, std: float) -> dcc.Graph:
    """Plot the figure that shows how the stochastic monthly return is distributed."""
    xwidth = 3 * std
    xmin = min(mean - xwidth, -10)
    xmax = max(mean + xwidth, 10)

    x = np.linspace(xmin, xmax, 1000)
    y = stats.norm.cdf(x, loc=mean, scale=std)

    fig = go.Figure()

    fig.add_scatter(
        x=x,
        y=y,
        mode="lines",
        line={
            "color": CHART_COLORS["accent"],
            "width": 3,
            "shape": "spline",
            "smoothing": 0.7,
        },
        fill="tozeroy",
        fillcolor=CHART_COLORS["accent_soft"],
        hovertemplate=(
            "<b>Monthly return: %{x:.2f}%<br>"
            "Probability: %{y:.1%}</b>"
            "<extra></extra>"
        ),
    )

    fig.add_vline(
        x=0,
        line_width=1,
        line_dash="dash",
        line_color=CHART_COLORS["reference"],
        annotation_text="0%",
        annotation_position="top",
        annotation_font={
            "size": 11,
            "color": CHART_COLORS["muted"],
        },
    )

    fig.update_xaxes(
        title_text=r"$r\ \mathrm{[\%]}$",
        range=[xmin, xmax],
    )

    fig.update_yaxes(
        title_text=r"$P(X \le r)$",
        range=[0, 1],
        tickformat=".0%",
    )

    fig = apply_card_figure_style(fig)

    return dcc.Graph(
        className="card-graph",
        figure=fig,
        mathjax=True,
        responsive=True,
        config={
            "responsive": True,
            "displaylogo": False,
        },
    )
