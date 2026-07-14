"""Module 07, Exercise 1 — Build a mini-orchestrator.

Airflow, Dagster, and Prefect are large; the ideas inside them are small.
You will implement the two functions at the heart of every orchestrator —
dependency-ordered execution and retry-with-skip-downstream — in ~60 lines.
Afterward, reading any real orchestrator's docs feels like recognizing,
not learning.

A DAG here is a dict mapping each task name to the set of tasks it
depends on:

    dag = {
        "load_stores":   set(),
        "load_products": set(),
        "load_sales":    set(),
        "quality_gate":  {"load_sales", "load_stores", "load_products"},
        "daily_revenue": {"quality_gate"},
        "top_products":  {"quality_gate"},
    }

Run:  make check MODULE=07
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

Status = Literal["success", "failed", "skipped"]


class CycleError(ValueError):
    """The 'A' in DAG is load-bearing: cyclic dependencies cannot be run."""


@dataclass
class TaskResult:
    name: str
    status: Status
    attempts: int  # 0 for skipped tasks


def topological_order(dag: dict[str, set[str]]) -> list[str]:
    """Return the task names in an order that satisfies every dependency
    (each task appears after all of its dependencies).

    Raise CycleError if the graph contains a cycle, and ValueError if a
    task depends on an unknown task. Make the order DETERMINISTIC by
    breaking ties alphabetically — you learned why determinism matters in
    Module 4; it applies to schedulers too (debuggability, reproducible
    incident timelines).
    """
    raise NotImplementedError


def run_dag(
    dag: dict[str, set[str]],
    actions: dict[str, Callable[[], None]],
    max_attempts: int = 1,
) -> dict[str, TaskResult]:
    """Execute every task in dependency order. The rules:

    - A task's action is called with no arguments; raising = failure.
    - On failure, retry up to `max_attempts` total attempts, then mark the
      task "failed".
    - A task whose dependencies did not ALL succeed is "skipped" (attempts
      0) — never executed. Failure must cascade: dependents of skipped
      tasks are skipped too.
    - Tasks on unaffected branches still run: one dead branch must not
      take the whole graph down with it.

    Return a TaskResult for every task in the dag.
    """
    raise NotImplementedError
