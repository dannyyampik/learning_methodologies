"""Module 03, Exercise 2 — One real integration test.

Unit tests (Exercise 1) prove the logic; an integration test proves the
WIRING: files really read, rows really loaded, marts really built. You will
write the classic arrange-act-assert pattern against a REAL (temporary)
warehouse — no mocks, small data, disposable environment.

Implement `run_pipeline_in(workdir)`:

  ARRANGE  generate 2 days of source data (2026-06-01, seed 42) into
           workdir/"raw" using datagen.write_dataset
  ACT      run the corecafe pipeline with a Config pointing at that raw dir
           and a warehouse at workdir/"test.duckdb"
  ASSERT   (the grading tests do the asserting — you return the evidence)

Return a dict with:
    "summary"        the RunSummary the pipeline returned
    "sales_count"    row count of the sales table
    "mart_days"      number of distinct days in daily_revenue
    "revenue_total"  SUM(revenue) from daily_revenue, rounded to 2 decimals

Run:  make check MODULE=03
"""

from __future__ import annotations

from pathlib import Path


def run_pipeline_in(workdir: Path) -> dict:
    raise NotImplementedError
