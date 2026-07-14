# Software Engineering Methodologies for Data Engineers

A hands-on course for data professionals who build pipelines but didn't
come up through software engineering — BI developers, analysts, DBAs,
DevOps folks who drifted data-ward. You'll inherit a realistic, messy,
*working* pipeline and renovate it, module by module, into
production-grade software — learning not just each practice, but the
failure mode it exists to prevent.

**Everything runs locally and offline.** No cloud accounts, no downloads,
no cost: Python + DuckDB + pytest + Git, and a synthetic data generator
with injectable defects. Expect ~60–80 hours for the full course including
the capstone.

## The course thesis

> **In data engineering, the deployable unit is code *and* the data it
> produces.** Roll back a web app and it's healed; roll back a pipeline
> and yesterday's corrupted tables are still corrupted. The blast radius
> of a data bug is `bad code × every run × every consumer × time until
> noticed` — and every practice in this course shrinks one of those
> factors.

## The story

You're the new data person at **CoreCafé**, a five-store coffee chain.
The entire analytics platform is one script, written by Dave, who left.
Finance's dashboard runs on it. In Module 0 you break it (by *running it
twice*). Over eight modules you renovate it — each module applying one
methodology family and each `project/` folder containing the pipeline as
it stands at that point, so every module is self-contained:

| Module | Title | You learn to... | The pipeline becomes... |
|---|---|---|---|
| [00](modules/00-orientation/) | Orientation | diagnose *why* pipelines rot; feel a silent failure | understood (v0, the patient) |
| [01](modules/01-version-control/) | Version Control & Collaboration | think in Git's graph; review data PRs for row-level meaning | tracked & reviewable |
| [02](modules/02-code-design/) | From Scripts to Software | separate pure logic from I/O; exile config; lint as bug-finder | testable (v1) |
| [03](modules/03-testing/) | Testing Data Systems | the data testing pyramid; beliefs-first tests; hunt live mutants | tested |
| [04](modules/04-functional-data-engineering/) | Functional Data Engineering | idempotency, partitions as unit of work, fearless backfills | rerunnable (v2) |
| [05](modules/05-data-quality/) | Data Quality & Contracts | build the engine inside dbt tests/Great Expectations; contracts | gated (v3) |
| [06](modules/06-ci-cd/) | CI/CD & Environments | unskippable checks; env-by-config; Write-Audit-Publish | deployable |
| [07](modules/07-orchestration-operations/) | Orchestration & Operations | build a mini-orchestrator; monitors; runbooks; SLOs | operable (v4) |
| [08](modules/08-capstone/) | Capstone | everything, unassisted, in a new domain | *yours* |

## How the course works

Every module follows the same arc — **the failure first**, then the
concept, then the practice, then tools — and ends with exercises graded by
tests you run yourself:

```bash
make check MODULE=03      # runs that module's tests against YOUR exercise code
make solutions MODULE=03  # same tests against the reference solutions
```

Exercise files start out raising `NotImplementedError`; green means done.
Solutions (with explanations — they're half the teaching) live in each
module's `solutions/`, honor-system-locked until you've genuinely tried.
Reflection questions close each module; they're ungraded and they're where
the *deep* understanding lives — suggested answers included.

The repo itself practices what it teaches: the [CI workflow](.github/workflows/ci.yml)
that checks every PR is Module 6's case study, the test suite is a Module 3
worked example, and the data generator is Module 2-grade code you're
encouraged to read.

## Getting started

1. Work through [SETUP.md](SETUP.md) (~15 minutes: fork, clone,
   `make setup`, `make data`).
2. Start at [Module 00](modules/00-orientation/README.md). Do the modules
   in order — each builds on the last's renovation.
3. From Module 1 onward: do all work on branches in your fork, merged via
   PRs. Solo PRs feel silly for about two weeks, then they catch your
   first bug.

## Repository layout

```
modules/NN-name/
├── README.md      the lesson (objectives → failure → concepts → walkthrough)
├── project/       the CoreCafé pipeline as it stands at this module's start
├── exercises/     your work: starter files with failing tests
├── tests/         the self-grading suite (make check MODULE=NN)
└── solutions/     reference solutions + reflection answers
tools/datagen/     seeded synthetic-data generator (defects on demand)
docs/              glossary (BI-friendly) & research bibliography
COURSE_DESIGN.md   why the course is built this way (research, exemplars, pedagogy)
```

## Provenance

The curriculum distills how modern data teams actually apply software
engineering — sources in [docs/bibliography.md](docs/bibliography.md);
design rationale and the exemplar courses studied (DataTalksClub's
[Data Engineering Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp),
MIT's [Missing Semester](https://missing.csail.mit.edu/)) in
[COURSE_DESIGN.md](COURSE_DESIGN.md).
