"""Reference solution for the Module 01 git kata.

Solves the kata programmatically — used by CI to prove the kata is solvable,
and by you (after a real attempt!) to see one correct command sequence.

    python modules/01-version-control/solutions/m01_solve_kata.py [path]
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    )
    return result.stdout


def solve(repo: Path) -> None:
    # ------------------------------------------------------------------
    # Task A — stop versioning secrets and data.
    # `git rm --cached` removes from tracking but keeps the file on disk.
    # NOTE: in a real repo that was ever pushed, the secret is still in
    # HISTORY — you must also rotate the credential. Untracking ≠ erasing.
    # ------------------------------------------------------------------
    _git(repo, "rm", "-q", "--cached", "secrets.txt")
    _git(repo, "rm", "-q", "-r", "--cached", "exports")
    (repo / ".gitignore").write_text("secrets.txt\nexports/\n")
    _git(repo, "add", ".gitignore")
    _git(
        repo,
        "commit",
        "-qm",
        "Stop tracking secrets and data exports\n\n"
        "Code belongs in Git; credentials and generated data do not.\n"
        "The API key must also be rotated - it remains in history.",
    )

    # ------------------------------------------------------------------
    # Task B — fix the README typo on a branch, merge it back.
    # ------------------------------------------------------------------
    _git(repo, "checkout", "-qb", "fix/readme-typo")
    readme = repo / "README.md"
    readme.write_text(readme.read_text().replace("pipline", "pipeline"))
    _git(repo, "commit", "-qam", "Fix 'pipline' typo in README title")
    _git(repo, "checkout", "-q", "main")
    _git(repo, "merge", "-q", "--no-edit", "fix/readme-typo")

    # ------------------------------------------------------------------
    # Task C — merge the conflicting feature branch, keep BOTH intents.
    # ------------------------------------------------------------------
    result = subprocess.run(
        ["git", "-C", str(repo), "merge", "--no-edit", "feature/add-city-column"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0, "expected a merge conflict"

    pipeline = repo / "pipeline.py"
    text = pipeline.read_text()
    resolved = []
    in_conflict = False
    for line in text.splitlines():
        if line.startswith("<<<<<<<"):
            in_conflict = True
            resolved.append('GROUP_COLS = ["day", "store_id", "store_name", "city"]')
        elif line.startswith(">>>>>>>"):
            in_conflict = False
        elif not in_conflict:
            resolved.append(line)
    pipeline.write_text("\n".join(resolved) + "\n")
    _git(repo, "add", "pipeline.py")
    _git(repo, "commit", "-q", "--no-edit")


if __name__ == "__main__":
    target = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else (Path(__file__).resolve().parents[1] / "exercises" / "kata")
    )
    solve(target)
    print(f"Kata solved at {target}")
