"""Tests for the course's own data generator.

Yes, the teaching tool has tests. That is the point of the course.
"""

import random
from datetime import date

import pytest
from datagen import generate_dimensions, generate_sales_day, write_dataset
from datagen.generator import SALES_HEADER


def test_generation_is_deterministic():
    a = generate_sales_day(date(2026, 6, 1), random.Random(42))
    b = generate_sales_day(date(2026, 6, 1), random.Random(42))
    assert [r.as_list() for r in a] == [r.as_list() for r in b]


def test_dimensions_are_static():
    stores, products = generate_dimensions()
    assert len(stores) == 5
    assert len(products) == 12


def test_duplicates_defect_adds_repeated_sale_ids():
    rows = generate_sales_day(date(2026, 6, 1), random.Random(1), {"duplicates"})
    ids = [r.sale_id for r in rows]
    assert len(ids) > len(set(ids))


def test_nulls_defect_blanks_store_ids():
    rows = generate_sales_day(date(2026, 6, 1), random.Random(1), {"nulls"})
    assert any(r.store_id is None for r in rows)


def test_unknown_defect_kind_is_rejected():
    with pytest.raises(ValueError, match="Unknown defect"):
        generate_sales_day(date(2026, 6, 1), random.Random(1), {"gremlins"})


def test_write_dataset_layout(tmp_path):
    report = write_dataset(tmp_path, days=3, seed=42)
    assert (tmp_path / "stores.csv").exists()
    assert (tmp_path / "products.csv").exists()
    sales_files = sorted((tmp_path / "sales").glob("sales_*.csv"))
    assert len(sales_files) == 3
    assert report.days == ["2026-06-01", "2026-06-02", "2026-06-03"]

    header = sales_files[0].read_text().splitlines()[0]
    assert header.split(",") == SALES_HEADER
