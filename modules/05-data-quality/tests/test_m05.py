"""Self-check for Module 05: the expectations engine and the data contract."""

import os
import subprocess
import sys
from pathlib import Path

import duckdb

MODULE_DIR = Path(__file__).resolve().parents[1]

# --------------------------------------------------------------------------
# Exercise 1 — the expectations engine, against a deliberately dirty table
# --------------------------------------------------------------------------


def test_not_null_finds_the_null_store(dirty_warehouse):
    from m05_expectations import check_not_null

    result = check_not_null(dirty_warehouse, "sales", "store_id")
    assert result.passed is False
    assert result.failing_rows == 1
    clean = check_not_null(dirty_warehouse, "sales", "sale_id")
    assert clean.passed is True and clean.failing_rows == 0


def test_unique_counts_extra_copies(dirty_warehouse):
    from m05_expectations import check_unique

    result = check_unique(dirty_warehouse, "sales", "sale_id")
    assert result.passed is False
    assert result.failing_rows == 1, (
        "s-2 appears twice = ONE extra copy. Count the surplus rows, not the "
        "distinct values involved."
    )


def test_accepted_values_spots_bitcoin(dirty_warehouse):
    from m05_expectations import check_accepted_values

    result = check_accepted_values(
        dirty_warehouse, "sales", "payment_method", ["card", "cash", "app"]
    )
    assert result.passed is False
    assert result.failing_rows == 1


def test_relationship_finds_the_ghost_store(dirty_warehouse):
    from m05_expectations import check_relationship

    result = check_relationship(dirty_warehouse, "sales", "store_id", "stores", "store_id")
    assert result.passed is False
    assert result.failing_rows == 1, (
        "Store 99 exists in no dimension. Note: the NULL store_id row is NOT an "
        "orphan — unknown is a different problem from wrong, and it is "
        "not_null's job. One defect per check keeps failures diagnosable."
    )


def test_expression_catches_negative_quantities(dirty_warehouse):
    from m05_expectations import check_expression

    result = check_expression(dirty_warehouse, "sales", "positive_quantity", "quantity > 0")
    assert result.passed is False
    assert result.failing_rows == 1


def test_expression_treats_null_predicate_as_failing(dirty_warehouse):
    from m05_expectations import check_expression

    # store_id IS NULL makes `store_id > 0` evaluate to NULL — neither true
    # nor false. A row that can't PROVE it satisfies the rule fails the rule.
    result = check_expression(dirty_warehouse, "sales", "store_positive", "store_id > 0")
    assert result.failing_rows == 1, (
        "SQL three-valued logic strikes: NOT (NULL) is NULL, which WHERE "
        "treats as false — so the NULL row silently escapes. COALESCE the "
        "predicate to FALSE."
    )


def test_verdict_separates_errors_from_warnings(dirty_warehouse):
    from m05_expectations import (
        check_accepted_values,
        check_not_null,
        check_unique,
        verdict,
    )

    results = [
        check_unique(dirty_warehouse, "sales", "sale_id", severity="error"),
        check_not_null(dirty_warehouse, "sales", "store_id", severity="warn"),
        check_accepted_values(
            dirty_warehouse,
            "sales",
            "payment_method",
            ["card", "cash", "app"],
            severity="warn",
        ),
        check_not_null(dirty_warehouse, "sales", "sale_id", severity="error"),  # passes
    ]
    v = verdict(results)
    assert v.passed is False, "A failed error-severity check must block."
    assert len(v.errors) == 1
    assert len(v.warnings) == 2, "Failed warn checks are reported, not blocking."

    v2 = verdict([r for r in results if r.severity == "warn"])
    assert v2.passed is True, "Warnings alone must not block the pipeline."


def test_clean_data_passes_the_full_suite(dirty_warehouse):
    from m05_expectations import (
        check_expression,
        check_not_null,
        check_relationship,
        check_unique,
        verdict,
    )

    con = duckdb.connect(":memory:")
    con.execute("CREATE TABLE stores AS SELECT * FROM range(1) t(store_id)")
    con.execute("""
        CREATE TABLE sales AS SELECT
            'ok-' || i AS sale_id, 0 AS store_id, 101 AS product_id,
            1 AS quantity, 2.5 AS unit_price, 2.925 AS revenue,
            TIMESTAMP '2026-06-03 09:00:00' AS sold_at, 'card' AS payment_method
        FROM range(10) t(i)
    """)
    v = verdict(
        [
            check_not_null(con, "sales", "sale_id"),
            check_unique(con, "sales", "sale_id"),
            check_relationship(con, "sales", "store_id", "stores", "store_id"),
            check_expression(con, "sales", "positive_quantity", "quantity > 0"),
        ]
    )
    assert v.passed is True and not v.errors and not v.warnings
    con.close()


# --------------------------------------------------------------------------
# Exercise 2 — the contract
# --------------------------------------------------------------------------

SALES_DDL = """
CREATE TABLE sales (
    sale_id VARCHAR, store_id INT, product_id INT, quantity INT,
    unit_price DOUBLE, revenue DOUBLE, sold_at TIMESTAMP, payment_method VARCHAR
)
"""


def test_contract_matches_reality():
    from m05_contract import SALES_CONTRACT, validate_schema

    con = duckdb.connect(":memory:")
    con.execute(SALES_DDL)
    violations = validate_schema(con, SALES_CONTRACT)
    assert violations == [], (
        f"The contract disagrees with the table the pipeline actually builds: "
        f"{violations}. Contract-first is fine, but the contract must be TRUE."
    )
    assert len(SALES_CONTRACT["columns"]) == 8
    con.close()


def test_contract_catches_dropped_column():
    from m05_contract import SALES_CONTRACT, validate_schema

    con = duckdb.connect(":memory:")
    con.execute(SALES_DDL)
    con.execute("ALTER TABLE sales DROP COLUMN payment_method")
    violations = validate_schema(con, SALES_CONTRACT)
    assert any("missing column: payment_method" in v for v in violations)
    con.close()


def test_contract_catches_type_drift():
    from m05_contract import SALES_CONTRACT, validate_schema

    con = duckdb.connect(":memory:")
    con.execute(SALES_DDL)
    con.execute("ALTER TABLE sales ALTER COLUMN store_id SET DATA TYPE VARCHAR")
    violations = validate_schema(con, SALES_CONTRACT)
    assert any(v.startswith("type mismatch on store_id") for v in violations), (
        "store_id silently became VARCHAR — the classic upstream drift that "
        "breaks every downstream join. The contract must catch it."
    )
    con.close()


def test_contract_catches_surprise_column():
    from m05_contract import SALES_CONTRACT, validate_schema

    con = duckdb.connect(":memory:")
    con.execute(SALES_DDL)
    con.execute("ALTER TABLE sales ADD COLUMN discount_pct DOUBLE")
    violations = validate_schema(con, SALES_CONTRACT)
    assert any("unexpected column: discount_pct" in v for v in violations), (
        "New columns sound harmless — until a SELECT * downstream doubles its "
        "byte bill or a BI extract breaks. Surprises violate contracts."
    )
    con.close()


# --------------------------------------------------------------------------
# The project snapshot itself still works (run in a subprocess so this
# module's corecafe v2 can't collide with other modules' snapshots)
# --------------------------------------------------------------------------


def test_project_snapshot_is_idempotent(tmp_path):
    from datagen import write_dataset

    write_dataset(tmp_path / "data" / "raw", days=2, seed=42)
    env = {**os.environ, "PYTHONPATH": str(MODULE_DIR / "project")}
    for _ in range(2):
        result = subprocess.run(
            [sys.executable, "-m", "corecafe"],
            cwd=tmp_path,
            env=env,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
    con = duckdb.connect(str(tmp_path / "data" / "warehouse.duckdb"), read_only=True)
    days = con.execute(
        "SELECT count(DISTINCT CAST(sold_at AS DATE)), count(*) FROM sales"
    ).fetchone()
    con.close()
    assert days[0] == 2 and days[1] > 0
