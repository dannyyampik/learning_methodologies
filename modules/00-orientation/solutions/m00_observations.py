"""Module 00, Exercise 2 — reference answers with explanations."""

# Every run re-INSERTs every CSV file into `sales` without deleting what a
# previous run loaded (`CREATE TABLE IF NOT EXISTS` + append-only INSERTs),
# so a second run exactly doubles the table.
SALES_MULTIPLIER_AFTER_SECOND_RUN = 2

# `daily_revenue` is rebuilt from `sales` on every run, so it faithfully
# aggregates the doubled facts: finance now sees 2x revenue. Derived tables
# inherit the corruption of their inputs.
FINANCE_DASHBOARD_IS_ALSO_WRONG = True

# Idempotent = running it N times leaves the same state as running it once.
# This pipeline fails that test in the most literal way possible.
PIPELINE_IS_IDEMPOTENT = False

# Extraction reads the same files, transformation computes the same revenue —
# it is the LOAD step that appends instead of replacing or upserting.
STAGE_WHERE_THE_BUG_LIVES = "load"

# `stores` is created with CREATE OR REPLACE, which drops and recreates the
# table each run — accidentally idempotent. The inconsistency between the two
# loading strategies in one file is itself a code smell (Module 2).
WHY_STORES_SURVIVES = "OR REPLACE"
