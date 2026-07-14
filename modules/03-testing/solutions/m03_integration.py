"""Module 03, Exercise 2 — reference solution.

Arrange-act-assert with real I/O, all inside a disposable directory. Note
what is NOT here: no cleanup code (pytest's tmp_path owns the directory),
no mocks (integration tests earn their slowness by being real), and no
dependence on `make data` having been run (a test that needs manual setup
isn't a test, it's a ritual).
"""

from __future__ import annotations

from pathlib import Path

import duckdb
from corecafe.config import Config
from corecafe.pipeline import run
from datagen import write_dataset


def run_pipeline_in(workdir: Path) -> dict:
    # ARRANGE — small, seeded, generated on the spot.
    raw = workdir / "raw"
    write_dataset(raw, days=2, seed=42)

    # ACT — the pipeline sees only Config; nothing global, nothing shared.
    warehouse = workdir / "test.duckdb"
    summary = run(Config(vat_rate=1.17, raw_dir=str(raw), warehouse_path=str(warehouse)))

    # EVIDENCE — queried fresh from the warehouse the run produced.
    con = duckdb.connect(str(warehouse), read_only=True)
    sales_count = con.execute("SELECT count(*) FROM sales").fetchone()[0]
    mart_days = con.execute("SELECT count(DISTINCT day) FROM daily_revenue").fetchone()[0]
    revenue_total = con.execute("SELECT round(sum(revenue), 2) FROM daily_revenue").fetchone()[0]
    con.close()

    return {
        "summary": summary,
        "sales_count": sales_count,
        "mart_days": mart_days,
        "revenue_total": revenue_total,
    }
