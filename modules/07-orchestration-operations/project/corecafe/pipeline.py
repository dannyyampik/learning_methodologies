"""The imperative shell, final form: load → gate → audited publish.

Also demonstrates operable logging (Module 07): every stage emits one
structured, timestamped line to stderr. When this runs unattended at 3 a.m.,
these lines ARE the interface between the pipeline and whoever is debugging.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from corecafe import extract, load
from corecafe.config import Config
from corecafe.quality import QualityGateError, Verdict, sales_suite
from corecafe.transform import clean_batch
from corecafe.wap import WapResult, write_audit_publish

logger = logging.getLogger("corecafe")

DAILY_REVENUE_SQL = """
    SELECT CAST(s.sold_at AS DATE) AS day, s.store_id, st.store_name, st.city,
           SUM(s.revenue) AS revenue, COUNT(*) AS transactions
    FROM sales s LEFT JOIN stores st ON s.store_id = st.store_id
    GROUP BY 1, 2, 3, 4
"""

TOP_PRODUCTS_SQL = """
    SELECT p.product_name, p.category, SUM(s.quantity) AS units,
           SUM(s.revenue) AS revenue
    FROM sales s JOIN products p ON s.product_id = p.product_id
    GROUP BY 1, 2 ORDER BY revenue DESC
"""


@dataclass
class RunSummary:
    files_processed: int = 0
    rows_loaded: int = 0
    rows_rejected: int = 0
    reject_reasons: list[str] = field(default_factory=list)
    quality: Verdict | None = None
    publications: list[WapResult] = field(default_factory=list)


class PublicationError(RuntimeError):
    """A mart candidate failed its WAP audits; consumers kept the old table."""


def partition_date_of(csv_path: Path) -> date:
    """Daily files are named sales_YYYY-MM-DD.csv; refuse anything else."""
    stem = csv_path.stem
    if not stem.startswith("sales_"):
        raise ValueError(f"cannot determine partition date from filename: {csv_path.name}")
    try:
        return date.fromisoformat(stem.removeprefix("sales_"))
    except ValueError:
        raise ValueError(
            f"cannot determine partition date from filename: {csv_path.name}"
        ) from None


def _audit_not_empty(con, staging: str) -> tuple[str, bool]:
    n = con.execute(f"SELECT count(*) FROM {staging}").fetchone()[0]
    return ("not_empty", n > 0)


def _audit_reconciles_with_sales(con, staging: str) -> tuple[str, bool]:
    """The mart's total must equal the fact table's total, to the cent."""
    diff = con.execute(
        f"""
        SELECT abs(coalesce((SELECT sum(revenue) FROM {staging}), 0)
                 - coalesce((SELECT sum(revenue) FROM sales), 0))
        """
    ).fetchone()[0]
    return ("reconciles_with_sales", diff < 0.01)


def run(config: Config) -> RunSummary:
    raw_dir = Path(config.raw_dir)
    con = load.connect(config.warehouse_path)
    summary = RunSummary()

    load.load_dimension(con, "stores", str(raw_dir / "stores.csv"))
    load.load_dimension(con, "products", str(raw_dir / "products.csv"))
    logger.info("dimensions loaded", extra={})

    for path in extract.list_sales_files(raw_dir):
        day = partition_date_of(path)
        result = clean_batch(extract.read_csv_dicts(path), config.vat_rate)
        loaded = load.overwrite_sales_partition(con, day, result.rows)
        logger.info("partition loaded day=%s rows=%d rejects=%d", day, loaded, len(result.rejects))
        summary.rows_loaded += loaded
        summary.rows_rejected += len(result.rejects)
        summary.reject_reasons += [reason for _, reason in result.rejects]
        summary.files_processed += 1

    summary.quality = sales_suite(con)
    for warning in summary.quality.warnings:
        logger.warning("quality warn %s failing_rows=%d", warning.name, warning.failing_rows)
    if not summary.quality.passed:
        for error in summary.quality.errors:
            logger.error("quality FAIL %s failing_rows=%d", error.name, error.failing_rows)
        con.close()
        raise QualityGateError(summary.quality)

    for table, sql, audits in (
        ("daily_revenue", DAILY_REVENUE_SQL, [_audit_not_empty, _audit_reconciles_with_sales]),
        ("top_products", TOP_PRODUCTS_SQL, [_audit_not_empty]),
    ):
        wap = write_audit_publish(con, table, sql, audits)
        summary.publications.append(wap)
        if not wap.published:
            logger.error(
                "publication BLOCKED table=%s failed_audits=%s (candidate kept at %s)",
                table,
                wap.failed_audits,
                wap.staging_table,
            )
            con.close()
            raise PublicationError(f"{table}: failed audits {wap.failed_audits}")
        logger.info("published table=%s", table)

    con.close()
    return summary
