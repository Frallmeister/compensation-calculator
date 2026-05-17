"""Summary card builders for the Dash dashboard."""

from dash import html

from web.view_models import OfferSummary

def build_cards(summaries: list[OfferSummary]) -> list[html.Div]:
    """Create simple value cards with key monthly and yearly numbers."""
    cards: list[html.Div] = []
    for summary in summaries:
        cards.append(
            html.Div(
                [
                    html.H3(summary.company, className="summary-card-title"),
                    html.P(
                        f"Monthly net salary: {summary.monthly_net_salary:,.0f} SEK",
                        className="summary-card-primary",
                    ),
                    html.P(
                        f"Annual total value: {summary.annual_total_value:,.0f} SEK",
                        className="summary-card-secondary",
                    ),
                ],
                className="summary-card",
            ),
        )
    return cards
