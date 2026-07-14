"""I/O edge: writing to the warehouse."""

from __future__ import annotations

from collections.abc import Iterable

import duckdb

from corecafe.transform import Sale

SALES_DDL = """
CREATE TABLE IF NOT EXISTS sales (
    sale_id VARCHAR, store_id INT, product_id INT, quantity INT,
    unit_price DOUBLE, revenue DOUBLE, sold_at TIMESTAMP, payment_method VARCHAR
)
"""


def connect(warehouse_path: str) -> duckdb.DuckDBPyConnection:
    return duckdb.connect(warehouse_path)


def load_dimension(con: duckdb.DuckDBPyConnection, table: str, csv_path: str) -> None:
    """(Re)load a small dimension table straight from its CSV."""
    con.execute(f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM read_csv_auto(?)", [csv_path])


def append_sales(con: duckdb.DuckDBPyConnection, rows: Iterable[Sale]) -> int:
    """Append parsed sales to the sales table.

    KNOWN ISSUE: append-only — re-running the pipeline re-inserts every file
    it has already loaded (the Module 00 bug, faithfully preserved by the
    refactor). Module 04 replaces this with idempotent partition overwrites.
    """
    con.execute(SALES_DDL)
    data = [
        (
            s.sale_id,
            s.store_id,
            s.product_id,
            s.quantity,
            s.unit_price,
            s.revenue,
            s.sold_at,
            s.payment_method,
        )
        for s in rows
    ]
    con.executemany("INSERT INTO sales VALUES (?, ?, ?, ?, ?, ?, ?, ?)", data)
    return len(data)


def build_marts(con: duckdb.DuckDBPyConnection) -> None:
    """Rebuild the derived tables the dashboards read."""
    con.execute("""
        CREATE OR REPLACE TABLE daily_revenue AS
        SELECT CAST(s.sold_at AS DATE) AS day, s.store_id, st.store_name, st.city,
               SUM(s.revenue) AS revenue, COUNT(*) AS transactions
        FROM sales s LEFT JOIN stores st ON s.store_id = st.store_id
        GROUP BY 1, 2, 3, 4
    """)
    con.execute("""
        CREATE OR REPLACE TABLE top_products AS
        SELECT p.product_name, p.category, SUM(s.quantity) AS units,
               SUM(s.revenue) AS revenue
        FROM sales s JOIN products p ON s.product_id = p.product_id
        GROUP BY 1, 2 ORDER BY revenue DESC
    """)
