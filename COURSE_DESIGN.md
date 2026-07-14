# Course Design Document

**Course title:** Software Engineering Methodologies for Data Engineers
**Repository:** `learning_methodologies`
**Status:** Approved for implementation (v1.0, 2026-07)

This document records *why* the course is shaped the way it is. It is the
reference for anyone maintaining or extending the course. Students don't need
to read it, but curious ones are welcome to.

---

## 1. Purpose and audience

### Who this course is for

Data professionals who build pipelines, models, and reports but did **not**
come up through software engineering — typically people from BI/analytics,
DBA, DevOps/infra, or data-analyst backgrounds. They can write SQL fluently
and enough Python to get a job done, but they have not internalized the
practices software engineers use to keep systems correct, changeable, and
operable over years.

Concretely, the target student:

- Writes SQL confidently; writes "script-style" Python (one long file, few
  functions, no tests).
- Uses Git at the level of `add / commit / push`, mostly solo, mostly on one
  branch.
- Has felt the pain: a dashboard silently wrong for three weeks, a pipeline
  nobody dares touch, a "quick fix" in production that broke something else.
- May have DevOps exposure (CI servers, containers) without having applied
  those ideas to *data* work.

### What "success" means

The stated purpose from the course owner: **grant a deep understanding** —
not tool familiarity. A graduate should be able to:

1. Explain *why* each practice exists (what failure mode it prevents), not
   just execute it.
2. Apply the practices to any stack — the course's local stack is a teaching
   vehicle, not the point.
3. Judge trade-offs: know when a practice is overkill and when skipping it is
   negligence.
4. Walk into an existing codebase and *improve* it incrementally — because
   that is the real job, far more often than greenfield building.

### Explicit non-goals

- Not a "learn data engineering" course (no Spark/Kafka/warehouse tour — the
  Zoomcamp already does that well).
- Not a tool certification. Tools appear as concrete instances of ideas.
- Not a Python course, though Module 2 raises Python code quality directly.

---

## 2. Research summary: SWE methodologies in modern data engineering

Research was conducted July 2026 across industry sources (lakeFS, dbt Labs,
Ascend, Dagster, Databricks, MotherDuck, Datadog, SYNQ, practitioner blogs)
and canonical writing (Beauchemin's *Functional Data Engineering*). The
practices below are the ones repeatedly identified as the "software
engineering core" that modern data teams adopt — they form the course's
syllabus skeleton.

| # | Methodology family | What data teams actually do | Key failure mode it prevents |
|---|---|---|---|
| 1 | **Version control & collaboration** | All transformation logic, config, and scheduling metadata in Git; feature-branch or trunk-based workflows; PR review as the quality gate | Untracked changes, unreviewable "SQL in a BI tool", no rollback path |
| 2 | **Code design & modularity** | Separation of I/O from logic; config out of code; dependency pinning/lockfiles; linters/formatters (ruff) and pre-commit hooks; typed, documented modules | The 2,000-line script nobody can change safely |
| 3 | **Automated testing** | The testing pyramid adapted to data: unit tests on transformations (pytest), integration tests on pipeline wiring, *data tests* on the data itself; mocked/stubbed I/O; tiny synthetic fixtures instead of prod data | "We test by running it in prod and watching the dashboard" |
| 4 | **Functional data engineering** (Beauchemin) | Deterministic, idempotent tasks; immutable raw zone; partitions as the unit of work; safe reruns and backfills | Double-counted rows on rerun; unable to reproduce yesterday's numbers |
| 5 | **Data quality & contracts** | Declarative expectations (dbt tests: `unique`, `not_null`, `accepted_values`, `relationships`; Great Expectations / dbt-expectations for distributions & freshness); schema validation at boundaries; data contracts versioned in Git and enforced in CI | Silent upstream schema change breaks everything downstream |
| 6 | **CI/CD & environments (DataOps)** | Lint + test on every PR (GitHub Actions et al.); dev/staging/prod separation for *data*, not just code; **Write-Audit-Publish** — the data equivalent of blue-green deployment; automated rollback | Bad data or bad code reaching consumers before anyone checks |
| 7 | **Operations & observability** | Orchestrators (Airflow/Dagster/Prefect) encoding dependencies as DAGs; retries with idempotency; structured logging; the observability pillars (freshness, volume, schema, lineage); runbooks and blameless postmortems; SLAs/SLOs for data | 3 a.m. failures debugged by archaeology; silent staleness |

Two cross-cutting findings shaped the design:

- **The unit of deployment in data is not just code — it's code *plus* the
  data it produces.** This is the single biggest conceptual shift for the
  audience, and it recurs in modules 4, 5, and 6 (idempotency, contracts,
  WAP). The course treats it as the central thesis.
- **CI for data must confront scale**: you cannot run prod volumes on every
  commit. Sampled/synthetic fixtures for CI plus data audits at runtime is
  the standard resolution — which is exactly the testing architecture the
  course teaches and itself uses.

Primary sources are cited in each module's "Further reading" and in the root
README's bibliography.

---

## 3. Exemplar course analysis

Repo-based courses that demonstrably work were studied for structure:

**[DataTalksClub / data-engineering-zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp)** (~30k stars)
- Numbered module folders (`01-docker-terraform`, `02-workflow-orchestration`…)
  make the path unmistakable.
- Every module README is self-sufficient: objectives, materials, homework.
- Homework per module + peer-reviewed capstone = knowledge is *exercised*,
  not just read.
- Weakness for our purposes: depends on cloud accounts and videos; content
  breadth over conceptual depth.

**[MIT — The Missing Semester](https://github.com/missing-semester/missing-semester)**
- Proof that *methodology* (vs. technology) courses work: it teaches the
  tooling craft around programming, exactly analogous to what we teach around
  data work.
- Strength: every lesson explains the *model* behind the tool (e.g., Git's
  object graph before Git commands). We adopt this "mental model first"
  approach wholesale.

**[cnstlungu / portable-data-stack](https://github.com/cnstlungu/portable-data-stack-dagster)** and the "local data stack" movement (DuckDB + dbt + Dagster)
- Proof that a credible, warehouse-shaped stack runs on a laptop with zero
  cloud accounts. We adopt the local-first constraint.

Design lessons extracted:

1. **Numbered folders + per-module README** — adopted.
2. **Self-contained modules with a shared narrative** — adopted (see §5:
   snapshot-per-module).
3. **Exercises must be verifiable without a grader** — adopted, strengthened:
   exercises ship with pytest suites so `make check MODULE=03` tells the
   student objectively whether they're done. The self-grading harness *is
   itself a demonstration of the course's subject matter*.
4. **Capstone with a rubric** — adopted.
5. **No cloud accounts, no videos, no paid anything** — adopted. Everything
   runs offline after `make setup`.

---

## 4. Design principles

1. **One narrative, one codebase.** The whole course is the story of
   inheriting a realistic, messy-but-working pipeline ("CoreCafé", a
   fictional coffee-chain analytics pipeline) and progressively renovating it
   into production-grade software. Refactoring-under-constraints is the real
   job; greenfield courses teach the wrong instincts.
2. **Mental model before mechanics.** Every module opens with the failure
   story and the concept, then the practice, then the tool. A student who
   changes stacks keeps everything but the syntax.
3. **The pain comes first.** Module 0 has the student *run and break* the
   messy pipeline before any theory. Each subsequent module opens by
   demonstrating the failure mode it addresses — you can't deeply understand
   a cure without the disease.
4. **Verification is the pedagogy.** Every exercise is checked by tests the
   student runs locally; the course repo runs its own CI on GitHub Actions.
   The medium is the message: the course practices what it preaches, and
   module 6 literally studies the repo's own CI as its case material.
5. **Self-contained modules, shared story.** Each module folder contains a
   `project/` snapshot of the pipeline as it stands at that module's start.
   A student can start at module 4 without completing 1–3, yet a
   start-to-finish student experiences continuous renovation. (Cost:
   duplicated code between snapshots. Accepted deliberately — snapshots are
   small, and self-containedness is worth more.)
6. **BI-background empathy.** Analogies map from what the student knows:
   Git ↔ SSAS/report versioning pain, data tests ↔ reconciliation checks,
   WAP ↔ swapping a view to a rebuilt table. Jargon is defined at first use.
7. **Depth over breadth.** Eight modules plus capstone, each deep, rather
   than a survey. Sections marked ⚠️ *Going deeper* are optional
   depth for faster students.

## 5. Technology stack and rationale

| Choice | Rationale |
|---|---|
| **Python 3.11+ & SQL** | The two lingua francas of data engineering; the audience already half-knows both. |
| **DuckDB** | A real columnar analytical database as a single file — warehouse semantics (schemas, constraints, window functions) with zero setup, zero cost, fully offline. |
| **pytest** | Industry standard; fixtures/parametrize teach transferable testing design. |
| **ruff** | One fast tool for lint + format; low ceremony. |
| **uv / pyproject.toml** | Modern dependency management with lockfile discipline (the point being taught). |
| **Make** | Ubiquitous, readable task runner; doubles as an interface-design lesson. |
| **GitHub Actions** | CI/CD taught on the repo's own real pipeline; free tier suffices. |
| **No orchestrator dependency** | Module 7 teaches DAGs/retries/scheduling by *building a ~100-line mini-orchestrator*, then maps concepts to Airflow/Dagster/Prefect. Deeper understanding than tool tutorials, zero install pain. |
| **dbt: concepts, optional practice** | dbt's testing/environments model is taught natively in modules 5–6 via the course's own assertion runner; an optional dbt track is provided for those who want the tool itself. Keeps the required path dependency-light. |
| **Synthetic data generator** | A seeded generator (`tools/datagen`) produces realistic coffee-chain data *with controllable defects* (dupes, nulls, late records, schema drift). No downloads, reproducible, and defects arrive exactly when the curriculum needs them. |

## 6. Curriculum map

Progression logic: *make it tracked → make it readable → make it tested →
make it rerunnable → make the data trustworthy → make delivery safe → make it
operable → prove it all.*

| Module | Title | Core question | Key practices | Deliverable |
|---|---|---|---|---|
| 00 | Orientation: Why Data Needs Engineering | Why do pipelines rot? | Course thesis; environment setup; run & break the inherited pipeline | Working environment; a written "incident report" on the messy pipeline |
| 01 | Version Control & Collaboration | How do teams change code safely? | Git mental model (graph, staging), branching strategies, PRs, code review for data, what *not* to version | Bug fixed via real branch→PR→review workflow; review of a provided bad diff |
| 02 | From Scripts to Software | Why can't anyone touch this code? | Separation of concerns, I/O boundaries, config vs code, dependency lockfiles, typing, docstrings, ruff, pre-commit | The monolith refactored into a package — behavior proven unchanged by provided tests |
| 03 | Testing Data Systems | How do you know it works? | Testing pyramid for data; pytest (fixtures, parametrize); unit vs integration vs data tests; designing tiny fixtures; regression tests | Test suite that catches 5 seeded bugs; coverage of the core transforms |
| 04 | Functional Data Engineering | Why did rerunning it double the numbers? | Determinism, idempotency, immutability, partitions as unit of work, incremental loads, backfills | Idempotent, partitioned loader + working backfill command |
| 05 | Data Quality & Contracts | The code is right — why is the data wrong? | Expectations (unique/not_null/accepted/relationships/freshness), severity levels, boundary validation, data contracts, dbt mapping | Quality gate that blocks 3 injected bad batches; a versioned data contract |
| 06 | CI/CD & Environments | How does a change get to prod safely? | GitHub Actions anatomy, the repo's own CI dissected, dev/staging/prod for data, Write-Audit-Publish, rollback | Extended CI workflow; WAP-based publish step with automatic rollback |
| 07 | Orchestration & Operations | It's 3 a.m. and the pipeline is red. | DAGs from first principles (build a mini-orchestrator), retries+idempotency, structured logging, observability pillars, runbooks, SLOs | Mini-orchestrator completed; alerting rule; incident runbook |
| 08 | Capstone | Can you do this unassisted? | Everything | A new pipeline (new domain) built to the course rubric, reviewable as a PR |

Estimated effort: 4–8 hours per module; 20–30 for the capstone. ~60–80 hours
total — deliberately in "serious commitment" territory, consistent with the
deep-understanding goal.

## 7. Repository layout

```
learning_methodologies/
├── README.md                 ← curriculum home: pitch, map, how to start
├── COURSE_DESIGN.md          ← this document
├── SETUP.md                  ← one canonical environment setup guide
├── Makefile                  ← setup / check / test entry points
├── pyproject.toml            ← course tooling package (datagen, checker)
├── .github/workflows/ci.yml  ← the repo's real CI (module 6 case study)
├── tools/
│   └── datagen/              ← seeded synthetic-data generator (+defect injection)
├── modules/
│   ├── 00-orientation/
│   │   ├── README.md         ← the lesson (objectives → story → concepts → walkthrough)
│   │   ├── project/          ← pipeline snapshot at module start
│   │   ├── exercises/        ← numbered exercises w/ starter code
│   │   ├── tests/            ← self-grading pytest suite for the exercises
│   │   └── solutions/        ← reference solutions (peek-last honor system)
│   ├── 01-version-control/   (same shape)
│   ├── ...
│   └── 08-capstone/
│       ├── README.md         ← spec + rubric
│       └── rubric.md
└── docs/
    ├── glossary.md           ← every term defined in BI-friendly language
    └── bibliography.md       ← research sources & further reading
```

Module README template (uniform across modules):
1. **Where we are** (narrative recap) → 2. **Learning objectives** →
3. **The failure** (demonstrate the disease) → 4. **Concepts** (the deep
part) → 5. **Guided walkthrough** → 6. **Exercises** → 7. **Self-check**
(`make check MODULE=NN`) → 8. **Going deeper** → 9. **Reflection questions**
→ 10. **Further reading**.

## 8. Assessment model

- **Per-module self-check:** `make check MODULE=NN` runs that module's pytest
  suite against the student's exercise work. Red → keep going; green → done.
  Tests are written to give *diagnostic* failure messages (teaching, not just
  judging).
- **Reflection questions:** un-graded, but answers are the real test of
  "deep understanding"; suggested answers live in solutions/.
- **Capstone rubric:** explicit checklist mirroring the seven methodology
  families; designed so a colleague (or the student a week later) can review
  the capstone as a PR.

## 9. Risks & mitigations

| Risk | Mitigation |
|---|---|
| Snapshot duplication drifts across modules | Pipeline kept intentionally small (~300 lines max); CI tests every snapshot |
| Student environments vary | Single SETUP.md, `make setup` bootstrap, CI proves a clean-machine path; Codespaces/devcontainer friendly |
| Depth reads as length | Rigid README template, failure-first openings, "Going deeper" fences keep the required path tight |
| Tool churn (2026's tools age) | Concepts carry the modules; tools are confined to walkthrough sections and a per-module "in the wild" mapping table |

## 10. Design review record (v1.0)

Self-review findings and resolutions before implementation:

1. **Finding:** original draft taught dbt as a required dependency in module 5.
   *Resolution:* dbt demoted to optional track; the expectations engine is
   built in course code instead — deeper understanding, lighter setup.
2. **Finding:** an "evolving single codebase" breaks students who join
   mid-course or get stuck. *Resolution:* per-module `project/` snapshots.
3. **Finding:** module 7 originally taught Airflow directly, contradicting
   the local-first and depth-first principles. *Resolution:* build a
   mini-orchestrator; map to real tools afterward.
4. **Finding:** no explicit place where the "code+data deploy together"
   thesis is stated. *Resolution:* made the course thesis in module 0 and
   the README; revisited at modules 4/5/6 openings.
5. **Finding:** exercises without objective completion criteria ("refactor
   this") frustrate self-learners. *Resolution:* every exercise gets a
   pytest suite; refactoring exercises use behavior-preservation tests.
