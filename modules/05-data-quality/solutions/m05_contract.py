"""Module 05, Exercise 2 — reference solution."""

from __future__ import annotations

import duckdb

SALES_CONTRACT: dict = {
    "table": "sales",
    "version": 1,
    "owner": "data-team@corecafe.example",
    "columns": {
        "sale_id": {"type": "VARCHAR", "nullable": False},
        "store_id": {"type": "INTEGER", "nullable": True},  # source drops it sometimes;
        # admitted as NULL by policy (Module 02), monitored by the not_null
        # check at "warn" severity rather than promised away.
        "product_id": {"type": "INTEGER", "nullable": False},
        "quantity": {"type": "INTEGER", "nullable": False},
        "unit_price": {"type": "DOUBLE", "nullable": False},
        "revenue": {"type": "DOUBLE", "nullable": False},
        "sold_at": {"type": "TIMESTAMP", "nullable": False},
        "payment_method": {"type": "VARCHAR", "nullable": False},
    },
}


def validate_schema(con: duckdb.DuckDBPyConnection, contract: dict) -> list[str]:
    live = {
        row[0]: row[1]
        for row in con.execute(
            """
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = ?
            ORDER BY ordinal_position
            """,
            [contract["table"]],
        ).fetchall()
    }

    violations: list[str] = []
    expected = contract["columns"]

    for name, spec in expected.items():
        if name not in live:
            violations.append(f"missing column: {name}")
        elif live[name] != spec["type"]:
            violations.append(
                f"type mismatch on {name}: expected {spec['type']}, found {live[name]}"
            )
    for name in live:
        if name not in expected:
            violations.append(f"unexpected column: {name}")

    return violations
