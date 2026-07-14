"""Wire this module's tests to either `exercises/` (default) or `solutions/`.

Every module in the course uses this same pattern. `make check` sets
COURSE_TARGET=exercises to grade YOUR work; `make solutions` and CI set
COURSE_TARGET=solutions to prove the reference answers pass.
"""

import os
import sys
from pathlib import Path

MODULE_DIR = Path(__file__).resolve().parents[1]
TARGET = os.environ.get("COURSE_TARGET", "exercises")
sys.path.insert(0, str(MODULE_DIR / TARGET))
