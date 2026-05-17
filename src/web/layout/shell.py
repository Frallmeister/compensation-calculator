"""Top-level Dash layout."""

from dash import dcc, html

from web.layout.controls import build_comparison_controls
from web.layout.tables import build_summary_table


def build_header() -> html.Div:
    """Build the dashboard header."""
    return html.Div(
        [
            html.H1(
                "Offer Comparison",
                style={
                    "margin": "0",
                    "fontSize": "2rem",
                    "fontWeight": "700",
                },
            ),
            html.P(
                "Quick dashboard for comparing two offers with taxes and benefits.",
                style={"margin": "6px 0 0", "color": "#334155"},
            ),
        ],
        style={"marginBottom": "18px"},
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
                id="summary-cards",
                style={
                    "display": "flex",
                    "gap": "14px",
                    "flexWrap": "wrap",
                    "marginTop": "16px",
                },
            ),
            dcc.Graph(id="comparison-figure", style={"marginTop": "16px"}),
            build_summary_table(),
        ],
        style={
            "maxWidth": "1100px",
            "margin": "0 auto",
            "padding": "24px 18px 40px",
            "fontFamily": "'Segoe UI', 'Aptos', sans-serif",
            "background": (
                "linear-gradient(180deg, #ecfeff 0%, "
                "#f8fafc 45%, #ffffff 100%)"
            ),
            "minHeight": "100vh",
        },
    )
