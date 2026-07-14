import os
import sys
from pathlib import Path

MODULE_DIR = Path(__file__).resolve().parents[1]
TARGET = os.environ.get("COURSE_TARGET", "exercises")

# Graded target first; exercises/ kept importable (mutants.py lives there);
# project/ provides the corecafe package under test.
sys.path.insert(0, str(MODULE_DIR / "project"))
sys.path.insert(0, str(MODULE_DIR / "exercises"))
sys.path.insert(0, str(MODULE_DIR / TARGET))
