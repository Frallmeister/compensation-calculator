"""Calculations related to benefits."""

def vacation_value_rate(days: int) -> float:
    """Räkna ut semesteravsättningen.

    12 % på 25 dagar och ytterligare 0.48 % per extra dag.
    """
    extra_days = max(days - 25, 0)
    return 0.12 + 0.0048 * extra_days
