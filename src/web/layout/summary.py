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
