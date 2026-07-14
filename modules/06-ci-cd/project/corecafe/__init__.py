"""CoreCafé pipeline, v3 — after Module 05's renovation.

Changes since v2:
- quality.py: the expectations engine (checks + severity verdict)
- the pipeline runs the sales quality suite AFTER loading and BEFORE
  building marts; error-severity failures raise QualityGateError and the
  marts are left untouched (consumers keep seeing the last good version)
- __main__ exits non-zero on a failed gate, so schedulers notice

KNOWN GAP (on purpose): the gate protects the marts from bad *sales* data,
but mart building itself is not audited — a bug in the mart SQL still
publishes directly to consumers. Module 06 fixes this with
Write-Audit-Publish.
"""

__version__ = "3.0.0"
