# Query and table performance

## Rules
- Find the slow or costly statements in `query.history` first; then explain one with its **query profile** (UI: Query History → statement → profile) and `EXPLAIN FORMATTED <query>`; then check the tables' layout with `DESCRIBE DETAIL`, `DESCRIBE HISTORY`, `SHOW TBLPROPERTIES`.
- `query.history` covers SQL warehouses, serverless notebooks/jobs and pipelines; classic-cluster Spark work is not in it (use the Spark UI).
- Timing columns are ms: `total_duration_ms` (excludes result fetch) ≈ waits + `compilation_duration_ms` + `execution_duration_ms` (check: query history page; the sum is not stated there); `total_task_duration_ms` sums all cores (can exceed wall clock).
- Text: `statement_text` needs admin or `databricks_pii_access`; group by a fingerprint (literals stripped) so near-identical statements pool; a `<REDACTED>` text is keyed by its own `statement_id`, never pooled.
- Statements that read the result cache (`from_result_cache`) cost ~nothing; exclude them from "slow" lists.
- All fixes (OPTIMIZE, ALTER … CLUSTER BY, VACUUM, table properties) are proposals for the user's changes notebook.

## Questions
### P1 Slowest statement shapes per warehouse
```sql
WITH s AS (
  SELECT workspace_id, compute.warehouse_id AS warehouse_id, statement_id, executed_by,
         sha2(regexp_replace(lower(statement_text), "'[^']*'|\\b\\d+\\b", '?'), 256) AS shape,
         total_duration_ms, execution_duration_ms, read_bytes, spilled_local_bytes
  FROM system.query.history
  WHERE start_time >= date_sub(current_date(), :days) AND execution_status = 'FINISHED'
    AND NOT from_result_cache AND statement_text <> '<REDACTED>')
SELECT workspace_id, warehouse_id, shape, COUNT(*) AS runs,
       percentile_approx(total_duration_ms, 0.95) / 1000 AS p95_s, SUM(total_duration_ms) / 3600000 AS total_h,
       MAX(spilled_local_bytes) AS max_spill, ANY_VALUE(statement_id) AS example_statement
FROM s GROUP BY ALL ORDER BY total_h DESC LIMIT 50;
```
- Read: `total_h` ranks where time goes; open `example_statement` in the UI profile. Regex is Java: escape backslashes as shown.

### P2 Statements that spill
- `spilled_local_bytes > 0` ordered by it; spill + large shuffle → join or aggregation exceeds memory: filter earlier, fix skew (P6), or size up (compute K9).

### P3 Poor file pruning
```sql
SELECT workspace_id, statement_id, read_files, pruned_files, read_bytes, read_rows, produced_rows,
       ROUND(100 * pruned_files / NULLIF(pruned_files + read_files, 0), 1) AS pruned_pct
FROM system.query.history
WHERE start_time >= date_sub(current_date(), :days) AND read_bytes > :min_bytes
ORDER BY read_bytes DESC LIMIT 100;
```
- Read: low `pruned_pct` on a selective query (`produced_rows` ≪ `read_rows`) → filters do not match the table layout → cluster on the filter columns (P10). Set a volume floor (`:min_bytes`) and look across several days, not one.

### P4 Cache use
- `read_io_cache_percent` weighted by `read_bytes` (plain AVG is diluted by non-scan statements reporting 0) and `from_result_cache` share per warehouse. Low IO-cache on a warehouse that stops often → cache lost on every stop.

### P5 Shuffle-heavy statements
- `shuffle_read_bytes / NULLIF(read_bytes, 0)` high → wide joins or aggregations moving most data; check join strategy (P7).

### P6 Skew
- Profile: one task far longer than the median in a stage; `EXPLAIN` alone does not show skew. AQE (`spark.sql.adaptive.enabled`, on by default) splits skewed partitions in sort-merge joins (`spark.sql.adaptive.skewJoin.enabled`). Persistent skew on a hot key → salt the key or handle the hot key separately.

### P7 Which join strategy did a query use?
```sql
EXPLAIN FORMATTED
SELECT ... ;   -- the statement under study
```
- Read: `BroadcastHashJoin` (small side broadcast; fine), `SortMergeJoin` (both large; shuffle), `BroadcastNestedLoopJoin` / `CartesianProduct` (missing or non-equi join condition → fix). AQE can switch to broadcast at run time; the profile shows the final plan. Hint: `/*+ BROADCAST(dim) */` when the small side is under memory limits. Threshold `spark.sql.autoBroadcastJoinThreshold` (check: Databricks default value on the compute in use).

### P8 Compilation-heavy statements
- `compilation_duration_ms / total_duration_ms` high → many small files or partitions, huge views, or metadata calls; fix file count (P9) or simplify views.

### P9 Small files per table
```sql
SELECT catalog_name, schema_name, table_name, active_files, active_bytes,
       ROUND(active_bytes / NULLIF(active_files, 0) / 1048576, 1) AS avg_file_mb
FROM system.storage.table_metrics_history
WHERE snapshot_date >= date_sub(current_date(), :days)
QUALIFY ROW_NUMBER() OVER (PARTITION BY table_id ORDER BY snapshot_date DESC) = 1 AND table_dropped_time IS NULL
ORDER BY active_files DESC LIMIT 100;
```
- Read: many files with a small average size → compaction (`OPTIMIZE`) or predictive optimization. Confirm one table with `DESCRIBE DETAIL <table>` (`numFiles`, `sizeInBytes`). Table not in the result → no snapshot in the window, not "fine".

### P10 Is a table clustered, partitioned, Z-ordered?
```sql
DESCRIBE DETAIL  <catalog>.<schema>.<table>;            -- clusteringColumns, partitionColumns, numFiles, sizeInBytes
SHOW TBLPROPERTIES  <catalog>.<schema>.<table>;         -- delta.dataSkippingNumIndexedCols / dataSkippingStatsColumns
DESCRIBE HISTORY <catalog>.<schema>.<table> LIMIT 50;     -- OPTIMIZE, ZORDER, VACUUM, writes per operation
```
- Proposals: liquid clustering (`CLUSTER BY (cols)` or `CLUSTER BY AUTO`) instead of partitioning plus Z-order for selective filter columns; partitions only on low-cardinality date-like columns, never on IDs; Z-order and liquid clustering are not combined. Data skipping stats cover the first 32 columns by default: filter columns must be among them (check: data skipping page).

### P11 Maintenance history: did OPTIMIZE / VACUUM run?
```sql
SELECT catalog_name, schema_name, table_name, operation_type, operation_status,
       COUNT(DISTINCT operation_id) AS ops, SUM(usage_quantity) AS est_dbu
FROM system.storage.predictive_optimization_operations_history
WHERE start_time >= date_sub(current_date(), :days) AND start_time < current_date()
GROUP BY ALL ORDER BY est_dbu DESC LIMIT 100;
```
- Read: `operation_status` is `SUCCESSFUL` or `FAILED: <REASON>` (split on the first `': '` only). `FAILED: PRIVATE_LINK_SETUP_ERROR` → storage firewall blocks serverless. `usage_quantity` can lag up to a day. Managed tables only.

### P12 Tables without predictive optimization
- Latest `table_metrics_history` row per `table_id` (QUALIFY first), then `table_dropped_time IS NULL AND predictive_optimization_enabled = false`, largest `active_bytes` first; external tables are out of scope.

### P13 Repeated identical work
- P1 shapes with many runs and identical results → result cache, a materialized view or a scheduled table instead of re-running.

### P14 Failed statements by error class
```sql
SELECT workspace_id, compute.warehouse_id AS warehouse_id,
       regexp_extract(error_message, '^\\[([A-Za-z0-9_.]+)\\]', 1) AS error_class, COUNT(*) AS statements
FROM system.query.history
WHERE execution_status = 'FAILED' AND start_time >= date_sub(current_date(), :days)
GROUP BY ALL ORDER BY statements DESC LIMIT 50;
```
- Read: classes like `TABLE_OR_VIEW_NOT_FOUND`, `INSUFFICIENT_PERMISSIONS`, `DIVIDE_BY_ZERO` point to the fix; `error_message` can echo data → aggregate only.

### P15 Where does a dashboard's or job's SQL time go?
- `query.history` grouped by `query_source.dashboard_id` or `query_source.job_info.job_id`, summing `total_duration_ms` and `read_bytes`; then P1 inside that source.

## Tune one statement (given its SQL text or `statement_id`)
1. Its row in `query.history`: `total_duration_ms` split into `waiting_for_compute_duration_ms` (cold start → compute K8), `waiting_at_capacity_duration_ms` (queue → K8), `compilation_duration_ms` (P8), `execution_duration_ms`; plus `read_bytes`, `pruned_files` vs `read_files`, `spilled_local_bytes`, `shuffle_read_bytes`, `from_result_cache`.
2. Waits dominate → fix the warehouse, not the query. Compilation dominates → small files or heavy views.
3. `EXPLAIN FORMATTED <statement>`: red flags `CartesianProduct`, `BroadcastNestedLoopJoin`, a `SortMergeJoin` with a small side, a scan with no `PushedFilters` / `PartitionFilters` on a selective filter, a filter on a function of the column (`date(ts) = …`, `cast`) that blocks pruning.
4. Query profile (UI): the operator with the most time; one task far above the stage median (skew, P6); spill per operator; rows in vs out per join (exploding join → wrong or missing key).
5. Tables read: `DESCRIBE DETAIL` (files, size, clustering), P9 file sizes, P10 layout against the filter columns.
6. Fix in this order: query (filters, projections, join keys, pre-aggregation) → table layout (clustering, OPTIMIZE) → warehouse size or clusters. Re-measure the same statement after each change, never two changes at once.

## Tuning playbook (proposals)
- Filter and project early; avoid `SELECT *` on wide tables; push filters below joins.
- Join a large fact to small dims with broadcast; fix non-equi or missing join keys; deduplicate the build side before joining.
- Target file sizes of roughly 100 MB–1 GB (check: Delta file size tuning page); `OPTIMIZE` or predictive optimization for small files.
- `VACUUM` default retention 7 days; shorter breaks time travel and concurrent readers.
- Photon and serverless for SQL-heavy workloads; disk (IO) cache benefits from warehouses that stay up during work hours.
- PySpark: built-in functions over Python UDFs (pandas UDFs if unavoidable); no `collect()`/`toPandas()`/`count()` on large data to inspect or loop; explicit schemas on production reads; `cache()` only for reused expensive DataFrames, `unpersist()` after; no `repartition(n)` or `coalesce(1)` without a reason.
- Delta writes: `MERGE` for upserts, `replaceWhere` for partition overwrites, idempotent reruns; `mergeSchema` only when intended.
