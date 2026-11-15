# Materializations, incremental models, snapshots

## Materializations
| Type | Use when | Cost / risk |
|---|---|---|
| view | Default; light logic, few reads | Every read recomputes |
| table | Heavy logic or many reads | Full rebuild each run |
| incremental | Full rebuild too slow or costly | Logic must equal a full refresh |
| ephemeral | Small reusable CTE | Not queryable; can't be deferred; hard to debug |
| materialized_view (Databricks, others) / dynamic_table (Snowflake) | Warehouse-managed refresh | Config changes often drop and recreate; Snowflake dynamic table SQL change needs `--full-refresh` |
- Snowflake tables from dbt are **transient by default** (no fail-safe, 1-day time travel); set `+transient: false` for tables that need recovery (docs: snowflake-configs).

## Incremental strategies per adapter (docs: incremental-strategy, snowflake-configs, databricks-configs)
| Strategy | Snowflake | Databricks | Needs | Use for |
|---|---|---|---|---|
| merge | Default | Default (Delta, Hudi) | `unique_key` | Upserts by key |
| delete+insert | Yes (needs temp table, not `tmp_relation_type: view`) | 1.11+, Delta, needs `unique_key` | `unique_key` | Key not unique in target ("nondeterministic merge") or batch replace by key |
| insert_overwrite | Replaces the **whole table** (no partition overwrite) | Overwrites partitions / clusters; no `partition_by` → whole table | `partition_by` (Databricks) | Rebuild recent partitions (Databricks) |
| replace_where | — | Delta, uses `incremental_predicates` | predicates | Replace a date range |
| append | Yes | Yes | — | Immutable events, no dedupe |
| microbatch | Yes | Delta (implemented with replace_where) | `event_time`, `begin`, `batch_size` | Large time series, backfills, late data |

## is_incremental() and late data
```sql
{{ config(materialized='incremental', unique_key='order_line_id',
          incremental_strategy='merge', on_schema_change='append_new_columns') }}
select ...
from {{ ref('stg_erp__order_lines') }}
{% if is_incremental() %}
where updated_at >= (select dateadd(day, -3, max(updated_at)) from {{ this }})
{% endif %}
```
- `is_incremental()` is true only when: the target exists, it is a table, the model is incremental, and `--full-refresh` is not set.
- **Lookback** (`-3` days) catches late rows; merge on `unique_key` makes reprocessing idempotent. No lookback + `>` max → late rows lost forever.
- The `max()` subquery scans `{{ this }}`; on big targets filter it by a cluster/partition column or store the watermark.
- `unique_key` must be unique **in the new rows** too; duplicates → Snowflake "nondeterministic merge" error, Databricks merge error on multiple source matches. Dedupe with `qualify row_number() over (partition by key order by updated_at desc) = 1`.
- Composite key: `unique_key=['order_id','line_no']`; NULL in a key column never matches → duplicates.
- `incremental_predicates` limit the target scan in merge (`DBT_INTERNAL_DEST.order_date >= dateadd(day,-7,current_date)`); rows older than the predicate are inserted again → duplicates.
- `on_schema_change`: `ignore` (default; new columns silently missing), `fail`, `append_new_columns`, `sync_all_columns` (drops removed columns). Neither backfills new columns: needs `--full-refresh` or a backfill.
- Full refresh must give the same result as the incremental history; check with an old-vs-new reconciliation (tests-contracts.md).
- `full_refresh: false` on huge or history-holding models stops an accidental `--full-refresh`.
- Deletes in the source: merge never deletes; Databricks `not_matched_by_source_action='delete'` (1.9+), else soft-delete flags or a snapshot.

## Microbatch (dbt 1.9+, docs: incremental-microbatch)
```sql
{{ config(materialized='incremental', incremental_strategy='microbatch',
          event_time='event_ts', begin='2024-01-01', batch_size='day', lookback=2) }}
select * from {{ ref('stg_app__events') }}   -- no is_incremental() block: dbt filters by batch
```
- Upstream `ref`/`source` with `event_time` set are filtered per batch; without it, **each batch scans the whole upstream**. Set `event_time` on upstream models.
- Backfill: `dbt run --select m --event-time-start "2025-01-01" --event-time-end "2025-01-31"` (both required). `dbt retry` reruns only failed batches.
- All times UTC. `concurrent_batches` overrides auto-detection.
- `--full-refresh` without `begin` does not reload; use both event-time flags with `--full-refresh`.

## Snapshots (YAML form, dbt 1.9+, docs: snapshots)
```yaml
snapshots:
  - name: customers_snapshot
    relation: ref('stg_crm__customers')
    config:
      schema: snapshots
      unique_key: customer_id
      strategy: timestamp
      updated_at: updated_at
      hard_deletes: new_record
      dbt_valid_to_current: "to_date('9999-12-31')"
```
- `timestamp` (recommended) needs a reliable `updated_at`; else `check` with explicit `check_cols` (not `all`).
- `hard_deletes`: `ignore` (default) · `invalidate` (old `invalidate_hard_deletes=true`) · `new_record` (adds `dbt_is_deleted`).
- Snapshots ignore `--full-refresh` and cannot be rebuilt: own schema, restricted grants, never drop.
- `unique_key` must be unique in the input: dedupe in a staging model first. Run on a schedule (hourly to daily); changes between runs are not captured.
- Current row: `dbt_valid_to is null` (or the `dbt_valid_to_current` value). Point-in-time join: `t.ts >= s.dbt_valid_from and t.ts < coalesce(s.dbt_valid_to, '9999-12-31')`.

## Question catalogue
| Question | How | Read it | Pitfall |
|---|---|---|---|
| Should this model be incremental? | Run time and cost per model (performance-cost.md S1, D1) + rows added per run | Incremental if full build is slow and new rows are a small share | Small tables: incremental adds complexity for nothing |
| Which strategy on Snowflake? | merge with key; delete+insert when the target holds duplicates by key; append for immutable events | — | Snowflake insert_overwrite rewrites the whole table |
| Which strategy on Databricks? | insert_overwrite / replace_where by date partition; merge for keyed upserts; microbatch for time series | — | insert_overwrite without partition_by replaces the table |
| Why does my merge fail with duplicate rows? | Duplicate check SQL below | Any row = key not unique in the new batch | Fix the source, don't switch strategy blindly |
| Are rows being lost to late data? | Compare source vs model counts per day for the last 14 days | Gap on recent days only = lookback too short | Run after the source's own latency |
| Does the merge scan the whole target? | performance-cost.md S5 / D5 | `partitions_scanned / partitions_total` near 1 | Add `incremental_predicates` on the cluster key |
| New column missing in the target? | `on_schema_change` of the model | `ignore` = silently dropped | New column NULL for old rows until backfill |
| Which incremental models have no unique_key / on_schema_change? | `dbt_inventory.py health` → `incremental_no_unique_key`, `incremental_no_on_schema_change` | One row per model | Append-only by design is fine: say so in the description |
| Is this snapshot capturing deletes? | `hard_deletes` config | `ignore` = deleted rows stay current | Legacy `invalidate_hard_deletes` → `hard_deletes` |
| Which snapshot rows are current twice? | SQL below | Any row = broken unique_key | Usually duplicates in the input |

```sql
-- Duplicate keys in the rows an incremental run would merge (run the model's select in a CTE)
with new_rows as ( /* paste the compiled select of the model, incremental branch */ select 1 as order_line_id )
select order_line_id, count(*) as n
from new_rows
group by order_line_id
having count(*) > 1
order by n desc
limit 100;

-- Snapshot: keys with more than one current row
select customer_id, count(*) as current_rows
from analytics.snapshots.customers_snapshot
where dbt_valid_to is null
group by customer_id
having count(*) > 1
limit 100;
```
