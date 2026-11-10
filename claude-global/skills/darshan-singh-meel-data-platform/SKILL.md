---
name: darshan-singh-meel-data-platform
description: Rules for data platform work — SQL, dbt, Snowflake, Databricks, Spark/PySpark, Athena, Iceberg, Python, Airflow, Azure Data Factory, Terraform, AWS S3 and Azure storage, RBAC, and data governance — including using current versions and checking official documentation when in doubt. Use whenever writing, reviewing, deploying, or documenting anything on that stack.
---

# Data Platform Rules

Read only the reference files (`references/<file>`) for the tools in the task. Same rules apply when writing and when reviewing.

| Tool / topic | File | Official docs |
|---|---|---|
| SQL (any engine) | `sql.md` | the engine's own docs |
| dbt | `dbt.md` | docs.getdbt.com |
| Snowflake (incl. RBAC, cost) | `snowflake.md` | docs.snowflake.com |
| Databricks, Spark/PySpark (any platform), Delta, Unity Catalog | `databricks.md` | docs.databricks.com · spark.apache.org/docs · docs.delta.io |
| Athena, Glue Data Catalog | `athena.md` | docs.aws.amazon.com |
| Iceberg tables | `iceberg.md` | iceberg.apache.org/docs |
| Python pipelines, pandas | `python.md` | docs.python.org · pandas.pydata.org/docs · each library's own docs site |
| Airflow | `airflow.md` | airflow.apache.org/docs |
| Azure Data Factory / Synapse pipelines | `adf.md` | learn.microsoft.com |
| Terraform | `terraform.md` | developer.hashicorp.com/terraform · registry.terraform.io (providers) |
| AWS S3, Azure Blob / ADLS | `cloud-storage.md` | docs.aws.amazon.com · learn.microsoft.com |
| Access model across all platforms | `rbac.md` | IAM, Lake Formation → docs.aws.amazon.com · Entra ID → learn.microsoft.com |
| Data governance: ownership, classification, lineage, retention | `governance.md` | — |
| Minimal tests for data work | `testing.md` | — |

Querying data (checks, analysis, metadata) → always via `darshan-singh-meel-notebook`: notebook cells only; what Claude may execute: notebook skill, "What Claude may execute".

## Rules for every tool
- **Grain first.** State what one row means before writing a query, model, or table.
- **Idempotent.** Rerunning a job, task, or `terraform apply` gives the same result. No blind appends.
- **Least privilege.** Groups/roles get access, never individual users. Service identities per pipeline. No admin roles in pipelines.
- **No secrets in code.** Use the secrets manager, key-pair auth, managed identity, or IAM roles. Names only in docs.
- **Everything as code.** Infra and grants in Terraform or migration scripts; no manual console changes.
- **Push work to the engine.** Transform in the warehouse/Spark, not in Python loops.
- **Mind cost.** Scan less, compute less, auto-suspend, right-size. Flag changes that raise cost.
- **Destructive changes need a yes.** `DROP`, `TRUNCATE`, unfiltered `DELETE`/`UPDATE`, `CREATE OR REPLACE` on tables, overwrite writes, `--full-refresh` outside dev, `terraform destroy` or replace (`-/+`), `VACUUM` with short retention, snapshot expiry, bucket/container deletes, anything else that loses data — ask first. The yes covers writing it; the user runs it, never Claude.
- **Environments separate.** Dev/test/prod isolated by database/catalog/account/state; never write to prod while testing.

## Versions and official documentation
- **Use current features — of the version the project actually runs.** First check pinned versions: `requirements*.txt` / `pyproject.toml` / lock files, `dbt_project.yml` (`require-dbt-version`) and `packages.yml`, Terraform `required_version` / `required_providers`, Airflow version and providers, Databricks runtime, Spark version, ADF/ARM API versions, Snowflake features enabled.
- Write code for that version, using its newest stable features. Never use a feature the pinned version doesn't have; never use deprecated syntax when a supported replacement exists.
- Nothing pinned (new project) → use the latest stable release, and pin it.
- **A newer version has a clearly better way** for the task at hand (simpler code, a real fix, better performance or security): before writing, say so in 2–3 lines — what the newer version offers, what the upgrade involves — and ask one question:
  - Use the pinned version (works now, no upgrade) (Recommended) · Upgrade to <version> and use <feature>. If the gain is large, list Upgrade first and recommend it.
  - Example: `dbt 1.7 is pinned. 1.9 adds microbatch incremental models, which would replace the custom lookback macro (~40 lines). Upgrade means bumping dbt-core + adapter and re-running CI.`
- Never upgrade without that yes. No answer → stay on the pinned version.
- **When in doubt** (syntax, defaults, limits, behaviour, deprecations, version support), check the **official docs** — only the sites in the table above. Never send code, data, or project names in a search. Name the page used in one line.
