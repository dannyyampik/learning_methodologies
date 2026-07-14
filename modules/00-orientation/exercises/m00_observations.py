"""Module 00, Exercise 2 — Observe the patient.

Run the inherited pipeline (see the module README for exact steps), study its
behavior, and record what you observed by replacing each ``...`` below with
your answer. Then run:

    make check MODULE=00

The tests will run the pipeline themselves and compare reality against your
answers. Guessing is possible but pointless — the goal is that you *watch*
the failure happen with your own eyes.
"""

# After running the pipeline ONCE on a fresh database, and then running it a
# SECOND time (changing nothing), the row count of the `sales` table is
# multiplied by what factor?  (int)
SALES_MULTIPLIER_AFTER_SECOND_RUN = ...

# Is the `daily_revenue` table (the one finance reads) also wrong after the
# second run?  (True / False)
FINANCE_DASHBOARD_IS_ALSO_WRONG = ...

# A pipeline you can safely run twice with the same result is called
# *idempotent*. Is this pipeline idempotent?  (True / False)
PIPELINE_IS_IDEMPOTENT = ...

# The bug lives in ONE of the three classic pipeline stages. Which one?
# Answer with exactly one of: "extract", "transform", "load"
STAGE_WHERE_THE_BUG_LIVES = ...

# The `stores` table does NOT double on a second run. Which SQL keyword pair
# in the script protects it? Answer with the exact two words, uppercase,
# e.g. "CREATE TABLE"
WHY_STORES_SURVIVES = ...
