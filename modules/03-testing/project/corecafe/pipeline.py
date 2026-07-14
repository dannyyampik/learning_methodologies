"""The imperative shell: wiring only. If this file gets interesting, refactor."""

from __future__ import annotations

from dataclasses import dataclass, field
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


def run(config: Config) -> RunSummary:
    raw_dir = Path(config.raw_dir)
    con = load.connect(config.warehouse_path)
    summary = RunSummary()

    load.load_dimension(con, "stores", str(raw_dir / "stores.csv"))
    load.load_dimension(con, "products", str(raw_dir / "products.csv"))

    for path in extract.list_sales_files(raw_dir):
        raw_rows = extract.read_csv_dicts(path)
        result = clean_batch(raw_rows, config.vat_rate)
        summary.rows_loaded += load.append_sales(con, result.rows)
        summary.rows_rejected += len(result.rejects)
        summary.reject_reasons += [reason for _, reason in result.rejects]
        summary.files_processed += 1

    load.build_marts(con)
    con.close()
    return summary
