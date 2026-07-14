"""Module 02, Exercise 2 — reference solution.

What each linter complaint was really telling you:

- F401 (unused imports os/sys/json/csv): dead weight that misleads readers
  about what this module touches.
- F403 (`from datetime import *`): nobody can tell where `datetime` came
  from; star imports also invite silent name collisions.
- B006 (mutable default `totals={}`): THE BUG. Default values are created
  once, at function definition — every call shared and mutated the same
  dict, so the second call returned doubled numbers. A linter, for free,
  just caught the same class of bug as Module 00's doubled dashboard.
- E701 / style: one statement per line; code is read far more than written.
"""

from datetime import datetime


def weekly_summary(rows: list[dict]) -> list[tuple[str, float]]:
    """Revenue per weekday name, largest first."""
    totals: dict[str, float] = {}
    for row in rows:
        weekday = datetime.fromisoformat(row["sold_at"]).strftime("%A")
        totals[weekday] = totals.get(weekday, 0.0) + row["revenue"]
    return sorted(
        ((day, round(total, 2)) for day, total in totals.items()),
        key=lambda item: -item[1],
    )
