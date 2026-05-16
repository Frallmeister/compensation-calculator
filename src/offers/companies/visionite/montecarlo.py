"""Monte Carlo simulation to compare salary withdrawal and postponed salary."""

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
    salary_now_values: np.ndarray
    delayed_salary_values: np.ndarray
    sampled_monthly_profits: np.ndarray
    configs: SimulationConfig

    @property
    def final_salary_now_values(self) -> np.ndarray:
        """Final-month outcomes for strategy: withdraw as salary now."""
        return self.salary_now_values[:, -1]

    @property
    def final_delayed_salary_values(self) -> np.ndarray:
        """Final-month outcomes for strategy: keep in pot and withdraw later."""
        return self.delayed_salary_values[:, -1]

    @property
    def spread(self) -> np.ndarray:
        return self.salary_now_values - self.delayed_salary_values

    @property
    def final_spread(self) -> np.ndarray:
        """Final-month paired difference: salary-now minus delayed."""
        return self.final_salary_now_values - self.final_delayed_salary_values

    @property
    def probability_salary_now_wins(self) -> float:
        return float(np.mean(self.final_spread > 0))

    @property
    def mean_final_spread(self) -> float:
        return float(np.mean(self.final_spread))

    @property
    def median_final_spread(self) -> float:
        return float(np.median(self.final_spread))

    @property
    def final_spread_std(self) -> float:
        return float(np.std(self.final_spread, ddof=1))

    @property
    def paired_effect_size(self) -> float:
        """Paired Cohen's d (dz) for final-month strategy difference."""
        std = self.final_spread_std
        if np.isclose(std, 0.0):
            return float(np.nan)
        return self.mean_final_spread / std

    @property
    def final_spread_skewness(self) -> float:
        """Sample skewness of final-month paired difference."""
        diff = self.final_spread
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
        """Summary stats for final outcomes and paired strategy difference."""
        table = pd.DataFrame(
            {
                "salary_now_final": self._distribution_stats(self.final_salary_now_values),
                "salary_later_final": self._distribution_stats(self.final_delayed_salary_values),
                "spread_final": self._distribution_stats(self.final_spread),
            },
        )
        table.loc["win_probability_salary_now"] = [
            np.nan,
            np.nan,
            self.probability_salary_now_wins,
        ]
        table.loc["paired_effect_size_dz"] = [
            np.nan,
            np.nan,
            self.paired_effect_size,
        ]
        table.loc["spread_skewness"] = [
            np.nan,
            np.nan,
            self.final_spread_skewness,
        ]
        return table.round(2)


@dataclass(frozen=True, slots=True)
class ExperimentRun:
    salary_now_results: np.ndarray
    salary_later_results: np.ndarray

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
        salary_now_values = np.zeros((cfg.n_simulations, cfg.n_months))
        delayed_salary_values = np.zeros((cfg.n_simulations, cfg.n_months))
        sampled_monthly_profits = self._monthly_returns()

        for isim, profits in enumerate(sampled_monthly_profits):
            res = self._run_one_experiment(profits=profits)
            salary_now_values[isim] = res.salary_now_results
            delayed_salary_values[isim] = res.salary_later_results

        return SimulationResult(
            salary_now_values=salary_now_values,
            delayed_salary_values=delayed_salary_values,
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
        salary_now_results = self._simulate_salary_now(profits)
        salary_later_results = self._simulate_salary_later(profits)
        return ExperimentRun(
            salary_now_results=salary_now_results,
            salary_later_results=salary_later_results,
        )

    def _simulate_salary_now(self, profits: np.ndarray) -> np.ndarray:
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

    def _simulate_salary_later(self, profits: np.ndarray) -> np.ndarray:
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

if __name__ == "__main__":
    config = SimulationConfig(
        total_income=120960,
        pension=7332,
        car_cost=0,
        monthly_salary_investment=2500,
        monthly_mean_return=1.20 ** (1/12) - 1,
        monthly_volatility=0.15 / 12**0.5,
        months_between_withdrawals=4,
        n_months=12,
        n_simulations=1,
    )

    sim = StrategyMonteCarlo(config)
    res = sim.run()

    print(res)
