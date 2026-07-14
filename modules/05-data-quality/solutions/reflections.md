# Module 05 — Suggested reflection answers

**1. Revenue 40% below trend at 6 a.m.**
Legitimate: a public holiday (stores closed), yesterday's late file hasn't
been delivered yet (the drop is *incompleteness*, not sales), a store
closed for renovation. Defect-shaped twins: a partition half-loaded before
a crash, a join silently dropping rows after a dimension change, the
duplicates check finally fixed and yesterday's *inflation* was the anomaly.
What's missing is **context to disambiguate**: delivery/completeness
metadata ("all expected files arrived?"), a calendar dimension, run/lineage
history ("what changed in code or data since the last green run?"), and
per-partition load counts. Numbers alone can't tell "the world changed"
from "we broke it" — metadata about the pipeline's own operation can.
That's the observability thesis of Module 7.

**2. The check that warned daily for six months.**
Process failure: a warning with no owner, no threshold, and no consequence
is *noise being generated on purpose*. Alert fatigue is a design defect,
not a human weakness. Options, all defensible: (a) fix the root cause —
six months of data quantifies the POS firmware bug; that evidence is a
vendor escalation ticket; (b) formalize tolerance — convert to a
thresholded check (warn >0.1%, error >1%) so it only speaks when something
*changes*; (c) delete it — honest if NULL store_ids genuinely don't matter,
but then delete the *belief*, too: update the contract to say store_id is
nullable and stop pretending otherwise. The indefensible option is the
status quo: a check whose failure is ignored trains the team to ignore
checks.

**3. The vendor who won't sign.**
Then the contract moves to *your* edge: you publish a contract for the
**cleaned, validated layer you produce**, and your ingest gate becomes the
enforcement point of an implicit contract the vendor never signed —
quarantine what violates it, load what conforms, alert on drift.
Architecturally: a rawest "landing" zone that accepts anything (immutable,
Module 4), a validation layer that is the real boundary, and downstream
consumers who depend only on the validated layer. You can't force a
producer to make promises; you can refuse to *propagate* their chaos. And
your daily defect statistics become the negotiation leverage the missing
signature never provided.
