"""Chart builders for the dashboard."""

from dash import dcc
import numpy as np
import plotly.graph_objects as go
from scipy import stats


def build_return_dist_plot(mean: float, std: float) -> dcc.Graph:
    xwidth = 3 * std
    xmin = min(mean - xwidth, -20)
    xmax = max(mean + xwidth, 20)
    x = np.linspace(xmin, xmax, 1000)
    y = stats.norm.cdf(x, loc=mean, scale=std)

    fig = go.Figure()
    fig.add_scatter(x=x, y=y)
    fig.add_vline(0, line_color="black")
    fig.update_yaxes(title_text=r"$P(X \le r)$")
    fig.update_xaxes(title_text="<i>r</i> (%)", range=[xmin, xmax])
    fig.update_layout(
        margin={
            "t": 0,
            "r": 0,
            "b": 0,
            "l": 0,
        },
    )
    return dcc.Graph(
        className="card-graph",
        figure=fig,
        mathjax=True,
        responsive=True,
        config={"responsive": True},
    )
