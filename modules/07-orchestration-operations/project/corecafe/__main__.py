"""Entry point: python -m corecafe

Exit codes are part of the interface — schedulers and orchestrators react
to them: 0 = published, 1 = quality gate blocked, 2 = publication blocked.
"""

import logging
import os
import sys

from corecafe.config import load_config
from corecafe.pipeline import PublicationError, QualityGateError, run

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        stream=sys.stderr,
    )
    try:
        summary = run(load_config(os.environ))
    except QualityGateError as exc:
        print(f"BLOCKED (quality gate): {exc}", file=sys.stderr)
        sys.exit(1)
    except PublicationError as exc:
        print(f"BLOCKED (publication audit): {exc}", file=sys.stderr)
        sys.exit(2)

    print(
        f"processed {summary.files_processed} files: "
        f"{summary.rows_loaded} rows loaded, {summary.rows_rejected} rejected; "
        f"published {', '.join(p.table for p in summary.publications)}"
    )
    sys.exit(0)
