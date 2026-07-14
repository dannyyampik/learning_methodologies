# Module 02 — From Scripts to Software

> *"It's only 120 lines. How bad can it be?"* — everyone, before trying to change line 60

## Where we are

CoreCafé's pipeline is now in Git (Module 1): changes are tracked and
reviewable. But *reviewable* is doing heavy lifting — reviewing a change to
the monolith means re-simulating the whole script in your head, because
everything touches everything. This module is about **shape**: reorganizing
code so that it can be understood, changed, and — the payoff in Module 3 —
tested in pieces.

If you come from BI, you have written this monolith. Everyone has. The skill
here is not writing pretty code; it's knowing the three or four structural
moves that turn a working script into workable software *without changing
what it does*.

## Learning objectives

1. Restructure a pipeline along its natural seams — extract / transform /
   load — and articulate the deeper principle: **pure logic in the core,
   I/O at the edges**.
2. Move policy out of code: configuration, magic numbers, environment
   differences.
3. Explain what dependency management actually solves (the "works on my
   machine" mechanism) and use `pyproject.toml` + a lockfile + a virtualenv
   accordingly.
4. Use a linter/formatter (ruff) not as a style cop but as a bug detector —
   and prove it by letting it catch a real one.
5. Perform a **behavior-preserving refactor** and demonstrate, with tests,
   that behavior was preserved.

## The failure, first

Three changes the business asked for this quarter. Try to locate each in
`project/pipeline.py` and notice what goes wrong in your head:

1. *"VAT is changing from 17% to 18% in January."* — `1.17` appears twice.
   Are there others? Are you sure? Search-and-pray is not a change process.
2. *"Can we get a weekly email instead of running it manually?"* — To run
   this code at all you need the files in place, the warehouse writable, and
   the working directory correct. There is no piece you can call — only the
   whole ritual.
3. *"Finance says June 3rd looks low."* — The revenue calculation cannot be
   examined without loading actual files into an actual database. The logic
   is *welded to the plumbing*.

That third one is the deep problem, and its name is **coupling of logic and
I/O**. Fix that, and testing (Module 3), reuse, and debugging all become
possible. Leave it, and every improvement fights the same swamp.

## Concepts

### 1. Functional core, imperative shell

The architecture this course uses everywhere, worth stating as a rule:

> **Pure functions compute. A thin shell reads and writes.**

"Pure" means: output depends only on inputs — no file access, no database,
no clock, no `os.environ`, no `print`. The pipeline becomes:

```
             ┌────────────────────────────────────────────┐
   files ──▶ │ extract.py  →  transform.py  →  load.py    │ ──▶ warehouse
   (I/O)     │   (I/O)         (PURE)          (I/O)      │
             └───────────────── pipeline.py ───────────────┘
                          (the shell: wiring only)
```

Why this exact split earns its keep:

- **Testability.** Pure functions are testable with literal values — no
  fixtures, no database, microsecond-fast. Watch how small Module 3's tests
  are because of what you do here.
- **Debuggability.** "June 3rd looks low" becomes: feed June 3rd's rows to
  `clean_batch` in a REPL and *look*. No environment required.
- **Reasoning.** I/O code has to worry about missing files, locks,
  encodings. Logic code has to worry about business rules. A function that
  worries about both is worse at both.

The BI translation: this is the same instinct as separating a *view* (logic)
from the *tables it reads* (I/O) — you already believe in this; we're just
applying it to Python.

### 2. Config is not code

`1.17` hardcoded twice is three distinct sins: it's **unnamed** (is that
VAT? a margin? a fudge factor?), it's **duplicated** (they *will* drift
apart), and it's **compiled in** (changing policy requires a code deploy).

The cure is boring and absolute: constants get names, policy gets a
`Config` object, environment differences (paths, database targets) get
environment variables — with `Config` constructed **once, at the edge**, and
passed in. Code deep inside the pipeline never reads `os.environ`; it
receives values. That discipline (dependency injection, minus the
enterprise framework connotations) is what makes Module 6's dev/prod
environments a five-line change instead of a rewrite.

### 3. Dependencies: why `requirements.txt` alone keeps burning you

"Works on my machine" is not a mystery; it's an unpinned transitive
dependency. The machinery, once, properly:

- **`pyproject.toml`** declares what you need (`duckdb>=1.0`) — *intent*.
- **A lockfile** (`uv lock`, `pip-compile`) records what was actually
  installed, every package, exact versions — *fact*. CI and teammates
  install from the lockfile and get your exact reality.
- **A virtualenv per project** keeps projects from contaminating each other.

Data-specific footnote: your *database* is a dependency too. The DuckDB
file-format version, warehouse extensions, even the VAT rate above are all
"environment". The more of it you write down in versioned files, the more
Module 6's automation can do for you.

### 4. Linters: a reviewer that never sleeps

ruff runs hundreds of checks in milliseconds. Most findings are style; the
valuable ones are *bug classes*: unused variables (often a typo'd name),
mutable default arguments (state leaking between calls — you'll meet one in
the exercise), shadowed builtins, unreachable code. The point of
formatters (`ruff format`) is different: they end style debates by making
them moot. Nobody reviews indentation ever again.

Wire both into a pre-commit hook and CI (Module 6 does this for real), and
an entire category of review comments simply stops existing.

### 5. Refactoring means *proven* behavior preservation

A refactor that changes behavior is just a bug with confidence. The
professional move: characterize current behavior first, then restructure,
then re-verify. The exercise tests encode the monolith's behavior — including
its *questionable* choices, like admitting rows with no store_id. Resist the
itch to fix those now: **one PR, one intent** (you learned why in Module 1's
review exercise). The fixes come in Module 5, deliberately, with tests.

## Guided walkthrough

Study the *destination* of this refactor — the `corecafe` package in
[`../03-testing/project/`](../03-testing/project/). Read it in this order:

1. `corecafe/transform.py` — the functional core. Notice: importable and
   runnable with zero infrastructure.
2. `corecafe/config.py` — policy in one place; `load_config(env)` takes the
   environment as an argument.
3. `corecafe/extract.py`, `corecafe/load.py` — thin I/O edges. (`load.py`
   still contains the append bug! Known, documented, and scheduled for
   Module 4 — renovation is incremental.)
4. `corecafe/pipeline.py` — the shell. Wiring only; almost too boring to
   review, which is the compliment.

## Exercises

1. **The extraction** — implement
   [`exercises/m02_refactor.py`](exercises/m02_refactor.py): pull
   `compute_revenue`, `parse_sale`, `clean_batch`, and `load_config` out of
   the monolith as pure functions. The tests are strict about purity (they
   run your code where no files exist) and about behavior parity.
2. **The linter as bug-finder** — fix
   [`exercises/m02_tidy.py`](exercises/m02_tidy.py) until ruff is silent
   *and* the function stops lying on its second call. Read every ruff
   message before fixing it; the messages are the lesson.

```bash
make check MODULE=02
```

## Reflection questions

1. The monolith's author would say: "your version is five files instead of
   one — how is that simpler?" Give the honest answer, including what was
   genuinely lost.
2. Where should the list of *store opening dates* live: code, config, or a
   database table? What about the VAT rate history? Defend the difference.
3. Your team's SQL transformations live in a BI tool with no linter. What's
   the equivalent discipline for SQL? (You'll meet one answer in Module 5.)

(Suggested answers: [`solutions/reflections.md`](solutions/reflections.md).)

## Further reading

- [Functional Core, Imperative Shell — Gary Bernhardt (talk)](https://www.destroyallsoftware.com/screencasts/catalog/functional-core-imperative-shell)
- [The Twelve-Factor App — Config](https://12factor.net/config) — the classic statement of config-out-of-code.
- [ruff rules index](https://docs.astral.sh/ruff/rules/) — skim B (bugbear): it's a catalog of real Python bugs.

---

**Next:** [Module 03 — Testing Data Systems](../03-testing/README.md), where
the pure functions you just extracted pay for themselves.
