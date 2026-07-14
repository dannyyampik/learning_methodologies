"""Module 01, Exercise 2 — reference answers with explanations."""

# Git commits what is in the STAGING AREA (index), not what is in your
# working directory. `git add` took a snapshot; the second edit stayed
# unstaged. This staging model is why `git status` shows a file as both
# "staged" and "modified" at once — two different snapshots of it exist.
Q1_WHAT_GETS_COMMITTED = "first"

# `git commit --amend` replaces the last commit (new hash!). Safe while the
# commit is local; after pushing, amending rewrites shared history — that's
# when you stop amending and add a follow-up commit instead.
Q2_FIX_LAST_MESSAGE = "commit --amend"

# Nothing is corrupted. Git is a graph of immutable snapshots; the histories
# have merely diverged, and a rejected push is Git *protecting* the remote.
# You reconcile with pull/rebase or a merge. Panic-deleting the repo folder
# and re-cloning — the classic move — throws away a perfectly healthy graph.
Q3_HISTORY_IS_CORRUPTED = False

# Version the code that PRODUCES data, not the data. Data is large, changes
# constantly, diffs meaninglessly, and may contain PII — Git history is
# forever, which turns committed PII into a compliance incident you cannot
# delete. (Data VERSIONING is a real practice — lakeFS, Iceberg snapshots —
# but it's a different tool for a different job.)
Q4_COMMIT_THE_DATA = "no"

# Hunk 2 commits a live credential. Once pushed, that password is in history
# permanently — rotating the secret AND rewriting history is the only cure.
# "temp, will move to env later" is how credentials die of old age in repos.
Q5_BLOCKING_HUNK = 2

# Hunk 4 quietly adds `WHERE payment_method != 'cash'` inside a "cleanup"
# PR: cash sales silently vanish from the top-products report. Nothing about
# the code is wrong as code — it's a business-meaning change smuggled past
# review by the PR title. This is the single most data-specific review skill:
# ask "which ROWS does this change affect?", not just "is the code clean?"
Q6_SNEAKY_LOGIC_CHANGE = 4

# Even with the secret removed: hunk 1 changes revenue figures (rounding
# per-line vs at aggregation compounds), and hunk 4 changes report meaning —
# both need justification, tests, or removal. Also note the PR bundles four
# unrelated changes; asking for a split IS a valid review outcome.
Q7_VERDICT = "request_changes"
