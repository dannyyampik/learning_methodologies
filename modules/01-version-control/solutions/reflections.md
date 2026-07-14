# Module 01 — Suggested reflection answers

**1. 200 reports with SQL trapped in the BI tool.**
Don't attempt a big-bang export. Establish a ratchet: from today, any report
that gets *touched* has its SQL extracted to the repo first (many BI tools
support referencing versioned SQL or at least a paste-back workflow), and new
reports start in the repo. Untouched reports are, by definition, the ones
changing least — the risk they carry is stable. Prioritize a one-time export
only for the reports feeding decisions (finance, exec dashboards). The
general shape — *make the good path the default and let traffic migrate the
rest* — recurs in every legacy situation in this course.

**2. The 12-second LGTM.**
It cost the team twice: the defect-catching value of review (zero here) and,
worse, the *information transfer* — the reviewer learned nothing about a
codebase they're now nominally co-responsible for. Fixes are structural, not
moral: smaller PRs (a 40-line PR invites real reading; a 900-line one begs
for rubber-stamping), PR descriptions that state what to scrutinize, and a
team norm that "I reviewed the row-impact of the WHERE change" is a sentence
reviewers are expected to be able to say.

**3. `git blame`.**
The name frames history as fault-finding, but its real use is *context
recovery*: "what problem was this line solving?" — usually answered by the
commit message it points to (write them accordingly). Healthy teams read
blame output as documentation. The blameless framing returns in Module 7's
postmortems; the mindset is the same.
