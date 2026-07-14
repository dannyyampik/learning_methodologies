"""Module 01, Exercise 2 — Git mental model & code review judgment.

Replace each ``...`` with your answer, then run:  make check MODULE=01

For questions Q5-Q7, first read ``exercises/review_me.diff`` — a pull
request you have been asked to review.
"""

# Q1. You edited pipeline.py, ran `git add pipeline.py`, then edited the file
# AGAIN before committing. What does the commit contain?
#   "first"  = the version at the time of `git add`
#   "second" = the version at the time of `git commit`
Q1_WHAT_GETS_COMMITTED = ...

# Q2. `git commit` succeeded but you immediately realize the message is wrong.
# Nothing is pushed yet. Which command rewrites the last commit's message?
# Answer with the exact two-word subcommand + flag, e.g. "commit --amend"
Q2_FIX_LAST_MESSAGE = ...

# Q3. A teammate pushed commits to `main` while you also committed to your
# local `main`. `git push` is rejected. Is your history now corrupted?
# (True / False)
Q3_HISTORY_IS_CORRUPTED = ...

# Q4. Your 400 MB of daily CSV exports: should they be committed to Git?
# Answer with exactly one of: "yes", "no", "only_zipped"
Q4_COMMIT_THE_DATA = ...

# --- Code review: read exercises/review_me.diff first ---------------------

# Q5. One hunk in that diff must block the merge no matter how urgent the
# change is. Which hunk number? (int, 1-4 as labeled in the file)
Q5_BLOCKING_HUNK = ...

# Q6. One hunk silently changes business logic while claiming to be a
# refactor. Which hunk number? (int)
Q6_SNEAKY_LOGIC_CHANGE = ...

# Q7. Should you approve this PR if the author fixes only the blocking hunk?
# Answer with exactly one of: "approve", "request_changes"
Q7_VERDICT = ...
