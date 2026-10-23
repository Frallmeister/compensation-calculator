"""Regression tests for the consultant's share of invoiced revenue."""

import unittest
from unittest.mock import patch

from flask import Response

from web import dash_app
from web.ids import Ids


class ConsultantShareTest(unittest.TestCase):
    """Exercise the percentage control through Dash's HTTP callback endpoint."""

    def setUp(self) -> None:
        self.client = dash_app.server.test_client()

    def update(
        self,
        output_id: str,
        share: float | None,
        hourly_rate: int = 900,
        trigger: str = Ids.TABLE_BUTTON,
    ) -> Response:
        """Submit the controls in the order registered with Dash."""
        property_name = "children" if output_id == Ids.COMPENSATION_TABLE else "data"
        output = f"{output_id}.{property_name}"
        callback = dash_app.app.callback_map[output]
        values = {
            Ids.TABLE_BUTTON: int(trigger == Ids.TABLE_BUTTON),
            Ids.SIMULATION_BUTTON: int(trigger == Ids.SIMULATION_BUTTON),
            Ids.HOURLY_RATE: hourly_rate,
            Ids.CONSULTANT_SHARE: share,
            Ids.PENSION: 5500,
            Ids.DEFERRED_INCOME: 3000,
            Ids.TAX_TABLE_DROPDOWN: 33,
            Ids.MONTHLY_RETURN: 1.5,
            Ids.MONTHLY_VOLATILITY: 4,
            Ids.MONTHS_TO_WITHDRAWAL: 12,
            Ids.MONTHS_TO_SIMULATE: 3,
        }
        return self.client.post(
            "/_dash-update-component",
            json={
                "output": output,
                "outputs": {"id": output_id, "property": property_name},
                "inputs": [
                    {**entry, "value": values[entry["id"]]}
                    for entry in callback["inputs"]
                ],
                "state": [
                    {**entry, "value": values[entry["id"]]}
                    for entry in callback["state"]
                ],
                "changedPropIds": [f"{trigger}.n_clicks"],
            },
        )

    def test_share_control_starts_at_eighty_percent(self) -> None:
        response = self.client.get("/_dash-layout")
        self.assertEqual(response.status_code, 200)
        pending = [response.get_json()]
        while pending:
            node = pending.pop()
            if isinstance(node, dict):
                props = node.get("props", {})
                if props.get("id") == Ids.CONSULTANT_SHARE:
                    self.assertEqual(node["type"], "Input")
                    self.assertEqual(props["value"], 80)
                    self.assertEqual(props["min"], 0)
                    self.assertEqual(props["max"], 100)
                    self.assertEqual(props["step"], 1)
                    return
                pending.extend(node.values())
            elif isinstance(node, list):
                pending.extend(node)
        self.fail("The consultant share control is missing from the layout")

    def test_table_uses_hourly_rate_and_selected_share(self) -> None:
        for rate, share, expected in [
            (900, 80, "120 960 kr"),
            (900, 70, "105 840 kr"),
            (1000, 70, "117 600 kr"),
            (901, 70, "105 958 kr"),
            (900, 100, "151 200 kr"),
            (900, 0, "0 kr"),
        ]:
            with self.subTest(rate=rate, share=share):
                response = self.update(Ids.COMPENSATION_TABLE, share, rate)
                self.assertEqual(response.status_code, 200)
                table = response.get_json()["response"][Ids.COMPENSATION_TABLE]["children"]
                rows = table["props"]["children"]["props"]["children"]
                income = rows[0]["props"]["children"][1]["props"]["children"]
                self.assertEqual(income, expected)
                if rate == 900 and share == 80:
                    amounts = [row["props"]["children"][1]["props"]["children"] for row in rows]
                    self.assertEqual(amounts[7], "72 916 kr")
                    self.assertEqual(amounts[9], "50 031 kr")

    def test_simulation_button_also_updates_table_with_selected_share(self) -> None:
        response = self.update(Ids.COMPENSATION_TABLE, 70, trigger=Ids.SIMULATION_BUTTON)
        self.assertEqual(response.status_code, 200)
        self.assertIn("105 840 kr", response.get_data(as_text=True))

    def test_simulation_receives_income_after_applying_share(self) -> None:
        for rate, share, expected in [(900, 80, 120960), (900, 70, 105840), (1000, 70, 117600)]:
            with self.subTest(rate=rate, share=share):
                with patch("web.callbacks.core.run_monte_carlo_simulation", return_value={}) as run:
                    response = self.update(
                        Ids.MONTE_CARLO_RESULTS_STORE, share, rate, Ids.SIMULATION_BUTTON,
                    )
                self.assertEqual(response.status_code, 200)
                run.assert_called_once()
                self.assertEqual(run.call_args.kwargs["total_income"], expected)

    def test_simulation_returns_results_with_selected_share(self) -> None:
        with patch("web.callbacks.core.N_SIMULATIONS", 3):
            response = self.update(
                Ids.MONTE_CARLO_RESULTS_STORE, 70, trigger=Ids.SIMULATION_BUTTON,
            )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()["response"][Ids.MONTE_CARLO_RESULTS_STORE]["data"]
        self.assertEqual(len(data["immediate"]), 3)
        self.assertEqual(len(data["deferred"]), 3)
        self.assertEqual(len(data["percentiles"]["p50"]), 3)

    def test_missing_or_invalid_share_preserves_previous_results(self) -> None:
        for share in [None, -1, 101]:
            for output_id in [Ids.COMPENSATION_TABLE, Ids.MONTE_CARLO_RESULTS_STORE]:
                with self.subTest(share=share, output_id=output_id):
                    with patch("web.callbacks.core.run_monte_carlo_simulation") as run:
                        response = self.update(output_id, share, trigger=Ids.SIMULATION_BUTTON)
                    self.assertEqual(response.status_code, 204)
                    run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
