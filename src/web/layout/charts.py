"""Chart builders for the dashboard."""

from dash import dcc
import numpy as np
import plotly.graph_objects as go
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
    )

    fig.update_xaxes(
        showline=False,
        showgrid=False,
        zeroline=False,
        ticks="outside",
        tickcolor=CHART_COLORS["grid"],
        tickfont={"color": CHART_COLORS["muted"], "size": 11},
        title_font={"color": CHART_COLORS["muted"], "size": 12},
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
        title_font={"color": CHART_COLORS["muted"], "size": 12},
        automargin=True,
    )

    return fig


def build_return_dist_plot(mean: float, std: float) -> dcc.Graph:
    xwidth = 3 * std
    xmin = min(mean - xwidth, -20)
    xmax = max(mean + xwidth, 20)

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
            "Monthly return: %{x:.2f}%<br>"
            "Probability: %{y:.1%}"
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
            "modeBarButtonsToRemove": [
                "select2d",
                "lasso2d",
                "autoScale2d",
            ],
        },
    )