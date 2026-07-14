"""The imperative shell: wiring only.

v2: each daily file becomes an atomic partition overwrite. Ingestion keeps
Module 02's skip-and-record policy (clean_batch); replacement of the
partition is all-or-nothing (overwrite_sales_partition). Two error
policies, two stages, both deliberate — Module 04's README explains why.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from corecafe import extract, load
from corecafe.config import Config
from corecafe.transform import clean_batch


@dataclass
class RunSummary:
    files_processed: int = 0
    rows_loaded: int = 0
    rows_rejected: int = 0
    reject_reasons: list[str] = field(default_factory=list)


def partition_date_of(csv_path: Path) -> date:
    """Daily files are named sales_YYYY-MM-DD.csv; refuse anything else."""
    stem = csv_path.stem
    if not stem.startswith("sales_"):
        raise ValueError(f"cannot determine partition date from filename: {csv_path.name}")
    try:
        return date.fromisoformat(stem.removeprefix("sales_"))
    except ValueError:
        raise ValueError(
            f"cannot determine partition date from filename: {csv_path.name}"
        ) from None


def run(config: Config) -> RunSummary:
    raw_dir = Path(config.raw_dir)
    con = load.connect(config.warehouse_path)
    summary = RunSummary()

    load.load_dimension(con, "stores", str(raw_dir / "stores.csv"))
    load.load_dimension(con, "products", str(raw_dir / "products.csv"))

    for path in extract.list_sales_files(raw_dir):
        day = partition_date_of(path)
        raw_rows = extract.read_csv_dicts(path)
        result = clean_batch(raw_rows, config.vat_rate)
        summary.rows_loaded += load.overwrite_sales_partition(con, day, result.rows)
        summary.rows_rejected += len(result.rejects)
        summary.reject_reasons += [reason for _, reason in result.rejects]
        summary.files_processed += 1

    load.build_marts(con)
    con.close()
    return summary
