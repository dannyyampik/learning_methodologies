# Module 06 — Suggested reflection answers

**1. Green CI, passed audits, wrong number anyway.**
No automated layer failed — they all checked what they were told to check.
The failure was in *specification*: the author's intent was wrong, and the
one mechanism designed to confront intent with a second human brain is
**code review** (Module 1), specifically the data-review question "which
rows does this change affect, and does the business agree?". Artifacts
that raise the odds review catches it: a PR description stating expected
metric impact ("this should not change total revenue"), and a
reconciliation audit in WAP comparing the candidate's total against the
previous version with a tolerance — an automated "did the meaning move?"
tripwire. The general lesson: tests verify code against beliefs; only
humans verify beliefs against the business.

**2. Where to skip WAP.**
A reasonable skip: an internal engineering-health table — say, a
`pipeline_run_log` mart consumed by two engineers on an internal Grafana
board. Failure impact is low (its consumers are exactly the people who'd
be debugging it anyway), errors are self-evident (a broken run log looks
broken), and it changes shape often, so audit maintenance would cost more
than the incidents it prevents. Risk acceptance in one line: worst case, we
mislead ourselves briefly, and we are equipped to notice. What you must NOT
skip WAP for: anything read by people who can't tell wrong from right —
which is precisely finance dashboards.

**3. Analysts developing against prod (read-only).**
Still wrong, four ways: heavy exploratory queries compete with production
workloads (a SELECT can't corrupt data but can absolutely torch the
warehouse's compute or your bill); work-in-progress logic reads
work-in-progress-shaped conclusions off real PII; "read-only" erodes the
moment someone needs a scratch table and gets one in prod; and nothing
about their queries is reproducible (they reference live tables that
change under them). Cheapest fix, in order of increasing effort: (a) a
per-analyst schema with `CREATE TABLE AS` samples of the tables they use,
refreshed weekly; (b) dbt-style per-developer target schemas built from a
sampled subset by an automated job; (c) this course's own answer scaled
down — a seeded synthetic generator for the domain, which also unlocks
CI for their models. Even option (a) breaks the four failure modes above.
