# Building audit-type apps with dbt

Patterns for a read-only app that turns platform metadata (system tables, account usage) into checks, cached locally and tested with fakes.

## Shape
```
platform metadata ──export (read-only SELECTs)──▶ parquet snapshot ──dbt (DuckDB)──▶ local .duckdb ──▶ API / UI
                  └─────────── same check SQL rendered for the platform dialect ───────────┘
```
- One check = one model with a stated grain, a status column (`OK` / `WARN` / `CRITICAL` / `NOT_ASSESSED`) and a reason column.
- Sources point at snapshot files (DuckDB `read_parquet` via `meta.external_location`); a `test` target points at fixture parquet.
- `meta` on each source table: `time_column`, `retention_days` — the app uses them to clamp windows.

## Rules that held up
- **As-of pinning:** `as_of_date()` / `as_of_ts()` macros: test target → fixed literal; else an `as_of` var (regex-validated); else the dialect's current date. Every window anchors on it.
- **Vars with defaults** in `dbt_project.yml` so `dbt parse` never fails; the wrapper merges config files into one `--vars` JSON.
- **Thresholds as a macro** (`threshold(check_id, name, default)`): per-check override → global override → header default; strings quoted and escaped.
- **Schema names verbatim** (`generate_schema_name` override) so the app reads `<checks_schema>.<check>` on every target — only safe when each target writes to its own database file.
- **Grain test on every check:** a generic grain test (e.g. `dbt_utils.unique_combination_of_columns`, or an own one passed to `dbt_inventory.py health --pk-tests`); severity from a var (`warn` on real snapshots, `error` on fixtures).
- **Reconciliation as a singular test:** the split total must equal the bill within 0.005 currency units; fails the build when a split loses money.
- **Adapter guard:** models that only work on DuckDB raise `exceptions.raise_compiler_error` on other targets; the platform twin lives elsewhere.
- **Generated models carry a GENERATED marker**; the generator refuses to overwrite hand-edited files and has a `--check` mode (stale / missing / extra) run in CI.
- **Second-dialect render:** models rendered offline for the platform with `enabled=false` in dbt, so dbt never builds them but one source of SQL serves both.
- **Atomic build:** dbt builds into a temp copy of the database; swap in with `os.replace` only after reading `run_results.json` (not just the exit code): no results file = parse failure, keep the old db; some models succeeded = swap and exit with a distinct code.
- **Read-only open** of the local db by the app; refresh writes a new file.
- **Not assessed ≠ empty:** a check whose source the role can't read emits one explicit `NOT_ASSESSED` row with the reason, never zero rows.
- **Money:** one price per row from a de-duplicated price interval (end capped at the next start); credits/DBUs and currency in separate columns; list price labelled as such.
- **Identity masking** by macro behind a var (hash prefix + first characters), applied in the model, not the UI.
- **Tests with fakes:** a fake account (fixture parquet with synthetic values covering every check's edge cases), a fixed as-of date, and assertions that totals from different checks agree (same total at 7 / 30 / 90 days).
- **No anonymous usage events:** `flags: send_anonymous_usage_stats: false`.

## Questions
| Question | How |
|---|---|
| How do I add a check? | Model with grain comment + status/reason → YAML with the grain test + `not_null` keys → fixture rows for OK / WARN / NOT_ASSESSED → unit test on the status logic |
| How do I keep two dialects in sync? | One SQL source, generator renders both, `--check` in CI; no hand edits in generated files |
| How do I test without a warehouse? | DuckDB target over fixture parquet; unit tests; never real data in fixtures |
| How do I know the window is valid? | `window_days ≤ retention_days` of every source read; window ends before the view's latency |
