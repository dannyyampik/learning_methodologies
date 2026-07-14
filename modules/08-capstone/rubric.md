# Capstone Review Rubric

Score each item 0 (absent), 1 (present but shallow), 2 (would pass review
on a professional data team). Target: ≥ 2 on every **bold** item, ≥ 44/58
overall. Review as a PR review: leave line comments, not just scores.

## Version control & collaboration (Module 1)
| | 0/1/2 |
|---|---|
| **History tells a story** — small commits, messages explain *why* | |
| **No data, secrets, or generated artifacts ever committed** (check history, not just tip!) | |
| Branch/PR workflow visible; PR description states intent and metric impact | |

## Code design (Module 2)
| | 0/1/2 |
|---|---|
| **Transform layer is pure** — importable and callable with zero infrastructure | |
| **Config out of code** — one Config object, env-injected at the edge, no buried constants | |
| Lint clean; dependencies declared and locked; layout navigable in 60 seconds | |

## Testing (Module 3)
| | 0/1/2 |
|---|---|
| **Unit tests are beliefs-first** — small probes, meaningful failure messages | |
| **The self-mutant is killed** — a deliberate bug variant exists and the suite catches it | |
| Integration test: temp warehouse, arrange-act-assert, *independent* reconciliation | |
| Tests need no ritual (no "run make data first"), share no state, pass twice in a row | |

## Functional data engineering (Module 4)
| | 0/1/2 |
|---|---|
| **Partition overwrite in a transaction** — rerun test proves count/sum stability | |
| **Corrected re-delivery test** — updated rows take, removed rows leave no zombies | |
| Backfill command exists, is idempotent, reports missing days without crashing | |

## Data quality & contracts (Module 5)
| | 0/1/2 |
|---|---|
| **Gate blocks error-severity failures before publication** (prove with a poisoned batch) | |
| Severities are justified policy (comments/README say *why* warn vs error) | |
| Schema contract enforced; drift test exists (dropped/renamed/typed column caught) | |

## CI/CD & environments (Module 6)
| | 0/1/2 |
|---|---|
| **CI runs the same entry points as local** (`make …`), on PRs, and is green | |
| **WAP on marts** — failed audit leaves production bit-for-bit intact, staging kept | |
| Environments differ by config only; a dev run is documented and takes one command | |

## Operations (Module 7)
| | 0/1/2 |
|---|---|
| **Freshness + volume monitors with actionable messages** (context in the alert) | |
| Structured logs: a stranger can reconstruct a run's timeline from stderr alone | |
| Runbook exists for the top failure mode and was walked through once | |
| Exit codes distinguish outcome classes; README's "when it's red" section is real | |

## The reviewer's meta-question
After everything: **would you let this pipeline feed a dashboard your own
salary depended on?** If not, the gap you can name is the most valuable
comment on the review.
