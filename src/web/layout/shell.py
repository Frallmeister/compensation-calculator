"""Top-level Dash layout."""

from dash import dcc, html

from web.ids import Ids
from web.layout import cards


def create_layout() -> html.Div:
    """Create the top-level app layout."""
    return html.Div(
        [
            dcc.Store(
                id=Ids.MONTE_CARLO_RESULTS_STORE,
                storage_type="memory",
            ),
            html.Header(
                [
                    html.H1("Compensation Calculator", className="site-title"),
                ],
                className="site-header",
            ),
            html.Main(
                [
                    cards.control_panel(),
                    cards.compensation_table(),
                    cards.monte_carlo_timeseries(),
                    cards.final_return_distributions(),
                    cards.final_advantage(),
                    cards.monthly_return_distribution(),
                ],
                className="site-container",
            ),
            html.Footer(
                [
                    html.Div("© 2026 Compensation Calculator", className="site-footer-text"),
                ],
                className="site-footer",
            ),
        ],
        className="app-shell",
    )
