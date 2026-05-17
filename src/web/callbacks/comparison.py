"""Callbacks for the offer comparison dashboard."""

from dash import Dash, Input, Output
from web.ids import Ids

def register_comparison_callbacks(
    app: Dash,
) -> None:
    """Register callbacks for the offer comparison view."""
    return