"""Module 04, Exercise 1 — reference solution."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

import duckdb

SALES_DDL = """
CREATE TABLE IF NOT EXISTS sales (
    sale_id VARCHAR, store_id INT, product_id INT, quantity INT,
    unit_price DOUBLE, revenue DOUBLE, sold_at TIMESTAMP, payment_method VARCHAR
)
"""

SALES_COLUMNS = (
    "sale_id",
    "store_id",
    "product_id",
    "quantity",
    "unit_price",
    "revenue",
    "sold_at",
    "payment_method",
)


@dataclass
class LoadReport:
    day: date
    rows: int
    replaced_existing: bool


def partition_date_of(csv_path: Path) -> date:
    stem = csv_path.stem  # "sales_2026-06-03"
    prefix = "sales_"
    if not stem.startswith(prefix):
        raise ValueError(f"cannot determine partition date from filename: {csv_path.name}")
    try:
        return date.fromisoformat(stem.removeprefix(prefix))
    except ValueError:
        raise ValueError(
            f"cannot determine partition date from filename: {csv_path.name}"
        ) from None


def overwrite_partition(con: duckdb.DuckDBPyConnection, day: date, rows: list[tuple]) -> LoadReport:
    con.execute(SALES_DDL)
    existing = con.execute(
        "SELECT count(*) FROM sales WHERE CAST(sold_at AS DATE) = ?", [day]
    ).fetchone()[0]

    # The transaction is the whole trick: DELETE + INSERT become one
    # indivisible event. Readers see the old partition or the new one —
    # never an empty or half-loaded in-between.
    con.execute("BEGIN TRANSACTION")
    try:
        con.execute("DELETE FROM sales WHERE CAST(sold_at AS DATE) = ?", [day])
        if rows:
            con.executemany("INSERT INTO sales VALUES (?, ?, ?, ?, ?, ?, ?, ?)", rows)
        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        raise

    return LoadReport(day=day, rows=len(rows), replaced_existing=existing > 0)


def _parse_row_strict(raw: dict[str, str], vat_rate: float) -> tuple:
    try:
        quantity = int(raw["quantity"])
        unit_price = float(raw["unit_price"])
        sold_at = datetime.fromisoformat(raw["sold_at"])
    except (KeyError, ValueError):
        raise ValueError(f"unparseable row: {raw!r}") from None
    store_raw = raw.get("store_id") or None
    return (
        raw["sale_id"],
        int(store_raw) if store_raw is not None else None,
        int(raw["product_id"]),
        quantity,
        unit_price,
        quantity * unit_price * vat_rate,
        sold_at,
        raw["payment_method"],
    )


def load_sales_csv(con: duckdb.DuckDBPyConnection, csv_path: Path, vat_rate: float) -> LoadReport:
    day = partition_date_of(csv_path)
    with csv_path.open(newline="") as f:
        # Parse the WHOLE file before touching the database: a parse error
        # on row 400 must not leave rows 1-399 half-written. Parse fully,
        # then write atomically.
        rows = [_parse_row_strict(raw, vat_rate) for raw in csv.DictReader(f)]
    return overwrite_partition(con, day, rows)


def backfill(
    con: duckdb.DuckDBPyConnection,
    raw_dir: Path,
    start: date,
    end: date,
    vat_rate: float,
) -> dict[date, LoadReport | None]:
    if end < start:
        raise ValueError("backfill range is reversed")
    results: dict[date, LoadReport | None] = {}
    day = start
    while day <= end:
        path = raw_dir / "sales" / f"sales_{day.isoformat()}.csv"
        results[day] = load_sales_csv(con, path, vat_rate) if path.exists() else None
        day = date.fromordinal(day.toordinal() + 1)
    return results
