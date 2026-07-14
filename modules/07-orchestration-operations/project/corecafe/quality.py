"""The expectations engine — Module 05's exercise, promoted into the product.

A check is a query that returns failing rows; passing = zero failures.
`verdict` turns measurements into policy: failed error-severity checks
block, failed warn-severity checks report.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import duckdb

Severity = Literal["error", "warn"]


@dataclass(frozen=True)
class CheckResult:
    name: str
    passed: bool
    failing_rows: int
    severity: Severity


@dataclass(frozen=True)
class Verdict:
    passed: bool
    errors: list[CheckResult]
    warnings: list[CheckResult]


class QualityGateError(RuntimeError):
    """Raised when error-severity checks fail — the pipeline must not publish."""

    def __init__(self, verdict: Verdict):
        self.verdict = verdict
        names = ", ".join(r.name for r in verdict.errors)
        super().__init__(f"quality gate failed: {names}")


def _count(con: duckdb.DuckDBPyConnection, sql: str, params: list | None = None) -> int:
    return con.execute(sql, params or []).fetchone()[0]


def _result(name: str, failing: int, severity: Severity) -> CheckResult:
    return CheckResult(name=name, passed=failing == 0, failing_rows=failing, severity=severity)


def check_not_null(con, table: str, column: str, severity: Severity = "error") -> CheckResult:
    failing = _count(con, f"SELECT count(*) FROM {table} WHERE {column} IS NULL")
    return _result(f"not_null: {table}.{column}", failing, severity)


def check_unique(con, table: str, column: str, severity: Severity = "error") -> CheckResult:
    failing = _count(con, f"SELECT count({column}) - count(DISTINCT {column}) FROM {table}")
    return _result(f"unique: {table}.{column}", failing, severity)


def check_accepted_values(
    con, table: str, column: str, values: list[str], severity: Severity = "error"
) -> CheckResult:
    placeholders = ", ".join("?" for _ in values)
    failing = _count(
        con,
        f"SELECT count(*) FROM {table} "
        f"WHERE {column} IS NOT NULL AND {column} NOT IN ({placeholders})",
        list(values),
    )
    return _result(f"accepted_values: {table}.{column}", failing, severity)


def check_relationship(
    con,
    table: str,
    column: str,
    ref_table: str,
    ref_column: str,
    severity: Severity = "error",
) -> CheckResult:
    failing = _count(
        con,
        f"""
        SELECT count(*) FROM {table} t
        WHERE t.{column} IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM {ref_table} r WHERE r.{ref_column} = t.{column})
        """,
    )
    return _result(f"relationship: {table}.{column} -> {ref_table}.{ref_column}", failing, severity)


def check_expression(
    con, table: str, name: str, predicate_sql: str, severity: Severity = "error"
) -> CheckResult:
    failing = _count(
        con, f"SELECT count(*) FROM {table} WHERE NOT COALESCE(({predicate_sql}), FALSE)"
    )
    return _result(f"expression: {table}.{name}", failing, severity)


def verdict(results: list[CheckResult]) -> Verdict:
    errors = [r for r in results if not r.passed and r.severity == "error"]
    warnings = [r for r in results if not r.passed and r.severity == "warn"]
    return Verdict(passed=not errors, errors=errors, warnings=warnings)


def sales_suite(con: duckdb.DuckDBPyConnection) -> Verdict:
    """CoreCafé's standing promises about the sales table.

    Severities are POLICY, reviewed in PRs like any other code change:
    - store_id nulls: known POS firmware issue, tolerated, monitored (warn)
    - everything else: blocks publication (error)
    """
    return verdict(
        [
            check_not_null(con, "sales", "sale_id"),
            check_unique(con, "sales", "sale_id"),
            check_not_null(con, "sales", "store_id", severity="warn"),
            check_relationship(con, "sales", "store_id", "stores", "store_id"),
            check_relationship(con, "sales", "product_id", "products", "product_id"),
            check_accepted_values(con, "sales", "payment_method", ["card", "cash", "app"]),
            check_expression(con, "sales", "positive_quantity", "quantity > 0"),
        ]
    )
