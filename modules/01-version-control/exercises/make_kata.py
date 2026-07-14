"""Build the Module 01 git kata — a small repository in a realistically bad state.

Run from the repo root:

    python modules/01-version-control/exercises/make_kata.py

This creates ``modules/01-version-control/exercises/kata/`` — a standalone
git repository (it is .gitignored, so it won't nest into the course repo).
Your tasks are in the module README. Re-running this script resets the kata.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

KATA_DIR = Path(__file__).resolve().parent / "kata"

PIPELINE_V1 = '''\
"""Daily revenue rollup for the CoreCafé dashboard."""

GROUP_COLS = ["day", "store_id"]

QUERY = f"""
    SELECT {", ".join(GROUP_COLS)}, SUM(revenue) AS revenue
    FROM sales
    GROUP BY {", ".join(GROUP_COLS)}
"""
'''

PIPELINE_MAIN_EDIT = PIPELINE_V1.replace(
    'GROUP_COLS = ["day", "store_id"]',
    'GROUP_COLS = ["day", "store_id", "store_name"]',
)

PIPELINE_FEATURE_EDIT = PIPELINE_V1.replace(
    'GROUP_COLS = ["day", "store_id"]',
    'GROUP_COLS = ["day", "store_id", "city"]',
)

README = "# CoreCafé pipline\n\nRuns the daily revenue rollup.\n"

SECRETS = "WAREHOUSE_API_KEY=sk-live-9f8e7d6c5b4a\n"

BIG_CSV = "sale_id,revenue\n" + "\n".join(f"{i},{i * 3.5:.2f}" for i in range(200)) + "\n"


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    )
    return result.stdout


def build(target: Path = KATA_DIR) -> Path:
    """Create (or reset) the kata repository and return its path."""
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)

    subprocess.run(["git", "init", "-q", "-b", "main", str(target)], check=True)
    # Local identity so commits work even without global git config.
    _git(target, "config", "user.name", "Kata Student")
    _git(target, "config", "user.email", "student@example.com")

    # Commit 1 — Dave's original sin: code, secrets, and data all tracked.
    (target / "pipeline.py").write_text(PIPELINE_V1)
    (target / "README.md").write_text(README)
    (target / "secrets.txt").write_text(SECRETS)
    (target / "exports").mkdir()
    (target / "exports" / "big_data.csv").write_text(BIG_CSV)
    _git(target, "add", "-A")
    _git(target, "commit", "-q", "-m", "initial commit")

    # A feature branch that will conflict with main.
    _git(target, "checkout", "-q", "-b", "feature/add-city-column")
    (target / "pipeline.py").write_text(PIPELINE_FEATURE_EDIT)
    _git(target, "commit", "-qam", "Add city to revenue rollup grouping")

    # Meanwhile, main moved: someone grouped by store_name instead.
    _git(target, "checkout", "-q", "main")
    (target / "pipeline.py").write_text(PIPELINE_MAIN_EDIT)
    _git(target, "commit", "-qam", "Add store_name to revenue rollup grouping")

    return target


if __name__ == "__main__":
    path = build()
    print(f"Kata repository ready at: {path}")
    print("Open the module README and work through Tasks A-C inside that directory.")
    sys.exit(0)
