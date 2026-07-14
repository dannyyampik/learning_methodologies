"""Module 05, Exercise 2 — The data contract.

A data contract is a versioned, machine-checkable statement of what a
dataset promises its consumers: columns, types, nullability, and semantic
rules. It lives in Git, changes via reviewed PRs, and is ENFORCED — a
contract nobody checks is a wish.

Part 1 — write the contract for the `sales` table as CoreCafé actually
builds it (see project/corecafe/load.py's SALES_DDL and the checks the
README motivates).

Part 2 — implement the enforcement: validate_schema() compares the
contract against the live table's schema (DuckDB exposes it via
`information_schema.columns`, columns: column_name, data_type,
is_nullable ('YES'/'NO')).

Run:  make check MODULE=05
"""

from __future__ import annotations

import duckdb

# Fill in every column of the sales table.
# Types are DuckDB's names as reported by information_schema.columns
# (e.g. VARCHAR, INTEGER, DOUBLE, TIMESTAMP).
SALES_CONTRACT: dict = {
    "table": "sales",
    "version": 1,
    "owner": "data-team@corecafe.example",
    "columns": {
        # "sale_id": {"type": "VARCHAR", "nullable": False},
        # ... 7 more ...
    },
}


def validate_schema(con: duckdb.DuckDBPyConnection, contract: dict) -> list[str]:
    """Compare the live table against the contract; return violations.

    Detect, as human-readable strings (one per violation):
    - a contract column missing from the table:      "missing column: X"
    - a table column not in the contract:            "unexpected column: X"
    - a type mismatch:      "type mismatch on X: expected T1, found T2"

    An empty list means the schema honors the contract.
    (Nullability is enforced by the expectations engine at the ROW level —
    schema-level nullability in the contract documents intent.)
    """
    raise NotImplementedError
