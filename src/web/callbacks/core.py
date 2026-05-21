"""Callbacks for the offer comparison dashboard."""

from dash import Dash, dcc, html, Input, Output, State
from offers.companies.visionite import calc_compensation
from web.ids import Ids
from web.layout.charts import build_return_dist_plot
from web.layout.tables import build_total_compensation_table


def register_callbacks(
    app: Dash,
) -> None:
    """Register callbacks for the offer comparison view."""
    @app.callback(
        Output("compensation-table-id", "children"),
        Input("table-button-id", "n_clicks"),
        State("hourly-rate-id", "value"),
        State("pension-id", "value"),
        State("deferred-id", "value"),
    )
    def update_compensation_table(
        n_clicks: int,
        hourly_rate: int,
        pension: int,
        deferred: int,
    ) -> html.Table:
        total_income = round(134.4 * hourly_rate)
        total_compensation = calc_compensation(
            income=total_income,
            pension=pension,
            pot=deferred,
            car=0,
        )

        return build_total_compensation_table(total_compensation)

    @app.callback(
        Output("monthy-return-distribution-id", "children"),
        Input("simulation-button-id", "n_clicks"),
        State("monthly-return-id", "value"),
        State("monthly-volatility-id", "value"),
    )
    def plot_monthyl_return_figure(n_clicks: int, mean: float, std: float) -> dcc.Graph:
        return build_return_dist_plot(mean=mean, std=std)
