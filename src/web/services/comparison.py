"""Offer comparison service functions for the Dash dashboard."""

from typing import Any, Final, cast

from offers.benefits import vacation_value_rate
from offers.loader import load_tax_table, load_toml
from offers.pension import itp1
from offers.tax import tax_for_salary
from web.view_models import OfferSummary

CONFIG_KEYS: Final[tuple[str, ...]] = ("visionite", "volvo_cars")


def available_tax_tables() -> list[int]:
    """Return all available table numbers in the source tax data."""
    df_tax = load_tax_table()
    return sorted(df_tax["table_no"].dropna().astype(int).unique().tolist())


def default_salary() -> int:
    """Get default salary from assumptions config."""
    assumptions = load_toml("assumptions")
    return int(assumptions["current_salary"])


def build_offer_summary(config_key: str, salary: int, table_no: int) -> OfferSummary:
    """Build a comparable summary for one company config."""
    config = cast(dict[str, Any], load_toml(config_key))  # type: ignore[arg-type]
    monthly_tax = tax_for_salary(salary, table_no=table_no)
    monthly_net_salary = salary - monthly_tax

    annual_pension = 0
    if bool(config.get("itp1", False)):
        annual_pension += itp1(salary) * 12

    flex_pension_rate = float(config.get("flex_pension", 0.0))
    annual_pension += round(salary * flex_pension_rate * 12)

    annual_fixed_benefits = (
        int(config.get("wellness_allowance", 0))
        + int(config.get("insurance_value", 0))
        + int(config.get("other_benefits_value", 0))
    )

    vacation_days = int(config.get("vacation_days", 25))
    annual_vacation_value = round(salary * 12 * vacation_value_rate(vacation_days))

    annual_total_value = (
        salary * 12 + annual_pension + annual_fixed_benefits + annual_vacation_value
    )

    return OfferSummary(
        company=str(config["name"]),
        monthly_salary=salary,
        monthly_tax=monthly_tax,
        monthly_net_salary=monthly_net_salary,
        annual_pension=annual_pension,
        annual_fixed_benefits=annual_fixed_benefits,
        annual_vacation_value=annual_vacation_value,
        annual_total_value=annual_total_value,
    )
