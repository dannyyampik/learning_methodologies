"""Self-check for Module 06: Write-Audit-Publish and CI concepts."""

import os
import subprocess
import sys
from pathlib import Path

import duckdb
import pytest

MODULE_DIR = Path(__file__).resolve().parents[1]

# --------------------------------------------------------------------------
# Exercise 1 — Write-Audit-Publish
# --------------------------------------------------------------------------


def _warehouse_with_sales():
    con = duckdb.connect(":memory:")
    con.execute("""
        CREATE TABLE sales AS SELECT
            's-' || i AS sale_id,
            1 + (i % 3) AS store_id,
            2.5 * (1 + (i % 2)) AS revenue,
            DATE '2026-06-01' + INTERVAL (i % 3) DAY AS day
        FROM range(30) t(i)
    """)
    return con


def _audit_not_empty(con, staging_table):
    n = con.execute(f"SELECT count(*) FROM {staging_table}").fetchone()[0]
    return ("not_empty", n > 0)


def _audit_revenue_positive(con, staging_table):
    bad = con.execute(f"SELECT count(*) FROM {staging_table} WHERE revenue <= 0").fetchone()[0]
    return ("revenue_positive", bad == 0)


GOOD_BUILD = "SELECT day, sum(revenue) AS revenue FROM sales GROUP BY day"
# The sabotaged build: a "refactor" that flipped a sign.
BAD_BUILD = "SELECT day, -sum(revenue) AS revenue FROM sales GROUP BY day"


def test_wap_publishes_a_good_build():
    from m06_wap import write_audit_publish

    con = _warehouse_with_sales()
    result = write_audit_publish(
        con, "daily_revenue", GOOD_BUILD, [_audit_not_empty, _audit_revenue_positive]
    )
    assert result.published is True
    assert result.failed_audits == []
    rows = con.execute("SELECT count(*) FROM daily_revenue").fetchone()[0]
    assert rows == 3
    staging = con.execute(
        "SELECT count(*) FROM information_schema.tables WHERE table_name = 'staging_daily_revenue'"
    ).fetchone()[0]
    assert staging == 0, "After a successful publish, the staging table should be cleaned up."


def test_wap_failed_audit_leaves_production_untouched():
    from m06_wap import write_audit_publish

    con = _warehouse_with_sales()
    write_audit_publish(con, "daily_revenue", GOOD_BUILD, [_audit_not_empty])
    before = con.execute("SELECT * FROM daily_revenue ORDER BY day").fetchall()

    result = write_audit_publish(
        con, "daily_revenue", BAD_BUILD, [_audit_not_empty, _audit_revenue_positive]
    )
    assert result.published is False
    assert result.failed_audits == ["revenue_positive"]

    after = con.execute("SELECT * FROM daily_revenue ORDER BY day").fetchall()
    assert after == before, (
        "The whole point of WAP: a failed audit must leave consumers looking at "
        "the previous good table, bit for bit. Stale beats wrong."
    )


def test_wap_keeps_staging_for_autopsy():
    from m06_wap import write_audit_publish

    con = _warehouse_with_sales()
    write_audit_publish(con, "daily_revenue", BAD_BUILD, [_audit_revenue_positive])
    negative = con.execute(
        "SELECT count(*) FROM staging_daily_revenue WHERE revenue <= 0"
    ).fetchone()[0]
    assert negative > 0, (
        "The rejected candidate must remain in staging so an engineer can "
        "inspect exactly what the audits refused to publish."
    )


def test_wap_runs_all_audits_even_after_a_failure():
    from m06_wap import write_audit_publish

    con = _warehouse_with_sales()
    calls: list[str] = []

    def audit_a(con_, staging):
        calls.append("a")
        return ("a", False)

    def audit_b(con_, staging):
        calls.append("b")
        return ("b", False)

    result = write_audit_publish(con, "daily_revenue", GOOD_BUILD, [audit_a, audit_b])
    assert calls == ["a", "b"], (
        "Run every audit even after one fails — the engineer fixing this at "
        "9 a.m. wants the complete diagnosis, not a one-failure-at-a-time loop."
    )
    assert result.failed_audits == ["a", "b"]


def test_wap_first_ever_publish_works():
    from m06_wap import write_audit_publish

    con = _warehouse_with_sales()  # no daily_revenue table exists yet
    result = write_audit_publish(con, "daily_revenue", GOOD_BUILD, [_audit_not_empty])
    assert result.published is True
    assert con.execute("SELECT count(*) FROM daily_revenue").fetchone()[0] == 3


# --------------------------------------------------------------------------
# Exercise 2 — CI concepts
# --------------------------------------------------------------------------


def _answered(value, name):
    if value is Ellipsis:
        pytest.fail(f"You haven't answered {name} yet — replace the ... in the exercise file.")
    return value


def test_ci_concepts():
    import m06_ci_concepts as ans

    assert _answered(ans.Q1_CI_TRIGGERS, "Q1") == "pr_and_main", (
        "Read the `on:` block of .github/workflows/ci.yml."
    )
    assert _answered(ans.Q2_NEEDS_LINT, "Q2") == "fail_fast"
    assert _answered(ans.Q3_MAKE_IN_CI, "Q3") == "one_truth", (
        "What goes wrong, slowly, when CI and developers run different commands?"
    )
    assert _answered(ans.Q4_CI_WAREHOUSE, "Q4") == "ephemeral", (
        "Determinism, parallelism, credentials, PII — which option wins on all four?"
    )
    assert _answered(ans.Q5_ENV_DIFFERENCE, "Q5") == "config", (
        "Module 2 exiled something from code — this is why."
    )
    assert _answered(ans.Q6_ROLLBACK_REALITY, "Q6") == "nothing", (
        "The course thesis: the deployable unit is code AND the data it produced."
    )


# --------------------------------------------------------------------------
# The project snapshot (v3): the quality gate actually gates
# --------------------------------------------------------------------------


def _run_snapshot(tmp_path, defect: str | None):
    from datagen import write_dataset

    defect_days = {"2026-06-02": {defect}} if defect else None
    write_dataset(tmp_path / "data" / "raw", days=2, seed=42, defect_days=defect_days)
    env = {**os.environ, "PYTHONPATH": str(MODULE_DIR / "project")}
    return subprocess.run(
        [sys.executable, "-m", "corecafe"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
    )


def test_project_snapshot_blocks_bad_data(tmp_path):
    result = _run_snapshot(tmp_path, "unknown_store")
    assert result.returncode == 1, "Orphan store_ids must block publication (exit 1)."
    assert "relationship" in result.stderr
    con = duckdb.connect(str(tmp_path / "data" / "warehouse.duckdb"), read_only=True)
    marts = con.execute(
        "SELECT count(*) FROM information_schema.tables WHERE table_name = 'daily_revenue'"
    ).fetchone()[0]
    con.close()
    assert marts == 0, "Marts must not be built from data that failed the gate."


def test_project_snapshot_publishes_good_data(tmp_path):
    result = _run_snapshot(tmp_path, None)
    assert result.returncode == 0, result.stderr
