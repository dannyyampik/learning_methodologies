"""Module 02, Exercise 1 — Extract the functional core from the monolith.

Implement the four functions below by EXTRACTING logic from
``project/pipeline.py`` — same behavior, new shape. The rules:

1. These functions must be PURE: no file access, no database, no reading
   os.environ, no printing. Inputs in, outputs out. (The tests call them
   with nothing but Python values, so any hidden I/O will fail loudly.)
2. Behavior must match the monolith's — this is a refactor, not a fix.
   The one deliberate improvement: bad rows must become *accountable*
   (collected with reasons) instead of silently swallowed.

Run:  make check MODULE=02
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Sale:
    """A parsed, typed sale — the shape the rest of the pipeline trusts."""

    sale_id: str
    store_id: int | None  # the source sometimes omits it; Module 5 will care
    product_id: int
    quantity: int
    unit_price: float
    revenue: float
    sold_at: datetime
    payment_method: str


@dataclass(frozen=True)
class Config:
    """Everything the pipeline needs to know that is not logic."""

    vat_rate: float
    raw_dir: str
    warehouse_path: str


@dataclass
class CleanResult:
    rows: list[Sale]
    rejects: list[tuple[dict, str]]  # (raw row, human-readable reason)


def compute_revenue(quantity: int, unit_price: float, vat_rate: float) -> float:
    """Revenue including VAT — the formula that appears TWICE in the monolith."""
    raise NotImplementedError


def parse_sale(raw: Mapping[str, str], vat_rate: float) -> Sale:
    """Parse one raw CSV row (a dict of strings) into a typed Sale.

    Must raise ValueError with an informative message when quantity,
    unit_price, or sold_at cannot be parsed. An empty store_id is allowed
    and becomes None (that's the monolith's behavior — whether it SHOULD be
    allowed is Module 5's question, not a parsing question).
    """
    raise NotImplementedError


def clean_batch(raw_rows: Iterable[Mapping[str, str]], vat_rate: float) -> CleanResult:
    """Parse a whole batch, collecting failures instead of hiding them.

    The monolith's `except: continue` threw away bad rows AND the fact that
    they existed. Keep the skipping (a batch shouldn't die for one bad row)
    but make it accountable: every reject is recorded with its reason.
    """
    raise NotImplementedError


def load_config(env: Mapping[str, str]) -> Config:
    """Build the pipeline Config from an environment mapping.

    Defaults: vat_rate 1.17, raw_dir "data/raw", warehouse_path
    "data/warehouse.duckdb". Overridable via CORECAFE_VAT_RATE,
    CORECAFE_RAW_DIR, CORECAFE_WAREHOUSE.

    Note the signature: `env` is an ARGUMENT, not a sneaky read of
    os.environ inside. Passing dependencies in instead of reaching out for
    them is called dependency injection, and it is why this function can be
    tested with a plain dict.
    """
    raise NotImplementedError
