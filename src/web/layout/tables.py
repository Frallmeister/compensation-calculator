"""Table builders for the Dash dashboard."""

from web.ids import Ids

from dash import html

from offers.companies.visionite import TotalCompensation


def format_sek(value: int) -> str:
    return f"{value:_} kr".replace("_", " ")


def build_total_compensation_table(total_compensation: TotalCompensation) -> html.Table:
    rows = [
        ("Income to distribute", total_compensation.income, True),
        ("Vacation allowance", total_compensation.holiday_provision, False),
        ("Fixed costs", total_compensation.fixed_costs, False),
        ("Employers fee", total_compensation.employers_fee, False),
        ("Pension tax", total_compensation.pension_tax, False),
        ("Pension", total_compensation.pension, True),
        ("Deferred income", total_compensation.set_aside, True),
        ("Gross salary", total_compensation.gross_salary, True),
        ("Income tax", total_compensation.table_tax, False),
        ("Net salary", total_compensation.net_salary, True),
    ]

    return html.Table(
        html.Tbody(
            [
                html.Tr(
                    [
                        html.Td(label, className="comp-table-label"),
                        html.Td(format_sek(value), className="comp-table-amount"),
                    ],
                    className="comp-table-row comp-table-row-bold"
                    if is_bold
                    else "comp-table-row",
                )
                for label, value, is_bold in rows
            ],
        ),
        className="comp-table",
    )
