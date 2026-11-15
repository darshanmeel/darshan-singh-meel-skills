# Project layout, sources, seeds, vars, packages

## Layers
| Layer | Folder | Does | Materialization |
|---|---|---|---|
| Sources | `models/staging/<source>/_<source>__sources.yml` | Declares raw tables, freshness, loaded_at | — |
| Staging | `models/staging/<source>/stg_<source>__<entity>.sql` | 1:1 with a source table: rename, cast, light cleanup, dedupe | view (or ephemeral) |
| Intermediate | `models/intermediate/<area>/int_<entity>_<verb>.sql` | Joins, business logic, re-grain | ephemeral or view; table if reused and heavy |
| Marts | `models/marts/<area>/fct_*.sql`, `dim_*.sql` | Consumer-facing, one grain each, tested and documented | table or incremental |
- One model = one grain, written in its description ("one row per order line per day").
- Only staging reads `source()`; everything else reads `ref()`. Never hard-code `db.schema.table`.
- Folder-level config in `dbt_project.yml` (`+materialized`, `+schema`, `+tags`); per-model `config()` only where it differs.

## Schemas and environments
- Default `generate_schema_name`: custom schema → `<target_schema>_<custom>` (dev isolation). Override it to use the custom name as-is only when every target writes to its own database; else dev runs overwrite prod schemas.
- `generate_database_name` / `generate_alias_name` follow the same rule.
- Targets: dev (per-developer schema), ci (per-PR schema), prod. `target.name` in Jinja for small differences (sample sizes), never for different logic.
- Credentials only via `env_var()` in `profiles.yml`; check without opening it: `git ls-files | grep profiles.yml` (should be empty or a template) and a script that lists `env_var(` names only.

## Sources and freshness
```yaml
sources:
  - name: erp
    database: raw
    schema: erp
    config:
      loaded_at_field: _loaded_at
      freshness:
        warn_after: {count: 6, period: hour}
        error_after: {count: 24, period: hour}
    tables:
      - name: orders
        columns:
          - name: order_id
            data_tests: [unique, not_null]
```
- Freshness config placement (`config:` vs top level) changed across versions → check: docs.getdbt.com/reference/resource-properties/freshness.
- `dbt source freshness` connects; writes `target/sources.json`; `source_status:fresher+` selects models downstream of fresher sources.
- No `loaded_at_field` → newer versions can use warehouse metadata for freshness on some adapters (check: docs.getdbt.com/docs/deploy/source-freshness).
- External files as sources: `meta.external_location` / `external` config are adapter- or package-specific (dbt-external-tables, DuckDB) — not portable.

## Seeds
- Small static lookups only (< ~1 MB, codes, mappings). Never data that changes daily or holds personal data.
- Column types in `seeds: <project>: <seed>: +column_types:`; else types are inferred and can flip (leading zeros lost).
- `seed-paths` can take `env_var()` to swap fixture seeds in a test target.

## Vars
- Declare every var with a safe default in `dbt_project.yml` so `dbt parse` works without `--vars`.
- Validate vars spliced into SQL (regex on dates) — `var()` text is not a bind parameter.
- Pin "today" with an `as_of` var for reproducible tests; default to the warehouse's current date.

## Packages
- `packages.yml` (or `dependencies.yml` for project dependencies in mesh) with pinned ranges: `version: [">=1.3.0", "<2.0.0"]`.
- Common: `dbt_utils` (surrogate keys, `unique_combination_of_columns`, `expression_is_true`), `dbt_expectations` (check maintainer: docs.getdbt.com hub), `dbt_project_evaluator` (layer and test-coverage rules), `dbt_artifacts` / platform metadata for run history.
- `dbt deps` writes `package-lock.yml`; commit it.

## Question catalogue
| Question | How | Read it | Pitfall |
|---|---|---|---|
| Where should this new logic live? | Grain + reuse: new grain → new model; same grain + one consumer → CTE in the mart | — | Logic in staging couples it to one source |
| Is the layering respected? | `dbt_inventory.py health` → `source_outside_staging` | Each row = a non-staging model reading `source()` | Packages' models are exempt |
| Why did my dev run write to prod schema? | Read `macros/generate_schema_name.sql` | Custom name used verbatim on all targets | Needs per-target database |
| Which sources have no freshness? | `dbt_inventory.py health` → `sources_without_freshness` | One row per source table | Freshness on huge tables without `loaded_at_field` scans the table |
| Is a source stale right now? | Warehouse SQL (performance-cost.md S11 / D12) or user runs `dbt source freshness` | `max_loaded_at` vs now | Timezone of `loaded_at_field` |
| Which seeds have inferred types? | `dbt_inventory.py health` → `seeds_without_column_types` | One row per seed | Never open seed files with personal data |
| Which package versions are pinned? | `packages.yml`, `package-lock.yml` | Ranges vs lock | Unpinned `git` packages float |
