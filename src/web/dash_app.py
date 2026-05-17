"""Minimal Dash app for comparing offer value side by side."""

import hmac
import os
from dataclasses import dataclass
from typing import Any

import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dash_table, dcc, html
from flask import Response, request

from offers.benefits import vacation_value_rate
from offers.loader import ensure_refined_skattetabell, load_tax_table, load_toml
from offers.pension import itp1
from offers.tax import tax_for_salary

CONFIG_KEYS = ("visionite", "volvo_cars")
PRIMARY_COLOR = "#0f766e"
SECONDARY_COLOR = "#f59e0b"
EXEMPT_PATHS = frozenset(("/healthz", "/robots.txt"))


@dataclass(frozen=True)
class OfferSummary:
    """Comparable values for one company offer."""

    company: str
    monthly_salary: int
    monthly_tax: int
    monthly_net_salary: int
    annual_pension: int
    annual_fixed_benefits: int
    annual_vacation_value: int
    annual_total_value: int

    def to_row(self) -> dict[str, int | str]:
        """Serialize to a table row for Dash."""
        return {
            "Company": self.company,
            "Monthly salary": self.monthly_salary,
            "Monthly tax": self.monthly_tax,
            "Monthly net": self.monthly_net_salary,
            "Annual pension": self.annual_pension,
            "Annual fixed benefits": self.annual_fixed_benefits,
            "Annual vacation value": self.annual_vacation_value,
            "Annual total value": self.annual_total_value,
        }


def available_tax_tables() -> list[int]:
    """Return all available table numbers in the source tax data."""
    df_tax = load_tax_table()
    return sorted(df_tax["table_no"].dropna().astype(int).unique().tolist())


def default_salary() -> int:
    """Get default salary from assumptions config."""
    assumptions = load_toml("assumptions")
    return int(assumptions["current_salary"])


def build_offer_summary(config_key: str, salary: int, table_no: int) -> OfferSummary:
    """Build a comparable summary for one company config."""
    config: dict[str, Any] = load_toml(config_key)  # type: ignore[arg-type]
    monthly_tax = tax_for_salary(salary, table_no=table_no)
    monthly_net_salary = salary - monthly_tax

    annual_pension = 0
    if bool(config.get("itp1", False)):
        annual_pension += itp1(salary) * 12

    flex_pension_rate = float(config.get("flex_pension", 0.0))
    annual_pension += round(salary * flex_pension_rate * 12)

    annual_fixed_benefits = (
        int(config.get("wellness_allowance", 0))
        + int(config.get("insurance_value", 0))
        + int(config.get("other_benefits_value", 0))
    )

    vacation_days = int(config.get("vacation_days", 25))
    annual_vacation_value = round(salary * 12 * vacation_value_rate(vacation_days))

    annual_total_value = (
        salary * 12 + annual_pension + annual_fixed_benefits + annual_vacation_value
    )

    return OfferSummary(
        company=str(config["name"]),
        monthly_salary=salary,
        monthly_tax=monthly_tax,
        monthly_net_salary=monthly_net_salary,
        annual_pension=annual_pension,
        annual_fixed_benefits=annual_fixed_benefits,
        annual_vacation_value=annual_vacation_value,
        annual_total_value=annual_total_value,
    )


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

    return app


app = create_app()
server = app.server


def _auth_credentials() -> tuple[str, str] | None:
    """Return configured credentials, or None when auth is disabled."""
    username = os.getenv("DASH_USERNAME")
    password = os.getenv("DASH_PASSWORD")
    if not username or not password:
        return None
    return username, password


def _unauthorized() -> Response:
    """Return a Basic Auth challenge response."""
    response = Response("Authentication required\n", status=401, mimetype="text/plain")
    response.headers["WWW-Authenticate"] = 'Basic realm="Dashboard"'
    return response


@server.before_request
def require_basic_auth() -> Response | None:
    """Protect dashboard routes with HTTP Basic Auth when configured."""
    if request.path in EXEMPT_PATHS:
        return None

    credentials = _auth_credentials()
    if credentials is None:
        return None

    auth = request.authorization
    if auth is None or auth.type.lower() != "basic":
        return _unauthorized()

    expected_username, expected_password = credentials
    if not hmac.compare_digest(auth.username or "", expected_username):
        return _unauthorized()
    if not hmac.compare_digest(auth.password or "", expected_password):
        return _unauthorized()
    return None


@server.route("/healthz", methods=["GET"])
def healthz() -> Response:
    """Return liveness status for platform health checks."""
    return Response("ok\n", mimetype="text/plain")


@server.route("/robots.txt", methods=["GET"])
def robots_txt() -> Response:
    """Disallow crawler indexing for this dashboard."""
    content = "User-agent: *\nDisallow: /\n"
    return Response(content, mimetype="text/plain; charset=utf-8")


def main() -> None:
    """Run the app locally or in a container."""
    port = int(os.getenv("PORT", "8050"))
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()
