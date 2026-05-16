"""General pension utils."""

from .loader import load_toml

def itp1(salary: int) -> int:
    """Calculate the ITP1 pension for a given salary."""
    assumptions = load_toml("assumptions")
    ibb = assumptions["inkomstbasbelopp"]
    salary_threshold = 7.5 * ibb / 12
    pension = 0.045 * min(salary_threshold, salary)
    if salary > salary_threshold:
        salary_ceiling = 30 * ibb / 12
        pension += 0.3 * (min(salary, salary_ceiling) - salary_threshold)
    return round(pension)
