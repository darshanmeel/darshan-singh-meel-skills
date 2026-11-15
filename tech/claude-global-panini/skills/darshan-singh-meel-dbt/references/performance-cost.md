# Performance and cost: Snowflake and Databricks

Every query here is read-only and goes through the chosen delivery (query-delivery.md). `:as_of` = one fixed UTC timestamp per topic (set in `00_connection`; Snowflake session `TIMEZONE = UTC`, else `TIMESTAMP_LTZ` columns shift by the offset), `:days` = window. In notebook cells the SQL is a raw string (`r"""`) so the regex backslashes below reach the warehouse unchanged; the catalogue is written as for a SQL editor. Names in `<angle brackets>` are the project's.

## Tuning levers
| Lever | Snowflake config | Databricks config |
|---|---|---|
| Compute per model | `snowflake_warehouse: transform_l` on heavy models only | `databricks_compute: <name>` (named computes in profile); Python models `http_path` / `submission_method` |
| Layout for pruning | `cluster_by: ['order_date']` on large (> ~1 TB) tables filtered by that column; auto clustering costs credits (S9) | `liquid_clustered_by` (runs `OPTIMIZE` after each run; `skip_optimize` 1.12.2+) or `auto_liquid_cluster`; `partition_by` only for low-cardinality date columns on large tables |
| Incremental window | `incremental_predicates` on the cluster key; lookback days, not weeks | `insert_overwrite` / `replace_where` per date partition; microbatch |
| Storage | `transient` (default true) for rebuildable tables | `tblproperties` (`delta.autoOptimize.*`, check: docs.databricks.com/aws/en/delta/tune-file-size) |
| Attribution | `query_tag` (JSON with node_id); comment appended by default | `query_tags` (1.11+); default comment in `statement_text` |
| Fewer rebuilds | views for light models; `+materialized: table` only where read often | same; materialized views are created from a Databricks SQL warehouse and refreshed by a serverless pipeline (check: docs.databricks.com/aws/en/views/materialized, compute requirements) |
| Tests | `where:` window on big-table tests; `limit` | same |

## Snowflake views used
| View | Grain | Latency | Retention | Key columns |
|---|---|---|---|---|
| `SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY` | one query | up to 45 min | 365 days | `QUERY_ID`, `QUERY_TEXT`, `QUERY_TAG`, `QUERY_TYPE`, `ROLE_NAME`, `USER_NAME`, `WAREHOUSE_NAME`, `WAREHOUSE_SIZE`, `EXECUTION_STATUS`, `ERROR_CODE`, `START_TIME`, `TOTAL_ELAPSED_TIME` (ms), `QUEUED_OVERLOAD_TIME` (ms), `BYTES_SCANNED`, `PARTITIONS_SCANNED`, `PARTITIONS_TOTAL`, `BYTES_SPILLED_TO_LOCAL_STORAGE`, `BYTES_SPILLED_TO_REMOTE_STORAGE`, `ROWS_INSERTED`, `ROWS_UPDATED` |
| `…ACCOUNT_USAGE.QUERY_ATTRIBUTION_HISTORY` | one query (not stated on the page; check: docs.snowflake.com/en/sql-reference/account-usage/query_attribution_history — guard in S1) | up to 8 h | 365 days (complete from mid-Aug 2024) | `QUERY_ID`, `QUERY_TAG`, `WAREHOUSE_NAME`, `CREDITS_ATTRIBUTED_COMPUTE`, `CREDITS_USED_QUERY_ACCELERATION`; excludes queries ≤ ~100 ms, idle time, cloud services, adaptive warehouses |
| `…ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY` | warehouse × hour | up to 3 h (check: docs.snowflake.com/en/sql-reference/account-usage/warehouse_metering_history) | 365 days | `WAREHOUSE_NAME`, `START_TIME`, `CREDITS_USED_COMPUTE`, `CREDITS_USED_CLOUD_SERVICES`, `CREDITS_ATTRIBUTED_COMPUTE_QUERIES` |
| `…ACCOUNT_USAGE.ACCESS_HISTORY` | one query | up to 3 h | 365 days; Enterprise edition | `QUERY_ID`, `QUERY_START_TIME`, `USER_NAME`, `BASE_OBJECTS_ACCESSED`, `DIRECT_OBJECTS_ACCESSED` (arrays: `objectName`, `objectDomain`, `columns[].columnName`), `OBJECTS_MODIFIED` |
| `…ACCOUNT_USAGE.OBJECT_DEPENDENCIES` | referencing × referenced object | up to 3 h | not stated (check: docs.snowflake.com/en/sql-reference/account-usage/object_dependencies) | `REFERENCED_DATABASE`, `REFERENCED_SCHEMA`, `REFERENCED_OBJECT_NAME`, `REFERENCED_OBJECT_DOMAIN`, `REFERENCING_DATABASE`, `REFERENCING_SCHEMA`, `REFERENCING_OBJECT_NAME`, `REFERENCING_OBJECT_DOMAIN`, `DEPENDENCY_TYPE` |
| `…ACCOUNT_USAGE.TABLE_STORAGE_METRICS` | one table | check: docs.snowflake.com/en/sql-reference/account-usage/table_storage_metrics | current + dropped | `TABLE_CATALOG`, `TABLE_SCHEMA`, `TABLE_NAME`, `ACTIVE_BYTES`, `TIME_TRAVEL_BYTES`, `FAILSAFE_BYTES`, `RETAINED_FOR_CLONE_BYTES`, `IS_TRANSIENT`, `DELETED` |
| `…ACCOUNT_USAGE.AUTOMATIC_CLUSTERING_HISTORY` | table × interval | up to 3 h (check: same site) | 365 days | `DATABASE_NAME`, `SCHEMA_NAME`, `TABLE_NAME`, `START_TIME`, `CREDITS_USED`, `NUM_BYTES_RECLUSTERED` |
- Visibility: `IMPORTED PRIVILEGES` on database `SNOWFLAKE`, or database roles `SNOWFLAKE.USAGE_VIEWER` / `GOVERNANCE_VIEWER`. Without them the views error or return nothing → "not assessed", never zero.
- Credits ≠ money. Currency per credit: `SNOWFLAKE.ORGANIZATION_USAGE.RATE_SHEET_DAILY.EFFECTIVE_RATE` or `USAGE_IN_CURRENCY_DAILY` (org-level, ORGADMIN-granted access, latency up to 72 h; check: docs.snowflake.com/en/sql-reference/organization-usage). Resolve one price for the window, paste it as `:price_per_credit`; never join a rate table per query (fan-out).
- Cloud services credits are billed only above 10% of daily compute; leave them out of per-model cost.

## Snowflake catalogue
**S1 — Cost per dbt model (credits)**
```sql
with q as (
  select q.query_id, q.start_time, q.warehouse_name, q.total_elapsed_time,
         try_parse_json(q.query_tag) as tag,
         try_parse_json(regexp_substr(q.query_text,
           '/\\*\\s*(\\{[^*]*"app"\\s*:\\s*"dbt"[^*]*\\})\\s*\\*/', 1, 1, 'e', 1)) as cmt
  from snowflake.account_usage.query_history q
  where q.start_time >= dateadd(day, -:days, :as_of) and q.start_time < :as_of
    and (q.query_tag ilike '%dbt%' or q.query_text ilike '%"app":%"dbt"%')
), d as (
  select query_id, start_time, warehouse_name, total_elapsed_time,
         coalesce(tag:node_id::string, cmt:node_id::string, '(dbt, no node)') as node_id,
         coalesce(tag:invocation_id::string, cmt:invocation_id::string) as invocation_id,
         tag:node_id is not null as tagged
  from q
)
select d.node_id,
       count(*) as queries,
       nullif(count(distinct d.invocation_id), 0) as invocations,   -- NULL unless a JSON tag carries invocation_id
       count(distinct date_trunc('hour', d.start_time)) as run_hours,
       count_if(d.tagged) / count(*) as tagged_pct,
       sum(d.total_elapsed_time) / 3600000 as elapsed_hours,
       sum(coalesce(a.credits_attributed_compute, 0)) as credits,
       sum(coalesce(a.credits_attributed_compute, 0)) * :price_per_credit as est_cost_list,
       any_value(d.warehouse_name) as a_warehouse
from d
left join snowflake.account_usage.query_attribution_history a on a.query_id = d.query_id   -- one row per query_id: run the guard first
group by d.node_id
order by credits desc
limit 100;
```
- Guard first (own cell): `select count(*) as n, count(distinct query_id) as ids from snowflake.account_usage.query_attribution_history where start_time >= dateadd(day, -:days, :as_of) and start_time < :as_of` → `n = ids`; else aggregate attribution by `query_id` before the join.
- Read: one row = one dbt node (`model.` / `test.` / `snapshot.` / `seed.`). `credits` = exact compute credits per query; idle time and queries ≤ ~100 ms are not in it.
- `invocations` needs a JSON query tag with `invocation_id` (the default query comment has none: docs reference/project-configs/query-comment); without it the column is NULL — `run_hours` (hours with dbt queries) is the proxy for runs.
- `tagged_pct` = share of the node's queries with a JSON `query_tag`; the rest were found through the query comment.
- `:as_of` at least 8 h before now, else recent runs look cheap.
- `(dbt, no node)` large → no JSON tag and comment stripped: add a query tag macro (jinja-macros-hooks.md). No rows at all → "not assessed: no dbt metadata", not "dbt is free".
- Next: S10 (week-over-week jump) or S3 (why it is expensive).

**S2 — Slowest models on the warehouse side**: same `d` CTE, `group by node_id` with `avg(total_elapsed_time)/1000 as avg_s`, `max(...)`, `sum(queued_overload_time)/1000 as queued_s` (add the column to `q`). Read: avg vs max spread = data skew or contention; queued_s > 10% of elapsed = warehouse too small or too busy (S4).

**S3 — Spill and pruning per model**
```sql
-- reuse q/d from S1, adding these columns to q: bytes_scanned, partitions_scanned, partitions_total,
-- bytes_spilled_to_local_storage, bytes_spilled_to_remote_storage
select node_id,
       sum(bytes_scanned) / power(1024, 3) as gb_scanned,
       sum(partitions_scanned) / nullif(sum(partitions_total), 0) as scan_ratio,
       sum(bytes_spilled_to_local_storage) / power(1024, 3) as gb_spilled_local,
       sum(bytes_spilled_to_remote_storage) / power(1024, 3) as gb_spilled_remote
from d
group by node_id
order by gb_spilled_remote desc, gb_scanned desc
limit 50;
```
- `scan_ratio` near 1 on a big incremental = no pruning (filter not on the cluster key, function on the column). Remote spill > 0 = warehouse too small for that model → `snowflake_warehouse` on that model only.

**S4 — Queueing during dbt runs**: `select warehouse_name, date_trunc('hour', start_time) as hr, count(*) as dbt_queries, sum(queued_overload_time)/60000 as queued_min from d … group by 1,2 order by queued_min desc limit 50`. Read: queued minutes in the run window → raise max clusters (multi-cluster) or split dbt to its own warehouse; threads in the profile beyond the warehouse's concurrency only queue.

**S5 — Merges scanning the whole target**: filter `q` to `query_type = 'MERGE'`, report `node_id`, `partitions_scanned / partitions_total`, `rows_updated + rows_inserted`. Read: ratio near 1 with few rows changed = add `incremental_predicates` / cluster on the date.

**S6 — Models nobody reads**
```sql
with objs as (
  select ah.query_id, ah.query_start_time, f.value as obj
  from snowflake.account_usage.access_history ah, lateral flatten(input => ah.base_objects_accessed) f
  where ah.query_start_time >= dateadd(day, -:days, :as_of) and ah.query_start_time < :as_of
  union all
  select ah.query_id, ah.query_start_time, f.value
  from snowflake.account_usage.access_history ah, lateral flatten(input => ah.direct_objects_accessed) f   -- views appear here
  where ah.query_start_time >= dateadd(day, -:days, :as_of) and ah.query_start_time < :as_of
), reads as (
  select lower(obj:objectName::string) as object_name, query_start_time, query_id
  from objs
  where upper(obj:objectDomain::string) in ('TABLE', 'VIEW', 'MATERIALIZED VIEW', 'DYNAMIC TABLE')   -- check: access_history "Supported objects"
), not_dbt as (
  select r.* from reads r
  join snowflake.account_usage.query_history q on q.query_id = r.query_id
  where coalesce(q.query_tag, '') not ilike '%dbt%' and q.query_text not ilike '%"app":%"dbt"%'
)
select m.relation_name, max(n.query_start_time) as last_read, count(distinct n.query_id) as reads
from (select lower(column1) as relation_name from values ('analytics.marts.fct_orders'), ('analytics.marts.dim_customer')) m   -- from dbt_inventory.py relations
left join not_dbt n on n.object_name = m.relation_name
group by m.relation_name
order by reads asc, last_read asc nulls first;
```
- `reads = 0` over 90 days = candidate to drop or turn into a view; check exposures and monthly jobs first. `objectName` is `DB.SCHEMA.NAME` unquoted upper case; compare lower-cased.
- Retention 365 days, latency 3 h, Enterprise edition only. A view read lists the base tables in `BASE_OBJECTS_ACCESSED` and the view in `DIRECT_OBJECTS_ACCESSED`; both are read, and `count(distinct query_id)` counts a query once.

**S7 — Storage per model**: `select table_catalog, table_schema, table_name, active_bytes/power(1024,4) as tb_active, time_travel_bytes/power(1024,4) as tb_tt, failsafe_bytes/power(1024,4) as tb_failsafe, is_transient from snowflake.account_usage.table_storage_metrics where deleted = false and table_schema in (<dbt schemas>) order by active_bytes desc limit 50`. Read: fail-safe on rebuildable tables → `transient: true`; time travel large on tables rebuilt daily → each rebuild keeps old versions.

**S8 — Failed dbt queries by model**: from `q`/`d` with `upper(execution_status) = 'FAIL'` (values `success` / `fail` / `incident`), `group by node_id, error_code` → `count(*)`, `max(start_time)`. Read the message itself only in the user's own worksheet (it can echo values).

**S9 — Clustering cost per dbt table**: `select database_name, schema_name, table_name, sum(credits_used) as credits, sum(num_bytes_reclustered)/power(1024,4) as tb_reclustered from snowflake.account_usage.automatic_clustering_history where start_time >= dateadd(day,-:days,:as_of) and start_time < :as_of and schema_name in (<dbt schemas>) group by 1,2,3 order by credits desc limit 50`. Read: clustering credits > the model's build credits (S1) on a table rebuilt fully each run → drop `cluster_by` (a full rebuild with `order by` already sorts).

**S10 — Why did dbt cost jump?** S1 grouped by `node_id, date_trunc('week', start_time)`; compare last two full weeks. Read: one node up = its SQL or data changed (git log on the model, row counts); all nodes up = warehouse size or a new full-refresh schedule; `queries` or `run_hours` up = extra runs (CI on every push?); `invocations` only with an `invocation_id` tag. `date_trunc('week', …)` starts the week per the session's `WEEK_START` parameter: set it or state it. Who caused it → S13.

**S11 — Source freshness without dbt**: `select table_schema, table_name, last_altered, row_count from <raw_db>.information_schema.tables where table_schema = '<RAW_SCHEMA>' order by last_altered limit 100`. No latency; `last_altered` also changes on DDL.

**S12 — Warehouse fit for dbt**: S1 grouped by `warehouse_name`, `warehouse_size` (add to `q`) → credits, elapsed, remote spill. Read: one size for all models while 5% of models drive 80% of credits → default small warehouse + `snowflake_warehouse` on those models.

**S13 — Who caused the change (role, target, warehouse)**
```sql
with d as (
  select q.query_id, q.start_time, q.role_name, q.user_name, q.warehouse_name, q.warehouse_size,
         try_parse_json(regexp_substr(q.query_text,
           '/\\*\\s*(\\{[^*]*"app"\\s*:\\s*"dbt"[^*]*\\})\\s*\\*/', 1, 1, 'e', 1)):target_name::string as target_name
  from snowflake.account_usage.query_history q
  where q.start_time >= dateadd(week, -2, date_trunc('week', :as_of)) and q.start_time < date_trunc('week', :as_of)
    and (q.query_tag ilike '%dbt%' or q.query_text ilike '%"app":%"dbt"%')
)
select d.role_name, d.target_name, d.warehouse_name, d.warehouse_size,
       count(distinct d.user_name) as users,
       sum(iff(d.start_time >= dateadd(week, -1, date_trunc('week', :as_of)), a.credits_attributed_compute, 0)) as credits_last_wk,
       sum(iff(d.start_time <  dateadd(week, -1, date_trunc('week', :as_of)), a.credits_attributed_compute, 0)) as credits_prev_wk
from d
left join snowflake.account_usage.query_attribution_history a on a.query_id = d.query_id
group by 1, 2, 3, 4
order by credits_last_wk - credits_prev_wk desc
limit 50;
```
- Read: one row = role × dbt target × warehouse × size. A new row (prev 0) = a new job, a CI target or a resized warehouse; `users` > 1 on a prod target = prod builds run by hand. Users stay counted, never listed.
- Idle share (next cell): `select warehouse_name, sum(credits_used_compute) as billed, sum(credits_attributed_compute_queries) as attributed, 1 - attributed / nullif(billed, 0) as idle_share from snowflake.account_usage.warehouse_metering_history where start_time >= dateadd(week, -2, date_trunc('week', :as_of)) and start_time < date_trunc('week', :as_of) group by 1 order by billed desc` (add `date_trunc('week', start_time)` to compare weeks). Idle share up = longer auto-suspend or more small runs, not heavier SQL.

**S14 — Who reads column c of a dbt model** (impact of a drop or rename)
```sql
select q.role_name,
       count(distinct ah.query_id) as reads,
       count(distinct ah.user_name) as users,
       max(ah.query_start_time) as last_read
from snowflake.account_usage.access_history ah,
     lateral flatten(input => ah.direct_objects_accessed) o,
     lateral flatten(input => o.value:columns) c,
     snowflake.account_usage.query_history q
where q.query_id = ah.query_id
  and ah.query_start_time >= dateadd(day, -:days, :as_of) and ah.query_start_time < :as_of
  and q.start_time >= dateadd(day, -:days - 1, :as_of)            -- prunes query_history to the window
  and lower(o.value:objectName::string) = :relation_name          -- from dbt_inventory.py relations
  and lower(c.value:columnName::string) = lower(:column_name)
group by 1
order by reads desc;
```
- Read: one row = role reading that column directly. dbt's role = a dbt child (confirm with `dbt_inventory.py column-users`); any other role = a consumer outside dbt (BI, ad-hoc) that breaks on the drop. Empty = no direct reads in the window, not "safe": check S15 for objects built on the model.

**S15 — Warehouse objects built on a dbt model**: `select referencing_database, referencing_schema, referencing_object_name, referencing_object_domain, dependency_type from snowflake.account_usage.object_dependencies where lower(referenced_database || '.' || referenced_schema || '.' || referenced_object_name) = :relation_name order by 1, 2, 3`. Read: views and other objects referencing the model, including ones outside the dbt project (not in the manifest); latency up to 3 h.

## Databricks tables used
| Table | Grain | Latency | Retention | Key columns |
|---|---|---|---|---|
| `system.query.history` | one statement | typically ≤ 1 h | check: docs.databricks.com/aws/en/admin/system-tables/query-history | `statement_id`, `statement_text`, `statement_type`, `execution_status`, `executed_by`, `compute.warehouse_id`, `start_time`, `total_duration_ms`, `execution_duration_ms`, `waiting_at_capacity_duration_ms`, `total_task_duration_ms`, `read_bytes`, `read_files`, `pruned_files`, `spilled_local_bytes`, `written_rows`, `query_tags` (map), `query_source` |
| `system.billing.usage` | one usage record | hours (check: docs.databricks.com/aws/en/admin/system-tables/billing) | 365 days (check: same) | `usage_date`, `usage_start_time`, `usage_end_time`, `sku_name`, `cloud`, `usage_unit`, `usage_quantity`, `usage_metadata.warehouse_id`, `usage_metadata.job_id`, `usage_metadata.job_run_id`, `record_type`, `workspace_id`, `custom_tags` |
| `system.billing.list_prices` | sku × price interval | — | full history | `sku_name`, `cloud`, `usage_unit`, `currency_code`, `price_start_time`, `price_end_time`, `pricing.default` |
| `system.access.table_lineage` | one read/write event | not stated (check: docs.databricks.com/aws/en/admin/system-tables/lineage) | 395 days, rolling | `source_table_full_name`, `source_type`, `target_table_full_name`, `entity_type`, `created_by`, `event_time`, `event_date` |
| `system.access.column_lineage` | one column read/write event | not stated (check: same page) | 395 days, rolling | `source_table_full_name`, `source_column_name`, `target_table_full_name`, `target_column_name`, `entity_type`, `created_by`, `event_time`, `event_date` |
- `query.history` covers SQL warehouses, serverless notebooks/jobs and pipelines, all workspaces in the region; `compute.cluster_id` is never filled → dbt on classic all-purpose clusters is not in it.
- Access: `USE` + `SELECT` on the `system` schemas granted by an admin; none → "not assessed".
- DBUs ≠ money: list price only (`pricing.default`, `currency_code = 'USD'`); contract discounts are not in system tables.
- `billing.usage` has `RETRACTION` / `RESTATEMENT` rows: sum all rows for the net, never filter to `ORIGINAL` only.
- `list_prices` intervals can overlap per sku: dedupe (one row per sku/cloud/unit/start, end capped at the next start) before joining, else cost doubles.

## Databricks catalogue
**D1 — Cost per dbt model**
```sql
with dq as (
  select statement_id, compute.warehouse_id as warehouse_id, date(start_time) as d,
         coalesce(nullif(regexp_extract(statement_text, '"node_id":\\s*"([^"]+)"', 1), ''),
                  query_tags['@@dbt_model_name']) as node,
         total_task_duration_ms, total_duration_ms
  from system.query.history
  where start_time >= cast(date_sub(date(:as_of), :days) as timestamp) and start_time < cast(date(:as_of) as timestamp)
    and (query_tags['@@dbt_model_name'] is not null or statement_text like '%"app": "dbt"%')
), all_q as (
  select compute.warehouse_id as warehouse_id, date(start_time) as d, sum(total_task_duration_ms) as wh_task_ms
  from system.query.history
  where start_time >= cast(date_sub(date(:as_of), :days) as timestamp) and start_time < cast(date(:as_of) as timestamp)
    and compute.warehouse_id is not null
  group by 1, 2
), prices as (
  select sku_name, cloud, usage_unit, price_start_time,
         least(price_end_time,   -- least() skips NULLs: open intervals end at the next start
               lead(price_start_time) over (partition by sku_name, cloud, usage_unit order by price_start_time)) as price_end_time,
         pricing.default as unit_price
  from system.billing.list_prices
  where currency_code = 'USD'
), wh_cost as (
  select u.usage_metadata.warehouse_id as warehouse_id, u.usage_date as d,
         sum(u.usage_quantity) as dbus, sum(u.usage_quantity * p.unit_price) as usd_list
  from system.billing.usage u
  left join prices p
    on u.sku_name = p.sku_name and u.cloud = p.cloud and u.usage_unit = p.usage_unit
   and u.usage_end_time > p.price_start_time and (p.price_end_time is null or u.usage_end_time <= p.price_end_time)
  where u.usage_date >= date_sub(date(:as_of), :days) and u.usage_date < date(:as_of)
    and u.usage_metadata.warehouse_id is not null
  group by 1, 2
)
select dq.node,
       count(*) as statements,
       sum(dq.total_duration_ms) / 3600000 as wall_hours,
       sum(dq.total_task_duration_ms / nullif(a.wh_task_ms, 0) * w.usd_list) as est_usd_list
from dq
join all_q a on a.warehouse_id = dq.warehouse_id and a.d = dq.d
left join wh_cost w on w.warehouse_id = dq.warehouse_id and w.d = dq.d
group by dq.node
order by est_usd_list desc nulls last
limit 100;
```
- Read: one row = one dbt node. `node` = the comment's `node_id` (`model.<project>.<name>`), else the `@@dbt_model_name` tag, which is the model name only — a model can show as two rows when some statements lack the comment; match both forms before comparing. Whole UTC days on both sides: the as-of day is excluded. `est_usd_list` = the warehouse-day list cost split by share of task time, so warehouse idle time is spread over all queries of that day (including non-dbt ones).
- `query_tags` is filled only with dbt-databricks 1.11+; older runs fall back to the comment in `statement_text` (`"app": "dbt"` spacing per dbt's JSON — check one statement first).
- `null` cost on recent days = billing latency; end the window a day before now.
- Duplicate `price_start_time` rows for one sku would still repeat: check `count(*)` vs `count(distinct sku_name, cloud, usage_unit, price_start_time)` once.

**D2 — Slowest models**: `dq` grouped by `node` with `avg(total_duration_ms)/1000`, `sum(waiting_at_capacity_duration_ms)/1000 as waiting_s` (add to `dq`). Read: waiting high = warehouse at capacity (D4), execution high = SQL or layout (D3).

**D3 — Pruning and spill**: add `read_files`, `pruned_files`, `read_bytes`, `spilled_local_bytes`, `read_io_cache_percent` to `dq`; per node `sum(pruned_files)/nullif(sum(pruned_files+read_files),0) as pruned_share`, `sum(spilled_local_bytes)/power(1024,3) as gb_spilled`. Read: pruned_share near 0 on a big incremental = filter not on the clustering/partition column.

**D4 — Capacity waits by hour**: `select compute.warehouse_id, date_trunc('hour', start_time) hr, count(*) n, sum(waiting_at_capacity_duration_ms)/60000 wait_min from system.query.history where … and statement_id in (select statement_id from dq) group by 1,2 order by wait_min desc limit 50`. Read: waits in the dbt window → raise max clusters or lower dbt `threads`.

**D5 — Merges reading the whole target**: `dq` filtered to `statement_type = 'MERGE'` (check value list: query-history page) → `read_bytes`, `pruned_share`, `written_rows`. Read: many GB read for few rows written → `incremental_predicates`, or `insert_overwrite` / `replace_where` by date.

**D6 — Models nobody reads**
```sql
select m.relation_name, max(l.event_time) as last_read, count(l.event_time) as reads   -- count(*) gives 1 when nothing matched
from (values ('main.marts.fct_orders'), ('main.marts.dim_customer')) as m(relation_name)   -- dbt_inventory.py relations
left join system.access.table_lineage l
  on lower(l.source_table_full_name) = m.relation_name
 and l.source_type is not null
 and l.event_date >= date_sub(date(:as_of), :days)
 and l.event_time >= timestampadd(DAY, -:days, :as_of) and l.event_time < :as_of
 and (l.created_by is null or l.created_by <> :dbt_principal)
group by m.relation_name
order by reads asc, last_read asc nulls first;
```
- `reads = 0` = candidate to drop; reads only by `entity_type = 'NOTEBOOK'` of one person = ad-hoc use. dbt's own reads are excluded by its principal (a service principal id, not a name to print).

**D7 — Size per model**: `describe detail <catalog>.<schema>.<table>` → `sizeInBytes`, `numFiles`, `clusteringColumns`, `partitionColumns`. Many small files (avg < 32 MB) → `OPTIMIZE` / auto-optimize. One statement per table (notebook loop over `dbt_inventory.py relations`).

**D8 — Failed dbt statements**: `dq` with `execution_status = 'FAILED'` (add the column to `dq`) → count per `node`, `max(start_time)`. The `error_message` stays in the user's own query (can echo values).

**D9 — OPTIMIZE after each run**: `dq` filtered to `statement_type = 'OPTIMIZE'` (check value), `sum(total_task_duration_ms)` per node vs the model's own build. High share on small tables → `skip_optimize: true` (1.12.2+) or schedule OPTIMIZE separately.

**D10 — Why did dbt cost jump?** D1 grouped by `node, date_trunc('week', d)`; same reading as S10. Databricks weeks start on Monday.

**D11 — dbt run as a job**: `select usage_metadata.job_run_id, sum(usage_quantity) dbus from system.billing.usage where usage_metadata.job_id = :dbt_job_id and usage_date >= … group by 1 order by dbus desc limit 50` (price as in D1). Read: DBUs per run; job compute cost is separate from the SQL warehouse cost of D1.

**D12 — Source freshness without dbt**: `select table_schema, table_name, last_altered from <catalog>.information_schema.tables where table_schema = '<raw_schema>' order by last_altered limit 100`.

**D13 — Who caused the change**: D1's `dq` plus `executed_by`, grouped by `warehouse_id` and week → `count(distinct executed_by) as principals`, `sum(total_task_duration_ms)`, and `est_usd_list` as in D1, last week vs the week before. Read: a new warehouse or principal row (previous week 0) = a new job or CI target; principals stay counted, not listed. D1 already spreads idle time over each warehouse-day's queries, so a rise with flat task time = more idle time (auto-stop, more small runs).

**D14 — Who reads column c of a dbt model**: `select entity_type, count(*) as events, count(distinct created_by) as principals, max(event_time) as last_read from system.access.column_lineage where lower(source_table_full_name) = :relation_name and lower(source_column_name) = lower(:column_name) and event_date >= date_sub(date(:as_of), :days) and event_time < :as_of group by 1 order by events desc`. Read: one row = kind of reader (`entity_type` values: check: docs.databricks.com/aws/en/admin/system-tables/lineage); dbt's principal = a dbt child (confirm with `dbt_inventory.py column-users`), any other = a consumer outside dbt. Covers what Unity Catalog lineage captures; empty is not "safe".
