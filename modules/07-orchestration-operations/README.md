# Module 07 — Orchestration & Operations

> *It's 3 a.m. The pipeline is red. The dashboard meeting is at 9.*

## Where we are

The CoreCafé pipeline has reached its final form (v4, in `project/`): pure
tested logic, idempotent partition loads, a quality gate, WAP-published
marts, structured logs. One question remains, and it's the one that
separates a good pipeline from a production *system*: **who runs it, what
happens when it breaks, and how do you find out before your stakeholders
do?**

This module covers the operational half of data engineering — the half
that never appears in demos. Instead of teaching you Airflow's UI, you'll
build the core of an orchestrator yourself (~60 lines), instrument the
pipeline with the two monitors that catch what nothing else can, and learn
the discipline of incidents: runbooks, blameless postmortems, SLOs.

## Learning objectives

1. Explain what an orchestrator fundamentally is — a DAG executor with
   retries, state, and scheduling — by having implemented one; then map
   your implementation onto Airflow/Dagster/Prefect vocabulary.
2. State why **retries require idempotency** (Module 4's payoff) and what
   an orchestrator does to a pipeline that lacks it.
3. Instrument freshness and volume monitoring, and design alerts a human
   half-asleep can act on — including *not* alerting when there's no signal.
4. Write a **runbook** before the incident, and a **blameless postmortem**
   after it.
5. Define an SLO for a data product and know what it changes about your
   priorities.

## The failure, first

CoreCafé's pipeline currently runs when someone runs it. Inventory of ways
that dies quietly:

- Nobody runs it → dashboards go stale. *Nothing alerts.* Staleness looks
  exactly like a slow news day.
- Ops wires it to cron → cron retries nothing, logs to a mailbox nobody
  reads, and if the stores file loads but the sales step dies, there is no
  record of *which half happened*.
- Two cron entries drift ("temporary" second schedule during a backfill,
  never removed) → double concurrent runs fight over the warehouse lock.

And the deepest one: on June 12th the vendor delivered nothing at all. The
pipeline didn't run, didn't fail, produced no error — *there was no run to
fail*. Every check built so far shares one blind spot: **they only speak
when the pipeline executes.** Detecting the absence of a thing requires a
watcher outside the thing. That's observability, and it's half this module.

## Concepts

### 1. An orchestrator is a small idea in a big costume

Strip Airflow's 4,000 pages of docs to the load-bearing core and you get:

1. **A DAG of tasks** — dependencies as a graph (the same DAG you met as
   Git history in Module 1; you'll now *execute* one).
2. **Topological execution** — every task runs after its dependencies.
3. **Failure policy** — retries for the flaky, skip-downstream for the
   failed, unrelated branches unharmed.
4. **State & schedule** — what ran when with what result; what should run
   next, tagged with its **logical date** (the period a run *is about*,
   distinct from when it executes — the orchestrator's answer to Module 4's
   `datetime.now()` prohibition, and the parameter your backfills already
   take).

You'll implement 1–3 in Exercise 1. The mapping afterward:

| You built | Airflow | Dagster | Prefect |
|---|---|---|---|
| dag dict | DAG of operators | asset graph | flow/tasks |
| `topological_order` | scheduler | — (asset resolution) | task runner |
| `max_attempts` | `retries` | RetryPolicy | `retries` |
| "skipped" cascade | trigger rules | blocked assets | upstream failure states |
| logical date | `execution_date` / data interval | partition key | scheduled time |

The moral from having built it: orchestrators add *reliability machinery*,
not *correctness*. **An orchestrator retrying a non-idempotent task is an
incident generator with a schedule.** Retries are only safe because
Module 4 made re-execution harmless — the practices compose; that
composition is the course.

### 2. Observability: the four questions

Logs answer "what did this run do?" — necessary (v4's structured,
timestamped lines exist exactly for this) but not sufficient, because logs
only exist *when runs exist*. Observability asks four standing questions of
the *data*, continuously, from outside any single run:

| Pillar | Question | Catches |
|---|---|---|
| **Freshness** | when did data last arrive? | the run that never happened |
| **Volume** | how much arrived vs. normally? | the half-delivered file that parsed fine |
| **Schema** | does shape match the contract? | upstream drift (your Module 5 validator) |
| **Lineage** | what feeds what? | blast-radius: "which dashboards care?" |

You build the first two in Exercise 2 — genuinely ~20 lines each — because
they're the pair whose absence kills silently. Two design rules the tests
enforce, both learned from decades of ops pain:

- **An alert must carry its own context.** "Data stale" forces the
  responder to run queries before understanding; "newest data is 48h old,
  SLA is 24h" can be acted on from a phone. Write messages for a
  half-asleep reader — usually future you.
- **No baseline, no alert.** A volume detector firing off two days of
  history is a coin flip with a pager. And every false alarm *trains* the
  team toward the response that eventually swallows a real one. Alert
  fatigue isn't a human weakness; it's a design defect (you met this in
  Module 5's warn-that-cried-wolf reflection).

### 3. Incidents: the runbook and the postmortem

At 3 a.m., intelligence is unavailable; *preparation* is what responds. A
**runbook** is preparation in document form — written calmly, versioned in
Git next to the pipeline it serves, one page per failure mode: symptom →
diagnosis queries (copy-pasteable) → remediation (exact commands) →
escalation (who, when). Note what v1–v4 did to the *content* of that page:
"re-run the pipeline" is a terrifying instruction against v0 and a safe
one against v4. Operability was built in Modules 4–6; the runbook just
writes it down. ([`runbook_template.md`](runbook_template.md) — Exercise 3
has you fill it in.)

After the incident: the **blameless postmortem**. Premise (from Module 0's
first reflection, now formalized): humans erring is a constant; systems
that *allow* the error are the variable. "Ops ran it twice" is not a root
cause — "the loader was unsafe to run twice" is, and it has a fix with a PR
attached. Teams that blame get silence and repeat incidents; teams that fix
systems get systems that stop failing the same way twice. The one-page
format: timeline (from logs — this is why logs carry timestamps), impact,
root cause *of the system*, action items with owners.

### 4. SLOs: how good is good enough, in writing

"Dashboards should be fresh" is a wish. *"daily_revenue is updated by
07:00 on 99% of business days, measured monthly"* is an SLO — a promise
chosen deliberately, with an error budget (the ~2.5 misses/year you're
*allowed*) that turns priority fights into arithmetic: budget burned →
reliability work preempts features; budget intact → ship faster, and
resist gold-plating. SLOs also expose impossible promises early: if the
vendor delivers at 06:45 and your run takes 40 minutes, the 07:00 SLO is
fiction *no matter how good your code is* — better discovered in a
planning doc than in a quarterly review.

> ⚠️ **Going deeper.** Lineage at scale (OpenLineage, dbt's graph) turns
> "sales is late" into "these 3 dashboards and 2 ML features will be stale
> by 9:00" — impact analysis as a query. Anomaly detection grows from your
> fixed-tolerance monitor into seasonal models (weekend vs weekday — your
> datagen data *has* that pattern; try it). Incident tooling (PagerDuty
> et al.) adds routing and escalation to the alert objects you built.

## Exercises

1. **The mini-orchestrator** —
   [`exercises/m07_orchestrator.py`](exercises/m07_orchestrator.py):
   `topological_order` (deterministic, cycle-rejecting) and `run_dag`
   (retries, skip-cascade, surviving branches). The test DAG is the
   CoreCafé pipeline itself.
2. **The monitors** —
   [`exercises/m07_monitors.py`](exercises/m07_monitors.py): freshness
   vs SLA, volume vs history — including the discipline of staying silent.
3. **The runbook (ungraded, do not skip):** using
   [`runbook_template.md`](runbook_template.md), write the page for
   *"morning run missing / dashboards stale"* against the v4 pipeline. Then
   — the real test — have someone else (or you, next week) execute it
   without you.
4. **Full circle (ungraded):** rewrite your Module 00 incident report as a
   blameless postmortem of the doubled-revenue incident. Compare with the
   original. That diff is the course.

```bash
make check MODULE=07
```

## Reflection questions

1. Your DAG retries `load_sales` 3 times with exponential backoff. Under
   what failure mode do retries make the incident *worse*, and what
   property of the task decides that? (You've known the answer since
   Module 4 — say it precisely.)
2. The volume monitor's tolerance is ±50%. CoreCafé's weekend traffic is
   legitimately ~40% above weekday. What false-alert/missed-alert trade-off
   is hiding in one global tolerance, and what's the smallest fix?
3. Leadership wants "five nines" freshness for `daily_revenue`. Using the
   vendor-delivers-at-06:45 constraint, negotiate: what SLO would you
   *counter-offer*, and what would 99.999% actually cost?

(Suggested answers: [`solutions/reflections.md`](solutions/reflections.md).)

## Further reading

- [Google SRE book — SLOs](https://sre.google/sre-book/service-level-objectives/) and [Postmortem culture](https://sre.google/sre-book/postmortem-culture/) — the canonical texts; both transfer to data almost unedited.
- [Dagster: DataOps guide](https://dagster.io/blog/dataops-with-dagster-a-practical-guide-to-building-a-reliable-data-platform) and [smoke-testing pipelines](https://dagster.io/blog/smoke-test-data-pipeline)
- [Airflow docs: DAG runs and the logical date](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dag-run.html) — now readable as "oh, it's my `run_dag` with persistence."

---

**Next:** [Module 08 — Capstone](../08-capstone/README.md). No more guided
work: a new domain, a blank repo, and everything you've built — done alone,
reviewed like a professional's PR.
