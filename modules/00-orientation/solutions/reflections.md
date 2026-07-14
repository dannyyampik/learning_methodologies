# Module 00 — Suggested reflection answers

**1. Whose fault is the double-run?**
Nobody's — and that's the point. Ops did the obvious thing; Dave wrote code
that worked under the assumptions of its time. Systems that require every
operator to know unwritten rules ("never run it twice!") are *designed* to
fail. Blame the design, fix the design: make the safe action and the obvious
action the same action. This "blameless" framing returns formally in
Module 7 (postmortems), and the design fix is Module 4 (idempotency).

**2. "It works" vs "it doesn't work".**
It produces correct tables when operated perfectly under undocumented
conditions. Engineering asks a stricter question: does it produce correct
results under *realistic* operation — retries, partial failures, new hires,
schema drift? By that definition it does not work; it has merely not failed
loudly yet. "Works" is a property of a system *plus* its operating
conditions, not of code alone.

**3. Which practice first?**
Defensible answers differ, but the course's ordering is deliberate: version
control first (Module 1). It is nearly free, it is the substrate every other
practice builds on (review, CI, rollback all presuppose Git), and it converts
"the script on the server" into a shared, inspectable artifact. The most
common competing answer — "tests first" — founders on a practical problem:
you cannot review, share, or CI-run tests for code that only exists as an
untracked file on one machine.
