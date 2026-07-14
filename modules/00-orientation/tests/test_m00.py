"""Self-check for Module 00.

These tests run the inherited pipeline for real (twice), measure what it
does, and compare reality with the observations you recorded in
exercises/m00_observations.py.
"""

import subprocess
import sys
from pathlib import Path

import duckdb
import pytest
from datagen import write_dataset

PIPELINE = Path(__file__).resolve().parents[1] / "project" / "pipeline.py"


@pytest.fixture(scope="module")
def pipeline_run_counts(tmp_path_factory):
    """Run the monolith twice against a small fresh dataset; return row counts."""
    workdir = tmp_path_factory.mktemp("corecafe")
    write_dataset(workdir / "data" / "raw", days=3, seed=42)

    counts = {}
    for run in (1, 2):
        result = subprocess.run(
            [sys.executable, str(PIPELINE)],
            cwd=workdir,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"pipeline crashed on run {run}:\n{result.stderr}"
        con = duckdb.connect(str(workdir / "data" / "warehouse.duckdb"), read_only=True)
        counts[run] = {
            "sales": con.execute("SELECT count(*) FROM sales").fetchone()[0],
            "stores": con.execute("SELECT count(*) FROM stores").fetchone()[0],
            "revenue": con.execute("SELECT sum(revenue) FROM daily_revenue").fetchone()[0],
        }
        con.close()
    return counts


def _answered(value, name):
    if value is Ellipsis:
        pytest.fail(f"You haven't answered {name} yet — replace the ... in the exercise file.")
    return value


def test_sales_multiplier(pipeline_run_counts):
    import m00_observations as ans

    student = _answered(ans.SALES_MULTIPLIER_AFTER_SECOND_RUN, "SALES_MULTIPLIER_AFTER_SECOND_RUN")
    actual = pipeline_run_counts[2]["sales"] / pipeline_run_counts[1]["sales"]
    assert student == actual, (
        f"You said the second run multiplies `sales` by {student}, but it actually "
        f"multiplied {pipeline_run_counts[1]['sales']} rows into "
        f"{pipeline_run_counts[2]['sales']} (x{actual:.0f}). Run it yourself and watch."
    )


def test_finance_dashboard(pipeline_run_counts):
    import m00_observations as ans

    student = _answered(ans.FINANCE_DASHBOARD_IS_ALSO_WRONG, "FINANCE_DASHBOARD_IS_ALSO_WRONG")
    actually_wrong = pipeline_run_counts[2]["revenue"] > pipeline_run_counts[1]["revenue"] * 1.5
    assert student == actually_wrong, (
        "Check `daily_revenue` after each run: derived tables are rebuilt from `sales`, "
        "so whatever happened to `sales` flows straight into the dashboard."
    )


def test_idempotency_conclusion():
    import m00_observations as ans

    student = _answered(ans.PIPELINE_IS_IDEMPOTENT, "PIPELINE_IS_IDEMPOTENT")
    assert student is False, (
        "Idempotent means: run it twice, get the same state as running it once. "
        "You just watched the row count double."
    )


def test_bug_stage():
    import m00_observations as ans

    student = _answered(ans.STAGE_WHERE_THE_BUG_LIVES, "STAGE_WHERE_THE_BUG_LIVES")
    assert student in {"extract", "transform", "load"}, "Answer must be one of the three stages."
    assert student == "load", (
        "Reading the same files twice is fine; computing revenue twice is fine; "
        "the damage happens where rows are APPENDED to a table that already has them."
    )


def test_stores_survival(pipeline_run_counts):
    import m00_observations as ans

    student = _answered(ans.WHY_STORES_SURVIVES, "WHY_STORES_SURVIVES")
    assert pipeline_run_counts[2]["stores"] == pipeline_run_counts[1]["stores"]
    assert student.strip().upper() == "OR REPLACE", (
        "Look at how the `stores` table is created vs how `sales` is created. "
        "One of them drops-and-recreates on every run."
    )
