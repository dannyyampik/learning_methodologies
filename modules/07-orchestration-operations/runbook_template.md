# Runbook: <pipeline> — <failure mode>

> One page per failure mode. Written calmly, in advance, versioned next to
> the pipeline. If a step can be a copy-pasteable command, it must be.

**Owner:** <team/person> · **Last verified:** <date — runbooks rot; re-walk them quarterly>

## Symptom
What the responder actually sees (the alert text, the user complaint, the
red task). Include the alert name verbatim so this page is findable by
searching it.

## Impact
Who/what is affected while this is broken, and how urgently it matters.
("daily_revenue stale → finance dashboard wrong after 09:00; exec review
uses it Tuesdays.")

## Diagnosis
Ordered checks, cheapest first. Each: a command/query + what each possible
result means.

1. Did the run happen? → `<where to look, exact command>`
2. Did the source deliver? → `ls <landing path> | tail`
3. What do the logs say? → `<log query>` (v4 logs one line per stage — the
   last line present tells you which stage died)
4. Quality gate or WAP block? → exit code 1 vs 2; failing checks are named
   in stderr; a WAP block leaves `staging_<table>` for inspection.

## Remediation
Exact commands for each diagnosis outcome. State loudly which actions are
safe to repeat (everything idempotent) and which need thought.

- Missing delivery → contact vendor (below); once delivered:
  `... backfill --start <day> --end <day>`
- Transient failure → re-run: `python -m corecafe` (safe: loads are
  idempotent partition overwrites)
- Quality gate block → inspect named check's failing rows; if data is
  legitimately anomalous (holiday, promo), <documented override process>;
  if defective, quarantine + vendor escalation.

## Escalation
Who to wake, in order, and *when* ("if not resolved within 60 min" /
"immediately if exec dashboards affected"). Include the vendor's support
channel and your account/feed identifiers.

## Postmortem trigger
Which outcomes require a postmortem (e.g., any consumer-visible staleness
past SLA; any manual data edit). Link to the postmortem template/folder.
