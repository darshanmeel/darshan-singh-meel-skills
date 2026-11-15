# Jinja, macros, hooks, grants

## Macros
- Write one only for logic used 3+ times or for adapter differences; check `dbt_utils` first.
- Dispatch for adapters: `{% macro my_date_add(d, n) %}{{ return(adapter.dispatch('my_date_add')(d, n)) }}{% endmacro %}` + `default__my_date_add`, `snowflake__…`, `databricks__…`. Prefer cross-database macros already in dbt (`dbt.dateadd`, `dbt.datediff`, `dbt.safe_cast`, `dbt.type_string`).
- Branch on `target.type` only inside macros; raise on unsupported adapters: `{{ exceptions.raise_compiler_error("x is only built on duckdb") }}`.
- `{{ log(msg, info=true) }}` for debugging; `{{ print() }}` in Fusion check: docs.getdbt.com/docs/fusion.
- `execute` is false at parse time: guard `run_query()` with `{% if execute %}`; introspective macros (`run_query`, `adapter.get_columns_in_relation`, `dbt_utils.get_column_values`) make compile connect and slow every parse.
- Whitespace: `{%-  -%}` to keep compiled SQL readable.
- Strings into SQL: escape quotes (`| replace("'", "''")`); validate vars with `modules.re.match` before splicing.
- No Jinja loops generating hundreds of columns when a pivot or plain SQL works.

## Hooks
| Hook | Runs | Use |
|---|---|---|
| `pre-hook` / `post-hook` (model) | Before / after the model's SQL, same connection | Session settings, `OPTIMIZE`, audit inserts |
| `on-run-start` / `on-run-end` (project) | Once per invocation | Create schemas, log invocation, grants on schemas |
- Hooks run with the model's role: keep them idempotent and cheap; failures fail the model.
- `on-run-end` has `results` (status per node): write a run log there instead of parsing logs.
- Avoid `GRANT` in hooks; use `grants:`.

## Grants
```yaml
models:
  my_project:
    marts:
      +grants:
        select: ['reporter', 'bi_reader']
```
- dbt applies the diff on each build; `+grants` with `+` in YAML appends to inherited grants (check: docs.getdbt.com/reference/resource-configs/grants).
- Snowflake: `copy_grants: true` keeps manual grants across rebuilds; default `false` adds `IGNORE GRANTS`.
- Databricks: grants on Unity Catalog objects; `databricks_tags` add UC tags and are not removed by dbt.
- Schema-level future grants are platform DCL: write them for the user's changes notebook, never run them.

## Query tags and comments
- Default query comment: JSON `{"app": "dbt", "dbt_version", "profile_name", "target_name", "node_id"}`; on Snowflake it is appended at the end (Snowflake strips leading comments) (docs: project-configs/query-comment).
- Snowflake `query_tag` config per model/folder sets the session tag; reset after the model; a failure mid-build can leave it set.
- A JSON query tag macro (`set_query_tag` override, or a package) with `node_id`, `invocation_id`, `materialized`, `target_name` makes cost per model exact (performance-cost.md S1).
- Databricks (dbt-databricks 1.11+): `query_tags` at connection or model level, max 20 tags, values ≤ 128 chars; reserved keys `@@dbt_model_name`, `@@dbt_core_version`, `@@dbt_databricks_version`, `@@dbt_materialized` (docs: databricks-configs). Read them in `system.query.history.query_tags`.

## Question catalogue
| Question | How | Read it | Pitfall |
|---|---|---|---|
| Why is `dbt parse` slow? | `dbt_inventory.py health` → `introspective_macros` (models calling run_query / get_column_values) | One row per model | Each introspective call = a warehouse query at compile |
| Which macros are unused? | `dbt_inventory.py macros` (project macros with no `depends_on.macros` reference) | Name, file | Macros called from hooks or YAML may not appear in depends_on |
| How do I write X for both Snowflake and Databricks? | `adapter.dispatch` + per-adapter macros | — | Test compile on each target (user runs `dbt compile --target <t>`) |
| Where is this macro used? | `dbt_inventory.py macro-users <name>` | Nodes depending on it | Packages' macros: use the full `package.macro` id |
| Is the query tag set on dbt queries? | performance-cost.md S1: `tagged_pct` per node (Snowflake); D1 on Databricks: statements whose `node` has no `model.` prefix came from the tag only | `tagged_pct` near 100 | Only queries after the change carry it |
| Are grants applied as configured? | Snowflake `SHOW GRANTS ON TABLE <t>`; Databricks `SHOW GRANTS ON TABLE <t>` | Privilege, grantee | `copy_grants` false drops manual grants on rebuild |
