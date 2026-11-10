---
name: darshan-singh-meel-data-platform
description: Rules for data platform work — SQL, dbt, Snowflake, Databricks, Spark/PySpark, Athena, Iceberg, Python, Airflow, Azure Data Factory, Terraform, AWS S3 and Azure storage, RBAC, and data governance — including using current versions and checking official documentation when in doubt. Use whenever writing, reviewing, deploying, or documenting anything on that stack.
---

# Data Platform Rules

Read only the reference files for the tools in the task. Same rules apply when writing and when reviewing.

| Tool / topic | File |
|---|---|
| SQL (any engine) | `references/sql.md` |
| dbt | `references/dbt.md` |
| Snowflake (incl. RBAC, cost) | `references/snowflake.md` |
| Databricks, Spark/PySpark (any platform), Delta, Unity Catalog | `references/databricks.md` |
| Athena, Glue Data Catalog | `references/athena.md` |
| Iceberg tables | `references/iceberg.md` |
| Python pipelines, pandas | `references/python.md` |
| Airflow | `references/airflow.md` |
| Azure Data Factory / Synapse pipelines | `references/adf.md` |
| Terraform | `references/terraform.md` |
| AWS S3, Azure Blob / ADLS | `references/cloud-storage.md` |
| Access model across all platforms | `references/rbac.md` |
| Data governance: ownership, classification, lineage, retention | `references/governance.md` |
| Minimal tests for data work | `references/testing.md` |

Querying data (checks, analysis, metadata) → always via `darshan-singh-meel-notebook`: notebook cells only, Claude runs read-only SELECTs only.

## Rules for every tool
- **Grain first.** State what one row means before writing a query, model, or table.
- **Idempotent.** Rerunning a job, task, or `terraform apply` gives the same result. No blind appends.
- **Least privilege.** Groups/roles get access, never individual users. Service identities per pipeline. No admin roles in pipelines.
- **No secrets in code.** Use the secrets manager, key-pair auth, managed identity, or IAM roles. Names only in docs.
- **Everything as code.** Infra and grants in Terraform or migration scripts; no manual console changes.
- **Push work to the engine.** Transform in the warehouse/Spark, not in Python loops.
- **Mind cost.** Scan less, compute less, auto-suspend, right-size. Flag changes that raise cost.
- **Destructive changes need a yes.** `DROP`, `CREATE OR REPLACE` on tables, `--full-refresh`, `terraform destroy`, `VACUUM` with short retention, bucket/container deletes — ask first.
- **Environments separate.** Dev/test/prod isolated by database/catalog/account/state; never test against prod data writes.

## Versions and official documentation
- **Use current features — of the version the project actually runs.** First check pinned versions: `requirements*.txt` / `pyproject.toml` / lock files, `dbt_project.yml` (`require-dbt-version`) and `packages.yml`, Terraform `required_version` / `required_providers`, Airflow version and providers, Databricks runtime, Spark version, ADF/ARM API versions, Snowflake features enabled.
- Write code for that version, using its newest stable features. Never use a feature the pinned version doesn't have; never use deprecated syntax when a supported replacement exists.
- Nothing pinned (new project) → use the latest stable release, and pin it.
- **A newer version has a clearly better way** for the task at hand (simpler code, a real fix, better performance or security): before writing, say so in 2–3 lines — what the newer version offers, what the upgrade involves — and ask one question:
  - Use the pinned version (works now, no upgrade) (Recommended unless the gain is large) · Upgrade to <version> and use <feature>
  - Example: `dbt 1.7 is pinned. 1.9 adds microbatch incremental models, which would replace the custom lookback macro (~40 lines). Upgrade means bumping dbt-core + adapter and re-running CI.`
- Never upgrade without that yes. No answer → stay on the pinned version.
- **When in doubt** (syntax, defaults, limits, behaviour, deprecations, version support), check the **official docs** — and only these sites. Never send code, data, or project names in a search. Name the page used in one line.

| Technology | Official docs |
|---|---|
| Snowflake | docs.snowflake.com |
| Databricks | docs.databricks.com |
| Spark / PySpark | spark.apache.org/docs |
| Delta Lake | docs.delta.io |
| Iceberg | iceberg.apache.org/docs |
| dbt | docs.getdbt.com |
| Airflow | airflow.apache.org/docs |
| Python | docs.python.org · each library's own docs site |
| pandas | pandas.pydata.org/docs |
| Terraform | developer.hashicorp.com/terraform · registry.terraform.io (providers) |
| AWS (S3, Athena, Glue, IAM, Lake Formation) | docs.aws.amazon.com |
| Azure (ADF, Storage, Entra ID, Synapse) | learn.microsoft.com |
| SQL standard behaviour | the engine's own docs above |

