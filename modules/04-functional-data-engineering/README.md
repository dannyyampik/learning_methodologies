# Module 04 — Functional Data Engineering

> *"Can I just re-run it?"* — the question that decides whether your weekend survives

## Where we are

The pipeline is versioned, structured, and unit-tested — and it *still* has
the bug from day one: run it twice, count everything twice. The tests of
Module 03 can detect that; this module is about a design under which the
question **cannot arise**. It is the single most important module for your
future 3 a.m. self.

The ideas here were crystallized for our field by Maxime Beauchemin
(creator of Airflow and Superset) in *Functional Data Engineering* — the
observation that batch pipelines become radically easier to operate when
they borrow two properties from functional programming: **pure functions**
and **immutable data**.

## Learning objectives

1. Define **determinism** and **idempotency**, distinguish them (they are
   *independent* properties), and spot the hidden inputs that break each.
2. Treat the **partition as the unit of work**: implement a loader where
   "load a file" means "atomically replace that day", making reruns,
   corrections, and backfills all the same boring operation.
3. Use **transactions** to guarantee all-or-nothing writes.
4. Explain the **immutable raw zone** and what capabilities die when raw
   data is deleted or mutated.
5. Run a **backfill** and articulate why it held no terror.

## The failure, first

Three production stories, all real patterns, all one disease:

- **The double-run** (you've met it): scheduler retried a half-failed job;
  revenue doubled; nobody noticed for a week.
- **The correction**: vendor re-sends June 3rd "with fixes". The engineer
  writes a one-off `UPDATE` by hand at 6 p.m. It fixes 2 of 3 discrepancies
  and introduces one of its own. There is no record of what it changed.
- **The backfill of dread**: a bug fixed in the revenue formula should be
  applied to last quarter. The team schedules a *weekend* for it, because
  reprocessing means hand-managed DELETEs before every step and any crash
  leaves the warehouse in a state no one can describe.

The common disease: **the pipeline's effect depends on what state the
warehouse was already in.** The cure is to make every task's effect a pure
function of its *inputs* — then the warehouse state is always "inputs,
projected", no matter how many times, in what order, after what failures.

## Concepts

### 1. Two properties, often confused, both required

**Deterministic**: same inputs → same *values*. Killed by hidden inputs:
`datetime.now()`, unseeded randomness, `os.environ` reads, queries against
tables that change between runs. (You've been fighting for this since
Module 2 — purity is determinism's enforcement mechanism.)

**Idempotent**: running once and running N times leave the same *state*.
Killed by relative effects — `INSERT` (append), `UPDATE x = x + 1` — and
guaranteed by absolute effects: *overwrite*, *replace*, *set to*.

They're independent — a loader can stamp `now()` on rows yet overwrite
partitions (idempotent, non-deterministic), or compute perfect values and
append them (deterministic, non-idempotent). Operations needs **both**:
determinism makes a rerun produce the *right values*; idempotency makes it
produce them *exactly once*.

### 2. The partition is the unit of work

CoreCafé's sales arrive as one file per day. That's not incidental — it's
the natural **partition** structure of almost all batch data (by day, hour,
region…). Functional data engineering's central move is to align the
*write* granularity with it:

> A load never inserts rows. A load **replaces a partition** —
> `DELETE WHERE day = X` + `INSERT`, inside one transaction.

Look what falls out, for free:

| Operational event | With append loads | With partition overwrite |
|---|---|---|
| Scheduler retries a job | duplicates | non-event |
| Vendor re-delivers a corrected file | hand-written UPDATEs | re-run that day |
| Bug fix must apply to history | weekend of dread | loop over days ("backfill") |
| A row was *removed* in the correction | zombie row survives | gone, by construction |
| "What produced this table?" | archaeology | "the current code over the raw files" |

That last row is the deep one: the warehouse stops being a *stateful
accumulation of everything that ever ran* and becomes a **projection of
(raw data × current logic)** — recomputable at will. The table is a cache.
Caches are not scary; ledgers with no provenance are scary.

(The BI translation: you already trust "drop and rebuild the view" over
"patch the view's rows by hand". Partition overwrite is that instinct,
scaled to fact tables, with a partition-sized blast radius.)

### 3. All-or-nothing, or: why transactions

A partition overwrite has a terrifying middle: after the `DELETE`, before
the `INSERT` completes. Crash there without a transaction and you've turned
"stale data" into "missing data" — strictly worse. Hence the two rules the
exercise enforces:

1. **Parse everything before writing anything.** A parse error on row 400
   must not leave rows 1–399 committed. (Notice this also motivates the
   *strict* parsing policy here, versus Module 2's skip-and-record
   `clean_batch`: skipping belongs at the *ingestion boundary* where you're
   accepting foreign data; replacement of trusted partitions should be
   all-or-nothing. Same pipeline, two stages, two deliberately different
   error policies — being able to say *why* is the level of understanding
   this course is after.)
2. **DELETE + INSERT inside `BEGIN…COMMIT`, `ROLLBACK` on any error.**
   Readers see the old partition or the new one, never the void.

### 4. The immutable raw zone

Rule: **raw data lands once and is never edited.** Files are the vendor's
truth; corrections arrive as *new deliveries*, not in-place edits.

This is what makes the whole scheme recomputable — bug fixes replay over
history, new columns can be derived for old dates, warehouse migrations are
possible at all. Delete or mutate raw, and today's warehouse becomes the
*only* copy of the past, frozen under whatever logic (and whatever bugs) it
was built with. Storage is cheap; the undo button is priceless.

> ⚠️ **Going deeper.** This module's ideas industrialized: partitioned
> `INSERT OVERWRITE` (Hive/Spark/BigQuery), snapshot-based table formats
> (Iceberg, Delta) where "overwrite" is a metadata swap and old snapshots
> remain time-travelable, and dbt's `--full-refresh` vs incremental
> materializations — all partition-functional thinking under different
> syntax. GDPR-style *right to erasure* is the legitimate exception to raw
> immutability; handle it as a governed, logged process, never ad-hoc.

## Exercises

1. **The idempotent loader** —
   [`exercises/m04_idempotent.py`](exercises/m04_idempotent.py):
   `partition_date_of`, `overwrite_partition` (transactional),
   `load_sales_csv` (strict), and `backfill`. The tests re-deliver
   corrected files, crash your loads halfway, and re-run everything twice —
   exactly like production will.
2. **Concepts** — [`exercises/m04_concepts.py`](exercises/m04_concepts.py):
   five judgment calls, including the MERGE-vs-overwrite trade-off that
   comes up in every design review.

```bash
make check MODULE=04
```

## Reflection questions

1. Your `daily_revenue` mart is rebuilt from scratch every run
   (`CREATE OR REPLACE ... AS SELECT`). Is that idempotent? Deterministic?
   At what data volume does "rebuild the world" stop being a strategy, and
   what replaces it?
2. Beauchemin argues for a "persistent immutable staging area". Your
   compliance team says raw files with PII must be deletable. Reconcile
   these — what exactly do you keep, delete, and re-derive?
3. The strict loader rejects a whole day for one bad row; `clean_batch`
   admits the day minus the bad row. The vendor's file has exactly one
   garbage row *every single day*. Which policy do you want in production,
   and what third option exists? (Module 5 has opinions.)

(Suggested answers: [`solutions/reflections.md`](solutions/reflections.md).)

## Further reading

- [Functional Data Engineering — Maxime Beauchemin](https://maximebeauchemin.medium.com/functional-data-engineering-a-modern-paradigm-for-batch-data-processing-2327ec32c42a) — *the* essay; read it in full now that you've built it.
- [Functional Data Engineering — a blueprint (Data Engineering Weekly)](https://www.dataengineeringweekly.com/p/functional-data-engineering-a-blueprint)
- [Let's Get 'Idempotence' Right (SSENSE Tech)](https://medium.com/ssense-tech/lets-get-idempotence-right-59f227178bb8)

---

**Next:** [Module 05 — Data Quality & Contracts](../05-data-quality/README.md):
the code is now trustworthy under any operational abuse. The *data* is not.
