# Module 00 — Orientation: Why Data Needs Engineering

> *"The pipeline works. Don't touch it."* — famous last words

## Where we are

Welcome to your first day at **CoreCafé**, a five-store coffee chain. You've
been hired as the data person. Your predecessor, Dave, left a year ago. The
entire analytics platform is one script — `project/pipeline.py` — which loads
point-of-sale exports into a DuckDB warehouse and builds the tables behind
finance's revenue dashboard. Ops runs it "when someone asks for fresh
numbers."

This module has one job: make you *feel*, precisely and viscerally, what is
wrong with this situation — because every later module cures one of the
diseases you're about to diagnose.

## Learning objectives

By the end of this module you can:

1. State the course thesis: **in data engineering, the deployable unit is
   code *and* the data it produces** — and explain why that makes data
   pipelines harder to change safely than ordinary programs.
2. Run the inherited pipeline and demonstrate, with evidence, that it is
   **not idempotent** — and explain what that word means.
3. Name the seven methodology families this course covers and match each to
   a concrete failure you observed in the monolith.
4. Write a short **incident report** — the document you'll learn to
   formalize in Module 7.

## The failure, first

Do this before reading any theory. From the repo root, with your virtualenv
active and `make data` already run:

```bash
# a fresh warehouse:
rm -f data/warehouse.duckdb

# first run:
python modules/00-orientation/project/pipeline.py

# look at what finance sees:
python -c "
import duckdb
con = duckdb.connect('data/warehouse.duckdb', read_only=True)
print(con.execute('SELECT count(*) FROM sales').fetchone())
print(con.execute('SELECT round(sum(revenue)) FROM daily_revenue').fetchone())
"
```

Note both numbers. Now imagine ops got paged that "the dashboard looks
stale", shrugged, and ran the script again — a completely reasonable thing
to do with any normal program:

```bash
python modules/00-orientation/project/pipeline.py
# ...then re-run the same two queries.
```

**Revenue just doubled.** No error was raised. No test failed — there are no
tests. Nothing in Git changed — the script isn't meaningfully in Git. If
nobody happens to eyeball the dashboard today, CoreCafé's finance team will
report fictional numbers.

Sit with how *quiet* that failure was. A web app that double-charged every
customer would page someone within minutes. A data pipeline that
double-counts revenue smiles and prints `done!`.

## Concepts

### The course thesis

When a software engineer deploys a bug, they roll back the code and the
system is healthy again. When *you* ship a bug, rolling back the code does
**not** un-corrupt the tables it wrote. The blast radius of a data bug is
`bad code × every run × every downstream consumer × time until noticed`.

That asymmetry is why this course exists, and why "just be careful" doesn't
scale. Every practice you'll learn is a machine for shrinking one factor:

| Factor | Practice that shrinks it | Module |
|---|---|---|
| Bad code gets written | Code review, small readable modules | 1, 2 |
| Bad code gets merged | Automated tests in CI | 3, 6 |
| Every run compounds damage | Idempotency — reruns are safe | 4 |
| Bad *data* gets through good code | Quality gates, contracts | 5 |
| Consumers see it before you do | Write-Audit-Publish, observability | 6, 7 |
| Time until noticed | Monitoring, alerting, runbooks | 7 |

### Why pipelines rot

`pipeline.py` was not written by an idiot. It was written by a competent
analyst under deadline, and it *worked*. Pipelines rot through a specific
mechanism worth naming:

1. **It starts as a query.** Someone needs a number; SQL in a notebook.
2. **It gets scheduled.** The query grows a script around it. Still fine.
3. **It gets depended on.** Finance builds a dashboard. Nobody tells the
   author. The script is now *production* — but nothing about how it's
   written, tested, or deployed changed.
4. **It gets feared.** The author leaves. Each new requirement is bolted on
   with minimal disturbance ("if it works, don't touch it"). Understanding
   decays; the comment `# ??? dave why` appears.

Step 3 is the trap: **in data work, things become production silently.**
Software engineering methodologies are, at bottom, the discipline of treating
things as production *before* they're depended on — because you never know
the moment that happens.

### Reading the monolith: a guided autopsy

Open `project/pipeline.py` and find each of these. Seriously — open it in
your editor now; the exercise below checks that you did.

- **No seams.** Extract, transform, and load are interleaved in one
  top-to-bottom flow. You cannot test the revenue calculation without a
  database and files on disk. *(Module 2: separation of concerns.)*
- **`except:` + `continue`.** Malformed rows vanish without a trace. How
  many rows were dropped last month? Nobody can know. *(Module 3 makes
  errors loud; Module 5 counts them.)*
- **The append bug.** `CREATE TABLE IF NOT EXISTS` + unconditional `INSERT`
  = every run adds every historical file again. Meanwhile `stores` uses
  `CREATE OR REPLACE` — a *different* strategy, accidentally safe. The
  inconsistency is the tell. *(Module 4: idempotency by design, not luck.)*
- **Magic numbers, twice.** VAT (`1.17`) is hardcoded in two places. When
  VAT changes, will whoever edits it find both? *(Module 2: config vs code.)*
- **No validation.** `store_id = 99` from a store that doesn't exist would
  sail straight into a `LEFT JOIN` and become a `NULL` store name on the
  dashboard. *(Module 5: contracts and quality gates.)*
- **`print("done!")`.** When this runs at 3 a.m., where does that print go?
  Who is told when it *doesn't* print? *(Module 7: logging and observability.)*

An important discipline while you did that: **contempt is not analysis.**
"This code is bad" is useless; "*this load step appends without deleting,
therefore reruns double-count*" is engineering. Precision about failure
modes is the skill — you'll use it in code reviews (Module 1) and incident
reports (Module 7) forever.

## Exercises

**Exercise 1 — Environment.** Complete [SETUP.md](../../SETUP.md) if you
haven't. `make solutions MODULE=00` must run (it will pass — it grades the
reference answers; yours come next).

**Exercise 2 — Observe the patient.** Follow "The failure, first" above,
then fill in your observations in
[`exercises/m00_observations.py`](exercises/m00_observations.py) and run:

```bash
make check MODULE=00
```

The tests execute the pipeline themselves and check reality against your
answers — this is the self-grading pattern the whole course uses, and by
Module 3 you'll understand exactly how it's built.

**Exercise 3 — The incident report (ungraded, do not skip).** Write
`my_incident_report.md` (anywhere you like; it's for you). One page, three
sections, addressed to a non-technical manager:

1. **What happened** — the doubled-revenue incident, in plain language.
2. **Why it happened** — the mechanism, precisely but without jargon.
3. **What would have prevented it** — pick the *two* cheapest changes, and
   justify the choice. (Cost-benefit judgment is the real question here.)

Keep it. You will rewrite it after Module 7 with a formal template, and the
diff between the two versions is a measure of what this course taught you.

## Self-check

```bash
make check MODULE=00   # green = done
```

## Reflection questions

Answer these to yourself (suggested answers in `solutions/reflections.md`):

1. Ops ran the script twice and corrupted production. Whose fault is that —
   ops', Dave's, or nobody's? What does your answer imply about *design*?
2. The script has worked for two years. In what sense is it still true that
   "it doesn't work"?
3. Which of the seven practice families would you adopt *first* at CoreCafé
   if you could only pick one this quarter? Why?

## Further reading

- [Functional Data Engineering — Maxime Beauchemin](https://maximebeauchemin.medium.com/functional-data-engineering-a-modern-paradigm-for-batch-data-processing-2327ec32c42a) — read at least the opening; Module 4 studies it deeply.
- [The Missing Semester (MIT)](https://missing.csail.mit.edu/) — the course that proved *tooling craft* deserves its own curriculum; we borrow its philosophy.
- Full bibliography: [docs/bibliography.md](../../docs/bibliography.md)

---

**Next:** [Module 01 — Version Control & Collaboration](../01-version-control/README.md), where the renovation begins with the only sane first step: getting the thing under control.
