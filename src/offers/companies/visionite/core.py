"""Functions pertaining to Visionite."""

from dataclasses import dataclass
import logging

import numpy as np
from rich import box
from rich.console import Console
from rich.table import Table

from offers.pension import itp1
from offers.tax import tax_for_salary

logger = logging.getLogger(__name__)

WORK_TOOLS = 700
INSURANCE = 800

@dataclass
class TotalCompensation:
    """Fields corresponding to the compensation table in the visionite app."""

    income: int
    gross_salary: int
    holiday_provision: int
    employers_fee: int
    pension: int
    pension_tax: int
    set_aside: int
    car: int
    fixed_costs: int
    table_tax: int
    net_salary: int

    def print_table(self) -> None:
        table = Table(
            show_header=False,
            show_lines=True,
            box=box.HORIZONTALS,
            leading=0,
            padding=(0, 2),
        )
        table.add_column("Field")
        table.add_column("Amount", justify="right")

        table.add_row("Egen intäkt", f"{self.income:_} kr".replace("_", " "), style="bold")
        table.add_row("Skatter och avgifter", "", style="bold")
        table.add_row("Semesteravsättning", f"{self.holiday_provision:_} kr".replace("_", " "))
        table.add_row(
            "Arbetsverktyg & Trygghetspaket", f"{self.fixed_costs:_} kr".replace("_", " "),
        )
        table.add_row("Arbetsgivaravgifter", f"{self.employers_fee:_} kr".replace("_", " "))
        table.add_row("Löneskatt på tjänstepension", f"{self.pension_tax:_} kr".replace("_", " "))
        table.add_row("Bruttolön", f"{self.gross_salary:_} kr".replace("_", " "), style="bold")
        table.add_row("Tjänstepension", f"{self.pension:_} kr".replace("_", " "), style="bold")
        table.add_row(
            "Sparande till Visionitekonto", f"{self.set_aside:_} kr".replace("_", " "),style="bold"
        )
        table.add_row("Bilkostnad", f"{self.car:_} kr".replace("_", " "))
        table.add_row("Tabellskatt", f"{self.table_tax:_} kr".replace("_", " "))
        table.add_row("Nettolön", f"{self.net_salary:_} kr".replace("_", " "), style="bold")
        Console().print(table)


def calc_compensation(income: int, pension: int, pot: int, car: int = 0) -> TotalCompensation:
    """Calculate the gross salary.

    The compensation is based on the invoiced income, pension provision, saved pot
    and car cost according to:

    R = GS + H + AG + TP + TP_tax + fixed_costs + pot + car_cost

    where
        R: invoiced income
        GS: gross salary
        H: semesteravsättning
        AG: arbetsgivaravgift
        TP: tjänstepension
        TP_tax: löneskatt på tjänstepension
        fixed_costs: arbetskostnad + försäkring
        pot: Avsättning till lönepott
        car_cost: Cost for car

    By substituting:
        H = 0.144 * GS
        AG = 0.3142 * (GS + H)

    the gross salary can be can be calculated as

        GS = (R - 1.2426 * TP - fixed_costs - pot - car_cost) / 1.5034448
    """
    fixed_costs = WORK_TOOLS + INSURANCE
    gs = (
        income - 1.2426 * pension - fixed_costs - pot - car
    ) / 1.5034448

    holiday_provision = 0.144 * gs
    employers_fee = 0.3142 * (gs + holiday_provision)
    table_tax = tax_for_salary(gs)
    net_salary = gs - table_tax
    return TotalCompensation(
        income=income,
        gross_salary=round(gs),
        holiday_provision=round(holiday_provision),
        employers_fee=round(employers_fee),
        pension=pension,
        pension_tax=round(0.2426 * pension),
        set_aside=pot,
        car=car,
        fixed_costs=fixed_costs,
        table_tax=round(table_tax),
        net_salary=round(net_salary),
    )

def find_itp1_pension(income: int, pot: int, car: int, verbose: int = 0) -> int:
    """Find the corresponding ITP1 pension for a given salary."""
    pension = 0
    delta = 100
    while np.abs(delta) > 1:
        total_compensation = calc_compensation(
            income=income,
            pension=pension,
            pot=pot,
            car=car,
        )

        gs = total_compensation.gross_salary
        new_pension = itp1(gs)
        delta = new_pension - pension
        if verbose > 0:
            logger.info(
                "Bruttolön %s kr, pension %s kr, Ny pension %s kr, Delta %s kr",
                gs,
                pension,
                new_pension,
                delta,
            )
        pension = new_pension
    return pension
