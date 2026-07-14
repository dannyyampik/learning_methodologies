"""Self-check for Module 02: the extraction refactor and the lint exercise."""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pytest

TARGET_DIR = Path(__file__).resolve().parents[1] / os.environ.get("COURSE_TARGET", "exercises")

GOOD_ROW = {
    "sale_id": "20260601-1-00000001",
    "store_id": "1",
    "product_id": "103",
    "quantity": "2",
    "unit_price": "3.5",
    "sold_at": "2026-06-01 09:30:00",
    "payment_method": "card",
}


# --------------------------------------------------------------------------
# Exercise 1 — the extraction refactor
# --------------------------------------------------------------------------


def test_compute_revenue_matches_monolith():
    from m02_refactor import compute_revenue

    # Same numbers the monolith produced: qty * price * VAT, no rounding.
    assert compute_revenue(2, 3.5, 1.17) == pytest.approx(8.19)
    assert compute_revenue(1, 2.5, 1.17) == pytest.approx(2.925)


def test_parse_sale_happy_path():
    from m02_refactor import parse_sale

    sale = parse_sale(GOOD_ROW, vat_rate=1.17)
    assert sale.store_id == 1
    assert sale.quantity == 2
    assert sale.revenue == pytest.approx(8.19)
    assert sale.sold_at == datetime(2026, 6, 1, 9, 30)


def test_parse_sale_allows_missing_store():
    from m02_refactor import parse_sale

    sale = parse_sale({**GOOD_ROW, "store_id": ""}, vat_rate=1.17)
    assert sale.store_id is None, (
        "The monolith let empty store_ids through as NULLs — a refactor "
        "preserves behavior, even questionable behavior. (Module 5 is where "
        "we get to question it.)"
    )


@pytest.mark.parametrize(
    ("field", "bad_value"),
    [("quantity", "two"), ("unit_price", "$3.50"), ("sold_at", "0000-00-00 00:00")],
)
def test_parse_sale_is_loud_about_garbage(field, bad_value):
    from m02_refactor import parse_sale

    with pytest.raises(ValueError):
        parse_sale({**GOOD_ROW, field: bad_value}, vat_rate=1.17)


def test_clean_batch_accounts_for_every_row():
    from m02_refactor import clean_batch

    batch = [GOOD_ROW, {**GOOD_ROW, "quantity": "NaN"}, {**GOOD_ROW, "sale_id": "x2"}]
    result = clean_batch(batch, vat_rate=1.17)
    assert len(result.rows) == 2
    assert len(result.rejects) == 1, (
        "Bad rows may be skipped, but never silently: clean_batch must return "
        "each reject with a reason. `except: continue` destroyed information; "
        "we keep it."
    )
    raw, reason = result.rejects[0]
    assert isinstance(reason, str) and reason, "Each reject needs a human-readable reason."


def test_load_config_defaults_and_overrides():
    from m02_refactor import load_config

    cfg = load_config({})
    assert cfg.vat_rate == pytest.approx(1.17)
    assert cfg.raw_dir == "data/raw"
    assert cfg.warehouse_path == "data/warehouse.duckdb"

    cfg = load_config({"CORECAFE_VAT_RATE": "1.18", "CORECAFE_RAW_DIR": "/srv/raw"})
    assert cfg.vat_rate == pytest.approx(1.18)
    assert cfg.raw_dir == "/srv/raw"


def test_load_config_uses_its_argument_not_the_real_environment(monkeypatch):
    from m02_refactor import load_config

    # If this fails, the function is reaching into os.environ behind the
    # caller's back — exactly the hidden dependency the exercise forbids.
    monkeypatch.setenv("CORECAFE_VAT_RATE", "9.99")
    assert load_config({}).vat_rate == pytest.approx(1.17)


def test_purity_no_files_or_database_needed(tmp_path, monkeypatch):
    """The whole point of the refactor: logic runs with zero infrastructure.

    We run the functions from an empty directory — any attempt to open the
    usual data files or warehouse will blow up with FileNotFoundError.
    """
    from m02_refactor import clean_batch, load_config

    monkeypatch.chdir(tmp_path)  # nothing here: no data/, no warehouse
    result = clean_batch([GOOD_ROW], vat_rate=load_config({}).vat_rate)
    assert result.rows[0].revenue == pytest.approx(8.19)


# --------------------------------------------------------------------------
# Exercise 2 — the lint exercise
# --------------------------------------------------------------------------


def test_tidy_passes_ruff():
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "--no-cache", str(TARGET_DIR / "m02_tidy.py")],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(TARGET_DIR),
    )
    assert result.returncode == 0, (
        "ruff still has complaints:\n"
        f"{result.stdout}\n"
        "Fix every finding. One of them (B006) is a genuine bug, not style."
    )


def test_tidy_behavior_correct_and_stable():
    from m02_tidy import weekly_summary

    rows = [
        {"sold_at": "2026-06-01 09:00:00", "revenue": 10.0},  # Monday
        {"sold_at": "2026-06-01 12:00:00", "revenue": 5.0},  # Monday
        {"sold_at": "2026-06-02 09:00:00", "revenue": 7.0},  # Tuesday
    ]
    expected = [("Monday", 15.0), ("Tuesday", 7.0)]

    first = weekly_summary(list(rows))
    second = weekly_summary(list(rows))
    assert first == expected
    assert second == expected, (
        "Second call with the same input returned different numbers — the "
        "mutable default argument is still hoarding state between calls. "
        "This is the doubled-dashboard bug from Module 00, in miniature."
    )
