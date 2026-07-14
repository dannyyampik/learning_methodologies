"""Self-check for Module 01: the git kata and the concepts quiz."""

import subprocess

import pytest


def _git(repo, *args):
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    return result


def _answered(value, name):
    if value is Ellipsis:
        pytest.fail(f"You haven't answered {name} yet — replace the ... in the exercise file.")
    return value


# --------------------------------------------------------------------------
# Task A — secrets and data out of version control
# --------------------------------------------------------------------------


def test_secrets_and_data_untracked(kata_repo):
    tracked = _git(kata_repo, "ls-files").stdout.splitlines()
    assert "secrets.txt" not in tracked, (
        "secrets.txt is still tracked. `git rm --cached secrets.txt` untracks it "
        "without deleting the file from disk."
    )
    assert not any(f.startswith("exports/") for f in tracked), (
        "The exports/ data files are still tracked. Version the code that produces "
        "data — not the data."
    )
    assert (kata_repo / "secrets.txt").exists(), (
        "secrets.txt should still exist on disk — you needed `git rm --cached`, "
        "not plain `git rm`. Re-run make_kata.py and try again."
    )


def test_gitignore_prevents_recurrence(kata_repo):
    gitignore = kata_repo / ".gitignore"
    assert gitignore.exists(), (
        "Untracking isn't enough — without a .gitignore the next `git add -A` "
        "will re-track everything."
    )
    content = gitignore.read_text()
    assert "secrets.txt" in content, ".gitignore should cover secrets.txt"
    assert "exports" in content, ".gitignore should cover the exports/ directory"
    tracked = _git(kata_repo, "ls-files").stdout.splitlines()
    assert ".gitignore" in tracked, ".gitignore itself must be committed to protect everyone."


# --------------------------------------------------------------------------
# Task B — a change made on a branch and merged
# --------------------------------------------------------------------------


def test_typo_fixed_on_branch(kata_repo):
    assert "pipline" not in (kata_repo / "README.md").read_text(), (
        "The README typo ('pipline') is still there."
    )
    branches = _git(kata_repo, "branch", "--list", "fix/readme-typo").stdout
    assert "fix/readme-typo" in branches, (
        "Create the fix on a branch named exactly 'fix/readme-typo' — the branch "
        "workflow is the exercise, not just the edit."
    )
    merged = _git(kata_repo, "merge-base", "--is-ancestor", "fix/readme-typo", "main")
    assert merged.returncode == 0, (
        "The fix/readme-typo branch exists but its work never reached main. Merge it."
    )


# --------------------------------------------------------------------------
# Task C — the merge conflict, resolved without losing either intent
# --------------------------------------------------------------------------


def test_conflict_resolved_keeping_both_changes(kata_repo):
    merged = _git(kata_repo, "merge-base", "--is-ancestor", "feature/add-city-column", "main")
    assert merged.returncode == 0, "feature/add-city-column has not been merged into main yet."
    text = (kata_repo / "pipeline.py").read_text()
    assert "<<<<<<<" not in text and ">>>>>>>" not in text, (
        "Conflict markers are still in pipeline.py — the conflict was committed, "
        "not resolved. This happens in real life more than anyone admits."
    )
    for col in ("store_name", "city"):
        assert f'"{col}"' in text, (
            f"The resolution lost the '{col}' column. A conflict is two valid "
            "intents colliding — resolving means honoring both, not picking the "
            "easier side."
        )


def test_commit_messages_carry_information(kata_repo):
    messages = _git(kata_repo, "log", "--format=%s", "-n", "8").stdout.splitlines()
    lazy = {"wip", "fix", "fixes", "update", "updates", "asdf", "changes", "stuff", "."}
    for msg in messages:
        assert msg.strip().lower() not in lazy, (
            f"Commit message {msg!r} says nothing. Messages are documentation "
            "for whoever debugs this at 3 a.m. — usually future you."
        )


# --------------------------------------------------------------------------
# Concepts quiz
# --------------------------------------------------------------------------


def test_quiz_staging_model():
    import m01_git_concepts as ans

    assert _answered(ans.Q1_WHAT_GETS_COMMITTED, "Q1") == "first", (
        "Commits snapshot the STAGING AREA, not the working directory. "
        "`git add` is the moment the snapshot is taken."
    )


def test_quiz_amend():
    import m01_git_concepts as ans

    assert _answered(ans.Q2_FIX_LAST_MESSAGE, "Q2").strip().lstrip("git ").strip() == (
        "commit --amend"
    ), "Look up amending — and when it becomes dangerous (hint: after pushing)."


def test_quiz_diverged_history():
    import m01_git_concepts as ans

    assert _answered(ans.Q3_HISTORY_IS_CORRUPTED, "Q3") is False, (
        "A rejected push means histories diverged — a normal, recoverable state. "
        "Git is a graph; nothing was lost."
    )


def test_quiz_data_in_git():
    import m01_git_concepts as ans

    assert _answered(ans.Q4_COMMIT_THE_DATA, "Q4") == "no", (
        "Version the recipe, not the cake. Large data in Git: slow clones, "
        "meaningless diffs, and PII that can never be deleted from history."
    )


def test_quiz_code_review():
    import m01_git_concepts as ans

    assert _answered(ans.Q5_BLOCKING_HUNK, "Q5") == 2, (
        "One hunk introduces something that, once pushed, lives in history "
        "forever and requires rotating a credential."
    )
    assert _answered(ans.Q6_SNEAKY_LOGIC_CHANGE, "Q6") == 4, (
        "Ask of every hunk: 'which ROWS does this change affect?' One hunk "
        "silently removes a whole payment method from a report."
    )
    assert _answered(ans.Q7_VERDICT, "Q7") == "request_changes", (
        "Removing the secret doesn't make the unexplained business-logic "
        "changes reviewable. Rounding revenue per-line and dropping cash sales "
        "both change numbers finance relies on."
    )
