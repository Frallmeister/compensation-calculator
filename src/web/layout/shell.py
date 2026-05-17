"""Top-level Dash layout."""

from dash import dcc, html

from web.ids import Ids
from web.layout.controls import build_comparison_controls
from web.layout.tables import build_summary_table


def build_header() -> html.Div:
    """Build the dashboard header."""
    return html.Div(
        [
            html.H1(
                "Offer Comparison",
                className="app-title",
            ),
            html.P(
                "Quick dashboard for comparing two offers with taxes and benefits.",
                className="app-subtitle",
            ),
        ],
        className="app-header",
    )


def create_layout(
    *,
    default_salary_value: int,
    tax_tables: list[int],
    default_table: int,
) -> html.Div:
    """Create the top-level app layout."""
    return html.Div(
        [
            build_header(),
            build_comparison_controls(
                default_salary_value=default_salary_value,
                tax_tables=tax_tables,
                default_table=default_table,
            ),
            html.Div(
                id=Ids.SUMMARY_CARDS,
                className="summary-card-grid",
            ),
            dcc.Graph(id=Ids.COMPARISON_FIGURE, className="comparison-figure"),
            build_summary_table(),
        ],
        className="app-shell",
    )
