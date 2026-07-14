# Module 03 — Suggested reflection answers

**1. What do green tests guarantee?**
They guarantee exactly this: *the beliefs encoded in the suite hold for the
inputs the suite tries*. They say nothing about beliefs nobody encoded (the
unknown unknowns), nothing about tomorrow's malformed vendor file (that's
Module 5's runtime gate), and nothing about operational failures — disk
full, credentials expired, half a file delivered (Modules 4 and 7). The
mature phrasing for marketing: "the *known* failure modes are fenced; we
add a fence every time we discover a new one." That last habit — every
production incident becomes a regression test — is worth more than any
single suite.

**2. Golden-file tests.**
Brilliant for: refactors (Module 2's behavior-preservation is exactly a
golden comparison), legacy code with no spec ("whatever it does today is
the spec"), and complex outputs where writing beliefs one-by-one is
impractical. The trap: on an *intentional* logic change the golden file
must be regenerated — and the diff reviewed like code. Teams that regenerate
blindly ("tests red → update goldens → green") have deleted the test while
keeping its ceremony. Rule of thumb: golden tests protect *unchanged*
behavior; belief tests protect *specified* behavior; you want mostly the
latter, with goldens at wide, stable seams.

**3. Flaky test vs no test.**
The flaky test is worse, and it's not close. A missing test leaves a known
gap with honest risk accounting. A flaky one *trains the team to ignore
red* — and an ignored red suite protects nothing while still costing CI
minutes and attention. Worse, the reflex generalizes: once "re-run it,
it's probably the flake" is normal, real failures get re-run too. Fix
flakes immediately, quarantine them visibly, or delete them; never let
them ambient-fail. (Data-eng corollary: unseeded randomness and wall-clock
dependence — the usual flake sources — are the same enemies Module 4
fights under the name "determinism".)
