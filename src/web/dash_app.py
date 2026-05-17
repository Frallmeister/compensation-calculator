"""Minimal Dash app for comparing offer value side by side."""

import os

from dash import Dash, dcc, html

from offers.loader import ensure_refined_skattetabell
from web.auth import configure_basic_auth
from web.callbacks.comparison import register_comparison_callbacks
from web.layout.tables import build_summary_table
from web.routes import register_routes
from web.services.comparison import (
    available_tax_tables,
    default_salary,
)


def create_app() -> Dash:
    """Create and configure the Dash app."""
    ensure_refined_skattetabell()
    default_salary_value = default_salary()
    tax_tables = available_tax_tables()
    default_table = 33 if 33 in tax_tables else tax_tables[0]

    app = Dash(__name__, title="Offer comparison")
    app.layout = html.Div(
        [
            html.Div(
                [
                    html.H1(
                        "Offer Comparison",
                        style={"margin": "0", "fontSize": "2rem", "fontWeight": "700"},
                    ),
                    html.P(
                        "Quick dashboard for comparing two offers with taxes and benefits.",
                        style={"margin": "6px 0 0", "color": "#334155"},
                    ),
                ],
                style={"marginBottom": "18px"},
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("Monthly salary (SEK)", style={"fontWeight": "600"}),
                            dcc.Input(
                                id="salary-input",
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
                            html.Label("Tax table", style={"fontWeight": "600"}),
                            dcc.Dropdown(
                                id="tax-table-dropdown",
                                options=[{"label": str(no), "value": int(no)} for no in tax_tables],
                                value=default_table,
                                clearable=False,
                            ),
                        ],
                        style={"flex": "1 1 220px"},
                    ),
                ],
                style={"display": "flex", "gap": "14px", "flexWrap": "wrap"},
            ),
            html.Div(
                id="summary-cards",
                style={"display": "flex", "gap": "14px", "flexWrap": "wrap", "marginTop": "16px"},
            ),
            dcc.Graph(id="comparison-figure", style={"marginTop": "16px"}),
            build_summary_table(),
        ],
        style={
            "maxWidth": "1100px",
            "margin": "0 auto",
            "padding": "24px 18px 40px",
            "fontFamily": "'Segoe UI', 'Aptos', sans-serif",
            "background": "linear-gradient(180deg, #ecfeff 0%, #f8fafc 45%, #ffffff 100%)",
            "minHeight": "100vh",
        },
    )

    register_comparison_callbacks(
        app=app,
        default_salary_value=default_salary_value,
        default_table=default_table,
    )

    # Register HTTP authentication and URL routes.
    configure_basic_auth(app.server)
    register_routes(app.server)
    return app


app = create_app()
server = app.server


def main() -> None:
    """Run the app locally or in a container."""
    port = int(os.getenv("PORT", "8050"))
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()
