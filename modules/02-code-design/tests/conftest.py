import os
import sys
from pathlib import Path

MODULE_DIR = Path(__file__).resolve().parents[1]
TARGET = os.environ.get("COURSE_TARGET", "exercises")
TARGET_DIR = MODULE_DIR / TARGET
sys.path.insert(0, str(TARGET_DIR))
