"""Module 03, Exercise 1 — The mutation hunt.

Write ONE function, `transform_test_suite(transform)`, that receives a
module-like object exposing the corecafe.transform API:

    transform.compute_revenue(quantity, unit_price, vat_rate)
    transform.parse_sale(raw_dict, vat_rate)         -> Sale
    transform.clean_batch(raw_rows, vat_rate)        -> CleanResult

Your function must run assertions against it such that:

- the REAL corecafe.transform passes (your suite raises nothing), and
- every one of the six sabotaged variants in mutants.py FAILS
  (your suite raises AssertionError).

This flips testing around: instead of "write tests" as a chore, you are
hunting live bugs. A test suite's value is measured by exactly this — the
bugs it would catch. (Tools like `mutmut` automate this game; here you play
it by hand once, so you never again believe a green checkmark blindly.)

Hints, if the hunt stalls (each mutant is one of these classic bug species):
  - a wrong operator in arithmetic         - overzealous rounding
  - inventing data instead of keeping NULL - swallowing errors silently
  - giving up on a batch too early         - losing the error record

Run:  make check MODULE=03
"""

from __future__ import annotations


def transform_test_suite(transform) -> None:
    """Assert everything you believe about a transform implementation.

    Raise AssertionError (via `assert`) when a belief is violated.
    Build it belief by belief: revenue arithmetic (including cents!),
    parsing of good rows, NULL handling, loud failure on garbage, batch
    completeness, and reject accounting.
    """
    raise NotImplementedError
