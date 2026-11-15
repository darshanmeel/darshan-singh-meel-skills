# Review checklist

Reference files named here are in `darshan-singh-meel-dbt/references/`.

## 1. Models and layering (project-layout.md)
- Only staging reads `source()`; no hard-coded `db.schema.table` (`health` → `hardcoded_relations`).
- Grain stated in the description and true: the final select is unique on the stated key (look for joins to non-unique sides).
- Joins: each join's key named; a 1:n join before an aggregate → fan-out → Must. Inner join to a dimension that can miss keys → silently dropped rows.
- `select *` in marts passes upstream renames silently → Should.
- Config only where it differs from folder defaults.

## 2. Incremental models and snapshots (incremental-snapshots.md)
- Strategy exists on the adapter and does what the author thinks (Snowflake `insert_overwrite` = whole table).
- `unique_key` unique in the new rows (dedupe step present), no NULL key parts.
- `is_incremental()` filter has a lookback that covers the source's late-arrival time; `>` without lookback → Must when late data exists.
- `incremental_predicates` window ≥ the lookback, else duplicates.
- `on_schema_change` chosen; new columns backfilled or the gap documented.
- Full-refresh parity: the incremental branch and full branch give the same rows (unit test with `is_incremental` override, or a reconciliation query).
- Microbatch: `event_time` on upstream models, `begin`, `batch_size`; no `is_incremental()` block needed.
- Snapshots: `strategy`, reliable `updated_at` or explicit `check_cols`, `hard_deletes` chosen, own schema, no legacy `invalidate_hard_deletes`.

## 3. Tests and contracts (tests-contracts.md)
- PK test per model (`unique` + `not_null` or combination test); `relationships` on critical FKs.
- Test arguments under `arguments:` on dbt ≥ 1.10.5.
- No weakened test (`severity: warn`, `where:`) without a stated reason.
- Contract on public models; data types match the adapter's names; constraint kinds the adapter enforces (Snowflake: `check` unsupported; Databricks: `unique` unsupported).
- Unit tests list every input; incremental logic tested with the override.

## 4. Macros, hooks, grants (jinja-macros-hooks.md)
- Introspective macros guarded by `execute`; no `run_query` in models without need.
- Vars spliced into SQL validated; `var()` defaults present.
- Grants via `grants:`, not hooks; hooks idempotent.

## 5. Selection, CI, deploy (selection-ci.md, engines.md)
- Slim CI command uses `state:modified+`, `--defer`, a prod manifest from a compatible version.
- Env-aware config that marks everything modified → Should.
- Version-gated features match the pinned dbt and adapter version.

## 6. Analysis queries and answers (performance-cost.md, query-delivery.md)
- Every view, column and function exists (reference table or docs); wrong name → Must.
- Join keys and cardinality: `QUERY_ATTRIBUTION_HISTORY` ↔ `QUERY_HISTORY` on `query_id`, one row per query expected but not stated by the docs → the guard cell (`count(*) = count(distinct query_id)`) is present; a join on `warehouse_name` or time → fan-out → Must; price joined once per row on a de-duplicated interval; `billing.usage` net of `RETRACTION`/`RESTATEMENT`.
- Window: ends before the view's latency (8 h attribution, 45 min query history, 3 h access history, ~1 h Databricks query history); length ≤ retention (365 days, attribution complete from mid-Aug 2024).
- One UTC as-of timestamp across the topic (pinned in `ANALYSIS_AS_OF`, Snowflake session `TIMEZONE = UTC`); no `current_timestamp()` mixed with a fixed `AS_OF`.
- Counts after a left join use a column of the right side (`count(l.col)`), not `count(*)`; `invocations` is not read as runs without an `invocation_id` tag.
- Cell SQL is a raw string (`r"""`) when it holds regex backslashes; else the regex silently matches nothing.
- Units: credits / DBUs vs currency in separate columns; list vs contract price labelled; cloud services credits not added per query.
- "Not assessed" vs zero: missing privilege, missing query tag, `(dbt, no node)` share stated.
- Identities aggregated or masked; query text never shown, only `node_id` extracted.
- Read-only: `SELECT`/`WITH`/`SHOW`/`DESCRIBE`/`EXPLAIN` only; no `system$`, `CALL`, `USE`; `check_queries.py` → 0 ERROR. It sees only SQL written in the cells: read every code cell anyway (SQL built at run time, read from files, or in helper functions).
- Notebook structure: `00_connection.ipynb` first with env-var names only and a test SELECT; markdown (what · reads · joins · grain · look for) before every query; findings in the author's voice.
- SQL files: header per file; numbered in run order.
- The answer matches the query: the stated number would come out of that SQL with that grain.
- Next query offered and sensible.

## 7. Audit-type apps on dbt (audit-app-patterns.md)
- Each check: grain, status and reason columns, explicit `NOT_ASSESSED` row when the source is unreadable.
- As-of pinning used everywhere; fixtures synthetic; totals that should agree across checks are tested.
- Generated files carry a marker and a `--check` mode runs in CI.
- Build swaps the local database only after reading `run_results.json`.

## 8. Secrets and paths
- No credentials, tokens, keys, connection strings in models, YAML, notebooks, SQL or the answer; names only.
- No absolute machine paths; no real account, workspace, customer or person names in templates or examples.
