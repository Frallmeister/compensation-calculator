"""Callbacks for the offer comparison dashboard."""

from dash import Dash, Input, Output, State, dcc, html
import numpy as np
from offers.companies.visionite import (
    calc_compensation,
)
from web.callbacks.utils import run_monte_carlo_simulation
from web.ids import Ids
from web.layout.charts import (
    build_final_advantage_plot,
    build_final_income_plot,
    build_mc_paths_plot,
    build_return_dist_plot,
)
from web.layout.tables import build_total_compensation_table


MONTHLY_BILLABLE_HOURS = 134.4
N_SIMULATIONS = 10000

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
        prevent_initial_call=True,
    )
    def update_compensation_table(
        n_clicks: int,
        hourly_rate: int,
        pension: int,
        deferred: int,
    ) -> html.Table:
        total_income = round(MONTHLY_BILLABLE_HOURS * hourly_rate)
        total_compensation = calc_compensation(
            income=total_income,
            pension=pension,
            pot=deferred,
            car=0,
        )

        return build_total_compensation_table(total_compensation)


    @app.callback(
        Output(Ids.MONTE_CARLO_SIMULATION_PATHS, "children"),
        Input(Ids.MONTE_CARLO_RESULTS_STORE, "data"),
        prevent_initial_call=True,
    )
    def plot_monte_carlo_paths(data: dict):
        percentiles = data["percentiles"]
        p5 = np.asarray(percentiles["p5"])
        p50 = np.asarray(percentiles["p50"])
        p95 = np.asarray(percentiles["p95"])
        return build_mc_paths_plot(p5=p5, p50=p50, p95=p95)


    @app.callback(
        Output(Ids.MONTE_CARLO_FINALS, "children"),
        Input(Ids.MONTE_CARLO_RESULTS_STORE, "data"),
        prevent_initial_call=True,
    )
    def plot_final_income_distribution(data: dict):
        arr_immediate = np.asarray(data["immediate"])
        arr_deferred = np.asarray(data["deferred"])
        return build_final_income_plot(immediate=arr_immediate, deferred=arr_deferred)


    @app.callback(
        Output(Ids.MONTE_CARLO_ADVANTAGE, "children"),
        Input(Ids.MONTE_CARLO_RESULTS_STORE, "data"),
        prevent_initial_call=True,
    )
    def plot_advantage_plot(data: dict):
        arr = np.asarray(data["advantage"])
        return build_final_advantage_plot(arr=arr)


    @app.callback(
        Output(Ids.MONTHLY_RETURN_DIST, "children"),
        Input(Ids.SIMULATION_BUTTON, "n_clicks"),
        State(Ids.MONTHLY_RETURN, "value"),
        State(Ids.MONTHLY_VOLATILITY, "value"),
        prevent_initial_call=True,
    )
    def plot_monthly_return_figure(n_clicks: int, mean: float, std: float) -> dcc.Graph:
        return build_return_dist_plot(mean=mean, std=std)


    @app.callback(
        Output(Ids.SIMULATION_BUTTON, "disabled"),
        Input(Ids.TABLE_BUTTON, "n_clicks"),
        prevent_initial_call=True,
    )
    def enable_simulation_button(n_clicks: int) -> bool:
        return not n_clicks


    @app.callback(
        Output(Ids.MONTE_CARLO_RESULTS_STORE, "data"),
        Input(Ids.SIMULATION_BUTTON, "n_clicks"),
        State(Ids.HOURLY_RATE, "value"),
        State(Ids.PENSION, "value"),
        State(Ids.MONTHLY_INVESTMENT, "value"),
        State(Ids.MONTHLY_RETURN, "value"),
        State(Ids.MONTHLY_VOLATILITY, "value"),
        State(Ids.MONTHS_TO_WITHDRAWAL, "value"),
        State(Ids.MONTHS_TO_SIMULATE, "value"),
        prevent_initial_call=True,
    )
    def write_mc_res_to_store(
        n_clicks,
        hourly_rate,
        pension,
        monthly_salary_investment,
        monthly_mean_return,
        monthly_volatility,
        months_between_withdrawals,
        n_months,
    ) -> dict:
        """Run the Monte Carlo simulation and write the results to the dcc.Store."""
        return run_monte_carlo_simulation(
            total_income=round(MONTHLY_BILLABLE_HOURS * hourly_rate),
            pension=pension,
            monthly_salary_investment=monthly_salary_investment,
            monthly_mean_return=monthly_mean_return / 100,
            monthly_volatility=monthly_volatility / 100,
            months_between_withdrawals=months_between_withdrawals,
            n_months=n_months,
            n_simulations=N_SIMULATIONS,
        )
