"""Write-Audit-Publish — Module 06's exercise, promoted into the product.

Blue-green deployment for tables: build under a staging name, audit the
candidate, publish only on green. On failure production is untouched and
the staging table is kept for autopsy.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import duckdb

Audit = Callable[[duckdb.DuckDBPyConnection, str], tuple[str, bool]]


@dataclass(frozen=True)
class WapResult:
    published: bool
    table: str
    staging_table: str
    failed_audits: list[str]


def write_audit_publish(
    con: duckdb.DuckDBPyConnection,
    table: str,
    build_sql: str,
    audits: list[Audit],
) -> WapResult:
    staging = f"staging_{table}"
    con.execute(f"CREATE OR REPLACE TABLE {staging} AS {build_sql}")

    failed = [name for name, passed in (audit(con, staging) for audit in audits) if not passed]
    if failed:
        return WapResult(published=False, table=table, staging_table=staging, failed_audits=failed)

    con.execute("BEGIN TRANSACTION")
    try:
        con.execute(f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM {staging}")
        con.execute(f"DROP TABLE {staging}")
        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        raise
    return WapResult(published=True, table=table, staging_table=staging, failed_audits=[])
