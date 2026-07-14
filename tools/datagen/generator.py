"""Generation logic for the CoreCafé synthetic dataset.

The dataset models a small coffee-shop chain:

- ``stores.csv``     — one row per café (dimension, small, static)
- ``products.csv``   — one row per menu item (dimension, small, static)
- ``sales/sales_<date>.csv`` — one file per day of point-of-sale transactions
  (fact, append-only, arrives in daily batches — like an SFTP drop or an
  export from a POS vendor)

Design notes (these choices are discussed in Module 2):

- Pure functions build rows in memory; a single writer function does all
  file I/O. Logic is testable without touching the filesystem.
- All randomness flows through one seeded ``random.Random`` instance —
  determinism is a property we *engineer*, not hope for (Module 4).
- Defects are injected explicitly and log what they did, because surprise
  randomness in a teaching tool is cruelty, not realism.
"""

from __future__ import annotations

import csv
import random
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path

# --------------------------------------------------------------------------
# Reference (dimension) data
# --------------------------------------------------------------------------

_STORES = [
    (1, "CoreCafé Central", "Tel Aviv", "2019-03-01"),
    (2, "CoreCafé Marina", "Herzliya", "2020-07-15"),
    (3, "CoreCafé Old Town", "Jaffa", "2021-01-10"),
    (4, "CoreCafé Campus", "Haifa", "2022-09-01"),
    (5, "CoreCafé Junction", "Beer Sheva", "2023-05-20"),
]

_PRODUCTS = [
    (101, "Espresso", "coffee", 2.50),
    (102, "Americano", "coffee", 3.00),
    (103, "Cappuccino", "coffee", 3.50),
    (104, "Flat White", "coffee", 3.75),
    (105, "Cold Brew", "coffee", 4.00),
    (201, "Croissant", "pastry", 3.25),
    (202, "Almond Croissant", "pastry", 4.00),
    (203, "Cinnamon Roll", "pastry", 3.75),
    (301, "Granola Bowl", "food", 6.50),
    (302, "Avocado Toast", "food", 7.00),
    (303, "Shakshuka Plate", "food", 8.50),
    (401, "Fresh Orange Juice", "drinks", 4.50),
]

_PAYMENT_METHODS = ["card", "cash", "app"]

#: Defect kinds the generator knows how to inject (see Modules 3 and 5).
DEFECT_KINDS = frozenset(
    {"duplicates", "nulls", "negative_quantity", "unknown_store", "bad_timestamp"}
)


@dataclass
class SaleRow:
    """One point-of-sale transaction, exactly as the source system exports it.

    Fields are strings-and-numbers as they appear in the CSV; parsing and
    typing happen in the pipeline (that boundary is the subject of Module 5).
    """

    sale_id: str
    store_id: int | None
    product_id: int
    quantity: int
    unit_price: float
    sold_at: str  # ISO timestamp string, as source systems typically send it
    payment_method: str

    def as_list(self) -> list:
        return [
            self.sale_id,
            self.store_id,
            self.product_id,
            self.quantity,
            self.unit_price,
            self.sold_at,
            self.payment_method,
        ]


SALES_HEADER = [
    "sale_id",
    "store_id",
    "product_id",
    "quantity",
    "unit_price",
    "sold_at",
    "payment_method",
]


@dataclass
class GenerationReport:
    """What the generator did — returned so callers (and tests) can assert on it."""

    days: list[str] = field(default_factory=list)
    rows_per_day: dict[str, int] = field(default_factory=dict)
    defects_injected: dict[str, list[str]] = field(default_factory=dict)


# --------------------------------------------------------------------------
# Pure generation functions
# --------------------------------------------------------------------------


def generate_dimensions() -> tuple[list[tuple], list[tuple]]:
    """Return (stores, products) reference rows. Static and deterministic."""
    return list(_STORES), list(_PRODUCTS)


def generate_sales_day(
    day: date,
    rng: random.Random,
    defects: set[str] | None = None,
) -> list[SaleRow]:
    """Generate one day of sales, optionally injecting the given defects.

    The row count varies by weekday (weekends are busier) and store, which
    gives later modules realistic volume patterns to monitor (Module 7).
    """
    defects = defects or set()
    unknown = defects - DEFECT_KINDS
    if unknown:
        raise ValueError(f"Unknown defect kind(s): {sorted(unknown)}")

    rows: list[SaleRow] = []
    weekend_boost = 1.4 if day.weekday() >= 4 else 1.0
    for store_id, *_ in _STORES:
        n = int(rng.randint(35, 60) * weekend_boost)
        for _ in range(n):
            product_id, _name, _cat, price = rng.choice(_PRODUCTS)
            ts = datetime(day.year, day.month, day.day, rng.randint(7, 21), rng.randint(0, 59))
            rows.append(
                SaleRow(
                    sale_id=f"{day:%Y%m%d}-{store_id}-{rng.randrange(10**8):08d}",
                    store_id=store_id,
                    product_id=product_id,
                    quantity=rng.choices([1, 2, 3], weights=[70, 22, 8])[0],
                    unit_price=price,
                    sold_at=ts.isoformat(sep=" "),
                    payment_method=rng.choice(_PAYMENT_METHODS),
                )
            )

    rows.sort(key=lambda r: r.sold_at)
    _inject_defects(rows, defects, rng)
    return rows


def _inject_defects(rows: list[SaleRow], defects: set[str], rng: random.Random) -> None:
    """Mutate ``rows`` in place to simulate common source-system pathologies."""
    if "duplicates" in defects:
        # POS retried a network call and the export contains the sale twice.
        for row in rng.sample(rows, k=max(3, len(rows) // 50)):
            rows.append(
                SaleRow(**{**row.__dict__})  # exact duplicate, same sale_id
            )
    if "nulls" in defects:
        # A firmware bug drops the store id on a handful of transactions.
        for row in rng.sample(rows, k=max(2, len(rows) // 80)):
            row.store_id = None
    if "negative_quantity" in defects:
        # Refunds encoded as negative quantities — undocumented, of course.
        for row in rng.sample(rows, k=2):
            row.quantity = -row.quantity
    if "unknown_store" in defects:
        # A new store starts sending data before anyone updated stores.csv.
        for row in rng.sample(rows, k=3):
            row.store_id = 99
    if "bad_timestamp" in defects:
        # One register has a dead clock battery.
        for row in rng.sample(rows, k=2):
            row.sold_at = "0000-00-00 00:00"


# --------------------------------------------------------------------------
# I/O boundary — the only place this package touches the filesystem
# --------------------------------------------------------------------------


def write_dataset(
    output_dir: Path,
    days: int = 30,
    seed: int = 42,
    start: date = date(2026, 6, 1),
    defect_days: dict[str, set[str]] | None = None,
) -> GenerationReport:
    """Write the full dataset under ``output_dir``.

    ``defect_days`` maps ISO date strings to the defect kinds to inject on
    that day, e.g. ``{"2026-06-12": {"duplicates", "nulls"}}``.
    """
    rng = random.Random(seed)
    defect_days = defect_days or {}
    report = GenerationReport()

    output_dir.mkdir(parents=True, exist_ok=True)
    sales_dir = output_dir / "sales"
    sales_dir.mkdir(exist_ok=True)

    stores, products = generate_dimensions()
    _write_csv(
        output_dir / "stores.csv",
        ["store_id", "store_name", "city", "opened_date"],
        stores,
    )
    _write_csv(
        output_dir / "products.csv",
        ["product_id", "product_name", "category", "unit_price"],
        products,
    )

    for offset in range(days):
        day = start + timedelta(days=offset)
        iso = day.isoformat()
        defects = set(defect_days.get(iso, set()))
        rows = generate_sales_day(day, rng, defects)
        _write_csv(
            sales_dir / f"sales_{iso}.csv",
            SALES_HEADER,
            [r.as_list() for r in rows],
        )
        report.days.append(iso)
        report.rows_per_day[iso] = len(rows)
        if defects:
            report.defects_injected[iso] = sorted(defects)

    return report


def _write_csv(path: Path, header: list[str], rows: list) -> None:
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
