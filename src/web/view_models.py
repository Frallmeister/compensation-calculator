"""View models used by the Dash dashboard."""

from dataclasses import dataclass


@dataclass(frozen=True)
class OfferSummary:
    """Comparable values for one company offer."""

    company: str
    monthly_salary: int
    monthly_tax: int
    monthly_net_salary: int
    annual_pension: int
    annual_fixed_benefits: int
    annual_vacation_value: int
    annual_total_value: int

    def to_row(self) -> dict[str, int | str]:
        """Serialize to a table row for Dash."""
        return {
            "Company": self.company,
            "Monthly salary": self.monthly_salary,
            "Monthly tax": self.monthly_tax,
            "Monthly net": self.monthly_net_salary,
            "Annual pension": self.annual_pension,
            "Annual fixed benefits": self.annual_fixed_benefits,
            "Annual vacation value": self.annual_vacation_value,
            "Annual total value": self.annual_total_value,
        }
