"""Module 06, Exercise 1 — reference solution."""

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

    # WRITE — consumers can't see this table; we can take all the risks
    # we like here.
    con.execute(f"CREATE OR REPLACE TABLE {staging} AS {build_sql}")

    # AUDIT — run everything; a complete diagnosis beats a fast one.
    failed = [name for name, passed in (audit(con, staging) for audit in audits) if not passed]

    if failed:
        # No PUBLISH. Production remains bit-for-bit what it was, and the
        # staging table stays around as the crime scene.
        return WapResult(published=False, table=table, staging_table=staging, failed_audits=failed)

    # PUBLISH — the swap is the only moment consumers are exposed, and it
    # is atomic: they see the old table or the new one, never a mixture.
    con.execute("BEGIN TRANSACTION")
    try:
        con.execute(f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM {staging}")
        con.execute(f"DROP TABLE {staging}")
        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        raise

    return WapResult(published=True, table=table, staging_table=staging, failed_audits=[])
