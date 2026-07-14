"""Self-check for Module 07: the mini-orchestrator and the monitors."""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import duckdb
import pytest

MODULE_DIR = Path(__file__).resolve().parents[1]

PIPELINE_DAG = {
    "load_stores": set(),
    "load_products": set(),
    "load_sales": set(),
    "quality_gate": {"load_sales", "load_stores", "load_products"},
    "daily_revenue": {"quality_gate"},
    "top_products": {"quality_gate"},
}


# --------------------------------------------------------------------------
# Exercise 1 — the orchestrator
# --------------------------------------------------------------------------


def test_topological_order_respects_dependencies():
    from m07_orchestrator import topological_order

    order = topological_order(PIPELINE_DAG)
    assert sorted(order) == sorted(PIPELINE_DAG)
    position = {task: i for i, task in enumerate(order)}
    for task, deps in PIPELINE_DAG.items():
        for dep in deps:
            assert position[dep] < position[task], f"{task} ran before its dependency {dep}"


def test_topological_order_is_deterministic():
    from m07_orchestrator import topological_order

    assert topological_order(PIPELINE_DAG) == topological_order(PIPELINE_DAG)
    # Alphabetical tie-break among the three independent loads:
    order = topological_order(PIPELINE_DAG)
    assert order[:3] == ["load_products", "load_sales", "load_stores"]


def test_cycle_is_rejected():
    from m07_orchestrator import CycleError, topological_order

    with pytest.raises(CycleError):
        topological_order({"a": {"b"}, "b": {"a"}})


def test_unknown_dependency_is_rejected():
    from m07_orchestrator import topological_order

    with pytest.raises(ValueError):
        topological_order({"a": {"ghost"}})


def test_run_dag_happy_path():
    from m07_orchestrator import run_dag

    log: list[str] = []
    actions = {task: (lambda t=task: log.append(t)) for task in PIPELINE_DAG}
    results = run_dag(PIPELINE_DAG, actions)
    assert all(r.status == "success" for r in results.values())
    assert len(log) == len(PIPELINE_DAG)


def test_retry_gives_flaky_tasks_a_second_chance():
    from m07_orchestrator import run_dag

    attempts = {"n": 0}

    def flaky():
        attempts["n"] += 1
        if attempts["n"] < 2:
            raise ConnectionError("vendor SFTP hiccup")

    results = run_dag({"ingest": set()}, {"ingest": flaky}, max_attempts=3)
    assert results["ingest"].status == "success"
    assert results["ingest"].attempts == 2, (
        "The task should succeed on its second attempt — and stop retrying then."
    )


def test_failure_cascades_but_only_downstream():
    from m07_orchestrator import run_dag

    def boom():
        raise RuntimeError("bad delivery")

    actions = {task: (lambda: None) for task in PIPELINE_DAG}
    actions["load_sales"] = boom
    results = run_dag(PIPELINE_DAG, actions, max_attempts=2)

    assert results["load_sales"].status == "failed"
    assert results["load_sales"].attempts == 2
    assert results["quality_gate"].status == "skipped", "depends on the failed task"
    assert results["daily_revenue"].status == "skipped", "skip must cascade transitively"
    assert results["top_products"].status == "skipped"
    assert results["quality_gate"].attempts == 0, "skipped tasks must never execute"
    assert results["load_stores"].status == "success", (
        "load_stores does not depend on load_sales — an unrelated branch must "
        "not be taken down by someone else's failure."
    )


# --------------------------------------------------------------------------
# Exercise 2 — the monitors
# --------------------------------------------------------------------------


def test_freshness_within_sla_is_quiet():
    from m07_monitors import check_freshness

    now = datetime(2026, 6, 10, 8, 0)
    assert check_freshness(datetime(2026, 6, 10, 6, 0), now, sla_hours=24) is None


def test_freshness_alerts_when_stale_with_useful_message():
    from m07_monitors import check_freshness

    now = datetime(2026, 6, 10, 8, 0)
    alert = check_freshness(datetime(2026, 6, 8, 8, 0), now, sla_hours=24)
    assert alert is not None and alert.monitor == "freshness"
    assert "48" in alert.message and "24" in alert.message, (
        "The alert must say how stale (48h) and what the SLA was (24h) — the "
        "responder should not need to run queries to understand the alert."
    )


def test_freshness_alerts_on_empty_table():
    from m07_monitors import check_freshness

    alert = check_freshness(None, datetime(2026, 6, 10), sla_hours=24)
    assert alert is not None, "An empty table is maximally stale, not 'no data, no problem'."


def test_volume_normal_days_are_quiet():
    from m07_monitors import detect_volume_anomaly

    assert detect_volume_anomaly([240, 250, 235, 260, 245], 251) is None


def test_volume_alerts_on_collapse_and_explosion():
    from m07_monitors import detect_volume_anomaly

    collapse = detect_volume_anomaly([240, 250, 235, 260, 245], 30)
    assert collapse is not None and collapse.monitor == "volume"

    explosion = detect_volume_anomaly([240, 250, 235, 260, 245], 700)
    assert explosion is not None, (
        "A doubling is as suspicious as a halving — remember what Module 00's "
        "bug did to row counts."
    )


def test_volume_needs_history_before_it_speaks():
    from m07_monitors import detect_volume_anomaly

    assert detect_volume_anomaly([250, 260], 30) is None, (
        "Two data points are not a baseline. An early-firing anomaly detector "
        "is a noise generator, and noise teaches humans to ignore alerts."
    )


# --------------------------------------------------------------------------
# The project snapshot (v4): WAP-published marts, end to end
# --------------------------------------------------------------------------


def test_project_snapshot_publishes_via_wap(tmp_path):
    from datagen import write_dataset

    write_dataset(tmp_path / "data" / "raw", days=2, seed=42)
    env = {**os.environ, "PYTHONPATH": str(MODULE_DIR / "project")}
    result = subprocess.run(
        [sys.executable, "-m", "corecafe"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "published daily_revenue" in result.stdout

    con = duckdb.connect(str(tmp_path / "data" / "warehouse.duckdb"), read_only=True)
    tables = {r[0] for r in con.execute("SHOW TABLES").fetchall()}
    con.close()
    assert "daily_revenue" in tables and "top_products" in tables
    assert not any(t.startswith("staging_") for t in tables), (
        "Successful publishes should leave no staging debris."
    )
