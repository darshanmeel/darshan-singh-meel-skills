---
name: darshan-singh-meel-data-platform
description: Cross-stack rules for data platform work — SQL, Spark/PySpark, Delta, Athena, Iceberg, Python, Airflow, Azure Data Factory, Terraform, AWS S3 and Azure storage, RBAC, and data governance — plus the shared rules (grain, idempotency, least privilege, destructive changes, current versions, official documentation when in doubt) that also hold for Snowflake, Databricks and dbt, whose deep work goes to darshan-singh-meel-snowflake, darshan-singh-meel-databricks and darshan-singh-meel-dbt. Use whenever writing, reviewing, deploying, or documenting anything on that stack.
---

# Data platform
Read only the refs (`references/<file>`) for tools in the task. Same rules for writing and reviewing.

| Topic | Ref | Official docs |
|---|---|---|
| SQL (any engine) | `sql.md` | the engine's docs |
| dbt (all dbt work) | `darshan-singh-meel-dbt` skill; `dbt.md` = pointer | docs.getdbt.com |
| Snowflake (questions · cost · performance · RBAC · pipelines · audit apps) | `darshan-singh-meel-snowflake` skill; `snowflake.md` = pointer | docs.snowflake.com |
| Databricks platform (Unity Catalog · compute · jobs · system tables · audit apps) | `darshan-singh-meel-databricks` skill | docs.databricks.com |
| Spark/PySpark (any platform), Delta | `databricks.md` | spark.apache.org/docs · docs.delta.io · docs.databricks.com |
| Athena, Glue | `athena.md` | docs.aws.amazon.com |
| Iceberg | `iceberg.md` | iceberg.apache.org/docs |
| Python, pandas | `python.md` | docs.python.org · pandas.pydata.org/docs · each library's docs |
| Airflow | `airflow.md` | airflow.apache.org/docs |
| ADF / Synapse pipelines | `adf.md` | learn.microsoft.com |
| Terraform | `terraform.md` | developer.hashicorp.com/terraform · registry.terraform.io |
| S3, Azure Blob/ADLS | `cloud-storage.md` | docs.aws.amazon.com · learn.microsoft.com |
| Access model | `rbac.md` | IAM, Lake Formation → docs.aws.amazon.com · Entra ID → learn.microsoft.com |
| Governance | `governance.md` | — |
| Minimal data tests | `testing.md` | — |

Snowflake · Databricks · dbt work → load that skill too (reviews → its `-review`). This skill = cross-stack rules below; stack skill = platform depth.

Querying data (checks, analysis, metadata) → always via `darshan-singh-meel-notebook`: notebook cells only; what Claude may execute: notebook skill, "Claude executes read-only only".

## Every tool
- Grain first: say what one row means before writing a query, model, or table.
- Idempotent: rerun (job, task, `terraform apply`) = same result; no blind appends.
- Least privilege: roles/groups, never users; one service identity per pipeline; no admin roles in pipelines.
- No secrets in code: secrets manager, key-pair, managed identity, IAM roles; names only in docs.
- Everything as code: infra and grants via Terraform or migrations; no manual console changes.
- Push work to the engine, not Python loops.
- Cost: scan less, compute less, auto-suspend, right-size; flag increases.
- Ask first: `DROP` · `TRUNCATE` · unfiltered `DELETE`/`UPDATE` · `CREATE OR REPLACE` table · overwrite writes · `--full-refresh` outside dev · `terraform destroy`/replace (`-/+`) · short-retention `VACUUM` · snapshot expiry · bucket/container deletes · anything else that loses data. Yes → Claude writes it; user runs it, never Claude.
- Dev/test/prod isolated (database, catalog, account, state); never write to prod while testing.

## Versions
- Check pins first: requirements/pyproject/locks · `dbt_project.yml` `require-dbt-version` + `packages.yml` · Terraform `required_version`/`required_providers` · Airflow + providers · Databricks runtime · Spark · ADF/ARM API · Snowflake features.
- Write for the pinned version, its newest stable features. Never features it lacks; never deprecated syntax with a supported replacement.
- Nothing pinned → latest stable, pin it.
- Newer version clearly better for this task (simpler, real fix, faster, safer) → before writing, 2–3 lines (what it offers, what upgrading takes) + ask: Pinned version (rec) · Upgrade to <version> and use <feature>; gain large → Upgrade first + rec.
  e.g. `dbt 1.7 pinned; 1.9 microbatch replaces the ~40-line lookback macro; upgrade = bump dbt-core + adapter, rerun CI.`
- No yes → no upgrade.

## Official docs
- In doubt (syntax, defaults, limits, behaviour, deprecations, version support) → official sites above only. Never send code, data, project names. Cite the page in one line.
