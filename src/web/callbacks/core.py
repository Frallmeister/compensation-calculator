"""Callbacks for the offer comparison dashboard."""

from dash import Dash, Input, Output, State, dcc, html
from offers.companies.visionite import calc_compensation
from web.ids import Ids
from web.layout.charts import build_return_dist_plot
from web.layout.tables import build_total_compensation_table


def register_callbacks(
    app: Dash,
) -> None:
    """Register callbacks for the offer comparison view."""
    @app.callback(
        Output(Ids.COMPENSATION_TABLE, "children"),
        Input(Ids.TABLE_BUTTON, "n_clicks"),
        State(Ids.HOURLY_RATE, "value"),
        State(Ids.PENSION, "value"),
        State(Ids.DEFERRED_INCOME, "value"),
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
        Output(Ids.MONTHLY_RETURN_DIST, "children"),
        Input(Ids.SIMULATION_BUTTON, "n_clicks"),
        State(Ids.MONTHLY_RETURN, "value"),
        State(Ids.MONTHLY_VOLATILITY, "value"),
    )
    def plot_monthyl_return_figure(n_clicks: int, mean: float, std: float) -> dcc.Graph:
        return build_return_dist_plot(mean=mean, std=std)
