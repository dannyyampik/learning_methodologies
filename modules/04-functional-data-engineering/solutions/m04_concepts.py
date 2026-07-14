"""Module 04, Exercise 2 — reference answers with explanations."""

# `datetime.now()` is a hidden INPUT that changes every run. Re-running
# yesterday's partition today produces different rows than it did yesterday
# — so no, not deterministic. If you need an audit stamp, make it explicit:
# pass a `run_id` / `execution_date` argument (exactly what orchestrators'
# "logical date" is for — Module 7). Hidden inputs (now(), random, os.environ,
# SELECTs against mutable tables) are where determinism quietly dies.
Q1_STILL_DETERMINISTIC = False

# The two properties are independent: a loader can be idempotent but not
# deterministic (overwrites the partition, stamps now() on rows), or
# deterministic but not idempotent (pure math, but INSERT-appends results).
# You need BOTH: determinism makes reruns produce the right values;
# idempotency makes reruns produce them exactly once.
Q2A_PROPERTY = "idempotency"
Q2B_PROPERTY = "determinism"

# The warehouse holds the OUTPUT of today's logic applied to the raw data.
# Delete the raw files and every past transformation decision is frozen
# forever: no bug fix can be replayed over history, no new column derived
# for old dates, no migration to a new warehouse. The immutable raw zone is
# the pipeline's undo button. (Compliance may force deletion — that's a
# governed exception with its own process, not housekeeping.)
Q3_DELETE_RAW_FILES = "no_reprocessing"

# This is the entire payoff of partition overwrites: a late correction is
# not an incident, it's a re-run. No hand-crafted UPDATEs (untested logic,
# no record), no full rebuild (hours of risk to fix one day).
Q4_LATE_CORRECTION = "reload_partition"

# MERGE updates matching rows and inserts new ones — but a row that EXISTS
# in the warehouse and is ABSENT from the corrected file matches nothing,
# so it survives: a zombie. Partition overwrite has no such gap because it
# derives its deletions from the partition boundary, not from row identity.
# MERGE earns its complexity for true incremental/CDC feeds; for "the file
# is the truth for that day", overwrite is both simpler AND more correct.
Q5_MERGE_TRADEOFF = "the_deletion"
