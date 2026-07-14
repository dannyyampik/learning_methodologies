"""Six broken variants of the transform layer. DO NOT EDIT (or peek, yet).

Each mutant re-implements the corecafe.transform API with exactly one subtle
bug of a kind that ships to production in real teams. Your test suite in
m03_hunt.py must catch ALL of them while passing on the correct code.

The names are only revealed in the test output when a mutant survives.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import datetime
from types import SimpleNamespace

from corecafe.transform import CleanResult, Sale
from corecafe.transform import clean_batch as _good_clean_batch
from corecafe.transform import compute_revenue as _good_compute_revenue
from corecafe.transform import parse_sale as _good_parse_sale


def _variant(compute_revenue=None, parse_sale=None, clean_batch=None) -> SimpleNamespace:
    ns = SimpleNamespace(
        Sale=Sale,
        CleanResult=CleanResult,
        compute_revenue=compute_revenue or _good_compute_revenue,
        parse_sale=parse_sale or _good_parse_sale,
        clean_batch=clean_batch or _good_clean_batch,
    )
    # A mutant's clean_batch must use ITS OWN parse_sale, so parse bugs
    # surface through batch behavior too.
    if parse_sale and not clean_batch:

        def batch(raw_rows: Iterable[Mapping[str, str]], vat_rate: float) -> CleanResult:
            result = CleanResult(rows=[], rejects=[])
            for raw in raw_rows:
                try:
                    result.rows.append(ns.parse_sale(raw, vat_rate))
                except ValueError as exc:
                    result.rejects.append((dict(raw), str(exc)))
            return result

        ns.clean_batch = batch
    return ns


# -- mutant: vat_added ------------------------------------------------------
def _revenue_vat_added(quantity, unit_price, vat_rate):
    return quantity * unit_price + vat_rate  # + instead of *


# -- mutant: revenue_rounded ------------------------------------------------
def _revenue_rounded(quantity, unit_price, vat_rate):
    return round(quantity * unit_price * vat_rate)  # loses cents, compounds at SUM


# -- mutant: null_store_becomes_zero ---------------------------------------
def _parse_null_store_zero(raw, vat_rate):
    sale = _good_parse_sale(raw, vat_rate)
    if sale.store_id is None:
        return Sale(**{**sale.__dict__, "store_id": 0})  # invents a store!
    return sale


# -- mutant: swallows_bad_timestamps ----------------------------------------
def _parse_quiet_timestamp(raw, vat_rate):
    try:
        return _good_parse_sale(raw, vat_rate)
    except ValueError:
        fixed = {**raw, "sold_at": "1970-01-01 00:00:00"}
        return _good_parse_sale(fixed, vat_rate)  # garbage in, epoch out


# -- mutant: batch_stops_at_first_error -------------------------------------
def _batch_gives_up(raw_rows, vat_rate):
    result = CleanResult(rows=[], rejects=[])
    for raw in raw_rows:
        try:
            result.rows.append(_good_parse_sale(raw, vat_rate))
        except ValueError:
            break  # one bad row silently costs the rest of the file
    return result


# -- mutant: rejects_vanish --------------------------------------------------
def _batch_loses_rejects(raw_rows, vat_rate):
    result = _good_clean_batch(raw_rows, vat_rate)
    return CleanResult(rows=result.rows, rejects=[])  # Dave's `except: continue` reborn


MUTANTS: dict[str, SimpleNamespace] = {
    "vat_added_not_multiplied": _variant(compute_revenue=_revenue_vat_added),
    "revenue_rounded_per_line": _variant(compute_revenue=_revenue_rounded),
    "null_store_becomes_zero": _variant(parse_sale=_parse_null_store_zero),
    "swallows_bad_timestamps": _variant(parse_sale=_parse_quiet_timestamp),
    "batch_stops_at_first_error": _variant(clean_batch=_batch_gives_up),
    "rejects_vanish": _variant(clean_batch=_batch_loses_rejects),
}
