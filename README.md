# Offer comparison sandbox

This project is organized so the notebook stays thin while the comparison logic,
config loading, and reference data handling live in a small Python package.

## Structure

- `src/offer_compare/`: calculation logic, models, and loaders
- `configs/employers/`: one TOML file per employer offer
- `configs/assumptions.toml`: shared assumptions that are not company-specific
- `data/raw/skatteverket/`: downloaded source data from Skatteverket
- `tests/`: narrow regression tests for the comparison logic
- `sandbox.ipynb`: current exploration notebook

## Quick start

Create or sync the local environment with uv:

```bash
uv sync
```

Generate or refresh the lockfile explicitly when needed:

```bash
uv lock
```

Run tests through uv so the managed environment is always used:

```bash
uv run python -m unittest discover -s tests
```

Then in the notebook or a script:

```python
from pathlib import Path

from offer_compare.compare.offers import build_offer_comparison
from offer_compare.loaders.employer_config import load_assumptions, load_employer_offer

root = Path.cwd()
assumptions = load_assumptions(root / "configs" / "assumptions.toml")

offers = [
    load_employer_offer(root / "configs" / "employers" / "visionite.toml"),
    load_employer_offer(root / "configs" / "employers" / "volvo_cars.toml"),
]

comparison = build_offer_comparison(offers=offers, assumptions=assumptions)
comparison
```

## Notes

- Keep employer-specific inputs in TOML, not in the notebook.
- Keep calculations in pure functions under `src/offer_compare/calc/`.
- Add Skatteverket loaders under `src/offer_compare/loaders/tax_tables.py` as you bring in real files.
- Use `uv run` for project commands instead of calling `pip` or the system Python directly.
