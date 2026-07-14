"""Module 07, Exercise 1 — reference solution (Kahn's algorithm + a walk)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

Status = Literal["success", "failed", "skipped"]


class CycleError(ValueError):
    pass


@dataclass
class TaskResult:
    name: str
    status: Status
    attempts: int


def topological_order(dag: dict[str, set[str]]) -> list[str]:
    for task, deps in dag.items():
        unknown = deps - dag.keys()
        if unknown:
            raise ValueError(f"{task} depends on unknown task(s): {sorted(unknown)}")

    # Kahn's algorithm: repeatedly take a task with no unsatisfied deps.
    # Sorting the ready set makes the order deterministic.
    remaining = {task: set(deps) for task, deps in dag.items()}
    order: list[str] = []
    while remaining:
        ready = sorted(task for task, deps in remaining.items() if not deps)
        if not ready:
            raise CycleError(f"cycle among: {sorted(remaining)}")
        for task in ready:
            order.append(task)
            del remaining[task]
        for deps in remaining.values():
            deps.difference_update(ready)
    return order


def run_dag(
    dag: dict[str, set[str]],
    actions: dict[str, Callable[[], None]],
    max_attempts: int = 1,
) -> dict[str, TaskResult]:
    results: dict[str, TaskResult] = {}

    for task in topological_order(dag):
        # Skip-cascade: every dependency must have succeeded. This is why
        # topological order matters — dependencies are always decided first.
        if any(results[dep].status != "success" for dep in dag[task]):
            results[task] = TaskResult(task, "skipped", 0)
            continue

        attempts = 0
        while True:
            attempts += 1
            try:
                actions[task]()
            except Exception:
                if attempts >= max_attempts:
                    results[task] = TaskResult(task, "failed", attempts)
                    break
                # Retrying is only SAFE because Module 4 made tasks
                # idempotent. An orchestrator retrying non-idempotent tasks
                # is an incident generator with a cron schedule.
                continue
            else:
                results[task] = TaskResult(task, "success", attempts)
                break

    return results
