"""Chart builders for the dashboard."""

import pandas as pd
import plotly.express as px
from web.view_models import OfferSummary

PRIMARY_COLOR = "#0f766e"
SECONDARY_COLOR = "#f59e0b"


def build_figure(summaries: list[OfferSummary]):
    """Create grouped bar chart of annual value components."""
    rows = [
        {
            "Company": summary.company,
            "Gross salary": summary.monthly_salary * 12,
            "Pension": summary.annual_pension,
            "Fixed benefits": summary.annual_fixed_benefits,
            "Vacation value": summary.annual_vacation_value,
            "Total value": summary.annual_total_value,
        }
        for summary in summaries
    ]
    df = pd.DataFrame(rows)
    df_long = df.melt(id_vars="Company", var_name="Component", value_name="SEK")

    fig = px.bar(
        df_long,
        x="Component",
        y="SEK",
        color="Company",
        barmode="group",
        color_discrete_sequence=[PRIMARY_COLOR, SECONDARY_COLOR],
    )
    fig.update_layout(
        margin={"l": 30, "r": 20, "t": 20, "b": 30},
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend_title_text="",
    )
    return fig
