"""Module 05, Exercise 1 — reference solution.

Note the one shape underneath all five checks: count the rows that violate
a promise. dbt generates exactly these queries from your schema.yml; Great
Expectations wraps them in a validation API. The concept fits in a page.
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


def _count(con: duckdb.DuckDBPyConnection, sql: str) -> int:
    return con.execute(sql).fetchone()[0]


def _result(name: str, failing: int, severity: Severity) -> CheckResult:
    return CheckResult(name=name, passed=failing == 0, failing_rows=failing, severity=severity)


def check_not_null(
    con: duckdb.DuckDBPyConnection, table: str, column: str, severity: Severity = "error"
) -> CheckResult:
    failing = _count(con, f"SELECT count(*) FROM {table} WHERE {column} IS NULL")
    return _result(f"not_null: {table}.{column}", failing, severity)


def check_unique(
    con: duckdb.DuckDBPyConnection, table: str, column: str, severity: Severity = "error"
) -> CheckResult:
    # Extra copies beyond the first are the failures: 3 rows sharing an id
    # = 2 failing rows. count(*) - count(DISTINCT ...) computes it directly.
    failing = _count(
        con,
        f"SELECT count({column}) - count(DISTINCT {column}) FROM {table}",
    )
    return _result(f"unique: {table}.{column}", failing, severity)


def check_accepted_values(
    con: duckdb.DuckDBPyConnection,
    table: str,
    column: str,
    values: list[str],
    severity: Severity = "error",
) -> CheckResult:
    placeholders = ", ".join("?" for _ in values)
    failing = con.execute(
        f"SELECT count(*) FROM {table} "
        f"WHERE {column} IS NOT NULL AND {column} NOT IN ({placeholders})",
        values,
    ).fetchone()[0]
    return _result(f"accepted_values: {table}.{column}", failing, severity)


def check_relationship(
    con: duckdb.DuckDBPyConnection,
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
          AND NOT EXISTS (
              SELECT 1 FROM {ref_table} r WHERE r.{ref_column} = t.{column}
          )
        """,
    )
    return _result(f"relationship: {table}.{column} -> {ref_table}.{ref_column}", failing, severity)


def check_expression(
    con: duckdb.DuckDBPyConnection,
    table: str,
    name: str,
    predicate_sql: str,
    severity: Severity = "error",
) -> CheckResult:
    # NOT (predicate) alone would miss NULLs (NULL is not TRUE and not FALSE);
    # COALESCE makes "predicate not satisfied" catch them too.
    failing = _count(
        con,
        f"SELECT count(*) FROM {table} WHERE NOT COALESCE(({predicate_sql}), FALSE)",
    )
    return _result(f"expression: {table}.{name}", failing, severity)


def verdict(results: list[CheckResult]) -> Verdict:
    errors = [r for r in results if not r.passed and r.severity == "error"]
    warnings = [r for r in results if not r.passed and r.severity == "warn"]
    return Verdict(passed=not errors, errors=errors, warnings=warnings)
