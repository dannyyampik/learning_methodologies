# Module 04 — Suggested reflection answers

**1. `CREATE OR REPLACE ... AS SELECT` marts.**
Idempotent: yes — the effect is absolute (the table becomes exactly the
query result). Deterministic: yes, *if* its inputs are (the sales table
under partitioned loads is a projection of raw files, so the chain holds).
Full rebuild is the correct default until it isn't: the usual breaking
points are runtime (rebuild slower than the schedule interval), cost
(cloud warehouses bill by scan), and freshness (consumers need minutes,
not daily). The replacement is *incremental processing* — but done
functionally: process only new/changed partitions and overwrite them,
never "append whatever seems new". dbt's incremental models and Iceberg's
partition-level rewrites are exactly this compromise. The mart stays a
cache; you're just refreshing it partition-wise.

**2. Immutability vs right-to-erasure.**
The principles compose once you split *identity* from *events*. Common
resolutions: (a) keep the immutable raw zone but encrypt per-subject and
"delete" by destroying keys (crypto-shredding); (b) pseudonymize at
ingestion — raw events carry surrogate keys, the PII mapping lives in one
small mutable, governed table, and erasure touches only that table while
history stays replayable; (c) where raw PII must truly be deleted, treat
deletion as a *governed pipeline* (logged, reviewed, itself idempotent) —
never an ad-hoc `rm`. What you never do: silently edit raw files in place,
because then nothing downstream is recomputable and no one can say what
was changed, when, or why.

**3. Strict vs skip-and-record vs the third option.**
With a guaranteed-daily garbage row, strict rejection means a guaranteed
daily incident — you've made the vendor's bug your outage. Pure
skip-and-record silently normalizes decay: one bad row today, four hundred
next month, nobody decides anything. The third option is the right one:
**thresholded quarantine**. Bad rows are diverted to a quarantine table
(with reasons and lineage back to the source file), the partition loads,
and a *quality gate* fails the run only when rejects exceed a declared
tolerance (say 0.5%). Now tolerance is an explicit, versioned, reviewed
number instead of an accident of error handling — which is precisely the
shape of Module 5.
