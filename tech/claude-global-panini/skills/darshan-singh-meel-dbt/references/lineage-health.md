# Lineage, impact, project health

All offline: `target/manifest.json` (from `dbt parse`, which does not connect) and `target/run_results.json` (from the user's last run). `scripts/dbt_inventory.py` reads structure only: names, resource types, `depends_on`, config, tests, columns' names, `raw_code` (for refs and joins). It never prints `compiled_code`, test failures or data.

## Script
```
python <skill>/scripts/dbt_inventory.py <manifest.json> health [--pk-tests unique,unique_combination_of_columns,<own>]  # every health check
python <skill>/scripts/dbt_inventory.py <manifest.json> impact <model>    # downstream nodes, tests, exposures
python <skill>/scripts/dbt_inventory.py <manifest.json> upstream <model>  # all parents incl. sources
python <skill>/scripts/dbt_inventory.py <manifest.json> joins <model>     # models joining <model> (either side), ON / USING text; children with no parsed join listed
python <skill>/scripts/dbt_inventory.py <manifest.json> column-users <model> <column>  # children using the column, select * pass-throughs, tests on it
python <skill>/scripts/dbt_inventory.py <manifest.json> relations [--select-prefix models/marts]  # relation names for S6/D6
python <skill>/scripts/dbt_inventory.py <manifest.json> macros            # project macros nothing depends on
python <skill>/scripts/dbt_inventory.py <manifest.json> macro-users <macro>
python <skill>/scripts/dbt_inventory.py <run_results.json> timing [--type model|test] [--top 20] [--order duration|started]
```
- No manifest → ask the user to run `dbt parse` (offline) or, with a yes, Claude runs it from the project dir.
- Manifest from another dbt version than the project → say so; schema v12 covers dbt 1.8–2.0 (docs: artifacts/manifest-json).

## Health checks (`health`)
| Check | Rule | Why it matters |
|---|---|---|
| `untested_models` | model with no data test attached | Silent breakage |
| `no_pk_test` | no `unique` or `unique_combination_of_columns` test (own grain tests: `--pk-tests`) | Duplicates fan out downstream |
| `sources_without_freshness` | source table with no freshness | Stale data goes unnoticed |
| `source_outside_staging` | non-staging model depends on a source | Layering broken |
| `orphan_models` | model with no children and no exposure | Unused cost, or an undeclared consumer |
| `fan_out` | top models by number of direct children | Change risk is highest here |
| `many_parents` | models with > 8 direct parents | Hard to reason about; split |
| `incremental_no_unique_key` | incremental without `unique_key` (not append/microbatch) | Duplicates on reprocessing |
| `incremental_no_on_schema_change` | incremental with default `ignore` | New columns silently missing |
| `public_no_contract` | `access: public` without enforced contract | Breaking changes reach consumers |
| `no_description` | model without description | Grain unknown |
| `no_group` | mart model without group | No owner |
| `warn_tests` | tests with `severity: warn` | Warnings nobody reads |
| `hardcoded_relations` | `raw_code` with `from|join db.schema.table` not in Jinja | Breaks environments and lineage |
| `introspective_macros` | `raw_code` calling `run_query`, `get_column_values`, `get_columns_in_relation`, `dbt_utils.star` | Compile connects; slow parse |
| `deprecated_configs` | snapshots with `invalidate_hard_deletes` (dbt's own deprecation warnings cover the rest) | Upgrade blockers (Fusion requires none) |
| `seeds_without_column_types` | seed without `column_types` | Types inferred, can flip |

## Question catalogue
| Question | How | Read it | Pitfall |
|---|---|---|---|
| What breaks if I change / drop model X? | `impact X` | Children by depth, tests, exposures | Other projects (mesh) and BI tools without exposures are not in the manifest → S6 / D6 for real reads |
| What breaks if I drop / rename column c of X? | `column-users X c`, then warehouse reads: S14 + S15 (Snowflake) / D14 (Databricks) | dbt children using c, `select *` pass-throughs (followed down), tests on c; roles and objects outside dbt reading c | Word match on `raw_code`: a column built in a macro or a same-named column of another model shows as a use — open the listed files |
| Which models join X, on which columns? | `joins X` | Model, alias, ON / USING text, X on either side | Regex-based: joins built in macros show as `depends on X but no join parsed` — open those files |
| Where does model X's data come from? | `upstream X` | Parents to sources | Ephemeral parents are inlined but still listed |
| Which models are never used? | `health` → `orphan_models`, then S6 / D6 for warehouse reads | No children + no reads 90 days | Marts consumed by BI look orphan until exposures exist |
| Which model fans out most? | `health` → `fan_out` | Children count | Base staging models naturally fan out |
| Which models are slowest in the last run? | `timing run_results.json --top 20` | `execute` seconds per node | One invocation only; queueing shows as slowness (S4 / D4) |
| Where did the run fail first? | `timing run_results.json --order started` | First `error` / `fail` by start time | Nodes without timing (skipped) sort last |
| Which tests failed or warned last run? | `timing run_results.json --type test` | status, failures count | Failing rows are not in the file (never read stored failures) |
| What is the critical path of a run? | `timing` (slowest nodes) + `upstream <slowest>` | Longest chain of slow sequential nodes | threads limit parallelism |
| How healthy is the project overall? | `health` counts | Share of models tested, documented, contracted | Counts, not a score; fix top-fan-out models first |
| Which sources feed exposure E? | `dbt ls --select +exposure:E --resource-type source` (offline) | Source list | — |
