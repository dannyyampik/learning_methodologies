# Module 03 — Testing Data Systems

> *"How do you know the pipeline is correct?"*
> *"Finance hasn't complained recently."*

## Where we are

The CoreCafé pipeline is now a structured package (`project/corecafe/` — the
destination of Module 02's refactor). Its logic is pure and callable with
plain values, which was the whole setup for this module: now we make
correctness *checkable by a machine*, repeatedly, for free, forever.

Testing is where data teams most under-invest, and the reason is honest:
testing data systems is genuinely confusing. Test the code? The data? With
which data? This module gives you the map.

## Learning objectives

1. Draw the **testing pyramid for data** and place any given check on it:
   unit / integration / data test — and articulate why the three are not
   interchangeable.
2. Write pytest tests fluently: plain asserts, `parametrize`, fixtures,
   `tmp_path`, `pytest.raises`, `pytest.approx`.
3. Design **beliefs-first** tests: the smallest input that can violate one
   belief about the code — and measure a suite by the bugs it can catch
   (you will literally hunt mutants).
4. Write an integration test with arrange–act–assert against a real,
   disposable warehouse — no mocks, no shared state, no manual setup.
5. Explain what test data should look like (tiny, synthetic, engineered)
   and why "a copy of prod" is the wrong answer.

## The failure, first

In Module 00 the dashboard doubled and *nothing noticed*. Consider what was
available to notice it: ops eyeballs, finance's gut feeling, and luck. Every
one of them is expensive, slow, and off-duty at 3 a.m.

A test is the opposite kind of observer: cheap, instant, tireless, and
pedantic. The doubled dashboard needed exactly one line of observer:

```python
assert rerun_row_count == first_run_row_count
```

The craft of this module is knowing *which* one-liners to write, at *which*
level, against *which* data.

## Concepts

### 1. The testing pyramid, data edition

```
        ▲  fewer, slower, broader
        │
        │      /  E2E \          run the whole pipeline on a small dataset,
        │     /________\         check the marts (minutes)
        │    /integration\       real files → real (temp) warehouse for one
        │   /______________\     component seam (seconds)
        │  /   unit tests    \   pure functions, literal values
        │ /___________________\  (microseconds — hundreds of them)
        │
        │  ...and, at runtime, a different animal entirely:
        │  ═══ DATA TESTS ═══    checks on real production data as it flows
        ▼                        (Module 5's subject)
```

The distinction that confuses every data team, stated once, sharply:

- **Code tests** (the pyramid) run *before merge*, on *synthetic* data, and
  answer: **"is my logic right?"** They must be deterministic and fast.
- **Data tests** run *in production*, on *real* data, and answer: **"is
  today's data sane?"** Your logic can be perfect while a vendor ships you
  garbage — and vice versa.

Teams that conflate them get one of two failure patterns: CI that queries
the warehouse (slow, flaky, needs credentials, breaks when data changes) or
production with no runtime checks because "we have tests". You need both
kinds, in their proper places. This module builds the pyramid; Module 5
builds the runtime gate.

### 2. What makes a good unit test: beliefs, not lines

The wrong question: "what code should I cover?" The right question: **"what
do I believe about this function, and what is the smallest input that could
prove me wrong?"**

From the reference suite you'll build:

| Belief | Smallest violating probe |
|---|---|
| Revenue keeps its cents | a case whose true value has 3 decimals (`1 × 2.5 × 1.17 = 2.925`) |
| Unknown store stays unknown | one row with `store_id: ""` |
| Garbage fails loudly | one impossible timestamp |
| One bad row can't sink the batch | `[good, bad, good]` — three rows |

Notice the size: three-row batches, single values. Big test inputs are a
smell — they mean you don't know *which* belief the test checks.

Coverage percentage measures lines executed, not beliefs checked; it's a
decent *smoke detector* (0% coverage of `transform.py` is certainly bad) and
a terrible *target* (100% coverage proves nothing about assertions). The
honest metric is: **which bugs would this suite catch?** — and Exercise 1
makes you face it directly.

### 3. pytest, the 20% you'll use daily

```python
def test_revenue():                                  # found by name, no classes needed
    assert compute_revenue(2, 3.5, 1.17) == pytest.approx(8.19)   # floats: approx, always

@pytest.mark.parametrize("field,bad", [("quantity", "two"), ("sold_at", "junk")])
def test_garbage_is_loud(field, bad):                # one belief × N cases
    with pytest.raises(ValueError):                  # "must fail" is also a belief
        parse_sale({**GOOD_ROW, field: bad}, 1.17)

@pytest.fixture
def warehouse(tmp_path):                             # shared setup, injected by name;
    return duckdb.connect(str(tmp_path / "t.db"))    # tmp_path = fresh dir, auto-cleaned
```

Two disciplines matter more than any feature: **tests share nothing** (each
builds its own world — the `tmp_path` habit) and **tests need no setup
ritual** (a test that requires `make data` first isn't a test, it's a trap
for the next hire). You met the enforcement of this in Module 02, where the
purity test ran your code in an empty directory.

### 4. Test data: engineered, tiny, synthetic

"Just test on a copy of prod" fails four ways: it's huge (slow tests get
skipped), it drifts (green yesterday, red today, nothing changed), it leaks
PII into laptops and CI logs, and — least obvious, most important — **it
contains only the pathologies that already happened**. Your engineered
three-row batch contains the pathology you're *worried about*, whether or
not it has occurred yet.

The course's own `datagen` shows the pattern at both scales: seeded (same
"world" for everyone, deterministic assertions possible) with *injectable
defects* (pathologies on demand). Real teams do the same with fixture
factories.

> ⚠️ **Going deeper — property-based testing.** Libraries like `hypothesis`
> generate hundreds of adversarial inputs against properties you declare
> ("parsing then serializing round-trips", "revenue is monotonic in
> quantity"). Superb for parsers like `parse_sale`. Optional side quest:
> re-express Belief 5 as a hypothesis property.

### 5. When code tests meet the database: integration

Unit tests can't catch: a column order mismatch between `INSERT` and DDL, a
`read_csv_auto` type surprise, a join key that's `VARCHAR` on one side and
`INT` on the other. Those live at the seams — which is what integration
tests are *for*. The recipe (Exercise 2): generate a tiny dataset → run the
real pipeline into a warehouse in `tmp_path` → query the result and
reconcile it against an **independent** recomputation. DuckDB makes this
almost unfairly easy — an integration test that spins up a real analytical
database in milliseconds is a luxury Spark teams dream about; spend it.

## Exercises

1. **The mutation hunt** — [`exercises/m03_hunt.py`](exercises/m03_hunt.py).
   Six sabotaged variants of the transform layer lurk in `mutants.py`. Write
   the test suite that kills them all *and* passes on the real code. Rules:
   don't read `mutants.py` until you've killed at least four honestly.
2. **The integration test** —
   [`exercises/m03_integration.py`](exercises/m03_integration.py):
   arrange–act–assert against a real temporary warehouse.

```bash
make check MODULE=03
```

3. **Ungraded, recommended:** run the course repo's whole suite
   (`make test`) and read one test file from a module you haven't reached.
   You now have the vocabulary for everything in it — this repo *is* a
   worked example of this module.

## Reflection questions

1. Your suite kills all six mutants. Marketing asks: "so the pipeline can't
   be wrong anymore?" What, precisely, do the tests guarantee — and what do
   they not?
2. A teammate proposes testing `daily_revenue` by comparing it against last
   month's saved output ("golden file"). When is that brilliant, and when is
   it a trap? (Hint: what happens on an *intentional* logic change?)
3. Which is worse: a flaky test or no test? Defend your answer with what
   flakiness does to a team's response to red.

(Suggested answers: [`solutions/reflections.md`](solutions/reflections.md).)

## Further reading

- [pytest documentation — how-tos](https://docs.pytest.org/en/stable/how-to/index.html)
- [Testing data pipelines (Data Pipelines with Apache Airflow, ch. 9)](https://livebook.manning.com/book/data-pipelines-with-apache-airflow/chapter-9) — the same ideas at orchestrator scale.
- [Hypothesis — property-based testing](https://hypothesis.readthedocs.io/)

---

**Next:** [Module 04 — Functional Data Engineering](../04-functional-data-engineering/README.md):
tests guard the logic; now we make the pipeline's *runs* safe — starting
with the append bug we've been living with since Module 00.
