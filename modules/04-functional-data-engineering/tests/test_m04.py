"""Self-check for Module 04: idempotent partition loads, atomicity, backfill."""

from datetime import date
from pathlib import Path

import duckdb
import pytest

HEADER = "sale_id,store_id,product_id,quantity,unit_price,sold_at,payment_method\n"


def _write_sales_file(path: Path, day: str, rows: list[str]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(HEADER + "".join(r + "\n" for r in rows))
    return path


def _mem_con():
    return duckdb.connect(":memory:")


def _day_count(con, day: str) -> int:
    return con.execute(
        "SELECT count(*) FROM sales WHERE CAST(sold_at AS DATE) = ?", [date.fromisoformat(day)]
    ).fetchone()[0]


ROWS_V1 = [
    "a-1,1,101,2,2.50,2026-06-03 09:00:00,card",
    "a-2,2,103,1,3.50,2026-06-03 10:00:00,cash",
    "a-3,1,201,3,3.25,2026-06-03 11:00:00,app",
]

# The vendor's corrected file: a-2 fixed, a-3 REMOVED, a-4 added.
ROWS_V2 = [
    "a-1,1,101,2,2.50,2026-06-03 09:00:00,card",
    "a-2,2,103,2,3.50,2026-06-03 10:00:00,cash",
    "a-4,3,105,1,4.00,2026-06-03 12:00:00,card",
]


def test_partition_date_from_filename():
    from m04_idempotent import partition_date_of

    assert partition_date_of(Path("sales_2026-06-03.csv")) == date(2026, 6, 3)
    with pytest.raises(ValueError):
        partition_date_of(Path("sales_final_v2_REAL.csv"))


def test_loading_twice_is_loading_once(tmp_path):
    from m04_idempotent import load_sales_csv

    con = _mem_con()
    f = _write_sales_file(tmp_path / "sales" / "sales_2026-06-03.csv", "2026-06-03", ROWS_V1)

    load_sales_csv(con, f, vat_rate=1.17)
    first = con.execute("SELECT count(*), round(sum(revenue), 2) FROM sales").fetchone()
    load_sales_csv(con, f, vat_rate=1.17)
    second = con.execute("SELECT count(*), round(sum(revenue), 2) FROM sales").fetchone()

    assert first == second, (
        f"Two loads of the same file changed the table from {first} to {second}. "
        "This is the Module 00 bug — the partition must be REPLACED, not appended."
    )


def test_corrected_file_replaces_partition_exactly(tmp_path):
    from m04_idempotent import load_sales_csv

    con = _mem_con()
    f = _write_sales_file(tmp_path / "sales" / "sales_2026-06-03.csv", "2026-06-03", ROWS_V1)
    load_sales_csv(con, f, vat_rate=1.17)

    _write_sales_file(f, "2026-06-03", ROWS_V2)
    report = load_sales_csv(con, f, vat_rate=1.17)

    ids = {r[0] for r in con.execute("SELECT sale_id FROM sales").fetchall()}
    assert ids == {"a-1", "a-2", "a-4"}, (
        f"After the corrected delivery the partition holds {sorted(ids)} — "
        "removed rows must disappear (no zombies) and new rows must arrive."
    )
    qty = con.execute("SELECT quantity FROM sales WHERE sale_id = 'a-2'").fetchone()[0]
    assert qty == 2, "The corrected quantity for a-2 didn't take."
    assert report.replaced_existing is True


def test_other_partitions_are_untouched(tmp_path):
    from m04_idempotent import load_sales_csv

    con = _mem_con()
    day3 = _write_sales_file(tmp_path / "sales" / "sales_2026-06-03.csv", "2026-06-03", ROWS_V1)
    day4 = _write_sales_file(
        tmp_path / "sales" / "sales_2026-06-04.csv",
        "2026-06-04",
        ["b-1,1,101,1,2.50,2026-06-04 09:00:00,card"],
    )
    load_sales_csv(con, day3, vat_rate=1.17)
    load_sales_csv(con, day4, vat_rate=1.17)

    load_sales_csv(con, day3, vat_rate=1.17)  # re-run day 3 only
    assert _day_count(con, "2026-06-04") == 1, (
        "Re-loading June 3rd disturbed June 4th — the DELETE must be scoped to "
        "the partition, not the table."
    )


def test_failed_load_leaves_partition_intact(tmp_path):
    from m04_idempotent import load_sales_csv

    con = _mem_con()
    f = _write_sales_file(tmp_path / "sales" / "sales_2026-06-03.csv", "2026-06-03", ROWS_V1)
    load_sales_csv(con, f, vat_rate=1.17)

    # A corrupted re-delivery: good row, then garbage.
    _write_sales_file(
        f,
        "2026-06-03",
        ["a-1,1,101,2,2.50,2026-06-03 09:00:00,card", "a-2,2,103,NaN,3.50,junk,cash"],
    )
    with pytest.raises(ValueError):
        load_sales_csv(con, f, vat_rate=1.17)

    assert _day_count(con, "2026-06-03") == 3, (
        "The failed load damaged the partition. All-or-nothing means the OLD "
        "data survives a failed replacement — parse fully first, write in a "
        "transaction, roll back on error."
    )


def test_overwrite_partition_rolls_back_on_bad_rows():
    from m04_idempotent import overwrite_partition

    con = _mem_con()
    good = [
        ("a-1", 1, 101, 2, 2.5, 5.85, "2026-06-03 09:00:00", "card"),
    ]
    overwrite_partition(con, date(2026, 6, 3), good)

    bad_batch = [
        ("a-2", 1, 101, 1, 2.5, 2.925, "2026-06-03 10:00:00", "card"),
        ("broken", "not-a-store"),  # wrong arity/type — executemany will raise
    ]
    with pytest.raises(duckdb.Error):
        overwrite_partition(con, date(2026, 6, 3), bad_batch)

    remaining = con.execute("SELECT sale_id FROM sales").fetchall()
    assert remaining == [("a-1",)], (
        "After the failed overwrite the partition should hold exactly the "
        "original row — neither emptied by the DELETE nor half-filled by the "
        "partial INSERT."
    )


def test_backfill_range(tmp_path):
    from datagen import write_dataset
    from m04_idempotent import backfill

    write_dataset(tmp_path, days=5, seed=42)  # 2026-06-01 .. 2026-06-05
    con = _mem_con()

    results = backfill(con, tmp_path, date(2026, 6, 2), date(2026, 6, 4), vat_rate=1.17)
    assert sorted(results) == [date(2026, 6, 2), date(2026, 6, 3), date(2026, 6, 4)]
    assert all(r is not None and r.rows > 0 for r in results.values())
    assert _day_count(con, "2026-06-01") == 0, "Backfill loaded a day outside the range."

    before = con.execute("SELECT count(*) FROM sales").fetchone()[0]
    backfill(con, tmp_path, date(2026, 6, 2), date(2026, 6, 4), vat_rate=1.17)
    after = con.execute("SELECT count(*) FROM sales").fetchone()[0]
    assert before == after, "A re-run backfill must be a non-event."


def test_backfill_reports_missing_days(tmp_path):
    from datagen import write_dataset
    from m04_idempotent import backfill

    write_dataset(tmp_path, days=2, seed=42)  # only 06-01 and 06-02 exist
    con = _mem_con()
    results = backfill(con, tmp_path, date(2026, 6, 1), date(2026, 6, 3), vat_rate=1.17)
    assert results[date(2026, 6, 3)] is None, (
        "A missing source file is a fact to report (None), not a crash — "
        "the vendor may simply not have delivered yet."
    )


# --------------------------------------------------------------------------
# Concepts quiz
# --------------------------------------------------------------------------


def _answered(value, name):
    if value is Ellipsis:
        pytest.fail(f"You haven't answered {name} yet — replace the ... in the exercise file.")
    return value


def test_concepts():
    import m04_concepts as ans

    assert _answered(ans.Q1_STILL_DETERMINISTIC, "Q1") is False, (
        "datetime.now() is a hidden input that changes every run."
    )
    assert _answered(ans.Q2A_PROPERTY, "Q2A") == "idempotency"
    assert _answered(ans.Q2B_PROPERTY, "Q2B") == "determinism"
    assert _answered(ans.Q3_DELETE_RAW_FILES, "Q3") == "no_reprocessing", (
        "Think about what you can no longer do when history exists only as "
        "the OUTPUT of today's logic."
    )
    assert _answered(ans.Q4_LATE_CORRECTION, "Q4") == "reload_partition"
    assert _answered(ans.Q5_MERGE_TRADEOFF, "Q5") == "the_deletion", (
        "What happens to a warehouse row that the corrected file no longer contains?"
    )
