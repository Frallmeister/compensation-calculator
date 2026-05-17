"""Top-level Dash layout."""

from dash import html

from web.ids import Ids


def create_layout() -> html.Div:
    """Create the top-level app layout."""
    return html.Div(
        [],
        className="app-shell",
    )
