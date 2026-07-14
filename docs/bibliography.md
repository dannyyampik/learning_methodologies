# Bibliography & research sources

The sources consulted while designing this course (July 2026), grouped by
the module they most inform. Each module's README carries its own
"Further reading"; this is the consolidated list.

## The canon (read these regardless)

- Maxime Beauchemin — [Functional Data Engineering: a modern paradigm for batch data processing](https://maximebeauchemin.medium.com/functional-data-engineering-a-modern-paradigm-for-batch-data-processing-2327ec32c42a) — the essay Module 4 is built on.
- MIT — [The Missing Semester of Your CS Education](https://missing.csail.mit.edu/) — the proof that tooling-craft courses work; a structural model for this one.
- Google — [SRE Book: Service Level Objectives](https://sre.google/sre-book/service-level-objectives/) and [Postmortem Culture](https://sre.google/sre-book/postmortem-culture/) — Module 7's operational discipline, nearly unedited.

## Software engineering practices in data engineering (Modules 0–2)

- lakeFS — [Data Engineering Best Practices](https://lakefs.io/blog/data-engineering-best-practices/)
- dbt Labs — [Best practices for modern data engineering](https://www.getdbt.com/blog/data-engineering)
- Secoda — [How to apply software engineering practices in data engineering](https://www.secoda.co/blog/how-to-apply-software-engineering-practices-in-data-engineering)
- MotherDuck — [Data engineering toolkit: infrastructure & DevOps](https://motherduck.com/blog/data-engineering-toolkit-infrastructure-devops/)
- cbeams — [How to write a Git commit message](https://cbea.ms/git-commit/)
- [Trunk-Based Development](https://trunkbaseddevelopment.com/)
- The Twelve-Factor App — [Config](https://12factor.net/config)

## Testing (Module 3)

- Manning — [Data Pipelines with Apache Airflow, ch. 9: Testing](https://livebook.manning.com/book/data-pipelines-with-apache-airflow/chapter-9)
- Astronomer — [Testing your Apache Airflow DAGs](https://www.astronomer.io/blog/testing-your-apache-airflow-dags/)
- Dagster — [Smoke test your data pipelines first](https://dagster.io/blog/smoke-test-data-pipeline)
- [pytest documentation](https://docs.pytest.org/) · [Hypothesis](https://hypothesis.readthedocs.io/)

## Functional data engineering (Module 4)

- Data Engineering Weekly — [Functional Data Engineering: a blueprint](https://www.dataengineeringweekly.com/p/functional-data-engineering-a-blueprint)
- SSENSE Tech — [Let's Get 'Idempotence' Right](https://medium.com/ssense-tech/lets-get-idempotence-right-59f227178bb8)
- ssp.sh — [Functional Data Engineering (notes)](https://www.ssp.sh/brain/functional-data-engineering/)

## Data quality & contracts (Module 5)

- dbt — [Data tests documentation](https://docs.getdbt.com/docs/build/data-tests) and [Building a data quality framework with dbt](https://www.getdbt.com/blog/building-a-data-quality-framework-with-dbt-and-dbt-cloud)
- Metaplane — [dbt-expectations](https://github.com/metaplane/dbt-expectations)
- Datadog — [Implement dbt data quality checks with dbt-expectations](https://www.datadoghq.com/blog/dbt-data-quality-testing/)
- Datacoves — [dbt testing: a complete guide](https://datacoves.com/post/dbt-test-options)
- Gable — [Data contract tools](https://www.gable.ai/blog/data-contract-tools)
- SYNQ — [Data observability guide](https://www.synq.io/blog/data-observability-guide)

## CI/CD, DataOps & Write-Audit-Publish (Module 6)

- Ascend — [CI/CD for data teams: roadmap to reliable pipelines](https://www.ascend.io/blog/ci-cd-for-data-teams-a-roadmap-to-reliable-data-pipelines)
- Databricks — [What is DataOps](https://www.databricks.com/blog/what-is-dataops) and [CI/CD best practices on Databricks](https://docs.databricks.com/aws/en/dev-tools/ci-cd/best-practices)
- lakeFS — [What is Write-Audit-Publish?](https://lakefs.io/blog/what-is-write-audit-publish/) and [WAP as a data engineering pattern](https://lakefs.io/blog/data-engineering-patterns-write-audit-publish/)
- dbt Labs — [Testing is not enough: WAP](https://www.getdbt.com/blog/testing-is-not-enough-transforming-data-quality-with-write-audit-publish)
- Calogica — [Blue-green data warehouse deployments with BigQuery and dbt](https://calogica.com/sql/bigquery/dbt/2020/05/24/dbt-bigquery-blue-green-wap.html)
- Julien Hurault — [The WAP pattern](https://juhache.substack.com/p/write-audit-publish-wap-pattern)

## Orchestration & operations (Module 7)

- Dagster — [DataOps with Dagster: a practical guide](https://dagster.io/blog/dataops-with-dagster-a-practical-guide-to-building-a-reliable-data-platform)
- Airflow — [DAG runs & the logical date](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dag-run.html)
- Datadog — [Understanding data lineage](https://www.datadoghq.com/blog/data-lineage/)
- Modern Data 101 — [Pillars of data observability](https://medium.com/@community_md101/5-key-pillars-of-data-observability-to-know-in-2026-814515c22a04)

## Exemplar courses studied for structure

- DataTalksClub — [Data Engineering Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp)
- [Portable data stack (Dagster + dbt + DuckDB + Docker)](https://github.com/cnstlungu/portable-data-stack-dagster) and the local-first data stack pattern
- KDnuggets — [10 GitHub repositories to master data engineering](https://www.kdnuggets.com/10-github-repositories-to-master-data-engineering)
