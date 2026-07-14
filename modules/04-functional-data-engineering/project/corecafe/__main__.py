"""Entry point: python -m corecafe

Configuration comes from the environment (see corecafe/config.py):
CORECAFE_RAW_DIR, CORECAFE_WAREHOUSE, CORECAFE_VAT_RATE.
"""

import os
import sys

from corecafe.config import load_config
from corecafe.pipeline import run

if __name__ == "__main__":
    summary = run(load_config(os.environ))
    print(
        f"processed {summary.files_processed} files: "
        f"{summary.rows_loaded} rows loaded, {summary.rows_rejected} rejected"
    )
    sys.exit(0)
