"""I/O edge: reading source files. Thin by design — no business logic here."""

from __future__ import annotations

import csv
from pathlib import Path


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    """Read a CSV file into a list of header-keyed string dicts."""
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def list_sales_files(raw_dir: Path) -> list[Path]:
    """All daily sales files, oldest first (deterministic order matters)."""
    return sorted((raw_dir / "sales").glob("sales_*.csv"))
