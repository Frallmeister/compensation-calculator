"""Verify the selected tax table reaches every simulation salary calculation."""

import unittest
from unittest.mock import patch

import numpy as np

from offers.companies.visionite import SimulationConfig, StrategyMonteCarlo, calc_compensation
from web import dash_app
from web.ids import Ids


class SimulationTaxTableTest(unittest.TestCase):
    """Exercise tax-table selection from the Dash callback through the model."""

    def simulate(self, table_no: int, deferred: int = 0) -> dict:
        """Run a small, deterministic simulation through the real callback."""
        output_id = Ids.MONTE_CARLO_RESULTS_STORE
        output = f"{output_id}.data"
        callback = dash_app.app.callback_map[output]
        values = {
            Ids.HOURLY_RATE: 900,
            Ids.CONSULTANT_SHARE: 80,
            Ids.PENSION: 5500,
            Ids.DEFERRED_INCOME: deferred,
            Ids.TAX_TABLE_DROPDOWN: table_no,
            Ids.MONTHLY_RETURN: 0,
            Ids.MONTHLY_VOLATILITY: 0,
            Ids.MONTHS_TO_WITHDRAWAL: 2,
            Ids.MONTHS_TO_SIMULATE: 3,
        }
        with patch("web.callbacks.core.N_SIMULATIONS", 2):
            response = dash_app.server.test_client().post(
                "/_dash-update-component",
                json={
                    "output": output,
                    "outputs": {"id": output_id, "property": "data"},
                    "inputs": [
                        {"id": Ids.SIMULATION_BUTTON, "property": "n_clicks", "value": 1},
                    ],
                    "state": [
                        {**entry, "value": values[entry["id"]]}
                        for entry in callback["state"]
                    ],
                    "changedPropIds": [f"{Ids.SIMULATION_BUTTON}.n_clicks"],
                },
            )
        self.assertEqual(response.status_code, 200)
        return response.get_json()["response"][output_id]["data"]

    def test_both_strategies_use_selected_tax_table(self) -> None:
        for table_no in [29, 33, 42]:
            with self.subTest(table_no=table_no):
                data = self.simulate(table_no)
                # With no savings or investment returns, each strategy must simply
                # accumulate three months of salary under the selected tax table.
                expected = 3 * calc_compensation(
                    income=120960, pension=5500, pot=0, table_no=table_no,
                ).net_salary
                self.assertEqual(data["immediate"], [expected, expected])
                self.assertEqual(data["deferred"], [expected, expected])
                self.assertEqual(data["advantage"], [0, 0])

    def test_deferred_deposits_and_withdrawals_keep_selected_tax_table(self) -> None:
        with patch(
            "offers.companies.visionite.montecarlo.calc_compensation",
            wraps=calc_compensation,
        ) as calculate:
            self.simulate(table_no=42, deferred=3000)
        calls = [call.kwargs for call in calculate.call_args_list]
        self.assertTrue(calls)
        self.assertTrue(all(call.get("table_no") == 42 for call in calls))
        self.assertTrue(any(call["pot"] == 3000 for call in calls))
        self.assertTrue(any(call["income"] > 120960 for call in calls))

    def test_existing_configs_still_default_to_table_33(self) -> None:
        config = SimulationConfig(
            total_income=120960,
            pension=5500,
            car_cost=0,
            monthly_salary_investment=0,
            monthly_mean_return=0,
            monthly_volatility=0,
            months_between_withdrawals=2,
            n_months=3,
            n_simulations=2,
        )
        self.assertEqual(config.table_no, 33)
        result = StrategyMonteCarlo(config).run()
        expected = 3 * calc_compensation(income=120960, pension=5500, pot=0).net_salary
        np.testing.assert_array_equal(result.final_immediate_withdrawal_values, [expected] * 2)
        np.testing.assert_array_equal(result.final_deferred_withdrawal_values, [expected] * 2)


if __name__ == "__main__":
    unittest.main()
