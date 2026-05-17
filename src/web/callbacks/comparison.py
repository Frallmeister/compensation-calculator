"""Callbacks for the offer comparison dashboard."""

from dash import Dash, Input, Output
from web.layout.charts import build_figure
from web.layout.summary import build_cards
from web.services.comparison import CONFIG_KEYS, build_offer_summary

def register_comparison_callbacks(
    app: Dash,
    *,
    default_salary_value: int,
    default_table: int,
) -> None:
    """Register callbacks for the offer comparison view."""
    @app.callback(
        Output("summary-cards", "children"),
        Output("comparison-figure", "figure"),
        Output("summary-table", "data"),
        Input("salary-input", "value"),
        Input("tax-table-dropdown", "value"),
    )
    def update_view(salary: int, table_no: int):
        salary_value = int(salary or default_salary_value)
        table_value = int(table_no or default_table)
        summaries = [build_offer_summary(key, salary_value, table_value) for key in CONFIG_KEYS]
        return build_cards(summaries), build_figure(summaries), [s.to_row() for s in summaries]
