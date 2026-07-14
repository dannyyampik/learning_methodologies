"""CoreCafé pipeline, v1 — the monolith after Module 02's refactor.

Architecture: functional core, imperative shell.

    extract.py    reads files             (I/O edge)
    transform.py  parses & computes       (pure core — no I/O anywhere)
    load.py       writes to the warehouse (I/O edge)
    pipeline.py   wires the above         (the shell)
    config.py     everything that is policy, not logic

KNOWN ISSUE (on purpose): load.append_sales still appends without checking
what a previous run loaded — the Module 00 double-counting bug survives the
refactor untouched, because a refactor preserves behavior. Module 04 fixes
it for real.
"""

__version__ = "1.0.0"
