"""CoreCafé pipeline, v2 — after Module 04's renovation.

Changes since v1:
- sales loads are atomic partition overwrites (idempotent; re-runs,
  corrections, and backfills are all safe non-events)
- partition date derived from the source filename, validated

KNOWN GAP (on purpose): nothing checks the DATA. A file full of duplicate
sale_ids, unknown stores, or negative quantities loads without complaint —
the code is correct, and the dashboard is still wrong. Module 05 closes
this with a quality gate.
"""

__version__ = "2.0.0"
