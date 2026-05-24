"""Dash component IDs.

They are defined here once so the strings only need to be used once, which makes it easy
to change one without having to change it everywhere.
"""


class Ids:
    """Stable IDs for Dash components."""

    # Control card
    HOURLY_RATE = "hourly-rate-id"
    PENSION = "pension-id"
    DEFERRED_INCOME = "deferred-id"
    TAX_TABLE_DROPDOWN = "tax-table-dropdown"
    TABLE_BUTTON = "table-button-id"
    MONTHLY_INVESTMENT = "monthly-investment-id"
    MONTHLY_RETURN = "monthly-return-id"
    MONTHLY_RETURN_DIST = "monthly-return-distribution-id"
    MONTHLY_VOLATILITY = "monthly-volatility-id"
    MONTHS_TO_WITHDRAWAL = "months-to-withdrawal-id"
    MONTHS_TO_SIMULATE = "months-to-simulate-id"
    SIMULATION_BUTTON = "simulation-button-id"
    COMPENSATION_TABLE = "compensation-table-id"

    # Monte Carlo simulation
    MONTE_CARLO_RESULTS_STORE = "monte-carlo-results-store"
    MONTE_CARLO_ADVANTAGE = "monte-carlo-advantage"
    MONTE_CARLO_FINALS = "monte-carlo-finals"
    MONTE_CARLO_SIMULATION_PATHS = "monte-carlo-simulation-paths"
