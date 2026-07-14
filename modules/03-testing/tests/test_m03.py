"""Self-check for Module 03: the mutation hunt and the integration test."""

import random
from datetime import date

import pytest

# --------------------------------------------------------------------------
# Exercise 1 — the mutation hunt
# --------------------------------------------------------------------------

MUTANT_NAMES = [
    "vat_added_not_multiplied",
    "revenue_rounded_per_line",
    "null_store_becomes_zero",
    "swallows_bad_timestamps",
    "batch_stops_at_first_error",
    "rejects_vanish",
]


def test_suite_passes_on_correct_code():
    from corecafe import transform
    from m03_hunt import transform_test_suite

    transform_test_suite(transform)  # a suite that rejects correct code is noise


@pytest.mark.parametrize("name", MUTANT_NAMES)
def test_suite_kills_mutant(name):
    from m03_hunt import transform_test_suite
    from mutants import MUTANTS

    try:
        transform_test_suite(MUTANTS[name])
    except AssertionError:
        return  # caught — this mutant is dead
    pytest.fail(
        f"The mutant {name!r} SURVIVED your test suite: it contains a real bug "
        "that none of your assertions noticed. Its name tells you where to aim "
        "the next assertion."
    )


# --------------------------------------------------------------------------
# Exercise 2 — the integration test
# --------------------------------------------------------------------------


@pytest.fixture(scope="module")
def evidence(tmp_path_factory):
    from m03_integration import run_pipeline_in

    return run_pipeline_in(tmp_path_factory.mktemp("integration"))


def test_integration_accounts_for_every_row(evidence):
    summary = evidence["summary"]
    assert evidence["sales_count"] == summary.rows_loaded, (
        "Rows in the sales table must equal what the RunSummary claims was loaded."
    )
    assert summary.rows_rejected == 0, "The clean seed-42 dataset has no bad rows."
    assert evidence["sales_count"] > 0


def test_integration_builds_marts(evidence):
    assert evidence["mart_days"] == 2, (
        "daily_revenue should contain exactly the 2 generated days — check that "
        "your Config pointed at the generated raw dir and that marts were built."
    )


def test_integration_revenue_reconciles(evidence):
    """Recompute expected revenue INDEPENDENTLY of the pipeline and compare.

    This is the reconciliation check every BI person has done by hand —
    automated, and run on every change forever. Because the generator is
    seeded, the expectation is exact.
    """
    from datagen import generate_sales_day

    rng = random.Random(42)
    expected = 0.0
    for day in (date(2026, 6, 1), date(2026, 6, 2)):
        for row in generate_sales_day(day, rng):
            expected += row.quantity * row.unit_price * 1.17

    assert evidence["revenue_total"] == pytest.approx(round(expected, 2)), (
        "The daily_revenue mart total doesn't match an independent recomputation "
        "from the same source rows."
    )
