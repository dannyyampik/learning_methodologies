import os
import sys
from pathlib import Path

import duckdb
import pytest

MODULE_DIR = Path(__file__).resolve().parents[1]
TARGET = os.environ.get("COURSE_TARGET", "exercises")
sys.path.insert(0, str(MODULE_DIR / TARGET))


@pytest.fixture
def dirty_warehouse():
    """An in-memory warehouse whose sales table contains one of each classic
    defect: a duplicated sale_id, a NULL store_id, an orphan store (99), a
    negative quantity, and an off-list payment method."""
    con = duckdb.connect(":memory:")
    con.execute("""
        CREATE TABLE stores (store_id INT, store_name VARCHAR, city VARCHAR,
                             opened_date DATE)
    """)
    con.execute("""
        INSERT INTO stores VALUES
        (1, 'Central', 'Tel Aviv', '2019-03-01'),
        (2, 'Marina', 'Herzliya', '2020-07-15')
    """)
    con.execute("""
        CREATE TABLE sales (
            sale_id VARCHAR, store_id INT, product_id INT, quantity INT,
            unit_price DOUBLE, revenue DOUBLE, sold_at TIMESTAMP,
            payment_method VARCHAR)
    """)
    con.execute("""
        INSERT INTO sales VALUES
        ('s-1', 1, 101, 2,  2.50,  5.85, '2026-06-03 09:00:00', 'card'),
        ('s-2', 2, 103, 1,  3.50,  4.095,'2026-06-03 09:10:00', 'cash'),
        ('s-2', 2, 103, 1,  3.50,  4.095,'2026-06-03 09:10:00', 'cash'),  -- dup
        ('s-3', NULL, 105, 1, 4.00, 4.68, '2026-06-03 09:20:00', 'app'),  -- null store
        ('s-4', 99, 101, 1,  2.50,  2.925,'2026-06-03 09:30:00', 'card'), -- orphan store
        ('s-5', 1, 201, -2, 3.25, -7.605,'2026-06-03 09:40:00', 'card'),  -- refund?
        ('s-6', 1, 101, 1,  2.50,  2.925,'2026-06-03 09:50:00', 'bitcoin')
    """)
    yield con
    con.close()
