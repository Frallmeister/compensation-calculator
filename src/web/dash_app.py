"""Minimal Dash app for comparing offer value side by side."""

import os

import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dash_table, dcc, html

from offers.loader import ensure_refined_skattetabell
from web.auth import configure_basic_auth
from web.routes import register_routes
from web.services.comparison import (
    CONFIG_KEYS,
    available_tax_tables,
    build_offer_summary,
    default_salary,
)
from web.view_models import OfferSummary

PRIMARY_COLOR = "#0f766e"
SECONDARY_COLOR = "#f59e0b"


def build_figure(summaries: list[OfferSummary]):
    """Create grouped bar chart of annual value components."""
    rows = [
        {
            "Company": summary.company,
            "Gross salary": summary.monthly_salary * 12,
            "Pension": summary.annual_pension,
            "Fixed benefits": summary.annual_fixed_benefits,
            "Vacation value": summary.annual_vacation_value,
            "Total value": summary.annual_total_value,
        }
        for summary in summaries
    ]
    df = pd.DataFrame(rows)
    df_long = df.melt(id_vars="Company", var_name="Component", value_name="SEK")

    fig = px.bar(
        df_long,
        x="Component",
        y="SEK",
        color="Company",
        barmode="group",
        color_discrete_sequence=[PRIMARY_COLOR, SECONDARY_COLOR],
    )
    fig.update_layout(
        margin={"l": 30, "r": 20, "t": 20, "b": 30},
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend_title_text="",
    )
    return fig


def build_cards(summaries: list[OfferSummary]) -> list[html.Div]:
    """Create simple value cards with key monthly and yearly numbers."""
    cards: list[html.Div] = []
    for summary in summaries:
        cards.append(
            html.Div(
                [
                    html.H3(summary.company, style={"margin": "0 0 8px", "fontSize": "1.2rem"}),
                    html.P(
                        f"Monthly net salary: {summary.monthly_net_salary:,.0f} SEK",
                        style={"margin": "0", "fontWeight": "600"},
                    ),
                    html.P(
                        f"Annual total value: {summary.annual_total_value:,.0f} SEK",
                        style={"margin": "4px 0 0", "color": "#334155"},
                    ),
                ],
                style={
                    "flex": "1 1 280px",
                    "background": "#ffffff",
                    "padding": "16px 18px",
                    "borderRadius": "14px",
                    "boxShadow": "0 10px 30px rgba(15, 23, 42, 0.08)",
                },
            ),
        )
    return cards


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
            dash_table.DataTable(
                id="summary-table",
                columns=[
                    {"name": "Company", "id": "Company"},
                    {"name": "Monthly salary", "id": "Monthly salary", "type": "numeric"},
                    {"name": "Monthly tax", "id": "Monthly tax", "type": "numeric"},
                    {"name": "Monthly net", "id": "Monthly net", "type": "numeric"},
                    {"name": "Annual pension", "id": "Annual pension", "type": "numeric"},
                    {
                        "name": "Annual fixed benefits",
                        "id": "Annual fixed benefits",
                        "type": "numeric",
                    },
                    {
                        "name": "Annual vacation value",
                        "id": "Annual vacation value",
                        "type": "numeric",
                    },
                    {
                        "name": "Annual total value",
                        "id": "Annual total value",
                        "type": "numeric",
                    },
                ],
                style_table={"overflowX": "auto", "marginTop": "12px"},
                style_header={"fontWeight": "700", "backgroundColor": "#f8fafc"},
                style_cell={"padding": "8px", "textAlign": "left"},
            ),
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
