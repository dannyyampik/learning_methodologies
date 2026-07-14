"""Module 05, Exercise 1 — Build the expectations engine.

You will build (a small but real version of) what dbt tests, Great
Expectations, and Soda sell: declarative checks that run against the
warehouse and gate the pipeline. Building it yourself — it's ~80 lines —
is the fastest route to *deep* understanding of every such tool.

Every check follows one universal shape (this IS the dbt test model):

    a check = a query that returns FAILING rows; pass = zero failures

Implement the five checks and the verdict function below. Each check
returns a CheckResult; none of them raises on failure — deciding what to
DO about failures is the verdict's job (separating measurement from
policy is what makes severity levels possible).

Run:  make check MODULE=05
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import duckdb

Severity = Literal["error", "warn"]


@dataclass(frozen=True)
class CheckResult:
    name: str  # e.g. "not_null: sales.store_id"
    passed: bool
    failing_rows: int
    severity: Severity


@dataclass(frozen=True)
class Verdict:
    passed: bool  # False iff any ERROR-severity check failed
    errors: list[CheckResult]  # failed checks with severity "error"
    warnings: list[CheckResult]  # failed checks with severity "warn"


def check_not_null(
    con: duckdb.DuckDBPyConnection, table: str, column: str, severity: Severity = "error"
) -> CheckResult:
    """Fail for every row where `column` IS NULL."""
    raise NotImplementedError


def check_unique(
    con: duckdb.DuckDBPyConnection, table: str, column: str, severity: Severity = "error"
) -> CheckResult:
    """Fail for every row whose `column` value appears more than once.

    Count the EXTRA rows (a value appearing 3x contributes 2 failing rows).
    """
    raise NotImplementedError


def check_accepted_values(
    con: duckdb.DuckDBPyConnection,
    table: str,
    column: str,
    values: list[str],
    severity: Severity = "error",
) -> CheckResult:
    """Fail for every (non-null) row whose `column` is not in `values`."""
    raise NotImplementedError


def check_relationship(
    con: duckdb.DuckDBPyConnection,
    table: str,
    column: str,
    ref_table: str,
    ref_column: str,
    severity: Severity = "error",
) -> CheckResult:
    """Referential integrity: fail for every (non-null) `table.column` value
    that does not exist in `ref_table.ref_column` — orphans, like a sale
    pointing at a store nobody has heard of."""
    raise NotImplementedError


def check_expression(
    con: duckdb.DuckDBPyConnection,
    table: str,
    name: str,
    predicate_sql: str,
    severity: Severity = "error",
) -> CheckResult:
    """The escape hatch: fail for every row where `predicate_sql` is NOT
    satisfied. Example: check_expression(con, "sales", "positive_quantity",
    "quantity > 0"). This one primitive can express almost any business
    rule — it is dbt's 'singular test'."""
    raise NotImplementedError


def verdict(results: list[CheckResult]) -> Verdict:
    """Turn measurements into a decision.

    The pipeline gates on `passed`: any failed error-severity check blocks
    publication; failed warn-severity checks are reported but do not block.
    """
    raise NotImplementedError
