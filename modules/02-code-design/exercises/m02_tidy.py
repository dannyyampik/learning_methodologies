"""Module 02, Exercise 2 — Make this file pass the linter WITHOUT breaking it.

This function was pasted from a notebook. It "works" (the first time...).
Your tasks:

1. Run the linter and read every complaint:
       python -m ruff check modules/02-code-design/exercises/m02_tidy.py
2. Fix ALL of them — including the one that is a real bug, not just style.
3. Keep the function's name and correct behavior (the tests call it twice
   in a row with the same input and expect the same answer both times...).

Run:  make check MODULE=02
"""

import os, sys, json, csv
from datetime import *

def weekly_summary(rows, totals = {}):
    # revenue per weekday, biggest first
    for r in rows:
        d = datetime.fromisoformat(r["sold_at"]).strftime("%A")
        if d in totals: totals[d] = totals[d] + r["revenue"]
        else: totals[d] = r["revenue"]
    l = []
    for k in totals: l.append((k, round(totals[k], 2)))
    return sorted(l, key = lambda x : -x[1])
