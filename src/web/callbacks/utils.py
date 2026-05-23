"""Functions and utilities used in the callbacks that doesn't fit anywhere else."""

from offers.companies.visionite import (
    SimulationConfig,
    StrategyMonteCarlo,
)
import numpy as np


def run_monte_carlo_simulation(
    total_income: int,
    pension: int,
    monthly_salary_investment: int,
    monthly_mean_return: float,
    monthly_volatility: float,
    months_between_withdrawals: int,
    n_months: int,
    n_simulations: int,
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