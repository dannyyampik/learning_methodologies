# Module 07 — Suggested reflection answers

**1. When retries make it worse.**
Retries assume failure left no footprint. If `load_sales` is
non-idempotent (v0's append), each retry *compounds* the damage — three
retries of a half-failed append can quadruple-load a partition, and
exponential backoff just schedules the corruption politely. The deciding
property is exactly idempotency: a retry is a bet that re-execution is
harmless, and Module 4 is what makes the bet safe. Precise phrasing:
**retry policies are only sound for tasks whose effects are absolute
(overwrite), never relative (append/increment).** Second-order case: even
idempotent tasks can make things worse under retry if the failure is
downstream overload (each retry adds load) — hence backoff + retry caps.

**2. One global tolerance vs weekend seasonality.**
With weekends legitimately +40%, a ±50% band around a mixed-day mean is
nearly saturated by *normal* variation: Saturdays sit close to the upper
edge (false-alarm risk) while a genuinely bad Saturday that drops to
weekday levels reads as "within tolerance" (missed alert). One knob is
trading its two error rates against each other across two different
regimes. Smallest fix: compare like with like — evaluate today against the
trailing mean of the *same weekday type* (the `history` parameter already
permits this; pass same-weekday counts). The general lesson: seasonality
belongs in the baseline, not in the tolerance.

**3. Negotiating five nines.**
99.999% freshness = ~5 minutes of allowable staleness *per year* — for a
daily batch fed by a vendor file at 06:45, not even wrong, just category
error: a single late vendor delivery per year already blows the budget by
orders of magnitude, and no amount of your engineering controls the
vendor. Counter-offer shape: "07:30 on 99% of business days (≈2.5 misses
a year), plus an alert to us within 15 minutes of any miss" — high enough
to feel like a promise, cheap enough to keep with the machinery this
course built (freshness monitor + runbook + idempotent re-run). Then the
educational part for leadership: each extra nine multiplies cost —
redundant vendor feeds, standby infrastructure, on-call rotation — so
what does the *business* lose at 99% that justifies the next nine? SLOs
are a negotiation between value and cost, and "five nines" is almost
always a wish that hasn't met its invoice.
