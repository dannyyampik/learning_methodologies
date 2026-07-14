# Module 06 — CI/CD & Environments

> *"How does a change get from your laptop to production?"*
> *"I run it and if nothing explodes I copy it to the server."*

## Where we are

The pipeline (v3, in `project/`) now refuses to publish bad data — the
Module 05 quality gate is wired in and a poisoned delivery exits with code 1
while dashboards keep yesterday's good numbers. What's still held together
by discipline alone is the *path of a change*: nothing forces tests to run
before a merge, nothing defines what "deploying" the pipeline means, and
dev work happens against... whatever warehouse was handy.

This module automates the promises: **CI** (continuous integration) makes
the checks unskippable; **environments** give changes a safe place to be
wrong; **Write-Audit-Publish** extends the same courtesy to every table you
build. Your DevOps background will recognize the machinery — the data twist
is deciding what "deploy", "environment", and "rollback" even *mean* when
the artifact is code **plus** the data it produces.

## Learning objectives

1. Read and extend a real GitHub Actions workflow — this repo's own CI,
   which has been checking your work since Module 0.
2. State what CI can and cannot promise for a data pipeline, and design the
   CI-vs-runtime split: synthetic fixtures before merge, data audits at
   runtime.
3. Set up dev/prod separation for a pipeline where environments differ by
   **config only** — and explain why per-environment branches are a trap.
4. Implement **Write-Audit-Publish** — blue-green deployment for tables —
   with atomic swap, untouched-production-on-failure, and staging kept for
   autopsy.
5. Tell the two halves of a data rollback apart: reverting code (stops new
   damage) and backfilling (repairs old damage).

## The failure, first

A story that requires no imagination: the Module 01 review exercise's PR —
the one with the smuggled `WHERE payment_method != 'cash'` — gets merged on
a Friday because the reviewer was in a hurry and *nothing made the tests
run*. It runs all weekend. Three days of `top_products` are now quietly
missing all cash sales.

Count the layers that had to fail: the author didn't run tests (busy), the
reviewer didn't catch it (rushed), nothing ran them automatically (the
actual defect), and the wrong numbers deployed *directly onto the tables
finance reads* (no staging, no audit). Human vigilance is real but it has
a duty cycle. **CI is vigilance with no duty cycle.**

## Concepts

### 1. CI: the checks become unskippable

Continuous integration is a small idea executed relentlessly: *every
proposed change is built and checked by a machine, before merge, every
time.* The repo you're sitting in does it — open
[`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) and read it
top to bottom; it's 35 lines and you have now personally used every tool it
invokes:

- `on: pull_request` + `push: branches: [main]` — check the gate *and* the
  post-merge reality.
- Job `lint` → seconds: ruff catches the cheap stuff.
- Job `test` (`needs: lint`, fail-fast) → runs `make test`: **the same
  command you run locally.** One entry point, one truth — CI that runs
  different commands than developers do will eventually check different
  things than developers think it checks.

What CI *cannot* do for a data pipeline: see tomorrow's production data.
This resolves the classic confusion about "testing with real data" —

| | runs when | data | catches |
|---|---|---|---|
| **CI checks** | before merge | tiny synthetic fixtures | logic bugs, wiring bugs, contract breaks |
| **runtime audits** (Gate 1/2, WAP) | every production run | today's real data | the world misbehaving |

CI on prod-sized data is a mirage anyway — too slow, too flaky, needs
credentials, leaks PII (Q4 of the exercise). Synthetic-small before merge,
audit-everything at runtime: that division of labor *is* modern DataOps.

### 2. Environments: same code, different blast radius

An environment = a complete, isolated place the pipeline can run: source
data + warehouse + config. The discipline that makes environments cheap is
one you already built in Module 2 — config out of code:

```bash
# dev: your sandbox, synthetic data, disposable warehouse
CORECAFE_RAW_DIR=data/raw CORECAFE_WAREHOUSE=dev.duckdb python -m corecafe

# prod: the real thing — same code, same artifact, different values
CORECAFE_RAW_DIR=/srv/deliveries CORECAFE_WAREHOUSE=/srv/warehouse.duckdb python -m corecafe
```

The rule with no exceptions: **environments differ by config, never by
branch.** Per-environment branches ("the prod branch has the hotfixes")
guarantee prod runs a combination of code nobody ever tested. Promotion is
moving an *artifact* through environments, not moving code between
branches. Secrets follow the same rule: values live in the environment
(CI secret stores, vaults) — never in Git, as the Module 01 kata's API key
taught permanently.

### 3. Write-Audit-Publish: blue-green for tables

The v3 gate has a blind spot: it validates `sales`, then builds marts
*directly onto the tables consumers read*. A bug in mart SQL — say, a
refactor that flips a sign — publishes instantly. Software engineering
solved this decades ago with blue-green deployment: build the new version
*beside* the old, verify it, then switch traffic atomically. The data
version is Write-Audit-Publish:

```
WRITE     CREATE TABLE staging_daily_revenue AS <build>   (invisible to consumers)
AUDIT     checks run against STAGING — not_empty? revenue positive? reconciles?
PUBLISH   all pass → atomic swap into daily_revenue; staging dropped
          any fail → prod untouched, staging KEPT for autopsy, humans paged
```

Two design details carry most of the value, and the exercise tests both:
the swap is **atomic** (consumers see old or new, never a mixture — the
same transaction discipline as Module 4's partition overwrite, one level
up), and a failed audit **keeps the evidence** — the staging table is the
crime scene, and dropping it means diagnosing from memory. Note the
philosophy: *stale beats wrong.* A dashboard showing yesterday's correct
numbers is an inconvenience; one showing today's wrong numbers is a
misinformation engine with an audience.

> ⚠️ **Going deeper.** WAP industrialized: Iceberg/Delta make the swap a
> metadata operation (snapshot commit) — same idea, better machinery;
> lakeFS wraps whole pipeline runs in data branches with merge-on-green;
> dbt's blue-green recipes swap schemas rather than tables. And `dbt build`
> interleaves model-then-test exactly so failures stop downstream models —
> WAP thinking as execution order.

### 4. Rollback: the data half is the real half

Deploy v2.1, discover on Wednesday it's been mangling revenue since Monday.
`git revert` + redeploy — done? **Half done.** The rollback stopped *new*
damage; Monday–Wednesday's partitions are still wrong and will stay wrong
forever unless reprocessed. The full runbook is always two lines:

1. Revert the code (stop the bleeding).
2. **Backfill the affected partitions** under the good code (heal the wound)
   — which is only a calm sentence because Module 4 made backfills a loop
   over idempotent overwrites. Teams without that property improvise their
   data repair at 2 a.m., by hand, in prod.

## Exercises

1. **Write-Audit-Publish** — [`exercises/m06_wap.py`](exercises/m06_wap.py).
   The tests publish a good build, then sabotage the build SQL; production
   must survive bit-for-bit, with the rejected candidate preserved.
2. **CI & environments** —
   [`exercises/m06_ci_concepts.py`](exercises/m06_ci_concepts.py): six
   decisions, three of them about this repo's actual workflow file — read
   it first.

```bash
make check MODULE=06
```

3. **Ungraded, strongly recommended:** in your fork, open a PR that
   deliberately breaks a Module 02 test, watch CI catch it, then fix it on
   the same branch and watch it go green. Feel the difference between
   "I think it works" and "the gate says it works."

## Reflection questions

1. Your CI is green, your WAP audits passed, and finance still reports a
   wrong number caused by a business-rule misunderstanding (the code did
   exactly what its author intended). Which layer failed — and what
   artifact from Modules 1–5 was the right place to catch it?
2. WAP doubles storage for the staging copy and delays publication by the
   audit duration. Name a table where you'd skip WAP, and defend the risk
   acceptance in one paragraph.
3. Your company runs dbt in prod but analysts develop against the prod
   warehouse directly ("it's read-only, it's fine"). List what can still go
   wrong, then design the cheapest dev environment that fixes it.

(Suggested answers: [`solutions/reflections.md`](solutions/reflections.md).)

## Further reading

- [Write-Audit-Publish pattern (lakeFS)](https://lakefs.io/blog/data-engineering-patterns-write-audit-publish/) and [dbt Labs: testing is not enough — WAP](https://www.getdbt.com/blog/testing-is-not-enough-transforming-data-quality-with-write-audit-publish)
- [Blue-green data warehouse deployments with dbt (Calogica)](https://calogica.com/sql/bigquery/dbt/2020/05/24/dbt-bigquery-blue-green-wap.html)
- [GitHub Actions documentation](https://docs.github.com/en/actions) — you now know enough to read any workflow you meet.

---

**Next:** [Module 07 — Orchestration & Operations](../07-orchestration-operations/README.md):
everything is safe; now we make it *run itself* — and teach you what to do
at 3 a.m. when it doesn't.
