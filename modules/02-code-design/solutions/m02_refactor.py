"""Module 02, Exercise 1 — reference solution.

Compare the shape, not just the code: every function here can be exercised
by a test in microseconds, with no files, no database, no environment. That
property was the entire point of the refactor — Module 3 cashes it in.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Sale:
    sale_id: str
    store_id: int | None
    product_id: int
    quantity: int
    unit_price: float
    revenue: float
    sold_at: datetime
    payment_method: str


@dataclass(frozen=True)
class Config:
    vat_rate: float
    raw_dir: str
    warehouse_path: str


@dataclass
class CleanResult:
    rows: list[Sale]
    rejects: list[tuple[dict, str]]


def compute_revenue(quantity: int, unit_price: float, vat_rate: float) -> float:
    # The magic 1.17 from the monolith now enters exactly once, by name,
    # from config. When VAT changes, one value changes.
    return quantity * unit_price * vat_rate


def parse_sale(raw: Mapping[str, str], vat_rate: float) -> Sale:
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

    store_raw = raw.get("store_id") or None  # empty string -> None, as the monolith did
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
    result = CleanResult(rows=[], rejects=[])
    for raw in raw_rows:
        try:
            result.rows.append(parse_sale(raw, vat_rate))
        except ValueError as exc:
            # Same skip-and-continue the monolith did — but now every skipped
            # row is on the record. Module 5 turns this record into a gate;
            # Module 7 turns it into a metric.
            result.rejects.append((dict(raw), str(exc)))
    return result


def load_config(env: Mapping[str, str]) -> Config:
    return Config(
        vat_rate=float(env.get("CORECAFE_VAT_RATE", "1.17")),
        raw_dir=env.get("CORECAFE_RAW_DIR", "data/raw"),
        warehouse_path=env.get("CORECAFE_WAREHOUSE", "data/warehouse.duckdb"),
    )
