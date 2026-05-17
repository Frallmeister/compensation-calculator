"""Monte Carlo simulation for immediate vs deferred withdrawal strategies."""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .core import calc_compensation


@dataclass(frozen=True)
class SimulationConfig:
    total_income: int
    pension: int
    car_cost: int
    monthly_salary_investment: int
    monthly_mean_return: float
    monthly_volatility: float
    months_between_withdrawals: int
    n_months: int
    n_simulations: int


@dataclass(frozen=True)
class SimulationResult:
    immediate_withdrawal_values: np.ndarray
    deferred_withdrawal_values: np.ndarray
    sampled_monthly_profits: np.ndarray
    configs: SimulationConfig

    @property
    def final_immediate_withdrawal_values(self) -> np.ndarray:
        """Final-month outcomes for the immediate-withdrawal strategy."""
        return self.immediate_withdrawal_values[:, -1]

    @property
    def final_deferred_withdrawal_values(self) -> np.ndarray:
        """Final-month outcomes for the deferred-withdrawal strategy."""
        return self.deferred_withdrawal_values[:, -1]

    @property
    def advantage(self) -> np.ndarray:
        """Path-wise strategy advantage: immediate minus deferred withdrawal."""
        return self.immediate_withdrawal_values - self.deferred_withdrawal_values

    @property
    def final_advantage(self) -> np.ndarray:
        """Final-month paired difference: immediate minus deferred withdrawal."""
        return self.final_immediate_withdrawal_values - self.final_deferred_withdrawal_values

    @property
    def probability_immediate_beats_deferred(self) -> float:
        return float(np.mean(self.final_advantage > 0))

    @property
    def mean_final_advantage(self) -> int:
        return round(np.mean(self.final_advantage))

    @property
    def median_final_advantage(self) -> int:
        return round(np.median(self.final_advantage))

    @property
    def final_advantage_std(self) -> float:
        return float(np.std(self.final_advantage, ddof=1))

    @property
    def paired_effect_size(self) -> float:
        """Paired Cohen's d (dz) for final-month strategy advantage."""
        std = self.final_advantage_std
        if np.isclose(std, 0.0):
            return float(np.nan)
        return self.mean_final_advantage / std

    @property
    def final_advantage_skewness(self) -> float:
        """Sample skewness of the final-month strategy advantage."""
        diff = self.final_advantage
        centered = diff - np.mean(diff)
        m2 = np.mean(centered**2)
        if np.isclose(m2, 0.0):
            return float(np.nan)
        m3 = np.mean(centered**3)
        return float(m3 / (m2 ** 1.5))

    @staticmethod
    def _distribution_stats(values: np.ndarray) -> dict[str, float]:
        return {
            "mean": float(np.mean(values)),
            "std": float(np.std(values, ddof=1)),
            "p05": float(np.percentile(values, 5)),
            "p25": float(np.percentile(values, 25)),
            "p50": float(np.percentile(values, 50)),
            "p75": float(np.percentile(values, 75)),
            "p95": float(np.percentile(values, 95)),
        }

    @property
    def summary_table(self) -> pd.DataFrame:
        """Summary stats for final outcomes and paired strategy advantage."""
        table = pd.DataFrame(
            {
                "immediate_withdrawal_final": self._distribution_stats(
                    self.final_immediate_withdrawal_values,
                ),
                "deferred_withdrawal_final": self._distribution_stats(
                    self.final_deferred_withdrawal_values,
                ),
                "advantage_final": self._distribution_stats(self.final_advantage),
            },
        )
        table = table.div(1000).round(1)

        table.loc["win_probability_immediate_withdrawal"] = [
            np.nan,
            np.nan,
            round(self.probability_immediate_beats_deferred, 2),
        ]
        table.loc["paired_effect_size_dz"] = [
            np.nan,
            np.nan,
            round(self.paired_effect_size, 2),
        ]
        table.loc["advantage_skewness"] = [
            np.nan,
            np.nan,
            round(self.final_advantage_skewness, 2),
        ]
        return table


@dataclass(frozen=True, slots=True)
class ExperimentRun:
    immediate_withdrawal_results: np.ndarray
    deferred_withdrawal_results: np.ndarray

    @property
    def salary_now_results(self) -> np.ndarray:
        return self.immediate_withdrawal_results

    @property
    def salary_later_results(self) -> np.ndarray:
        return self.deferred_withdrawal_results

class StrategyMonteCarlo:
    """Monte Carlo simulation comparing different strategies."""

    def __init__(self, config: SimulationConfig) -> None:
        """Initialize a Monte-Carlo simulator.

        Specify the configuration with a SimulationConfig class.

        Run the simulation with the `run()` method. The results are returned as a
        SimulationResult object that can be used to further analyze the results.
        """
        self.config = config

    def run(self) -> SimulationResult:
        """Run the simulation."""
        cfg = self.config
        immediate_withdrawal_values = np.zeros((cfg.n_simulations, cfg.n_months))
        deferred_withdrawal_values = np.zeros((cfg.n_simulations, cfg.n_months))
        sampled_monthly_profits = self._monthly_returns()

        for isim, profits in enumerate(sampled_monthly_profits):
            res = self._run_one_experiment(profits=profits)
            immediate_withdrawal_values[isim] = res.immediate_withdrawal_results
            deferred_withdrawal_values[isim] = res.deferred_withdrawal_results

        return SimulationResult(
            immediate_withdrawal_values=immediate_withdrawal_values,
            deferred_withdrawal_values=deferred_withdrawal_values,
            sampled_monthly_profits=sampled_monthly_profits,
            configs=cfg,
        )

    def _monthly_returns(self) -> np.ndarray:
        """Sample all monthly returns for all months and simulations.

        The values are returns in a (n_simulations, n_months) numpy array.
        """
        cfg = self.config
        loc = cfg.monthly_mean_return
        scale = cfg.monthly_volatility
        size = (cfg.n_simulations, cfg.n_months)
        rng = np.random.default_rng()
        return 1.0 + rng.normal(loc=loc, scale=scale, size=size)

    def _run_one_experiment(self, profits: np.ndarray) -> ExperimentRun:
        immediate_withdrawal_results = self._simulate_immediate_withdrawal(profits)
        deferred_withdrawal_results = self._simulate_deferred_withdrawal(profits)
        return ExperimentRun(
            immediate_withdrawal_results=immediate_withdrawal_results,
            deferred_withdrawal_results=deferred_withdrawal_results,
        )

    def _simulate_immediate_withdrawal(self, profits: np.ndarray) -> np.ndarray:
        cfg = self.config

        # Assuming the same salary each month
        compensation = calc_compensation(
            income=cfg.total_income,
            pension=cfg.pension,
            pot=0,
            car=cfg.car_cost,
        )
        net_salary = compensation.net_salary
        net_salary_after_savings = (net_salary - cfg.monthly_salary_investment)
        total_savings = (np.ones(cfg.n_months) * net_salary_after_savings).cumsum()

        portfolio = 0.0
        for i in range(cfg.n_months):
            portfolio += cfg.monthly_salary_investment
            portfolio *= profits[i]
            total_savings[i] += portfolio
        return total_savings

    def _simulate_deferred_withdrawal(self, profits: np.ndarray) -> np.ndarray:
        cfg = self.config

        portfolio = 0.0
        accumulated_salary = 0
        total_savings = np.zeros(cfg.n_months)
        deposit = 0.0
        for imonth in range(cfg.n_months):
            is_withdrawing_month = (
                (imonth + 1) % cfg.months_between_withdrawals == 0
                or imonth == cfg.n_months - 1
            )

            if is_withdrawing_month:
                pot = 0
                portfolio += (1 - 0.54) * deposit
                deposit = 0.0
            else:
                pot = cfg.monthly_salary_investment
                deposit += cfg.monthly_salary_investment

            compensation = calc_compensation(
                income=cfg.total_income,
                pension=cfg.pension,
                pot=pot,
                car=cfg.car_cost,
            )
            portfolio *= profits[imonth]
            accumulated_salary += compensation.net_salary
            total_savings[imonth] = accumulated_salary + portfolio
        return total_savings
