"""CoreCafé pipeline, v4 — after Module 06's renovation. The final form.

Changes since v3:
- wap.py: Write-Audit-Publish for derived tables
- marts are no longer built in place: each is written to staging, audited
  (non-empty; daily_revenue must reconcile with the sales table it came
  from), and atomically swapped in only on green
- structured, timestamped log lines instead of bare prints

The renovation arc, for the record:
  v0  the monolith                        (Module 00 — the patient)
  v1  functional core, imperative shell   (Module 02 — testable)
  v2  idempotent partition overwrites     (Module 04 — rerunnable)
  v3  quality gate on ingested data       (Module 05 — gated)
  v4  WAP publication + operable logging  (Modules 06/07 — deployable, operable)

What a real production deployment would still add: an orchestrator
(Module 07 teaches you to read one), secrets management, alert routing,
and a metadata/lineage catalog. The *shape* would not change.
"""

__version__ = "4.0.0"
