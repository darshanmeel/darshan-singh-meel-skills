# Query performance tuning

## Order of work for one slow query
1. P1: where the time went (compile, queue, execute) and the scan, spill and row numbers.
2. P2/P3: which operator is expensive (`GET_QUERY_OPERATOR_STATS`): a join that multiplies rows, a scan that prunes nothing, a spill.
3. Fix the query first (filters on clustered columns, join keys, earlier aggregation, fewer columns); then data layout (clustering P6-P7, search optimization P8); then the warehouse (size for spill, QAS P9, clusters for queueing).
- `GET_QUERY_OPERATOR_STATS(query_id)`: completed queries of the past 14 days; needs `OPERATE` or `MONITOR` on the warehouse the query ran on. Output: `QUERY_ID`, `STEP_ID`, `OPERATOR_ID`, `PARENT_OPERATORS`, `OPERATOR_TYPE`, `OPERATOR_STATISTICS`, `EXECUTION_TIME_BREAKDOWN`, `OPERATOR_ATTRIBUTES`. Pass one query id per call: a literal (or bound parameter), a session variable or `LAST_QUERY_ID()`; a column of another table (lateral join) is not supported.
- Older than 14 days → only `QUERY_HISTORY` metrics and the pruning views remain.

## Catalogue

### P1. Profile of one query from history
```sql
SELECT query_id, query_type, warehouse_name, warehouse_size, execution_status,
       total_elapsed_time / 1000 AS total_s, compilation_time / 1000 AS compile_s,
       execution_time / 1000 AS exec_s,
       (queued_overload_time + queued_provisioning_time + queued_repair_time) / 1000 AS queued_s,
       transaction_blocked_time / 1000 AS blocked_s,
       bytes_scanned / POWER(1024, 3) AS gb_scanned, percentage_scanned_from_cache,
       partitions_scanned, partitions_total,
       ROUND(100 * partitions_scanned / NULLIF(partitions_total, 0), 1) AS pct_partitions_scanned,
       bytes_spilled_to_local_storage / POWER(1024, 3) AS local_spill_gb,
       bytes_spilled_to_remote_storage / POWER(1024, 3) AS remote_spill_gb,
       rows_produced, bytes_sent_over_the_network / POWER(1024, 3) AS network_gb,
       query_acceleration_bytes_scanned, query_parameterized_hash
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE query_id = '<query_id>'
  AND start_time >= DATEADD(day, -14, CURRENT_TIMESTAMP());     -- time filter keeps the scan small
```
- Read: compile ≫ exec → very complex SQL or many small objects; queued → `warehouses.md` W4; blocked → locks (`troubleshooting.md` T6); `pct_partitions_scanned` near 100 on a big table → no pruning (P5); remote spill → memory (P4).
- Newer than 45 min → `TABLE(INFORMATION_SCHEMA.QUERY_HISTORY())` or Snowsight; the AU row is not there yet.

### P2. Most expensive operators of a query
```sql
SELECT operator_id, operator_type, parent_operators,
       execution_time_breakdown:overall_percentage::FLOAT AS pct_of_time,
       operator_statistics:input_rows::NUMBER AS input_rows,
       operator_statistics:output_rows::NUMBER AS output_rows,
       operator_statistics:pruning:partitions_scanned::NUMBER AS partitions_scanned,
       operator_statistics:pruning:partitions_total::NUMBER AS partitions_total,
       operator_statistics:spilling:bytes_spilled_remote_storage::NUMBER AS remote_spill_bytes,
       operator_attributes
FROM TABLE(GET_QUERY_OPERATOR_STATS('<query_id>'))
ORDER BY pct_of_time DESC NULLS LAST
LIMIT 20;
```
- Read: the top 1-3 operators hold the time. `TableScan` with `partitions_scanned` ≈ `partitions_total` → pruning; `Join` with `output_rows` ≫ `input_rows` → row explosion (P3); `Aggregate`/`Sort` with spill → memory; `ExternalScan`/`Result` large → result size.
- `EXECUTION_TIME_BREAKDOWN` keys: `overall_percentage`, `initialization`, `processing`, `synchronization`, `local_disk_io`, `remote_disk_io`, `network_communication`. High `remote_disk_io` = spill or cold data; high `synchronization` = skew or many small steps.

### P3. Join conditions and row explosion
```sql
SELECT operator_id, operator_attributes:join_type::STRING AS join_type,
       operator_attributes:equality_join_condition::STRING AS equality_condition,
       operator_attributes:additional_join_condition::STRING AS extra_condition,
       operator_statistics:input_rows::NUMBER AS input_rows,
       operator_statistics:output_rows::NUMBER AS output_rows,
       ROUND(operator_statistics:output_rows::NUMBER / NULLIF(operator_statistics:input_rows::NUMBER, 0), 2) AS rows_out_per_in,
       execution_time_breakdown:overall_percentage::FLOAT AS pct_of_time
FROM TABLE(GET_QUERY_OPERATOR_STATS('<query_id>'))
WHERE operator_type = 'Join'
ORDER BY pct_of_time DESC;
```
- Read: `rows_out_per_in` ≫ 1 → the key is not unique on one side (missing a column in the condition, duplicates in a dimension). An empty `equality_condition` with only `extra_condition` → non-equi join (range or `OR`), which cannot hash: rewrite. `CartesianJoin` operators → a missing condition.
- Many queries: loop over query ids in Python (one call each); see `joins-lineage.md` J2.

### P4. Queries that spill
```sql
WITH p AS (SELECT 7 AS days, CURRENT_DATE() AS end_date)
SELECT query_id, warehouse_name, warehouse_size, total_elapsed_time / 1000 AS total_s,
       bytes_spilled_to_local_storage / POWER(1024, 3) AS local_gb,
       bytes_spilled_to_remote_storage / POWER(1024, 3) AS remote_gb, query_parameterized_hash
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY, p
WHERE bytes_spilled_to_remote_storage > 0
  AND start_time >= DATEADD(day, -p.days, p.end_date) AND start_time < p.end_date
ORDER BY remote_gb DESC
LIMIT 50;
```
- Read: remote spill is the slow kind. Fix: reduce rows before the join or sort (filter, aggregate early), drop unused columns, fix exploding joins (P3); then one size up and compare cost per run.

### P5. Pruning per table
```sql
WITH p AS (SELECT 14 AS days, CURRENT_DATE() AS end_date)
SELECT table_id, MAX(database_name || '.' || schema_name || '.' || table_name) AS table_fqn,
       SUM(num_scans) AS scans, SUM(partitions_scanned) AS scanned, SUM(partitions_pruned) AS pruned,
       ROUND(100 * SUM(partitions_pruned) / NULLIF(SUM(partitions_scanned + partitions_pruned), 0), 1) AS prune_pct,
       SUM(rows_scanned) AS rows_scanned
FROM SNOWFLAKE.ACCOUNT_USAGE.TABLE_PRUNING_HISTORY, p
WHERE start_time >= DATEADD(day, -p.days, p.end_date) AND start_time < p.end_date
GROUP BY table_id
ORDER BY scanned DESC
LIMIT 50;
```
- Read: a big, often-scanned table with low `prune_pct` is a clustering or filter candidate; next P6 for the columns queries filter on.
- Pitfall: 6 h latency; top 1,000 scans per query only; hybrid tables not recorded.

### P6. Filter and join columns per table (clustering candidates)
```sql
WITH p AS (SELECT 14 AS days, CURRENT_DATE() AS end_date)
SELECT table_id, MAX(table_name) AS table_name, column_name, access_type,
       SUM(num_queries) AS queries,
       ROUND(100 * SUM(partitions_pruned) / NULLIF(SUM(partitions_scanned + partitions_pruned), 0), 1) AS prune_pct,
       SUM(aggregate_query_execution_time) / 1000 / 3600 AS exec_hours
FROM SNOWFLAKE.ACCOUNT_USAGE.COLUMN_QUERY_PRUNING_HISTORY, p
WHERE access_type IN ('WHERE', 'JOIN')
  AND interval_start_time >= DATEADD(day, -p.days, p.end_date) AND interval_start_time < p.end_date
GROUP BY table_id, column_name, access_type
ORDER BY exec_hours DESC
LIMIT 50;
```
- Read: a `WHERE` column with many queries, many hours and low `prune_pct` → clustering key candidate (low to medium cardinality, often a date) or search optimization (point lookups on high cardinality). `SEARCH_OPTIMIZATION_SUPPORTED_EXPRESSIONS` lists what SOS could serve.
- Pitfall: GROUP BY and SELECT columns are not recorded; only queries that scanned micro-partitions count; 4 h latency.
- Depth of the current layout: `SELECT SYSTEM$CLUSTERING_INFORMATION('<db.schema.table>', '(<col>)')` → `average_depth`, `average_overlaps`, `partition_depth_histogram`. A `SYSTEM$` call → user-run cell.

### P7. Is automatic clustering worth its credits?
```sql
WITH p AS (SELECT 30 AS days, CURRENT_DATE() AS end_date),
c AS (SELECT table_id, SUM(credits_used) AS clustering_credits, SUM(num_rows_reclustered) AS rows_reclustered
      FROM SNOWFLAKE.ACCOUNT_USAGE.AUTOMATIC_CLUSTERING_HISTORY, p
      WHERE start_time >= DATEADD(day, -p.days, p.end_date) AND start_time < p.end_date GROUP BY 1),
s AS (SELECT table_id, SUM(num_scans) AS scans,
             ROUND(100 * SUM(partitions_pruned) / NULLIF(SUM(partitions_scanned + partitions_pruned), 0), 1) AS prune_pct
      FROM SNOWFLAKE.ACCOUNT_USAGE.TABLE_PRUNING_HISTORY, p
      WHERE start_time >= DATEADD(day, -p.days, p.end_date) AND start_time < p.end_date GROUP BY 1)
SELECT c.table_id, t.table_catalog || '.' || t.table_schema || '.' || t.table_name AS table_fqn,
       t.clustering_key, c.clustering_credits, c.rows_reclustered, COALESCE(s.scans, 0) AS scans, s.prune_pct
FROM c
LEFT JOIN s ON s.table_id = c.table_id
LEFT JOIN SNOWFLAKE.ACCOUNT_USAGE.TABLES t ON t.table_id = c.table_id AND t.deleted IS NULL
ORDER BY c.clustering_credits DESC;
```
- Read: high credits with few scans or low `prune_pct` → the key does not match the filters (compare with P6) or the table churns too much; suspend clustering or change the key (user-run DDL).

### P8. Search optimization: cost vs benefit
```sql
WITH p AS (SELECT 30 AS days, CURRENT_DATE() AS end_date),
c AS (SELECT COALESCE(o:BASE_TABLE_ID, o:TABLE_ID)::NUMBER AS table_id, SUM(o:CREDITS_USED::FLOAT) AS sos_credits
      FROM (SELECT OBJECT_CONSTRUCT(*) AS o, start_time
            FROM SNOWFLAKE.ACCOUNT_USAGE.SEARCH_OPTIMIZATION_HISTORY) x, p
      WHERE x.start_time >= DATEADD(day, -p.days, p.end_date) AND x.start_time < p.end_date
      GROUP BY 1),
b AS (SELECT table_id, SUM(num_scans) AS sos_scans, SUM(partitions_pruned_additional) AS extra_pruned
      FROM SNOWFLAKE.ACCOUNT_USAGE.SEARCH_OPTIMIZATION_BENEFITS, p
      WHERE start_time >= DATEADD(day, -p.days, p.end_date) AND start_time < p.end_date GROUP BY 1)
SELECT c.table_id, c.sos_credits, COALESCE(b.sos_scans, 0) AS sos_scans, COALESCE(b.extra_pruned, 0) AS extra_pruned
FROM c LEFT JOIN b ON b.table_id = c.table_id
ORDER BY c.sos_credits DESC;
```
- Read: credits with no benefiting scans → drop search optimization (user-run). `OBJECT_CONSTRUCT(*)` reads the old `TABLE_ID` and the new `BASE_TABLE_ID` columns, so the query works before and after the rename. Enterprise.
- Estimate before enabling: `SYSTEM$ESTIMATE_SEARCH_OPTIMIZATION_COSTS('<table>')` → user-run.

### P9. Query acceleration candidates
```sql
WITH p AS (SELECT 14 AS days, CURRENT_DATE() AS end_date)
SELECT warehouse_name, COUNT(*) AS eligible_queries,
       SUM(eligible_query_acceleration_time) / 3600 AS eligible_hours,
       MAX(upper_limit_scale_factor) AS max_scale_factor
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_ACCELERATION_ELIGIBLE, p
WHERE start_time >= DATEADD(day, -p.days, p.end_date) AND start_time < p.end_date
GROUP BY warehouse_name
ORDER BY eligible_hours DESC;
```
- Read: warehouses with many eligible hours (large scans with selective filters, outlier queries) gain from QAS; QAS credits appear as service `QUERY_ACCELERATION` and in `QUERY_ATTRIBUTION_HISTORY.CREDITS_USED_QUERY_ACCELERATION`. Never select `QUERY_TEXT` here. Per query: `SYSTEM$ESTIMATE_QUERY_ACCELERATION('<query_id>')` → user-run.

### P10. Result cache misses (same query, recomputed)
```sql
WITH p AS (SELECT 7 AS days, CURRENT_DATE() AS end_date)
SELECT query_hash, COUNT(*) AS runs, COUNT(DISTINCT user_name) AS users,
       SUM(execution_time) / 1000 / 60 AS exec_min, MAX(warehouse_name) AS warehouse_name
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY, p
WHERE query_type = 'SELECT' AND execution_status = 'SUCCESS' AND execution_time > 1000
  AND start_time >= DATEADD(day, -p.days, p.end_date) AND start_time < p.end_date
GROUP BY query_hash
HAVING COUNT(*) >= 20
ORDER BY exec_min DESC
LIMIT 30;
```
- Read: the identical text run many times and each run executing → no reuse. Reuse needs identical text, unchanged data, the same privileges, no non-reusable functions (`RANDOM`, `UUID_STRING`, `CURRENT_TIMESTAMP` in some forms), no hybrid tables; results live 24 h, extended on reuse up to 31 days; `USE_CACHED_RESULT` can turn it off. check: query_history (no documented flag marks a result-cache hit; a hit typically shows near-zero execution time and no partitions scanned).
- Pitfall: tables that load every few minutes invalidate the cache; dashboards that inject the current time into the text never reuse.

### P11. Compilation-heavy queries
```sql
WITH p AS (SELECT 7 AS days, CURRENT_DATE() AS end_date)
SELECT query_parameterized_hash, COUNT(*) AS runs,
       AVG(compilation_time) / 1000 AS avg_compile_s, AVG(execution_time) / 1000 AS avg_exec_s
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY, p
WHERE compilation_time > 5000
  AND start_time >= DATEADD(day, -p.days, p.end_date) AND start_time < p.end_date
GROUP BY 1
ORDER BY avg_compile_s * runs DESC
LIMIT 25;
```
- Read: compile ≫ exec → deeply nested views, huge `IN` lists, many `UNION ALL` branches, or tables with very many micro-partitions and no pruning on metadata. Compilation also costs cloud services credits.

### P12. Has a query shape got slower?
```sql
WITH p AS (SELECT 60 AS days, CURRENT_DATE() AS end_date, '<query_parameterized_hash>' AS h)
SELECT DATE_TRUNC(day, start_time) AS day, COUNT(*) AS runs,
       APPROX_PERCENTILE(total_elapsed_time, 0.5) / 1000 AS p50_s,
       APPROX_PERCENTILE(total_elapsed_time, 0.95) / 1000 AS p95_s,
       AVG(bytes_scanned) / POWER(1024, 3) AS avg_gb, MAX(warehouse_size) AS size
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY, p
WHERE query_parameterized_hash = p.h
  AND start_time >= DATEADD(day, -p.days, p.end_date) AND start_time < p.end_date
GROUP BY 1
ORDER BY 1;
```
- Read: `avg_gb` rising with time → data growth or lost pruning; same bytes but slower → queueing, size change or plan change (compare P2 for a fast and a slow run).

### P13. Snowflake's own insights
```sql
WITH p AS (SELECT 14 AS days, CURRENT_DATE() AS end_date)
SELECT insight_topic, insight_type_id, COUNT(DISTINCT query_id) AS queries,
       SUM(total_elapsed_time) / 1000 / 3600 AS hours, ANY_VALUE(suggestions) AS example_suggestions
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_INSIGHTS, p
WHERE is_opportunity
  AND start_time >= DATEADD(day, -p.days, p.end_date) AND start_time < p.end_date
GROUP BY 1, 2
ORDER BY hours DESC;
```
- Read: insight types ranked by the time of the queries they flag; each row's `query_id` leads to P2. Latency 90 minutes; retention 1 year (ACCOUNT_USAGE index page).

### P14. Plan before running
- `EXPLAIN USING TEXT <select>` (read-only) shows operators and partitions to be scanned without running the query; compare `partitionsAssigned` with `partitionsTotal`. check: explain (output fields).

### P15. Warehouse cache warmth
- `QUERY_HISTORY.PERCENTAGE_SCANNED_FROM_CACHE` = share read from the warehouse's local disk cache (not the result cache). Low values right after resume are normal; a warehouse that suspends every minute never keeps its cache - weigh against idle cost (`warehouses.md` W3).
