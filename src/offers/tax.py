"""Tax utils."""

from dataclasses import dataclass
from functools import lru_cache

import numpy as np
import pandas as pd

from .loader import load_tax_table


@dataclass(frozen=True)
class TaxLookup:
    """Compiled tax table arrays for fast repeated lookups."""

    upper: np.ndarray
    tax: np.ndarray
    days: np.ndarray

    def tax_for_salary(self, salary: int) -> int:
        """Return tax for a single gross salary."""
        idx = int(np.searchsorted(self.upper, salary, side="left"))
        tax_value = self.tax[idx]
        if self.days[idx] == "30%":
            tax_value = salary * tax_value / 100
        return round(tax_value)

    def tax_for_salaries(self, salary: np.ndarray) -> np.ndarray:
        """Return taxes for many gross salaries."""
        idx = np.searchsorted(self.upper, salary, side="left")
        tax_array = self.tax[idx].copy()
        perc_rows = self.days[idx] == "30%"
        tax_array[perc_rows] = salary[perc_rows] * tax_array[perc_rows] / 100
        return tax_array.round().astype(int)


@lru_cache(maxsize=None)
def get_tax_lookup(table_no: int = 33) -> TaxLookup:
    """Load and compile one tax table for fast repeated lookups."""
    df_tax = load_tax_table(table_no=table_no).fillna(np.inf)
    return TaxLookup(
        upper=df_tax["upper_bound"].to_numpy(),
        tax=df_tax["tax"].to_numpy(),
        days=df_tax["days"].to_numpy(),
    )


def tax_for_salary(salary: int, table_no: int = 33) -> int:
    """Return tax for one gross salary using a cached tax table."""
    return get_tax_lookup(table_no=table_no).tax_for_salary(salary)


def salary_sweep(low: int = 1, high: int = 1000000, table_no: int = 33) -> pd.DataFrame:
    """Return an dataframe with taxes for different salaries."""
    lookup = get_tax_lookup(table_no=table_no)
    salary = np.arange(low, high)
    tax_array = lookup.tax_for_salaries(salary)
    return pd.DataFrame({"salary": salary, "tax": tax_array})
