"""Module 07, Exercise 2 — Freshness and volume monitors.

The two observability checks that catch the failures nothing else can:
the pipeline that silently STOPPED (freshness) and the pipeline that ran
fine on far too little data (volume). Commercial observability platforms
are, at their core, better-dressed versions of these ~20 lines.

Run:  make check MODULE=07
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Alert:
    monitor: str  # "freshness" or "volume"
    message: str  # human-readable; will be read at 3 a.m. — be kind


def check_freshness(
    latest_loaded: datetime | None, now: datetime, sla_hours: float
) -> Alert | None:
    """Alert if the newest loaded data is older than the SLA allows.

    - latest_loaded is None means the table is EMPTY: that's a freshness
      alert too (the most stale a table can be), not an error.
    - Return None when within SLA.
    - The message must include how stale the data actually is (in hours)
      and what the SLA was — an alert that makes the responder run the
      query themselves has failed at its one job.
    """
    raise NotImplementedError


def detect_volume_anomaly(
    history: list[int], today: int, tolerance: float = 0.5
) -> Alert | None:
    """Alert if today's row count deviates from recent history by more than
    `tolerance` (fraction of the historical mean, both directions —
    a doubling is as suspicious as a halving; remember Module 00).

    - history: daily row counts for recent comparable days, oldest first.
    - With fewer than 3 days of history, return None: an anomaly detector
      that alerts off two data points is a noise generator, and noise
      trains humans to ignore it (the fate of every noisy monitor).
    - The message must include today's count, the historical mean, and the
      deviation as a percentage.
    """
    raise NotImplementedError
