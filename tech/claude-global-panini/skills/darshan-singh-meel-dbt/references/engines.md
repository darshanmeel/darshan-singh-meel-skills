# dbt Core, Fusion engine, dbt platform

| | dbt Core (v1.x) | Fusion engine | dbt platform (Cloud) |
|---|---|---|---|
| What | Python CLI, open source | Rust engine; docs.getdbt.com labels it "dbt v2" (check: docs.getdbt.com/docs/fusion) | Hosted IDE, jobs, CI, Catalog, Semantic Layer; runs Core "Latest" track or Fusion |
| SQL understanding | Jinja → text | Parses SQL: static analysis, column lineage, errors before the warehouse | Depends on engine |
| Adapters | All community adapters | Snowflake, Databricks, BigQuery, Redshift; Spark beta (CLI); DuckDB CLI only (docs: fusion supported-features) | Supported adapters |
| Lint | SQLFluff | `dbt lint` (replaces SQLFluff there) | Per engine |
| Upgrade gate | — | Latest v1 with zero deprecation warnings; packages declare `require-dbt-version` range including 2.0.0; Semantic Layer YAML on the latest spec | — |
| State / artifacts | `manifest.json` v12 | Same artifact versions (manifest v12 to 2.0; run_results v6) | Artifacts per job via API |
| Env vars | `DBT_*` and newer `DBT_ENGINE_*` (v1.11+) | `DBT_ENGINE_*` | Platform env vars |

## What connects to the warehouse
- No: `parse`, `ls`, `clean`; `deps` reaches the package hub only.
- Yes: `compile` (introspective queries), `docs generate` (catalog), `show`, `debug`, `run`, `build`, `test`, `seed`, `snapshot`, `run-operation`, `source freshness`, `clone`, `retry`.
- Fusion static analysis can need schemas of upstream relations (it fetches and caches them) → treat Fusion `compile` as connecting (check: docs.getdbt.com/docs/fusion).

## Version questions
| Question | Answer from |
|---|---|
| Which version is pinned? | `requirements*.txt` / `pyproject.toml` (`dbt-core`, `dbt-snowflake`, `dbt-databricks`), `require-dbt-version` in `dbt_project.yml` |
| Is feature X available? | Feature's docs page version note (microbatch 1.9+, unit tests 1.8+, test `arguments` 1.10.5+, snapshot YAML and `hard_deletes` 1.9+, dbt-databricks `query_tags` 1.11+, `delete+insert` on Databricks 1.11+) |
| Can we move to Fusion? | `dbt_inventory.py health` → `deprecated_configs` empty; every package's `require-dbt-version` includes 2.0.0; adapter in the supported list; custom materializations reviewed |
| Core vs platform for us? | Platform adds hosted CI with defer, Catalog, Semantic Layer APIs, job scheduling; Core needs an orchestrator (Airflow + Cosmos, Databricks Jobs dbt task, Snowflake tasks) and artifact storage for slim CI |
| dbt inside the platform itself? | Snowflake: dbt projects on Snowflake (check: docs.snowflake.com/en/user-guide/data-engineering/dbt-projects-on-snowflake) · Databricks: dbt task in Lakeflow Jobs (check: docs.databricks.com/aws/en/jobs/dbt) |
