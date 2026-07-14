"""Module 06, Exercise 1 — Write-Audit-Publish.

The quality gate (v3) protects marts from bad SALES data — but a bug in the
mart SQL itself still publishes straight to the dashboards. WAP closes that
hole with the data equivalent of a blue-green deployment:

    WRITE    build the new table under a staging name, invisible to consumers
    AUDIT    run checks against the STAGING table
    PUBLISH  only if audits pass, atomically swap staging into place;
             otherwise leave production untouched and keep staging for autopsy

Implement `write_audit_publish` per the docstring. The tests publish a good
build, then sabotage one — production must survive the sabotage bit-for-bit.

Run:  make check MODULE=06
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import duckdb

#: An audit receives (connection, staging_table_name) and returns
#: (audit_name, passed). Audits never raise on failure — they measure.
Audit = Callable[[duckdb.DuckDBPyConnection, str], tuple[str, bool]]


@dataclass(frozen=True)
class WapResult:
    published: bool
    table: str
    staging_table: str  # where the candidate was built, e.g. "staging_daily_revenue"
    failed_audits: list[str]  # names of audits that failed (empty if published)


def write_audit_publish(
    con: duckdb.DuckDBPyConnection,
    table: str,
    build_sql: str,
    audits: list[Audit],
) -> WapResult:
    """Build `table` safely.

    1. WRITE:   CREATE OR REPLACE a staging table named f"staging_{table}"
                from `build_sql` (a SELECT statement).
    2. AUDIT:   run every audit against the staging table. Run ALL of them
                even after one fails — a complete failure report beats a
                fast one.
    3. PUBLISH: if all passed, atomically replace `table` with the staging
                contents and drop the staging table.
                If any failed: `table` must remain EXACTLY as it was, and
                the staging table must be KEPT so an engineer can inspect
                what the audits rejected.
    """
    raise NotImplementedError
