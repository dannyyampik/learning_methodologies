"""Module 04, Exercise 1 — Kill the Module 00 bug for good.

You will rebuild the sales loader around ONE idea: **the partition is the
unit of work**. Each daily file maps to one day-partition of the `sales`
table, and loading a file means *atomically replacing that partition* —
never appending to it.

Consequences you must engineer (the tests check all of them):

- Loading the same file twice leaves the table EXACTLY as after once.
- A corrected file re-delivered by the vendor REPLACES the old day cleanly.
- A load that fails halfway leaves the partition UNTOUCHED (all-or-nothing —
  use a transaction: BEGIN / COMMIT / ROLLBACK).
- A backfill is then just a loop over days — safe to re-run at will.

Unlike Module 02's clean_batch (skip-and-record), this loader is STRICT: any
unparseable row aborts the whole file. That is a deliberate design choice
for this stage of the pipeline — the README discusses why both policies
exist and where each belongs.

Run:  make check MODULE=04
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import duckdb

SALES_DDL = """
CREATE TABLE IF NOT EXISTS sales (
    sale_id VARCHAR, store_id INT, product_id INT, quantity INT,
    unit_price DOUBLE, revenue DOUBLE, sold_at TIMESTAMP, payment_method VARCHAR
)
"""

#: Column order for INSERTs, matching SALES_DDL.
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
    replaced_existing: bool  # True if the partition had rows before this load


def partition_date_of(csv_path: Path) -> date:
    """Derive the partition date from a daily file's name.

    Files are named ``sales_YYYY-MM-DD.csv``. Raise ValueError for anything
    else — a file whose partition you cannot determine must not be loaded.
    """
    raise NotImplementedError


def overwrite_partition(
    con: duckdb.DuckDBPyConnection, day: date, rows: list[tuple]
) -> LoadReport:
    """Atomically replace one day's rows in `sales` with `rows`.

    All-or-nothing: on ANY error, the partition must remain exactly as it
    was (transaction + rollback), and the exception must propagate.
    `rows` are tuples in SALES_COLUMNS order.
    """
    raise NotImplementedError


def load_sales_csv(
    con: duckdb.DuckDBPyConnection, csv_path: Path, vat_rate: float
) -> LoadReport:
    """Parse one daily file and overwrite its partition.

    Strict parsing: raise ValueError on the first unparseable row (bad
    quantity / unit_price / sold_at). Empty store_id still becomes None.
    Revenue = quantity * unit_price * vat_rate, as ever.
    """
    raise NotImplementedError


def backfill(
    con: duckdb.DuckDBPyConnection,
    raw_dir: Path,
    start: date,
    end: date,
    vat_rate: float,
) -> dict[date, LoadReport | None]:
    """(Re)load every day in [start, end], inclusive.

    Missing files are recorded as None (a gap to report, not a crash — the
    vendor may simply not have delivered yet). Because every load is an
    idempotent overwrite, running a backfill twice is boring — which is
    the highest compliment a data operation can receive.
    """
    raise NotImplementedError
