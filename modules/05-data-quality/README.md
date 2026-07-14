# Module 05 — Data Quality & Contracts

> *"The pipeline ran green. The dashboard is wrong. Both statements are true."*

## Where we are

After Module 04, CoreCafé's pipeline (v2, in `project/`) is operationally
bulletproof: deterministic, idempotent, atomic. And it will still cheerfully
load a file where half the sales point at store 99 (which doesn't exist),
sale IDs repeat, and quantities are negative. **Correct code, garbage data,
green run** — the failure mode that testing (Module 3) cannot touch,
because the defect isn't in your logic; it arrives *with the inputs*, at
runtime, after every test has already passed.

This module builds the missing organ: runtime checks on the data itself,
wired into the pipeline as a **gate**, and the social contract that pushes
quality responsibility upstream to where defects are born.

## Learning objectives

1. State the difference between *code tests* and *data tests* precisely,
   including **when** each runs and **what** each can catch.
2. Build an expectations engine from first principles — the universal
   "failing rows query" shape behind dbt tests, dbt-expectations, Great
   Expectations, and Soda — and map your five primitives onto those tools.
3. Use **severity** (error vs warn) to encode tolerance as reviewed policy
   instead of an accident of error handling.
4. Write and enforce a **data contract**: schema promises, versioned in
   Git, checked by machine — and detect schema drift before downstream does.
5. Decide *where* checks belong: on ingest, before publish, or upstream at
   the producer.

## The failure, first

Generate a poisoned delivery and feed it to the (fully tested, fully
idempotent) pipeline:

```bash
python -m datagen --output /tmp/poisoned --days 3 \
    --defect 2026-06-02:duplicates,unknown_store,negative_quantity

CORECAFE_RAW_DIR=/tmp/poisoned CORECAFE_WAREHOUSE=/tmp/poisoned.duckdb \
    PYTHONPATH=modules/05-data-quality/project python -m corecafe
```

Exit code 0. Rows loaded. Now look at what finance sees:

```bash
python -c "
import duckdb
con = duckdb.connect('/tmp/poisoned.duckdb', read_only=True)
print(con.execute('''
    SELECT store_name, round(sum(revenue),2)
    FROM daily_revenue GROUP BY 1 ORDER BY 2 DESC
''').fetchall())"
```

A `None` store earning revenue. Duplicated sales inflating June 2nd.
Negative quantities silently *deflating* it at the same time. Every test in
Module 3 still passes, because every test in Module 3 tests the **code**.

## Concepts

### 1. The two-gate model

```
 vendor file ──▶ [GATE 1: ingest checks] ──▶ warehouse ──▶ [GATE 2: publish checks] ──▶ marts/dashboards
                  "is this delivery sane?"                  "is what consumers will see sane?"
                  schema, freshness, volume,                reconciliation, referential
                  row-level validity                        integrity, business invariants
```

Gate 1 protects *you* from the world; Gate 2 protects *consumers* from you.
They're different because defects compose: two individually-sane deliveries
can still produce an insane join. Module 6 turns Gate 2 into the "Audit" of
Write-Audit-Publish; this module builds the checking machinery both gates
share.

### 2. Every data quality tool is the same query

The insight that demystifies the entire tool category:

> **A check is a query that returns the rows violating a promise.
> Passing = zero rows.**

`unique` on `sale_id`? Count the surplus copies. `relationship` to
`stores`? Count the orphans. Any bespoke business rule? `count(*) WHERE NOT
(predicate)` — the escape hatch that expresses everything else. You will
implement five such primitives and a verdict function in ~80 lines, and
afterward dbt's test block will read as configuration for a query generator
you once wrote yourself. That mapping, explicitly:

| Your engine (exercise) | dbt | Great Expectations |
|---|---|---|
| `check_not_null` | `not_null` | `expect_column_values_to_not_be_null` |
| `check_unique` | `unique` | `expect_column_values_to_be_unique` |
| `check_accepted_values` | `accepted_values` | `expect_column_values_to_be_in_set` |
| `check_relationship` | `relationships` | (custom / cross-table) |
| `check_expression` | singular test / `dbt_utils.expression_is_true` | `expect_*` + custom SQL |
| `verdict` + severity | `severity: warn/error` config | validation result + actions |

One SQL subtlety will bite you on the way (the tests make sure of it):
`NOT (store_id > 0)` does **not** catch NULL store_ids, because in SQL's
three-valued logic `NULL > 0` is `NULL`, and `NOT NULL` is still `NULL` —
not true, so the row escapes the failing-rows query. A row that cannot
*prove* it satisfies the rule should fail the rule: `COALESCE(pred, FALSE)`.
Every data quality tool has this decision buried in it somewhere; now you
know where to look.

### 3. Severity: tolerance as policy, not accident

Module 4's reflection asked what to do about a vendor that ships one
garbage row per day. The answer is severity levels:

- **error** — blocks the gate. For promises whose violation corrupts money:
  uniqueness of `sale_id`, referential integrity, non-negative revenue.
- **warn** — reported, counted, trended; doesn't block. For known,
  tolerated imperfection: the occasional NULL `store_id` the POS firmware
  drops.

The deep point: **the tolerance is now a reviewed, versioned decision.**
Moving `store_id` nulls from warn to error is a one-line PR that a human
approves with full context — not a 2 a.m. judgment call inside an `except`
block. (Real tools add thresholds — "warn above 0.1%, error above 1%" —
your `verdict` is where such policy would live.)

### 4. Data contracts: quality pushed to the producer

Checks catch defects *after* they arrive. Contracts aim earlier: an
explicit, versioned agreement between producer and consumer about what a
dataset promises — schema, nullability, semantics, freshness. The contract
lives in Git (like an API spec), changes via reviewed PRs, and its
enforcement is automated: your `validate_schema()` compares promise to
reality via `information_schema`, catching the classic upstream betrayals —
dropped column, drifted type, surprise column — **before** they detonate a
downstream join.

Contracts change the *conversation*: without one, the vendor renaming
`payment_method` is your incident; with one, it's their breaking change,
visible in a diff, negotiable before deployment. In event-driven systems
the same idea appears as schema registries with compatibility rules; in the
warehouse world, as dbt model contracts. Same social technology.

> ⚠️ **Going deeper — anomaly detection.** Fixed rules catch known
> pathologies; volume/freshness/distribution *monitoring* (Monte Carlo,
> Elementary, SYNQ et al.) catches unknown ones ("today's row count is 4σ
> below trend"). You'll build the trend-based volume detector yourself in
> Module 7 — it's ~20 lines.

## Exercises

1. **The expectations engine** —
   [`exercises/m05_expectations.py`](exercises/m05_expectations.py): five
   check primitives + severity verdict, graded against a warehouse
   containing one of every classic defect. Watch for the NULL-predicate
   trap.
2. **The contract** —
   [`exercises/m05_contract.py`](exercises/m05_contract.py): write the
   `sales` contract and its schema enforcement; the tests drift the schema
   under you and expect to get caught.

```bash
make check MODULE=05
```

3. **Ungraded:** wire your engine into the v2 pipeline (edit your copy of
   `project/corecafe/pipeline.py`): run the suite after loading, print the
   verdict, non-zero exit on failure. Module 6's project snapshot shows a
   reference wiring as its starting point.

## Reflection questions

1. A check on `daily_revenue` fails at 6 a.m.: revenue is 40% below the
   28-day average. Name three *legitimate* causes and three defects that
   look identical. What does the pipeline lack that would let it tell them
   apart? (This is Module 7's opening question.)
2. Your `store_id` not_null check is at warn severity and has warned every
   day for six months. Nobody reads it anymore. What's the failure of
   process here, and what are the options? ("Delete the check" is allowed
   as an answer — argue it.)
3. The vendor refuses to sign any contract ("you get the export as-is").
   Where does that move the contract boundary, and what changes in *your*
   architecture?

(Suggested answers: [`solutions/reflections.md`](solutions/reflections.md).)

## Further reading

- [dbt tests documentation](https://docs.getdbt.com/docs/build/data-tests) — read after the exercise; it will feel like documentation for your own code.
- [dbt-expectations](https://github.com/metaplane/dbt-expectations) — the 62-check catalog; skim the names as a checklist of promises you *could* make.
- [Data contracts in practice (Gable)](https://www.gable.ai/blog/data-contract-tools) and [SYNQ's observability guide](https://www.synq.io/blog/data-observability-guide)

---

**Next:** [Module 06 — CI/CD & Environments](../06-ci-cd/README.md): checks
exist, tests exist — now we make it *impossible to skip them*, and make
"deploying a pipeline" a real, safe, boring event.
