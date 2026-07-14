import os
import sys
from pathlib import Path

import pytest

MODULE_DIR = Path(__file__).resolve().parents[1]
TARGET = os.environ.get("COURSE_TARGET", "exercises")

# Put the graded target first, but keep exercises/ importable too — the kata
# builder lives there and is needed in both modes.
sys.path.insert(0, str(MODULE_DIR / "exercises"))
sys.path.insert(0, str(MODULE_DIR / TARGET))


@pytest.fixture(scope="session")
def kata_repo(tmp_path_factory):
    """The kata repository to grade.

    - exercises mode: YOUR kata at exercises/kata (created by make_kata.py).
    - solutions mode: a fresh kata solved by the reference solution.
    """
    if TARGET == "solutions":
        import m01_solve_kata
        import make_kata

        path = tmp_path_factory.mktemp("kata") / "m01"
        make_kata.build(path)
        m01_solve_kata.solve(path)
        return path

    path = MODULE_DIR / "exercises" / "kata"
    if not (path / ".git").exists():
        pytest.fail(
            "No kata found. Create it first:\n"
            "    python modules/01-version-control/exercises/make_kata.py\n"
            "then work through Tasks A-C in the module README."
        )
    return path
