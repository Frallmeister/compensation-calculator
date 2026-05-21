"""Summary card builders for the Dash dashboard."""

from dash import dcc, html

from web.ids import Ids


def numeric_input_group(
    label: str,
    input_id: str,
    value: float,
    min_value: float = 0,
    max_value: float | None = None,
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
                            numeric_input_group(
                                label="Hourly rate:",
                                input_id=Ids.HOURLY_RATE,
                                value=900,
                                min_value=0,
                                step=1,
                                suffix="kr/h",
                            ),

                            numeric_input_group(
                                label="Pension:",
                                input_id=Ids.PENSION,
                                value=5500,
                                min_value=0,
                                step=50,
                                suffix="kr",
                            ),

                            numeric_input_group(
                                label="Deferred:",
                                input_id=Ids.DEFERRED_INCOME,
                                value=0,
                                min_value=0,
                                step=1,
                                suffix="kr",
                            ),
                            dcc.Button(
                                "Update table",
                                id=Ids.TABLE_BUTTON,
                                className="button table-button",
                            ),
                        ],
                    ),

                    # Monte-Carlo controls
                    html.Div(
                        className="mc-control-block",
                        children=[
                            numeric_input_group(
                                label="Monthly investment:",
                                input_id=Ids.MONTHLY_INVESTMENT,
                                value=2500,
                                min_value=0,
                                step=1,
                                suffix="kr",
                            ),
                            numeric_input_group(
                                label="Monthly mean return:",
                                input_id=Ids.MONTHLY_RETURN,
                                value=1.5,
                                step=0.1,
                                suffix="%",
                            ),
                            numeric_input_group(
                                label="Monthly volatility:",
                                input_id=Ids.MONTHLY_VOLATILITY,
                                min_value=0.1,
                                value=4,
                                step=0.1,
                                suffix="%",
                            ),
                            numeric_input_group(
                                label="Months between withdrawals:",
                                input_id=Ids.MONTHS_TO_WITHDRAWAL,
                                min_value=0,
                                value=6,
                                step=1,
                                suffix=" ",
                            ),
                            numeric_input_group(
                                label="Months to simulate:",
                                input_id=Ids.MONTHS_TO_SIMULATE,
                                min_value=1,
                                value=24,
                                step=1,
                                suffix=" ",
                            ),
                            dcc.Button(
                                "Run simulation",
                                id=Ids.SIMULATION_BUTTON,
                                className="button simulation-button",
                                disabled=True,
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
            html.Div(id=Ids.COMPENSATION_TABLE),
        ],
        className="card card-table",
    )

def monte_carlo_timeseries() -> html.Div:
    return html.Div(
        [
            html.H1("Monte Carlo timeseries"),
            html.Div(""),
        ],
        className="card card-mc-timeseries",
    )

def final_return_distributions() -> html.Div:
    return html.Div(
        [
            html.H1("Final income distributions"),
            html.Div(""),
        ],
        className="card card-mc-final-dist",
    )

def final_advantage() -> html.Div:
    return html.Div(
        [
            html.H1("Strategy advantage"),
            html.Div(""),
        ],
        className="card card-mc-advantage",
    )

def monthly_return_distribution() -> html.Div:
    return html.Div(
        [
            html.H1("Monthly return distribution"),
            html.Div(
                id=Ids.MONTHLY_RETURN_DIST,
                className="graph-container",
            ),
        ],
        className="card card-mc-return-dist",
    )
