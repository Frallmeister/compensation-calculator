"""Summary card builders for the Dash dashboard."""

from dash import dcc, html


def integer_input_group(
    label: str,
    input_id: str,
    value: float,
    min_value: int = 0,
    max_value: int | None = None,
    step: float = 1,
    suffix: str | None = None,
) -> html.Div:
    return html.Div(
        className="control-group",
        children=[
            html.Label(
                label,
                htmlFor=input_id,
                className="control-label",
            ),
            html.Div(
                className="input-row",
                children=[
                    dcc.Input(
                        id=input_id,
                        className="input-field",
                        type="number",
                        min=min_value,
                        max=max_value,
                        step=step,
                        value=value,
                    ),
                    html.Span(suffix, className="input-suffix") if suffix else None,
                ],
            ),
        ],
    )

def control_panel() -> html.Div:
    return html.Div(
        [
            html.H1("Control panel"),
            html.Div(
                className="control-blocks",
                children=[
                    html.Div(
                        className="table-control-block",
                        children=[
                            integer_input_group(
                                label="Hourly rate:",
                                input_id="hourly-rate-id",
                                value=900,
                                min_value=0,
                                step=1,
                                suffix="kr/h",
                            ),

                            integer_input_group(
                                label="Pension:",
                                input_id="pension-id",
                                value=5500,
                                min_value=0,
                                step=50,
                                suffix="kr",
                            ),

                            integer_input_group(
                                label="Deferred:",
                                input_id="deferred-id",
                                value=0,
                                min_value=0,
                                step=1,
                                suffix="kr",
                            ),
                            dcc.Button(
                                "Update table",
                                id="table-button-id",
                                className="button table-button",
                            ),
                        ],
                    ),

                    # Monte-Carlo controls
                    html.Div(
                        className="mc-control-block",
                        children=[
                            integer_input_group(
                                label="Monthly investment:",
                                input_id="monthly-investment-id",
                                value=2500,
                                min_value=0,
                                step=1,
                                suffix="kr",
                            ),
                            integer_input_group(
                                label="Monthly mean return:",
                                input_id="monthly-return-id",
                                min_value=0,
                                value=1.5,
                                step=0.1,
                                suffix="%",
                            ),
                            integer_input_group(
                                label="Monthly volatility:",
                                input_id="monthly-volatility-id",
                                min_value=0,
                                value=4,
                                step=0.1,
                                suffix="%",
                            ),
                            integer_input_group(
                                label="Monthly between withdrawals:",
                                input_id="months-to-withdrawal-id",
                                min_value=0,
                                value=6,
                                step=1,
                                suffix=" ",
                            ),
                            integer_input_group(
                                label="Months to simulate:",
                                input_id="months-to-simulate-id",
                                min_value=1,
                                value=24,
                                step=1,
                                suffix=" ",
                            ),
                            dcc.Button(
                                "Run simulation",
                                id="simulation-button-id",
                                className="button simulation-button",
                            ),
                        ],
                    ),
                ],
            ),
        ],
        className="card card-widgets",
    )

def compensation_table() -> html.Div:
    return html.Div(
        [
            html.H1("Compensation"),
            html.Div(id="compensation-table-id"),
        ],
        className="card card-table",
    )

def monte_carlo_timeseries() -> html.Div:
    return html.Div(
        [
            html.H1("Monte Carlo timeseries"),
            html.Div("Show timeseries plot here"),
        ],
        className="card card-mc-timeseries",
    )

def final_return_distributions() -> html.Div:
    return html.Div(
        [
            html.H1("Final income distributions"),
            html.Div("Show plot."),
        ],
        className="card card-mc-final-dist",
    )

def final_advantage() -> html.Div:
    return html.Div(
        [
            html.H1("Strategy advantage"),
            html.Div("Show plot."),
        ],
        className="card card-mc-advantage",
    )

def monthly_return_distribution() -> html.Div:
    return html.Div(
        [
            html.H1("Monthly return distribution"),
            html.Div("Show plot."),
        ],
        className="card card-mc-return-dist",
    )
