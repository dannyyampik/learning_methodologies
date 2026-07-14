"""Module 06, Exercise 2 — reference answers with explanations."""

# The workflow declares `on: pull_request` plus `push: branches: [main]`.
# PRs get checked before merge (the gate); main gets checked after merge
# (catches bad merges and direct pushes). Running on every push to every
# branch would also be defensible — it trades CI minutes for earlier
# feedback on unopened work.
Q1_CI_TRIGGERS = "pr_and_main"

# Cheap checks first. Lint finishes in seconds; the test job runs every
# module's suite. `needs:` makes the pipeline spend expensive minutes only
# on code that already passed the cheap gate. (The opposite choice —
# running them in parallel for faster total feedback — is also legitimate;
# the point is that it IS a choice, with a stated trade-off.)
Q2_NEEDS_LINT = "fail_fast"

# If CI ran its own hand-rolled commands, local `make test` and CI's checks
# would drift apart until "passes locally, fails in CI" (or worse, the
# reverse) became normal. One entry point = one truth. This is also why the
# Makefile exists at all: it's the repo's executable interface.
Q3_MAKE_IN_CI = "one_truth"

# Ephemeral, always, as the default: fresh per run means deterministic
# (Module 4!), parallel-safe, credential-free, and PII-free. Prod replicas
# leak data into CI logs and make tests flaky as prod drifts;
# shared staging serializes every PR through one mutable bottleneck.
# DuckDB makes ephemeral nearly free; cloud warehouses offer the same via
# per-run schemas/databases (dbt's "custom schema per PR" pattern).
Q4_CI_WAREHOUSE = "ephemeral"

# Same code, same artifact, different Config — which is exactly why
# Module 2 exiled config from code. Per-environment branches guarantee
# that prod eventually runs code nobody ever tested together.
Q5_ENV_DIFFERENCE = "config"

# Code rollback stops NEW damage; it does nothing to damage already
# written. The three bad days persist until reprocessed — which is why
# Module 4's backfill is the second half of every data rollback story:
# revert the code, then re-run the affected partitions under the good
# logic. Teams that only rehearse code rollback discover this during an
# incident.
Q6_ROLLBACK_REALITY = "nothing"
