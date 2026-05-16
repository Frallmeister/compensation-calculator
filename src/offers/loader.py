"""Module with functions used to load data."""

import logging
import tomllib
from pathlib import Path
from typing import Any, Literal, overload

import pandas as pd

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "configs"
EMPLOYER_CONFIG_DIR = CONFIG_DIR / "employers"
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

type TomlKey = Literal["assumptions", "visionite", "volvo_cars"]

KNOWN_TOML_FILES: dict[TomlKey, Path] = {
    "assumptions": CONFIG_DIR / "assumptions.toml",
    "visionite": EMPLOYER_CONFIG_DIR / "visionite.toml",
    "volvo_cars": EMPLOYER_CONFIG_DIR / "volvo_cars.toml",
}

def refine_skattetabell() -> None:
    """Load the Skatteverket tax table CSV and store as a parquet."""
    file_path = RAW_DATA_DIR / "skattetabell.csv"
    df = pd.read_csv(file_path)
    df = df[["Antal dgr", "Tabellnr", "Inkomst fr.o.m.", "Inkomst t.o.m.", "Kolumn 1"]]
    df = df.rename(
        columns={
            "Antal dgr": "days",
            "Tabellnr": "table_no",
            "Inkomst fr.o.m.": "lower_bound",
            "Inkomst t.o.m.": "upper_bound",
            "Kolumn 1": "tax",
        },
    )
    file_destination = PROCESSED_DATA_DIR / "skattetabell.parquet"
    df.to_parquet(file_destination)
    logger.info("Wrote file %s", file_destination.relative_to(PROJECT_ROOT))


def load_tax_table(table_no: int|None=None) -> pd.DataFrame:
    """Load the general tax table."""
    df = pd.read_parquet(PROCESSED_DATA_DIR / "skattetabell.parquet")
    if table_no:
        df = df.query("table_no == @table_no")
    return df

@overload
def load_toml(source: TomlKey) -> dict[str, Any]: ...


@overload
def load_toml(source: Path) -> dict[str, Any]: ...


def load_toml(source: TomlKey | Path) -> dict[str, Any]:
    """Load a TOML config by known key or explicit path."""
    if isinstance(source, Path):
        file_path = source
    else:
        if source not in KNOWN_TOML_FILES:
            allowed = ", ".join(sorted(KNOWN_TOML_FILES))
            msg = f"Unknown TOML key {source!r}. Expected one of: {allowed}"
            raise ValueError(msg)
        file_path = KNOWN_TOML_FILES[source]

    with file_path.open("rb") as file:
        return tomllib.load(file)
