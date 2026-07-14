"""Command-line interface for the CoreCafé data generator.

Usage examples::

    python -m datagen --output data/raw --days 30
    python -m datagen --output data/raw --days 30 --defect 2026-06-12:duplicates,nulls
"""

from __future__ import annotations

import argparse
from pathlib import Path

from datagen.generator import DEFECT_KINDS, write_dataset


def _parse_defect(spec: str) -> tuple[str, set[str]]:
    """Parse ``YYYY-MM-DD:kind1,kind2`` into ``(date, {kinds})``."""
    try:
        day, kinds_csv = spec.split(":", maxsplit=1)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Expected DATE:kind1,kind2 — got {spec!r}") from None
    kinds = {k.strip() for k in kinds_csv.split(",") if k.strip()}
    unknown = kinds - DEFECT_KINDS
    if unknown:
        raise argparse.ArgumentTypeError(
            f"Unknown defect kind(s) {sorted(unknown)}. Available: {sorted(DEFECT_KINDS)}"
        )
    return day, kinds


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="datagen", description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="Output directory")
    parser.add_argument("--days", type=int, default=30, help="Number of daily sales files")
    parser.add_argument("--seed", type=int, default=42, help="RNG seed (keep the default!)")
    parser.add_argument(
        "--defect",
        action="append",
        type=_parse_defect,
        default=[],
        metavar="DATE:KINDS",
        help="Inject defects on a date, e.g. 2026-06-12:duplicates,nulls (repeatable)",
    )
    args = parser.parse_args(argv)

    report = write_dataset(
        output_dir=args.output,
        days=args.days,
        seed=args.seed,
        defect_days={day: kinds for day, kinds in args.defect},
    )

    total = sum(report.rows_per_day.values())
    print(f"Wrote {len(report.days)} sales files ({total} rows) to {args.output}")
    for day, kinds in report.defects_injected.items():
        print(f"  defects on {day}: {', '.join(kinds)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
