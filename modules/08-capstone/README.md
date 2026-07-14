# Module 08 — Capstone: Prove It

## The brief

No more CoreCafé, no more starter code, no more tests written for you. You
will build a small data platform for a **new domain**, alone, to the
standard this course has established — and package it so a professional
can review it as a pull request.

This is deliberately the hardest step. Every module so far handed you the
failure first and the shape of the solution second. The capstone hands you
neither. The measure of *deep understanding* is what you reach for when
nothing is scaffolded.

## The scenario

Pick one (or invent an equivalent — same shape, your interests):

- **CityWheels** — a bike-share operator. Stations (dimension), bikes
  (dimension), and daily trip files (facts): trip id, bike, start/end
  station, start/end time, user type. Marts: daily usage by station,
  bike utilization.
- **PacketPost** — a parcel courier. Depots, couriers, daily scan-event
  files (parcel id, scan type, depot, timestamp). Marts: daily volumes by
  depot, delivery-time distribution.
- **StreamFlix-ish** — a small streaming service. Titles, plans, daily
  view-event files. Marts: daily watch-time by title, plan engagement.

Whatever you pick, the source data must include a daily-partitioned fact
feed and at least two dimensions — the shape all the course's machinery
assumes.

## Requirements

Your repository must demonstrate every methodology family. Concretely:

1. **A seeded synthetic data generator** for your domain (Module 0's
   datagen is your reference), including at least three injectable defect
   types. No real/downloaded data — you must be able to poison your own
   inputs on demand.
2. **Version control done properly** (Module 1): meaningful history, work
   on branches merged via PRs (yes, solo), no data or secrets ever
   committed, a `.gitignore` that proves you thought about it.
3. **Functional core, imperative shell** (Module 2): pure transform layer,
   I/O at the edges, config from the environment via one dataclass, ruff
   clean, `pyproject.toml` + lockfile.
4. **A test pyramid** (Module 3): unit tests on every transform (write at
   least one deliberate mutant of your own logic and show your suite kills
   it — include it, marked, in the repo), one integration test running the
   whole pipeline against a temp warehouse with an *independent*
   reconciliation.
5. **Idempotent partitioned loading** (Module 4): partition overwrite in a
   transaction, a working backfill command, and a test that re-delivers a
   corrected file.
6. **A quality gate and a contract** (Module 5): at least five checks with
   severities that reflect actual policy (justify each in a comment), a
   schema contract, drift detection.
7. **CI + WAP** (Module 6): GitHub Actions running lint + tests on PR;
   marts published via write-audit-publish with at least one
   reconciliation audit.
8. **Operability** (Module 7): structured logs, freshness + volume
   monitors, exit codes that mean something, and a runbook for your most
   likely failure mode.
9. **A README** that a stranger could operate the pipeline from — setup,
   run, backfill, "what to do when it's red".

**Effort calibration:** 20–30 hours. Resist gold-plating the domain logic
— the pipeline is the product, not the analytics.

## Deliverable & review

Work in a fresh public repository. Open your final state as a single PR
from a `capstone-review` branch against your own initial scaffold commit,
so the whole system is reviewable as one diff with your history behind it.

Then get it reviewed against [`rubric.md`](rubric.md) — by a colleague, a
study partner, or a community (the course's spiritual ancestors at
DataTalksClub run peer reviews exactly like this). No reviewer available?
Wait one week, re-read your own PR cold, and fill in the rubric honestly.
A week-old you is a surprisingly effective stranger.

## Exit interview (write it down)

Three questions, one paragraph each, in your capstone README:

1. Which practice did you *almost* skip, and what convinced you not to
   (or to)?
2. Where did you deviate from the course's way, and why is your way right
   for your context?
3. What would break first if this ran daily for a year — and what did you
   do about it?

There are no correct answers. There are, by now, *your* answers — which is
the point of the course.
