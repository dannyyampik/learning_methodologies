"""Module 06, Exercise 2 — CI/CD and environments for data.

Questions 1-3 are about THIS repository's real CI: read
.github/workflows/ci.yml (all 35 lines of it) before answering.

Replace each ``...`` with your answer, then run:  make check MODULE=06
"""

# Q1. Which events trigger this repo's CI? Answer with exactly one of:
#   "every_push"          - any push to any branch
#   "pr_and_main"         - pull requests, plus pushes to main
#   "nightly"             - a schedule
Q1_CI_TRIGGERS = ...

# Q2. The `test` job declares `needs: lint`. What is the reasoning?
#   "dependency"   - tests import code that lint generates
#   "fail_fast"    - don't spend expensive minutes when a cheap check already failed
#   "ordering_bug" - GitHub Actions requires jobs to be sequential
Q2_NEEDS_LINT = ...

# Q3. CI runs `make lint` and `make test` — the same commands you run
# locally — rather than embedding its own commands in the YAML. Why does
# that matter?
#   "aesthetics"       - it just looks cleaner
#   "one_truth"        - local and CI can never silently check different things
#   "speed"            - make is faster than bash
Q3_MAKE_IN_CI = ...

# Q4. Your pipeline's CI needs a warehouse to run integration tests
# against. The RIGHT default is:
#   "prod_replica"     - a read replica of production
#   "ephemeral"        - a disposable database created fresh per CI run
#   "shared_staging"   - the team's long-lived staging warehouse
Q4_CI_WAREHOUSE = ...

# Q5. Dev, staging, and prod runs of a well-factored pipeline differ ONLY in:
#   "code_branch"  - each environment runs its own branch
#   "config"       - same artifact, different configuration values
#   "schedule"     - they differ only in when they run
Q5_ENV_DIFFERENCE = ...

# Q6. A bad deploy shipped wrong logic; it ran for three days before being
# noticed. Code is now rolled back. What does rolling back the CODE do to
# the three days of wrong DATA it produced?
#   "fixes_it"     - the data self-corrects on the next run
#   "nothing"      - the bad data persists until explicitly reprocessed
#   "deletes_it"   - the rollback removes the affected partitions
Q6_ROLLBACK_REALITY = ...
