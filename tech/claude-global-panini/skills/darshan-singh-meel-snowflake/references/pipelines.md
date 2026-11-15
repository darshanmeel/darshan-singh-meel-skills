# Tasks, alerts, loading, streams, dynamic tables

## Facts
- `TASK_HISTORY.STATE`: `SUCCEEDED`, `FAILED`, `CANCELLED`, `SKIPPED` only (completed runs; 45 min lag). Running and scheduled runs: `TABLE(INFORMATION_SCHEMA.TASK_HISTORY())` (7 days) or `SHOW TASKS`. `ERROR_CODE` is VARCHAR here.
- Task credits: warehouse tasks bill on their warehouse (find their queries by `TASK_HISTORY.QUERY_ID`); serverless tasks in `SERVERLESS_TASK_HISTORY` (`CREDITS_USED` VARCHAR).
- Graph runs: `COMPLETE_TASK_GRAPHS` (role-filtered, `FIRST_ERROR_TASK_NAME`). Definitions: `TASK_VERSIONS` (no DELETED column: a dropped task keeps its last row) and `TASKS`; live state: `SHOW TASKS IN ACCOUNT` (`state` started/suspended).
- `COPY_HISTORY` = bulk COPY and Snowpipe per file (role-filtered, `STATUS` mixed case: `'Loaded'`, `'Load failed'`, `'Partially loaded'`, `'Load skipped'`; `PIPE_NAME` NULL = bulk COPY). `LOAD_HISTORY` excludes Snowpipe and uses upper-case status.
- `PIPE_USAGE_HISTORY.PIPE_NAME` NULL = external or directory table auto-refresh, or Snowpipe Streaming. Streaming credits are `METERING_HISTORY` service `SNOWPIPE_STREAMING` (12 h lag).
- Streams: no AU view; `SHOW STREAMS IN ACCOUNT` (`stale`, `stale_after`, `mode`, `invalid_reason`). A stream goes stale when it is not consumed within the source table's retention (extended up to `MAX_DATA_EXTENSION_TIME_IN_DAYS`). check: streams-intro (staleness rules).
- Dynamic tables: no AU view of definitions (`TABLES.IS_DYNAMIC = 'YES'`, `SHOW DYNAMIC TABLES`); `DYNAMIC_TABLE_REFRESH_HISTORY.STATE`: `EXECUTING`, `SUCCEEDED`, `FAILED`, `CANCELLED`, `UPSTREAM_FAILED` (no SKIPPED); `REFRESH_ACTION`: `NO_DATA`, `REINITIALIZE`, `FULL`, `INCREMENTAL`.

## Catalogue

### L1. Failing tasks
```sql
WITH p AS (SELECT 7 AS days, CURRENT_DATE() AS end_date)
SELECT database_name || '.' || schema_name || '.' || name AS task_fqn,
       COUNT(*) AS runs, COUNT_IF(state = 'FAILED') AS failed, COUNT_IF(state = 'SKIPPED') AS skipped,
       MAX_BY(error_code, IFF(state = 'FAILED', completed_time, NULL)) AS last_error_code,
       MAX_BY(LEFT(error_message, 200), IFF(state = 'FAILED', completed_time, NULL)) AS last_error,
       MAX(IFF(state = 'SUCCEEDED', completed_time, NULL)) AS last_success
FROM SNOWFLAKE.ACCOUNT_USAGE.TASK_HISTORY, p
WHERE scheduled_time >= DATEADD(day, -p.days, p.end_date) AND scheduled_time < p.end_date
GROUP BY 1
HAVING failed > 0
ORDER BY failed DESC;
```
- Read: `last_success` NULL in the window = broken all week. Error codes: `troubleshooting.md`.
- Pitfall: error messages can echo values from data; do not send them to the model for sensitive tables.

### L2. Task duration regression
```sql
WITH p AS (SELECT 28 AS days, CURRENT_DATE() AS end_date),
r AS (SELECT name, DATE_TRUNC(week, scheduled_time) AS wk,
             DATEDIFF(second, query_start_time, completed_time) AS dur_s
      FROM SNOWFLAKE.ACCOUNT_USAGE.TASK_HISTORY, p
      WHERE state = 'SUCCEEDED'
        AND scheduled_time >= DATEADD(day, -p.days, p.end_date) AND scheduled_time < p.end_date)
SELECT name, wk, COUNT(*) AS runs, MEDIAN(dur_s) AS median_s, MAX(dur_s) AS max_s
FROM r GROUP BY 1, 2 ORDER BY 1, 2;
```
- Read: median rising week over week → growing data or lost pruning in the task's query (follow `QUERY_ID` into `performance.md` P1).

### L3. Skipped runs and start delays
```sql
WITH p AS (SELECT 7 AS days, CURRENT_DATE() AS end_date)
SELECT name, COUNT_IF(state = 'SKIPPED') AS skipped,
       APPROX_PERCENTILE(DATEDIFF(second, scheduled_time, query_start_time), 0.95) AS p95_start_delay_s
FROM SNOWFLAKE.ACCOUNT_USAGE.TASK_HISTORY, p
WHERE scheduled_time >= DATEADD(day, -p.days, p.end_date) AND scheduled_time < p.end_date
GROUP BY name
ORDER BY skipped DESC;
```
- Read: SKIPPED = the previous run was still going (overlap not allowed) or a `WHEN` condition was false; long start delay = queueing on a busy warehouse.

### L4. Task cost
```sql
WITH p AS (SELECT 30 AS days, CURRENT_DATE() AS end_date),
t AS (SELECT query_id, name FROM SNOWFLAKE.ACCOUNT_USAGE.TASK_HISTORY, p
      WHERE scheduled_time >= DATEADD(day, -p.days, p.end_date) AND scheduled_time < p.end_date AND query_id IS NOT NULL),
a AS (SELECT COALESCE(root_query_id, query_id) AS root_id, SUM(credits_attributed_compute) AS credits
      FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_ATTRIBUTION_HISTORY, p
      WHERE start_time >= DATEADD(day, -p.days, p.end_date) AND start_time < p.end_date GROUP BY 1)
SELECT 'warehouse' AS kind, t.name, SUM(a.credits) AS credits
FROM t JOIN a ON a.root_id = t.query_id GROUP BY 1, 2
UNION ALL
SELECT 'serverless', task_name, SUM(TRY_TO_DOUBLE(credits_used))
FROM SNOWFLAKE.ACCOUNT_USAGE.SERVERLESS_TASK_HISTORY, p
WHERE start_time >= DATEADD(day, -p.days, p.end_date) AND start_time < p.end_date GROUP BY 1, 2
ORDER BY credits DESC;
```
- Read: warehouse task credits = attributed compute of the task's query and its children (procedures). Idle time the task keeps alive is not included.
- Pitfall: `ROOT_QUERY_ID` is NULL for a query without a parent (a plain SQL task, a DT refresh): roll up by `COALESCE(ROOT_QUERY_ID, QUERY_ID)`, or those runs drop out.

### L5. Silent failures: tasks that stopped running
```sql
SHOW TASKS IN ACCOUNT ->> SELECT "database_name" || '.' || "schema_name" || '.' || "name" AS task_fqn,
                                  "state", "schedule", "warehouse", "last_committed_on", "last_suspended_on", "last_suspended_reason"
                           FROM $1 WHERE "state" = 'suspended' ORDER BY "last_suspended_on" DESC;
```
- Read: suspended tasks (manually, or after repeated failures with `SUSPEND_TASK_AFTER_NUM_FAILURES`); then compare started tasks with `TASK_HISTORY` runs in the last day - a started root with no runs is stuck or not visible. check: show-tasks (column `last_suspended_reason`).
- Pitfall: SHOW is role-filtered; TASK_HISTORY is not: runs without a SHOW row = task hidden from this role, not "gone".

### L6. Tasks and dynamic tables that touch an object
```sql
WITH p AS (SELECT 30 AS days, CURRENT_DATE() AS end_date, 'DB.SCHEMA.TABLE' AS fqn),
reads AS (
  SELECT DISTINCT ah.query_id
  FROM SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY ah, p, LATERAL FLATTEN(input => ah.base_objects_accessed) b
  WHERE UPPER(b.value:objectName::STRING) = p.fqn
    AND ah.query_start_time >= DATEADD(day, -p.days, p.end_date) AND ah.query_start_time < p.end_date
)
SELECT 'task' AS kind, t.database_name || '.' || t.schema_name || '.' || t.name AS reader, COUNT(*) AS runs
FROM SNOWFLAKE.ACCOUNT_USAGE.TASK_HISTORY t JOIN reads r ON r.query_id = t.query_id, p
WHERE t.scheduled_time >= DATEADD(day, -p.days, p.end_date) GROUP BY 1, 2
UNION ALL
SELECT 'dynamic table', d.qualified_name, COUNT(*)
FROM SNOWFLAKE.ACCOUNT_USAGE.DYNAMIC_TABLE_REFRESH_HISTORY d JOIN reads r ON r.query_id = d.query_id, p
WHERE d.refresh_start_time >= DATEADD(day, -p.days, p.end_date) GROUP BY 1, 2
ORDER BY runs DESC;
```
- Read: jobs whose own query read the object. Tasks that call a procedure read through child queries: also match the root (select `COALESCE(ah.root_query_id, ah.query_id)` instead of `ah.query_id` in `reads`; `ROOT_QUERY_ID` is NULL without a parent). Dynamic tables also appear in `OBJECT_DEPENDENCIES` (`joins-lineage.md` J7).

### L7. Snowpipe health: latency, errors, cost
```sql
WITH p AS (SELECT 7 AS days, CURRENT_DATE() AS end_date)
SELECT pipe_catalog_name || '.' || pipe_schema_name || '.' || pipe_name AS pipe_fqn,
       COUNT(*) AS files, COUNT_IF(status <> 'Loaded') AS not_loaded,
       SUM(row_count) AS rows_loaded, AVG(file_size) / POWER(1024, 2) AS avg_file_mb,
       APPROX_PERCENTILE(DATEDIFF(second, pipe_received_time, last_load_time), 0.95) AS p95_latency_s
FROM SNOWFLAKE.ACCOUNT_USAGE.COPY_HISTORY, p
WHERE pipe_name IS NOT NULL
  AND last_load_time >= DATEADD(day, -p.days, p.end_date) AND last_load_time < p.end_date
GROUP BY 1
ORDER BY not_loaded DESC, p95_latency_s DESC;
```
- Read: `avg_file_mb` under about 10 → many tiny files (per-file overhead; aim for 100-250 MB compressed); `not_loaded` → L8. Cost per pipe: `cost.md` C9.
- Pitfall: role-filtered; up to 2 h lag (2 days when quiet).

### L8. Load errors by file
```sql
WITH p AS (SELECT 7 AS days, CURRENT_DATE() AS end_date)
SELECT table_catalog_name || '.' || table_schema_name || '.' || table_name AS target, status,
       COUNT(*) AS files, SUM(error_count) AS errors,
       ANY_VALUE(LEFT(first_error_message, 200)) AS example_error, ANY_VALUE(first_error_column_name) AS example_column
FROM SNOWFLAKE.ACCOUNT_USAGE.COPY_HISTORY, p
WHERE status IN ('Load failed', 'Partially loaded')
  AND last_load_time >= DATEADD(day, -p.days, p.end_date) AND last_load_time < p.end_date
GROUP BY 1, 2
ORDER BY errors DESC;
```
- Read: same column in every error → schema drift or a file format option (date format, delimiter, `NULL_IF`). `'Load skipped'` = already loaded (load metadata) or `ON_ERROR = SKIP_FILE`.
- Pitfall: `FIRST_ERROR_MESSAGE` can contain row values: treat as sensitive.

### L9. Bulk COPY vs Snowpipe vs streaming
```sql
WITH p AS (SELECT 30 AS days, CURRENT_DATE() AS end_date)
SELECT IFF(pipe_name IS NULL, 'bulk COPY', 'Snowpipe') AS method, COUNT(*) AS files,
       SUM(file_size) / POWER(1024, 3) AS gb, COUNT(DISTINCT table_id) AS tables
FROM SNOWFLAKE.ACCOUNT_USAGE.COPY_HISTORY, p
WHERE last_load_time >= DATEADD(day, -p.days, p.end_date) AND last_load_time < p.end_date
GROUP BY 1;
```
- Read: Snowpipe Streaming does not appear here; its volume is in `SNOWPIPE_STREAMING_CHANNEL_HISTORY` (rows, errors) and cost in `METERING_HISTORY`.

### L10. Stale or soon-stale streams
```sql
SHOW STREAMS IN ACCOUNT ->> SELECT "database_name" || '.' || "schema_name" || '.' || "name" AS stream_fqn,
                                    "table_name", "mode", "stale", "stale_after", "invalid_reason"
                             FROM $1
                             WHERE "stale" = 'true' OR "stale_after" < DATEADD(day, 2, CURRENT_TIMESTAMP())
                             ORDER BY "stale_after";
```
- Read: a stale stream has lost changes: recreate it and reload (user-run). `stale_after` within 2 days → consume it now.
- Pitfall: role-filtered; `stale` is text. check: show-streams (`stale` value type).

### L11. Dynamic table refresh failures and lag
```sql
WITH p AS (SELECT 7 AS days, CURRENT_DATE() AS end_date)
SELECT qualified_name, COUNT(*) AS refreshes,
       COUNT_IF(state = 'FAILED') AS failed, COUNT_IF(state = 'UPSTREAM_FAILED') AS upstream_failed,
       COUNT_IF(refresh_action = 'FULL') AS full_refreshes,
       COUNT_IF(refresh_action = 'REINITIALIZE') AS reinits,
       MAX(target_lag_sec) AS target_lag_s,
       APPROX_PERCENTILE(DATEDIFF(second, data_timestamp, refresh_end_time), 0.95) AS p95_lag_s,
       MAX_BY(LEFT(state_message, 200), IFF(state = 'FAILED', refresh_start_time, NULL)) AS last_error
FROM SNOWFLAKE.ACCOUNT_USAGE.DYNAMIC_TABLE_REFRESH_HISTORY, p
WHERE state <> 'EXECUTING'
  AND refresh_start_time >= DATEADD(day, -p.days, p.end_date) AND refresh_start_time < p.end_date
GROUP BY 1
ORDER BY failed DESC, p95_lag_s DESC;
```
- Read: `p95_lag_s` > `target_lag_s` → the warehouse is too small or the refresh is FULL when it should be incremental (`REINIT_REASON` says why). Many `NO_DATA` refreshes keep a warehouse awake for nothing: a longer target lag saves credits. check: dynamic_table_refresh_history (lag definition).

### L12. Dynamic table cost
- Refresh queries run on the DT's warehouse: join `DYNAMIC_TABLE_REFRESH_HISTORY.QUERY_ID` to `QUERY_ATTRIBUTION_HISTORY` (as L4) and sum per `QUALIFIED_NAME`. Idle time between refreshes is not included; a short target lag on a warehouse with a long `auto_suspend` can cost more than the refreshes.

### L13. Alerts that fail or never fire
```sql
WITH p AS (SELECT 30 AS days, CURRENT_DATE() AS end_date)
SELECT database_name || '.' || schema_name || '.' || name AS alert_fqn, state, COUNT(*) AS evaluations
FROM SNOWFLAKE.ACCOUNT_USAGE.ALERT_HISTORY, p
WHERE scheduled_time >= DATEADD(day, -p.days, p.end_date) AND scheduled_time < p.end_date
GROUP BY 1, 2
ORDER BY 1, evaluations DESC;
```
- Read: `CONDITION_FAILED` / `ACTION_FAILED` → broken SQL or a missing integration; only `CONDITION_FALSE` for months → the alert never fires (check it still matters). Serverless alert credits: `SERVERLESS_ALERT_HISTORY`. check: serverless_alert_history.

### L14. Materialized views: refresh cost vs reads
- Credits: `cost.md` C9 (`MATERIALIZED_VIEW_REFRESH_HISTORY`, the MV itself in `TABLE_NAME`). Reads: `joins-lineage.md` J3 with the MV's name, or J9 for MVs never read. High refresh credits and few reads → drop or replace with a scheduled table (user-run DDL). Enterprise.
