"""Pipeline configuration — policy lives here, not in the logic."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    vat_rate: float
    raw_dir: str
    warehouse_path: str


def load_config(env: Mapping[str, str]) -> Config:
    """Build Config from an environment mapping.

    `env` is an argument (pass os.environ at the real edge, a dict in tests)
    so that nothing deeper in the pipeline ever touches global state.
    """
    return Config(
        vat_rate=float(env.get("CORECAFE_VAT_RATE", "1.17")),
        raw_dir=env.get("CORECAFE_RAW_DIR", "data/raw"),
        warehouse_path=env.get("CORECAFE_WAREHOUSE", "data/warehouse.duckdb"),
    )
