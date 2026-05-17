"""Table builders for the Dash dashboard."""

from dash import dash_table
from web.ids import Ids


def build_summary_table() -> dash_table.DataTable:
    """Create the offer summary table."""
    return dash_table.DataTable(
        id=Ids.SUMMARY_TABLE,
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
    )
