# dbt

All dbt work — models, layering, materializations, incrementals, snapshots, tests and contracts, macros, selectors and slim CI, docs, semantic layer, performance, lineage, debugging — → `darshan-singh-meel-dbt` (review: `darshan-singh-meel-dbt-review`). Build rules there: `project-layout.md` (layers, naming, targets), `incremental-snapshots.md`, `tests-contracts.md`, `selection-ci.md`, `jinja-macros-hooks.md` (macros, hooks, grants).

## Cross-stack rules that apply here
- Adapters other than Snowflake and Databricks (Athena, DuckDB, Postgres, …): the dbt skill's rules still hold; adapter-specific configs from the adapter's page on docs.getdbt.com.
- Warehouse rules under the models: `sql.md`, and the Snowflake or Databricks skill.
- Orchestration: `airflow.md`, `adf.md`. Minimal tests for any data work: `testing.md`.
