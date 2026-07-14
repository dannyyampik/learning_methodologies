# Module 01 — Version Control & Collaboration

> *"The pipeline lives in a folder on the BI server called `pipeline_FINAL_v3_REAL`."*

## Where we are

You diagnosed the CoreCafé monolith in Module 00. Before changing a single
line of it, you need the ability to change code **safely**: to try things on
a copy, to see exactly what changed, to undo, and to let a colleague catch
your mistakes before production does. That ability is version control — not
as three memorized commands, but as a mental model.

This is the right first renovation because every later practice stands on
it: code review needs branches, CI (Module 6) needs commits to react to,
rollback needs history.

## Learning objectives

1. Explain Git's actual model — an immutable graph of snapshots, plus the
   staging area — and use it to predict what commands do instead of
   memorizing them.
2. Work the **branch → commit → merge** cycle, including resolving a real
   merge conflict without losing either side's intent.
3. Decide what belongs in a data team's repository — and why data, secrets,
   and notebook output do not.
4. Review a pull request the way senior data engineers do: hunting for
   *row-level meaning changes*, not just style.

## The failure, first

Dave's world, which may look familiar from BI life:

- The "versions" were `pipeline_old.py`, `pipeline_old2.py`,
  `pipeline_FINAL.py`. Which one runs in production? (The one *not* named
  FINAL, obviously.)
- The one time someone edited SQL directly in the BI tool, the only record
  of the previous logic was a screenshot in a Slack thread.
- When the doubled-revenue incident from Module 00 happened, question one
  was *"what changed recently?"* — and there was no way to answer it.

Version control's superpower is exactly that: **it converts "what changed?"
from archaeology into a query.**

## Concepts

### 1. Git's mental model (learn this, forget the cheat sheets)

Three ideas explain ~90% of Git behavior:

**Commits are immutable snapshots, not diffs.** Every commit is a complete
picture of the whole project plus a pointer to its parent(s). Git shows you
diffs by *computing* them between snapshots. Consequence: nothing you have
committed is ever lost by a merge, a rebase, or a bad pull — the snapshot is
still in the graph. Most Git panic is unwarranted.

**History is a DAG** (a directed acyclic graph — the same structure your
pipelines form, which is not a coincidence; you'll build one in Module 7).
A *branch* is not a copy of anything: it is a 41-byte movable pointer to a
commit. That's why branching is instant and free, and why the workflow
"branch per change" costs nothing.

**The staging area sits between your files and history.** `git add` copies a
file's *current state* into the index; `git commit` snapshots the index. This
lets you commit a coherent subset of a messy working directory (`git add -p`
is the power tool). It's also the answer to the eternal "I edited after
adding — what gets committed?" (You'll answer that in the quiz.)

With the model in place, commands become sentences: `git checkout -b fix/x`
= "new pointer here, move me onto it." `git merge a` = "make a commit with
two parents." A rejected push = "the remote pointer moved since you last
looked" — divergence, not damage.

### 2. What goes in the repository? (the data team's special question)

Everything needed to **rebuild** the system; nothing the system **produces**.

| Version it | Never version it | Why |
|---|---|---|
| Pipeline code, SQL | The warehouse file, CSV exports | Data is output — huge, always changing, meaningless diffs |
| Config *structure* (`config.py`, `.env.example`) | Credentials, `.env` | History is forever; a pushed secret must be rotated, not just deleted |
| Schema definitions, migrations | Query *results* | Recipe, not cake |
| Tests + tiny fixture data (Module 3) | Production data samples | Fixtures are code-sized and PII-free by construction |
| `.gitignore` itself | Notebook output cells | Re-runnable ≠ reviewable; strip outputs before committing |

The tiny-fixture exception matters: a 20-row hand-crafted CSV that a test
depends on is *part of the code*. The 400 MB daily export is not.

> ⚠️ **Going deeper — versioning the data itself.** "Don't put data in Git"
> doesn't mean data versioning isn't real: lakeFS applies Git semantics to
> object storage, and table formats (Iceberg, Delta) keep snapshots you can
> time-travel to. Same idea, different machinery — because data's size and
> change-rate profile needs different machinery.

### 3. Branching strategies: pick boring

- **Trunk-based development** (recommended, and what this course uses):
  short-lived branches off `main`, merged within a day or two via PR. Works
  because pipelines are usually small-team, continuous-change codebases.
- **GitFlow** (develop/release/hotfix branches): built for versioned,
  released *products*. For pipelines it mostly adds ceremony — but you'll
  meet it in enterprises; recognize it rather than fight it.
- The actual rule: **branch lifetime is the metric that matters.** A branch
  alive for three weeks is a merge conflict with a countdown timer. Small
  PRs, merged fast, beat any named strategy.

### 4. Code review for data work

Review is the highest-leverage quality practice in existence — cheaper than
tests to start, and it transfers knowledge, which tests never do. But data
PRs need a review lens that generic checklists miss:

1. **Which rows does this change affect?** The deadliest data bugs are
   filters and join conditions: an innocent `WHERE` clause is a business
   decision wearing a code costume. (The kata's review exercise makes this
   concrete.)
2. **Is this change backfill-safe?** If the logic changes, do historical
   numbers need recomputing? Who decides? (Vocabulary for this arrives in
   Module 4.)
3. **Does the join change cardinality?** A join that can fan out 1→N turns
   SUM() into fiction two models downstream.
4. **Are magic values explained?** `* 1.17` needs a name and a home
   (Module 2).
5. Only *then* the universal stuff: naming, tests, dead code, unrelated
   changes bundled in.

Review etiquette compresses to: authors — small PRs, self-review first,
explain *why* in the description; reviewers — comment on the code not the
person, distinguish "blocking" from "nit", and approve when it's *better*,
not *perfect*.

## Guided walkthrough

Build your practice repo (a sandbox — break it freely; the builder resets it):

```bash
python modules/01-version-control/exercises/make_kata.py
cd modules/01-version-control/exercises/kata
git log --oneline --graph --all   # meet the DAG you'll be working in
git status                        # meet the crime scene
```

You inherit: a tracked `secrets.txt` with a live API key, tracked data
exports, a typo'd README, and a feature branch (`feature/add-city-column`)
that conflicts with `main`. In other words: Tuesday.

**Task A — Evict the non-code.** Untrack `secrets.txt` and `exports/`
*without deleting them from disk* (find the flag), add a `.gitignore` that
keeps them out forever, and commit it. Then consider — with feeling — why
untracking is not enough if this repo was ever pushed. (The reference
solution's commit message says it.)

**Task B — The branch cycle.** On a branch named exactly `fix/readme-typo`,
fix the README typo, commit with a message that would make sense to a
stranger in a year, and merge back to `main`.

**Task C — The conflict.** Merge `feature/add-city-column` into `main`. It
will conflict — on purpose. Open the file, read both sides, and understand
what each author *meant* before touching anything. The correct resolution
keeps both intents. Commit the merge.

Stuck on C? A conflict looks scarier than it is:

```
<<<<<<< HEAD
GROUP_COLS = ["day", "store_id", "store_name"]      ← what main meant
=======
GROUP_COLS = ["day", "store_id", "city"]            ← what the branch meant
>>>>>>> feature/add-city-column
```

Your job is to write the line that *both* authors would endorse, delete all
three marker lines, `git add`, and commit.

## Exercises

1. **The kata** (Tasks A–C above) — graded by inspecting your actual repo state.
2. **Concepts & review quiz** — read `exercises/review_me.diff` as if a
   teammate opened that PR, then answer
   [`exercises/m01_git_concepts.py`](exercises/m01_git_concepts.py).

```bash
make check MODULE=01
```

3. **Ungraded but real:** from now on, do *all* course work on branches in
   your fork, merged via PRs — even solo. Solo PRs sound absurd until you
   read your own diff and catch your own bug, which will happen by Module 3.

## Reflection questions

1. Your team's BI tool holds 200 reports whose SQL lives only inside the
   tool. What's your migration path to version control — and what do you do
   about the reports *while* they're unmigrated?
2. A reviewer's only comment on your PR is "LGTM 👍" twelve seconds after
   you opened it. What did the review cost the team? What would you change?
3. Why does `git blame` have the wrong name?

(Suggested answers: [`solutions/reflections.md`](solutions/reflections.md).)

## Further reading

- [The Missing Semester — Version Control](https://missing.csail.mit.edu/2020/version-control/) — teaches Git bottom-up from the object model; the single best hour you can spend on Git.
- [Trunk-Based Development](https://trunkbaseddevelopment.com/)
- [How to write a commit message — cbeams](https://cbea.ms/git-commit/)

---

**Next:** [Module 02 — From Scripts to Software](../02-code-design/README.md):
now that changes are trackable and reviewable, we make the monolith *worth*
reviewing.
