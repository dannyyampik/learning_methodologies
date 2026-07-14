"""Module 07, Exercise 2 — reference solution."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Alert:
    monitor: str
    message: str


def check_freshness(
    latest_loaded: datetime | None, now: datetime, sla_hours: float
) -> Alert | None:
    if latest_loaded is None:
        return Alert(
            monitor="freshness",
            message=f"table is EMPTY — no data has ever loaded (SLA: {sla_hours:g}h)",
        )
    age_hours = (now - latest_loaded).total_seconds() / 3600
    if age_hours <= sla_hours:
        return None
    return Alert(
        monitor="freshness",
        message=(
            f"newest data is {age_hours:.1f}h old, SLA is {sla_hours:g}h "
            f"(latest loaded: {latest_loaded:%Y-%m-%d %H:%M})"
        ),
    )


def detect_volume_anomaly(history: list[int], today: int, tolerance: float = 0.5) -> Alert | None:
    if len(history) < 3:
        return None  # not enough signal to distinguish anomaly from noise

    mean = sum(history) / len(history)
    if mean == 0:
        # History of empty days: any rows at all is the anomaly worth a look.
        return (
            None
            if today == 0
            else Alert(
                monitor="volume",
                message=f"today has {today} rows where history averages 0",
            )
        )

    deviation = (today - mean) / mean
    if abs(deviation) <= tolerance:
        return None
    return Alert(
        monitor="volume",
        message=(
            f"today has {today} rows vs a recent mean of {mean:.0f} "
            f"({deviation:+.0%}; tolerance ±{tolerance:.0%})"
        ),
    )
