"""Input controls for the Dash dashboard."""

from dash import dcc, html
from web.ids import Ids


def build_comparison_controls(
    *,
    default_salary_value: int,
    tax_tables: list[int],
    default_table: int,
) -> html.Div:
    """Build controls for salary and tax-table selection."""
    return html.Div(
        [
            html.Div(
                [
                    html.Label(
                        "Monthly salary (SEK)",
                        style={"fontWeight": "600"},
                    ),
                    dcc.Input(
                        id=Ids.SALARY_INPUT,
                        type="number",
                        min=10000,
                        step=500,
                        value=default_salary_value,
                        style={"width": "100%", "padding": "8px"},
                    ),
                ],
                style={"flex": "1 1 220px"},
            ),
            html.Div(
                [
                    html.Label(
                        "Tax table",
                        style={"fontWeight": "600"},
                    ),
                    dcc.Dropdown(
                        id=Ids.TAX_TABLE_DROPDOWN,
                        options=[
                            {"label": str(no), "value": int(no)}
                            for no in tax_tables
                        ],
                        value=default_table,
                        clearable=False,
                    ),
                ],
                style={"flex": "1 1 220px"},
            ),
        ],
        style={"display": "flex", "gap": "14px", "flexWrap": "wrap"},
    )
