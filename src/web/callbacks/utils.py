"""Functions and utilities used in the callbacks that doesn't fit anywhere else."""

import numpy as np
from dash.exceptions import PreventUpdate

from offers.companies.visionite import (
    SimulationConfig,
    StrategyMonteCarlo,
)

MONTHLY_BILLABLE_HOURS = 8 * 21


def calculate_monthly_income(hourly_rate: int, consultant_share: float | None) -> int:
    """Apply the consultant's share to revenue from a full working month."""
    if consultant_share is None or not 0 <= consultant_share <= 100:
        raise PreventUpdate
    return round(MONTHLY_BILLABLE_HOURS * hourly_rate * consultant_share / 100)


def run_monte_carlo_simulation(
    total_income: int,
    pension: int,
    monthly_salary_investment: int,
    monthly_mean_return: float,
    monthly_volatility: float,
    months_between_withdrawals: int,
    n_months: int,
    n_simulations: int,
    table_no: int = 33,
) -> dict:
    """Run the Monte carlo simulation and return a dict with results for dcc.Store."""
    config = SimulationConfig(
        total_income=total_income,
        pension=pension,
        car_cost=0,
        monthly_salary_investment=monthly_salary_investment,
        monthly_mean_return=monthly_mean_return,
        monthly_volatility=monthly_volatility,
        months_between_withdrawals=months_between_withdrawals,
        n_months=n_months,
        n_simulations=n_simulations,
        table_no=table_no,
    )

    sim = StrategyMonteCarlo(config)
    res = sim.run()
    return {
        "immediate": res.final_immediate_withdrawal_values,
        "deferred": res.final_deferred_withdrawal_values,
        "advantage": res.final_advantage,
        "percentiles": {
            "p5": np.percentile(res.advantage, 5, axis=0),
            "p50": np.percentile(res.advantage, 50, axis=0),
            "p95": np.percentile(res.advantage, 95, axis=0),
        },
    }
