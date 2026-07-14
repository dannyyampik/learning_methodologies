"""The functional core: parsing and business logic. No I/O in this file.

Every function here is pure — output depends only on inputs. That is a
maintained invariant, not an accident: it is what makes the fast unit tests
in Module 03 possible. If you are about to add an `open()`, a database
call, or an `os.environ` read to this file — stop; that belongs at an edge.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Sale:
    """A parsed, typed sale — the shape the rest of the pipeline trusts."""

    sale_id: str
    store_id: int | None  # source sometimes omits it; Module 5 decides policy
    product_id: int
    quantity: int
    unit_price: float
    revenue: float
    sold_at: datetime
    payment_method: str


@dataclass
class CleanResult:
    rows: list[Sale]
    rejects: list[tuple[dict, str]]  # (raw row, human-readable reason)


def compute_revenue(quantity: int, unit_price: float, vat_rate: float) -> float:
    """Revenue including VAT."""
    return quantity * unit_price * vat_rate


def parse_sale(raw: Mapping[str, str], vat_rate: float) -> Sale:
    """Parse one raw CSV row into a typed Sale.

    Raises ValueError (with the offending value in the message) when a field
    cannot be parsed. Empty store_id becomes None — inherited monolith
    behavior, revisited in Module 5.
    """
    try:
        quantity = int(raw["quantity"])
    except (KeyError, ValueError):
        raise ValueError(f"unparseable quantity: {raw.get('quantity')!r}") from None
    try:
        unit_price = float(raw["unit_price"])
    except (KeyError, ValueError):
        raise ValueError(f"unparseable unit_price: {raw.get('unit_price')!r}") from None
    try:
        sold_at = datetime.fromisoformat(raw["sold_at"])
    except (KeyError, ValueError):
        raise ValueError(f"unparseable sold_at: {raw.get('sold_at')!r}") from None

    store_raw = raw.get("store_id") or None
    return Sale(
        sale_id=raw["sale_id"],
        store_id=int(store_raw) if store_raw is not None else None,
        product_id=int(raw["product_id"]),
        quantity=quantity,
        unit_price=unit_price,
        revenue=compute_revenue(quantity, unit_price, vat_rate),
        sold_at=sold_at,
        payment_method=raw["payment_method"],
    )


def clean_batch(raw_rows: Iterable[Mapping[str, str]], vat_rate: float) -> CleanResult:
    """Parse a batch, skipping bad rows but keeping them on the record."""
    result = CleanResult(rows=[], rejects=[])
    for raw in raw_rows:
        try:
            result.rows.append(parse_sale(raw, vat_rate))
        except ValueError as exc:
            result.rejects.append((dict(raw), str(exc)))
    return result
