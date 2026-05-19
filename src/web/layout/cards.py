"""Summary card builders for the Dash dashboard."""

from dash import html

def control_panel() -> html.Div:
    return html.Div(
        [
            html.H1("Control panel"),
            html.Div("Some content here"),
            # timpris: slider
            # Pension: slider
            # Deferred: slider
            ### MONTE CARLO
            # monthly_salary_investment
            # Monthly mean return
            # Monthly volatility
            # Months between withdrawals
            # n_months 
            # n_simulations dropdown(100, 1k, 10k)

        ],
        className="card card-widgets",
    )

def compensation_table() -> html.Div:
    return html.Div(
        [
            html.H1("Compensation"),
            html.Div("Table here"),
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
