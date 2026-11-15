# Debugging dbt errors

## Process
1. Which phase failed: parse (YAML, Jinja, refs) · compile (Jinja rendering, introspection) · run (warehouse SQL) · test (failing rows) · deploy (permissions, schemas).
2. Ask for the error text and the node (`unique_id`) — never read `logs/` or `target/run/` contents that may hold data; the user pastes the message.
3. Reproduce offline where possible: `dbt parse` / `dbt ls --select <node>`; compile and run are the user's (connect).
4. Fix the cause, not the symptom (never weaken a test, never `--full-refresh` as a fix without knowing why).

## Error catalogue
| Error (shape) | Phase | Cause | Fix |
|---|---|---|---|
| `Compilation Error … depends on a node named 'x' which was not found` | parse | Typo, disabled model, wrong package, versioned model | `dbt ls --select x`; check `enabled`, `ref('pkg','x')`, `v=` |
| `Found a cycle` | parse | Model refs a child | Move shared logic to an upstream model |
| `… attempted to reference node …, which is not allowed` | parse | `access: private` / group boundary | Make it `protected`/`public` or move it into the group |
| `'dict object' has no attribute …` / `'None' has no attribute` | compile | Var or config missing; `execute` false at parse | Default the var; guard with `{% if execute %}` |
| `Required var 'x' not found` | parse | Var without default | Declare in `dbt_project.yml` vars |
| `env var required but not provided` | parse | `env_var('X')` without default | Set the env var or a default (never a secret default) |
| `Database Error … nondeterministic merge` (Snowflake) | run | `unique_key` not unique in new rows | Dedupe; or `delete+insert` if by design |
| `MERGE … multiple source rows matched` (Databricks) | run | Same | Dedupe with `qualify row_number()` |
| `Object does not exist or not authorized` | run | Missing grant, wrong database/schema, role | Check target role grants; `generate_schema_name` |
| `invalid identifier` / `UNRESOLVED_COLUMN` | run | Column renamed upstream; quoting/case | Check upstream SQL; Snowflake upper-cases unquoted names |
| `Contract … mismatch` | run | Columns or types differ from YAML | Align SQL or YAML; types must match the adapter's names |
| `Incremental … schema change` / `on_schema_change: fail` | run | New/removed column | Choose `append_new_columns` / `sync_all_columns` + backfill |
| `Snowflake: Statement reached its statement or warehouse timeout` | run | Large scan, small warehouse | S3; `snowflake_warehouse` per model; pruning |
| Databricks `DELTA_CONCURRENT_APPEND` / `ConcurrentAppendException` | run | Two writers to the same table/partition | Serialize jobs; partition-scoped writes |
| `Got a dbt_scd_id error` on snapshot | run | Table materialized as table before | Drop the old table (user) and rerun the snapshot |
| Test `Got N results, configured to fail if != 0` | test | Data breaks the rule | Look at counts (notebook), fix source or model; never delete the test |
| `deprecation` warnings | parse | Old syntax | Fix before upgrading; Fusion requires zero deprecations |
| `Could not find profile named 'x'` | parse | `profile:` vs profiles.yml name | Check `dbt_project.yml` profile name (never open profiles.yml; ask the user) |
| `dbt was unable to connect` | debug | Credentials, network, role | User runs `dbt debug`; never print the profile |
| Packages: `version conflict` | deps | Two packages pin incompatible ranges | Widen the range or upgrade the other package |
| Unit test `node not found` | test | Input not listed in `given` | List every ref/source input |

## Questions
| Question | How | Read it |
|---|---|---|
| Why does the model build in dev but fail in prod? | Diff `target.name` branches, env vars, schema macro, grants | Env-specific Jinja or permission |
| Why are there duplicates after an incremental run? | incremental-snapshots.md duplicate check | Key not unique, NULL keys, predicate window |
| Why did the row count drop? | Source vs model counts per day (notebook) | Inner join to a dim missing keys → left join + test |
| Why did a test start failing today? | Test's SQL + counts by day of the offending rows | New source values (`accepted_values`), late dims (`relationships`) |
| Where did this run fail first? | `dbt_inventory.py run_results.json timing --order started` → first `error` | Children show `skipped` |
| Which statement did dbt run? | User looks at `target/run/<path>` or the warehouse query history (S8 / D8 by node) | Claude reads only structure, not stored SQL with data |
