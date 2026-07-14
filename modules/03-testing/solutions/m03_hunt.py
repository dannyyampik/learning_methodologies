"""Module 03, Exercise 1 — reference solution.

Notice the shape: each block states ONE belief about the transform layer,
with the smallest input that can violate it. That's what "good coverage"
actually means — beliefs covered, not lines covered.
"""

from __future__ import annotations

GOOD_ROW = {
    "sale_id": "20260601-1-00000001",
    "store_id": "1",
    "product_id": "103",
    "quantity": "2",
    "unit_price": "3.5",
    "sold_at": "2026-06-01 09:30:00",
    "payment_method": "card",
}


def transform_test_suite(transform) -> None:
    # Belief 1: revenue is quantity * price * VAT — multiplied, not added.
    # (kills: vat_added_not_multiplied)
    assert abs(transform.compute_revenue(2, 3.5, 1.17) - 8.19) < 1e-9

    # Belief 2: revenue keeps its cents — no per-line rounding. A case whose
    # true value has >2 decimals separates round() from exact arithmetic.
    # (kills: revenue_rounded_per_line)
    assert abs(transform.compute_revenue(1, 2.5, 1.17) - 2.925) < 1e-9

    # Belief 3: a good row parses to faithful values.
    sale = transform.parse_sale(GOOD_ROW, 1.17)
    assert sale.store_id == 1
    assert sale.quantity == 2
    assert abs(sale.revenue - 8.19) < 1e-9

    # Belief 4: missing store_id stays None. Unknown is not zero — inventing
    # a store would silently misattribute revenue on the dashboard.
    # (kills: null_store_becomes_zero)
    assert transform.parse_sale({**GOOD_ROW, "store_id": ""}, 1.17).store_id is None

    # Belief 5: garbage timestamps fail LOUDLY. A quiet epoch default would
    # scatter 1970 rows through every date-partitioned table downstream.
    # (kills: swallows_bad_timestamps)
    try:
        transform.parse_sale({**GOOD_ROW, "sold_at": "0000-00-00 00:00"}, 1.17)
    except ValueError:
        pass
    else:
        raise AssertionError("parse_sale accepted an impossible timestamp")

    # Belief 6: one bad row must not cost the rest of the batch, and
    # Belief 7: every skipped row appears in rejects, with a reason.
    # (kills: batch_stops_at_first_error, rejects_vanish)
    batch = [
        GOOD_ROW,
        {**GOOD_ROW, "sale_id": "bad", "quantity": "NaN"},
        {**GOOD_ROW, "sale_id": "after-the-bad-one"},
    ]
    result = transform.clean_batch(batch, 1.17)
    assert len(result.rows) == 2, "good rows after a bad row were lost"
    assert len(result.rejects) == 1, "the bad row left no trace in rejects"
    raw, reason = result.rejects[0]
    assert isinstance(reason, str) and reason
