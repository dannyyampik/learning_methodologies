"""Seeded synthetic-data generator for the CoreCafé course pipeline.

Why synthetic data instead of a public dataset?

1. **Reproducibility** — the generator is seeded, so every student (and CI)
   sees byte-identical data. When an exercise says "store 3 is broken on
   day 12", it is broken for everyone.
2. **No network dependency** — the course runs fully offline.
3. **Controllable defects** — real pipelines break because of duplicates,
   nulls, late-arriving rows, and schema drift. We inject those *on purpose*,
   exactly when the curriculum needs them (Modules 3–5).

This package is also course material: it is written the way Module 2 says
pipeline code should be written. Read it.
"""

from datagen.generator import (
    DEFECT_KINDS,
    generate_dimensions,
    generate_sales_day,
    write_dataset,
)

__all__ = [
    "DEFECT_KINDS",
    "generate_dimensions",
    "generate_sales_day",
    "write_dataset",
]
