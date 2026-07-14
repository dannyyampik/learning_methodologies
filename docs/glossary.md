# Glossary

Every course term, defined for someone arriving from BI/analytics. Terms
appear roughly in the order the course introduces them.

**Idempotent** — an operation you can run twice (or ten times) and end in
the same state as running it once. *BI analogy: refreshing a report twice
doesn't double its numbers; a pipeline should earn the same trust.*
(Module 0, built in Module 4.)

**Deterministic** — same inputs always produce the same outputs. Broken by
hidden inputs: `now()`, unseeded randomness, environment reads, queries
against changing tables. (Modules 2, 4.)

**Monolith / script rot** — the one-file pipeline where reading, logic, and
writing interleave; changing anything requires re-simulating everything.
(Module 0.)

**Staging area (Git)** — Git's holding zone between your edited files and a
commit; `git add` snapshots a file into it. Commits record the staging
area, not your working directory. (Module 1.)

**DAG (directed acyclic graph)** — nodes with one-way dependencies and no
loops. Git history is one; your pipeline's task graph is one; Module 7 has
you execute one. *BI analogy: the dependency chain of views feeding views.*

**Trunk-based development** — everyone branches briefly off `main` and
merges back within a day or two via PR. The alternative (long-lived
branches) is a merge conflict on a countdown. (Module 1.)

**Pull request (PR) / code review** — proposing a change as a reviewable
diff before it lands. For data work, review's sharpest question is *"which
rows does this change affect?"* (Module 1.)

**Functional core, imperative shell** — architecture where pure logic
(computation only) is wrapped by a thin layer doing all I/O. What makes
fast tests possible. (Module 2.)

**Pure function** — output depends only on arguments: no file/database
access, no clock, no globals, no printing. (Module 2.)

**Dependency injection** — passing a function what it needs (config, a
connection) as arguments rather than letting it reach into global state.
Sounds enterprise-y; is literally "take it as a parameter". (Module 2.)

**Lockfile** — the exact-versions record of every installed package, so
teammates and CI reproduce your environment precisely. `pyproject.toml`
declares intent; the lockfile records fact. (Module 2.)

**Linter / formatter (ruff)** — automated code reviewers: the linter finds
bug-shaped patterns (unused names, mutable default arguments), the
formatter ends style debates by mooting them. (Module 2.)

**Testing pyramid (data edition)** — many fast unit tests on pure logic, a
few integration tests across the seams, a couple of end-to-end runs — plus
*data tests*, a separate category that runs in production on real data.
(Module 3.)

**Unit / integration / data test** — is my logic right (pre-merge,
synthetic inputs) / is the wiring right (pre-merge, temp warehouse) / is
today's actual data sane (runtime, production). (Modules 3, 5.)

**Fixture (pytest)** — reusable, injected test setup (e.g., a temp
directory, a seeded database). Also: the tiny engineered input files tests
run on. (Module 3.)

**Mutation testing** — judging a test suite by planting bugs and counting
how many it catches. The honest coverage metric. (Module 3.)

**Golden / snapshot test** — comparing output against a stored known-good
copy. Protects unchanged behavior; must be re-reviewed on intentional
change. (Module 3.)

**Partition** — the natural slice a batch dataset arrives in (a day, an
hour, a region). Functional data engineering makes it the unit of loading,
overwriting a whole partition at a time. (Module 4.)

**Partition overwrite** — `DELETE` the partition's rows + `INSERT` the new
ones, atomically. The idempotent alternative to appending. (Module 4.)

**Transaction / atomicity** — grouping writes so they all happen or none
do; readers never see the in-between. (Modules 4, 6.)

**Backfill** — re-running the pipeline over a historical date range, e.g.
after a bug fix or late delivery. Terrifying with append loads; a loop
with idempotent ones. (Module 4.)

**Immutable raw zone** — source data lands once and is never edited;
corrections arrive as new deliveries. Keeps history recomputable — the
pipeline's undo button. (Module 4.)

**Late-arriving / re-delivered data** — yesterday's facts showing up (or
changing) today. Handled structurally by partition overwrites. (Module 4.)

**Expectation / data quality check** — a promise about data expressed as a
query returning violating rows; zero rows = kept promise. The mechanism
inside dbt tests, Great Expectations, Soda. (Module 5.)

**Severity (warn/error)** — policy attached to a check: error blocks
publication, warn reports and trends. Tolerance as reviewed code instead
of 2 a.m. judgment. (Module 5.)

**Quality gate** — the pipeline stage that runs checks and refuses to
publish on error-severity failures. *Stale beats wrong.* (Module 5.)

**Data contract** — a versioned, machine-checked agreement about a
dataset's schema and semantics between producer and consumer. Turns
"vendor renamed a column" from your incident into their breaking change.
(Module 5.)

**Schema drift** — the shape of incoming data changing without
announcement: dropped/renamed columns, changed types. (Module 5.)

**CI (continuous integration)** — a machine runs lint + tests on every
proposed change, before merge, every time. Vigilance with no duty cycle.
(Module 6.)

**Environment (dev/staging/prod)** — an isolated place the pipeline runs:
data + warehouse + config. Environments differ by config, never by branch.
(Module 6.)

**Write-Audit-Publish (WAP)** — build the new table under a staging name,
check it, and only then atomically swap it into place; on failure, prod is
untouched and the rejected candidate is kept for autopsy. Blue-green
deployment for tables. (Module 6.)

**Rollback (data edition)** — reverting code stops *new* damage; the data
already written stays wrong until backfilled under good logic. Always two
steps. (Module 6.)

**Orchestrator** — the system that runs your DAG on schedule with retries,
state, and a logical date: Airflow, Dagster, Prefect. You build the core
of one in Module 7.

**Logical date / data interval** — the period a run is *about* (June 3rd's
data), as opposed to when it executes (June 20th, during a backfill). The
scheduler's answer to `datetime.now()`. (Modules 4, 7.)

**Observability (freshness, volume, schema, lineage)** — standing
questions asked of the data from outside any single run; catches the run
that never happened. (Module 7.)

**Alert fatigue** — what noisy monitors train teams into; a design defect,
not a human weakness. (Modules 5, 7.)

**Runbook** — the pre-written one-pager per failure mode: symptom →
diagnosis commands → remediation → escalation. (Module 7.)

**Blameless postmortem** — incident writeup that treats human error as a
constant and system design as the variable; produces action items, not
culprits. (Module 7.)

**SLO / error budget** — a deliberate, measurable reliability promise
("fresh by 07:00, 99% of business days") and the misses you're allowed;
turns priority fights into arithmetic. (Module 7.)
