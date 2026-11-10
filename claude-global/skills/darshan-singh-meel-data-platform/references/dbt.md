# dbt

## Structure
- Always `{{ ref() }}` / `{{ source() }}`; never hardcode `db.schema.table`.
- Layers: staging (1:1 with source; rename, cast, light cleanup) → intermediate (joins, logic) → marts (consumer-facing).
- One model = one purpose = one grain. Put the grain in the model description.
- Sources declared with `freshness` for key tables. Contracts on shared/public models.

## Materialization
- View by default; table when heavy or heavily used; incremental only when a full rebuild is truly too slow.
- Incremental: `unique_key`, `{{ is_incremental() }}` with a lookback for late data, deliberate `incremental_strategy` (merge / delete+insert / insert_overwrite). `--full-refresh` must give the same result.
- Don't repeat project defaults in `config()`.

## Minimal
- Macros only for logic used 3+ times; prefer existing packages (`dbt_utils`) over custom macros.
- No Jinja loops generating huge SQL when plain SQL works.

## Tests
- `unique` + `not_null` on every model's primary key (`dbt_utils.unique_combination_of_columns` for composite keys).
- `relationships` only on critical foreign keys; `accepted_values` on status columns that drive logic.
- 1–2 tests on the riskiest business rule. Don't test every column.
- Never delete or weaken a failing test; `severity: warn` / `where:` only with a stated reason.

## Deploy & access
- CI against a CI schema: `dbt build --select state:modified+ --state <prod-manifest dir>` (+ `--defer`) if a manifest exists, else `--select <changed_model>+`. Prod runs from the orchestrator, not laptops.
- Separate targets per environment; credentials from env vars or secrets, never in a committed `profiles.yml`. Verify without opening it: `git ls-files` + a script reporting key names / `env_var(` use only.
- Grants via `grants:` config (or post-hooks).
