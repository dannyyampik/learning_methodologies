"""Entry point: python -m corecafe

Exit codes are part of the interface: schedulers and CI react to them.
0 = published; 1 = quality gate blocked publication.
"""

import os
import sys

from corecafe.config import load_config
from corecafe.pipeline import QualityGateError, run

if __name__ == "__main__":
    try:
        summary = run(load_config(os.environ))
    except QualityGateError as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        for check in exc.verdict.errors:
            print(
                f"  FAIL [{check.severity}] {check.name}: {check.failing_rows} failing rows",
                file=sys.stderr,
            )
        sys.exit(1)

    for check in summary.quality.warnings:
        print(f"  warn {check.name}: {check.failing_rows} failing rows")
    print(
        f"processed {summary.files_processed} files: "
        f"{summary.rows_loaded} rows loaded, {summary.rows_rejected} rejected"
    )
    sys.exit(0)
