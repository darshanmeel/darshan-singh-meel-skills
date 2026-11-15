# Troubleshooting: failed queries, errors, locks, "it stopped working"

## Facts
- `QUERY_HISTORY.EXECUTION_STATUS`: `SUCCESS`, `FAIL`, `INCIDENT` (plus running and queued states only in the INFORMATION_SCHEMA function). `ERROR_MESSAGE` is cut at 5,000 characters and can echo data values: treat it as sensitive.
- Cancelled queries show `ERROR_MESSAGE = 'SQL execution canceled'`; the code is not documented.
- Snowflake publishes no full error code list. Codes seen in the field (check: no official list): `2003` object does not exist or not authorized · `3001` insufficient privileges · `2043` object does not exist or operation not authorized · `630` statement timed out. Confirm a code by reading its message, not the number alone.
- `ACCESS_HISTORY` omits failed queries: use `QUERY_HISTORY` for failures.
- Queries younger than 45 min: `TABLE(INFORMATION_SCHEMA.QUERY_HISTORY(END_TIME_RANGE_START => DATEADD(hour, -1, CURRENT_TIMESTAMP())))` (7 days, what the role can see).

## Catalogue

### T1. Failures by error, last 7 days
```sql
WITH p AS (SELECT 7 AS days, CURRENT_DATE() AS end_date)
SELECT error_code, LEFT(ANY_VALUE(error_message), 150) AS example_message,
       COUNT(*) AS failures, COUNT(DISTINCT user_name) AS users,
       COUNT(DISTINCT query_parameterized_hash) AS shapes, MAX(start_time) AS last_seen
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY, p
WHERE execution_status IN ('FAIL', 'INCIDENT')
  AND start_time >= DATEADD(day, -p.days, p.end_date) AND start_time < p.end_date
GROUP BY error_code
ORDER BY failures DESC
LIMIT 30;
```
- Read: one code with many failures and one shape → one broken job; many shapes → a platform change (a dropped object, a revoked grant).
- Cost of failures: join failed `QUERY_ID`s to `QUERY_ATTRIBUTION_HISTORY` - failed queries still bill the time they ran.

### T2. What failed for one user, role or job
```sql
WITH p AS (SELECT 2 AS days, DATEADD(day, 1, CURRENT_DATE()) AS end_date)
SELECT start_time, query_id, query_type, role_name, warehouse_name, error_code, LEFT(error_message, 200) AS error
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY, p
WHERE execution_status = 'FAIL' AND user_name = '<USER>'          -- or role_name, query_tag
  AND start_time >= DATEADD(day, -p.days, p.end_date) AND start_time < p.end_date
ORDER BY start_time DESC
LIMIT 100;
```
- Read: the first failure's time is when it broke; then T7 for what changed just before.

### T3. Access-denied errors (grant problems)
```sql
WITH p AS (SELECT 7 AS days, CURRENT_DATE() AS end_date)
SELECT role_name, user_name, error_code, COUNT(*) AS failures, MAX(start_time) AS last_seen
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY, p
WHERE execution_status = 'FAIL' AND error_code IN (2003, 3001, 2043)
  AND start_time >= DATEADD(day, -p.days, p.end_date) AND start_time < p.end_date
GROUP BY 1, 2, 3
ORDER BY failures DESC;
```
- Read: a role that started failing on a date → a revoke or a `CREATE OR REPLACE` that dropped grants (`security.md` X12, `joins-lineage.md` J11). "Does not exist or not authorized" cannot tell the two apart: check the object exists (`TABLES`, J11).

### T4. Timeouts and long runners
```sql
WITH p AS (SELECT 7 AS days, CURRENT_DATE() AS end_date)
SELECT warehouse_name, query_parameterized_hash, COUNT(*) AS runs,
       COUNT_IF(error_code = 630) AS timeouts, MAX(total_elapsed_time) / 1000 / 60 AS max_min
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY, p
WHERE (error_code = 630 OR total_elapsed_time > 30 * 60 * 1000)
  AND start_time >= DATEADD(day, -p.days, p.end_date) AND start_time < p.end_date
GROUP BY 1, 2
ORDER BY timeouts DESC, max_min DESC
LIMIT 30;
```
- Read: timeouts come from `STATEMENT_TIMEOUT_IN_SECONDS` (account, warehouse, user or session; default 2 days). Tune the query (`performance.md`) before raising the limit. check: parameters (STATEMENT_TIMEOUT_IN_SECONDS default).

### T5. Cancelled and retried queries
```sql
WITH p AS (SELECT 7 AS days, CURRENT_DATE() AS end_date)
SELECT user_name, warehouse_name,
       COUNT_IF(error_message = 'SQL execution canceled') AS cancelled,
       COUNT_IF(query_retry_time > 0) AS retried, SUM(query_retry_time) / 1000 AS retry_s
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY, p
WHERE start_time >= DATEADD(day, -p.days, p.end_date) AND start_time < p.end_date
GROUP BY 1, 2
HAVING cancelled > 0 OR retried > 0
ORDER BY cancelled DESC;
```
- Read: many cancels from one BI user → dashboards firing and abandoning queries; retries (`QUERY_RETRY_TIME`, `FAULT_HANDLING_TIME`) are Snowflake-side and usually transient.

### T6. Lock waits (blocked DML)
```sql
WITH p AS (SELECT 7 AS days, CURRENT_DATE() AS end_date)
SELECT l.database_name || '.' || l.schema_name || '.' || l.object_name AS object, l.lock_type,
       COUNT(*) AS waits, AVG(DATEDIFF(second, l.requested_at, l.acquired_at)) AS avg_wait_s,
       ARRAY_AGG(DISTINCT b.value:query_id::STRING) WITHIN GROUP (ORDER BY b.value:query_id::STRING) AS blocker_ids
FROM SNOWFLAKE.ACCOUNT_USAGE.LOCK_WAIT_HISTORY l, p,
     LATERAL FLATTEN(input => l.blocker_queries, OUTER => TRUE) b
WHERE l.requested_at >= DATEADD(day, -p.days, p.end_date) AND l.requested_at < p.end_date
GROUP BY 1, 2
ORDER BY waits DESC
LIMIT 30;
```
- Read: two jobs writing the same table at the same time; reschedule one or merge them. `QUERY_HISTORY.TRANSACTION_BLOCKED_TIME` shows the waiting side's time. `BLOCKER_QUERIES` elements have `is_snowflake`, `query_id`, `transaction_id`.

### T7. "It worked yesterday": what changed
- 1) DDL on the objects the job reads: `joins-lineage.md` J11. 2) Grants and roles: `security.md` X12. 3) Warehouse size or settings: `warehouses.md` W6. 4) Upstream loads failed: `pipelines.md` L1, L8, L11. 5) Data volume: `performance.md` P12. Run them for the hours before the first failure (T2).

### T8. A dashboard or tool got slow
```sql
WITH p AS (SELECT 14 AS days, CURRENT_DATE() AS end_date)
SELECT DATE_TRUNC(day, q.start_time) AS day, COUNT(*) AS queries,
       APPROX_PERCENTILE(q.total_elapsed_time, 0.95) / 1000 AS p95_s,
       SUM(q.queued_overload_time) / 1000 / 60 AS queued_min
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY q, p
WHERE (q.query_tag ILIKE '%<tool>%' OR q.user_name = '<SERVICE_USER>')
  AND q.start_time >= DATEADD(day, -p.days, p.end_date) AND q.start_time < p.end_date
GROUP BY 1 ORDER BY 1;
```
- Read: queueing up → warehouse busy (`warehouses.md` W4); elapsed up without queueing → the queries (P12). Client tools are named in `SESSIONS.CLIENT_APPLICATION_ID` (join on `SESSION_ID`).

### T9. Incidents
- `EXECUTION_STATUS = 'INCIDENT'` = an internal error. Collect `QUERY_ID`, time and warehouse, retry once; repeated incidents on one shape go to Snowflake support with the query id (no data needed).
