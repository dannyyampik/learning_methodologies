# Module 02 — Suggested reflection answers

**1. "Five files instead of one — how is that simpler?"**
It isn't simpler to *read top to bottom* — that's the honest loss, along
with a little indirection (you now chase a function to its definition). The
claim is different: it's simpler to *change safely*. Complexity hasn't
increased; it has been **sorted** — parsing worries live in one file,
database worries in another, and a change to one provably can't touch the
other. The monolith was simpler the way an unsorted drawer is simpler.
Also honest: for a 40-line one-off script, the monolith IS the right
design. Structure is bought with effort and must be justified by change
frequency and blast radius — this pipeline feeds finance; it qualifies.

**2. Store opening dates / VAT history.**
Opening dates are *data about the business domain*: they belong in a
database table (they already are — `stores.csv` → `stores`), maintained
like data, joined like data. The VAT rate is *policy the pipeline applies*:
config. The test: who changes it, how often, and what should the change
process be? Data changes via data pipelines with quality checks; config
changes via a reviewed PR and a deploy; code changes via PR plus tests.
When VAT gets a *history* (17% until Dec, 18% after) it crosses the line
and becomes data — a rate table joined by date — because now correctness of
*historical* computation depends on it. That migration path (constant →
config → dimension table) is extremely common and worth recognizing early.

**3. Linting SQL trapped in a BI tool.**
The disciplines transfer even when the tool resists: (a) extract the SQL to
files in Git (Module 1's answer) so anything CAN run against it;
(b) `sqlfluff` is the SQL world's ruff — lint + format, dialect-aware;
(c) dbt takes it further by compiling SQL from versioned, testable models —
Module 5 shows how its test framework maps onto what you build there.
The underlying principle: if logic matters, it must live somewhere a
machine can check it.
