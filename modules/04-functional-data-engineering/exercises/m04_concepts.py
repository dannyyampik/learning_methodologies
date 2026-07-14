"""Module 04, Exercise 2 — Functional data engineering concepts.

Replace each ``...`` with your answer, then run:  make check MODULE=04
"""

# Q1. A transform tags each row with `processed_at = datetime.now()`.
# Yesterday's partition is re-run today after a bug fix. Is the pipeline
# still DETERMINISTIC (same inputs -> same outputs)?  (True / False)
Q1_STILL_DETERMINISTIC = ...

# Q2. Two independent properties keep coming up. Match each statement to
# the property it describes — answer "idempotency" or "determinism":
#   (a) "Running it twice leaves the same state as running it once."
#   (b) "Running it with the same inputs always produces the same values."
Q2A_PROPERTY = ...
Q2B_PROPERTY = ...

# Q3. Storage is tight, and all raw CSVs are already loaded into the
# warehouse. Is deleting the raw files therefore harmless?
# Answer with exactly one of:
#   "yes"                 - the data lives in the warehouse now
#   "no_reprocessing"     - you lose the ability to rebuild/reprocess history
#   "no_performance"      - queries will get slower
Q3_DELETE_RAW_FILES = ...

# Q4. On June 20th the vendor re-delivers June 3rd's file with corrections.
# With loads implemented as idempotent partition overwrites, what is the
# correct operational response?
#   "reload_partition"  - just re-run June 3rd's load
#   "full_rebuild"      - truncate and reload everything
#   "manual_patch"      - UPDATE the differing rows by hand
Q4_LATE_CORRECTION = ...

# Q5. Your `sales` loader is a partition overwrite (DELETE day + INSERT).
# A colleague suggests switching to MERGE/upsert keyed on sale_id "to be
# more efficient". What does the pipeline LOSE if a corrected file no
# longer contains a sale_id that the original (bad) file did?
#   "nothing"        - MERGE handles corrections fine
#   "the_deletion"   - rows removed by the correction survive as zombies
#   "the_ordering"   - rows end up in the wrong order
Q5_MERGE_TRADEOFF = ...
