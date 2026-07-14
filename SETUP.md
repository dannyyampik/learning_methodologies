# Environment Setup

Everything in this course runs **locally and offline** — no cloud accounts,
no credit cards, no downloads beyond Python packages. Expect setup to take
10–20 minutes.

## Prerequisites

| Requirement | Check with | Notes |
|---|---|---|
| Python 3.11+ | `python3 --version` | 3.11, 3.12, or 3.13 all work |
| Git 2.30+ | `git --version` | Module 1 uses branches and interactive staging |
| GNU Make | `make --version` | Preinstalled on macOS/Linux; on Windows use WSL2 |
| A GitHub account | — | Needed from Module 1 (pull requests) and Module 6 (CI) |

**Windows users:** use [WSL2](https://learn.microsoft.com/windows/wsl/install).
The course assumes a Unix-like shell throughout; WSL2 gives you exactly that.

## Install

```bash
# 1. Fork this repository on GitHub (you will open PRs against your fork),
#    then clone YOUR fork:
git clone https://github.com/<your-username>/learning_methodologies.git
cd learning_methodologies

# 2. Create a virtualenv and install the course tooling:
make setup
source .venv/bin/activate

# 3. Generate the synthetic source data used by every module:
make data

# 4. Verify everything works:
make solutions MODULE=00
```

If step 4 prints a green pass line, you are ready. If not, read the failure
message carefully — diagnosing environment problems from error output is,
genuinely, lesson zero of this course.

<details>
<summary>Prefer <code>uv</code>? (faster, optional)</summary>

```bash
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
```
</details>

## What just got installed?

- **duckdb** — an in-process analytical database. It gives you real
  warehouse behavior (schemas, SQL, constraints) inside a single local file.
- **pytest** — the test runner you will live in from Module 3 onward.
- **ruff** — linter + formatter, introduced in Module 2.
- **datagen** (this repo's `tools/datagen`) — generates the CoreCafé
  synthetic source data, including deliberately defective batches when a
  module calls for them.

## Two commands you'll use constantly

```bash
make check MODULE=03      # run a module's tests against YOUR exercise code
make solutions MODULE=03  # run the same tests against the reference solutions
```

Your exercise files start out failing (they raise `NotImplementedError`).
Green means done. Only peek at `solutions/` after a real attempt — the
struggle is where the learning happens.

## Troubleshooting

- **`make: command not found`** → install build tools
  (`xcode-select --install` on macOS, `sudo apt install build-essential` on
  Debian/Ubuntu/WSL).
- **`ModuleNotFoundError: datagen`** → your virtualenv isn't active
  (`source .venv/bin/activate`) or `make setup` didn't finish.
- **Locked DuckDB file** (`Could not set lock`) → another process (a stray
  Python REPL, a DB viewer) has the `.duckdb` file open. Close it. DuckDB
  allows one writer at a time — this becomes a *feature* for reasoning about
  pipelines in Module 4.
