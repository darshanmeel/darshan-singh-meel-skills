# Warehouses: sizing, idle time, queueing, multi-cluster

## Rules of thumb
- Billing is per second with a 60-second minimum at each resume. Gen1 standard: X-Small = 1 credit/hour, each size up doubles. Gen2 and Snowpark-optimized warehouses cost more per hour: take the multiplier from the Service Consumption Table, never from memory. Adaptive warehouses have no fixed rate.
- Metering views already report credits: never rebuild spend from size x hours. Use rates only for what-if estimates, labelled as estimates.
- Size up for **spilling** and big scans (one query too slow). Add clusters for **queueing** (too many queries at once). Shorten auto-suspend for **idle** time.
- `WAREHOUSE_LOAD_HISTORY` columns are average load per 5-minute bucket: average or peak them, never sum.
- Current settings come from `SHOW WAREHOUSES` (size `'X-Small'`, `auto_suspend` seconds, NULL = never suspends, `generation`, `resource_constraint`, `scaling_policy`, `min/max_cluster_count`); history of changes from `WAREHOUSE_EVENTS_HISTORY`.

## Catalogue

### W1. Current configuration of every warehouse
```sql
SHOW WAREHOUSES ->> SELECT "name", "state", "type", "size", "generation", "min_cluster_count", "max_cluster_count",
                           "scaling_policy", "auto_suspend", "auto_resume", "enable_query_acceleration",
                           "resource_monitor", "owner"
                    FROM $1 ORDER BY "name";
```
- Read: `auto_suspend` NULL or above 600 s on an interactive warehouse is a waste candidate; `resource_monitor = 'null'` = no quota.
- Pitfall: role-filtered; compare with warehouses in W2 to find ones this role cannot see.

### W2. Credits and active hours per warehouse
```sql
WITH p AS (SELECT 30 AS days, CURRENT_DATE() AS end_date)
SELECT warehouse_id, MAX(warehouse_name) AS warehouse_name,
       SUM(credits_used_compute) AS compute_credits,
       COUNT_IF(credits_used_compute > 0) AS billed_hours,
       SUM(credits_used_compute) / NULLIF(COUNT_IF(credits_used_compute > 0), 0) AS credits_per_billed_hour
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY, p
WHERE start_time >= DATEADD(day, -p.days, p.end_date) AND start_time < p.end_date
GROUP BY warehouse_id
ORDER BY compute_credits DESC;
```
- Read: `credits_per_billed_hour` near the size's hourly rate = running the whole hour; much lower = short bursts (each with a 60 s minimum).

### W3. Idle time and auto-suspend fit
```sql
WITH p AS (SELECT 14 AS days, CURRENT_DATE() AS end_date),
q AS (
  SELECT warehouse_id, warehouse_name, start_time, end_time,
         MAX(end_time) OVER (PARTITION BY warehouse_id ORDER BY start_time
                             ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS prev_end
  FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY, p
  WHERE warehouse_name IS NOT NULL AND execution_time > 0
    AND start_time >= DATEADD(day, -p.days, p.end_date) AND start_time < p.end_date
)
SELECT warehouse_id, MAX(warehouse_name) AS warehouse_name, COUNT(*) AS gaps,
       APPROX_PERCENTILE(DATEDIFF(second, prev_end, start_time), 0.5) AS median_gap_s,
       COUNT_IF(DATEDIFF(second, prev_end, start_time) BETWEEN 60 AND 600) AS gaps_1_to_10_min
FROM q
WHERE prev_end IS NOT NULL AND start_time > prev_end
GROUP BY warehouse_id
ORDER BY gaps_1_to_10_min DESC;
```
- Read: many gaps just longer than `auto_suspend` → the warehouse suspends and resumes often (60 s minimum each time); many gaps shorter → it idles the whole gap. Combine with `cost.md` C7 for idle credits.
- Pitfall: `prev_end` is the latest end of all earlier queries, so a gap counts only when nothing was running; a gap counted against the previous query alone overstates idle time on a busy warehouse; multi-cluster warehouses need `cluster_number` in the partition.

### W4. Queueing: is the warehouse too busy?
```sql
WITH p AS (SELECT 14 AS days, CURRENT_DATE() AS end_date)
SELECT warehouse_name, COUNT(*) AS queries,
       COUNT_IF(queued_overload_time > 0) AS queued_queries,
       SUM(queued_overload_time) / 1000 / 60 AS queued_overload_min,
       APPROX_PERCENTILE(queued_overload_time, 0.95) / 1000 AS p95_queue_s,
       SUM(queued_provisioning_time) / 1000 / 60 AS provisioning_min
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY, p
WHERE warehouse_name IS NOT NULL
  AND start_time >= DATEADD(day, -p.days, p.end_date) AND start_time < p.end_date
GROUP BY warehouse_name
ORDER BY queued_overload_min DESC;
```
- Read: `queued_overload_time` = waited for a free slot → more clusters (multi-cluster, Enterprise) or split workloads; `queued_provisioning_time` = waited for resume or resize → normal after suspend, large values suggest a longer auto-suspend for latency-sensitive users.
- Next: W5 for the busy hours.

### W5. Load by hour (when it queues)
```sql
WITH p AS (SELECT 14 AS days, CURRENT_DATE() AS end_date, 'WH_NAME' AS wh)
SELECT DATE_TRUNC(hour, start_time) AS hour,
       AVG(avg_running) AS avg_running, MAX(avg_running) AS peak_running,
       AVG(avg_queued_load) AS avg_queued, MAX(avg_queued_load) AS peak_queued,
       MAX(avg_blocked) AS peak_blocked
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_LOAD_HISTORY, p
WHERE warehouse_name = p.wh
  AND start_time >= DATEADD(day, -p.days, p.end_date) AND start_time < p.end_date
GROUP BY 1
ORDER BY peak_queued DESC
LIMIT 48;
```
- Read: `peak_queued` above 0 in the same hours every day → add clusters for those hours or move a batch job; `avg_running` well below 1 all day → oversized or idle.
- Pitfall: load ratios, not query counts.

### W6. Size changes and resumes (what changed)
```sql
WITH p AS (SELECT 30 AS days, CURRENT_DATE() AS end_date)
SELECT timestamp, warehouse_name, event_name, event_reason, size, cluster_count, user_name, role_name
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_EVENTS_HISTORY, p
WHERE event_state = 'COMPLETED' AND cluster_number IS NULL
  AND event_name IN ('RESIZE_WAREHOUSE', 'ALTER_WAREHOUSE', 'CREATE_WAREHOUSE', 'DROP_WAREHOUSE', 'CONVERT_WAREHOUSE')
  AND timestamp >= DATEADD(day, -p.days, p.end_date) AND timestamp < p.end_date
ORDER BY timestamp DESC
LIMIT 200;
```
- Read: a resize just before a cost jump explains it. Resume counts: same query with `event_name = 'RESUME_WAREHOUSE'` grouped by warehouse and `event_reason` (`WAREHOUSE_AUTORESUME` vs manual `WAREHOUSE_RESUME`).
- Pitfall: one action has STARTED and COMPLETED rows at warehouse and cluster level; filter as above. `CLUSTER_COUNT` is VARCHAR.

### W7. Multi-cluster behaviour
```sql
WITH p AS (SELECT 14 AS days, CURRENT_DATE() AS end_date)
SELECT warehouse_name, event_name, COUNT(*) AS events
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_EVENTS_HISTORY, p
WHERE event_state = 'COMPLETED' AND event_name IN ('SPINUP_CLUSTER', 'SPINDOWN_CLUSTER')
  AND timestamp >= DATEADD(day, -p.days, p.end_date) AND timestamp < p.end_date
GROUP BY 1, 2
ORDER BY events DESC;
```
- Read: many spin-ups with little queueing in W4 → `ECONOMY` scaling policy or a lower `max_cluster_count` saves credits; queueing with `max_cluster_count` already reached → raise it or split workloads.
- Per-cluster credits: `QUERY_HISTORY.CLUSTER_NUMBER` shows which cluster ran each query.

### W8. Spilling per warehouse (sizing signal)
```sql
WITH p AS (SELECT 14 AS days, CURRENT_DATE() AS end_date)
SELECT warehouse_name, warehouse_size, COUNT(*) AS queries,
       COUNT_IF(bytes_spilled_to_local_storage > 0) AS local_spill_queries,
       COUNT_IF(bytes_spilled_to_remote_storage > 0) AS remote_spill_queries,
       SUM(bytes_spilled_to_remote_storage) / POWER(1024, 3) AS remote_spill_gb
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY, p
WHERE warehouse_name IS NOT NULL
  AND start_time >= DATEADD(day, -p.days, p.end_date) AND start_time < p.end_date
GROUP BY 1, 2
ORDER BY remote_spill_gb DESC;
```
- Read: remote spill on many queries → the size is too small for the workload (or the queries need tuning, `performance.md` P4). No spill and low load → try one size down.
- Pitfall: one bad query can spill on any size: look at it first before resizing.

### W9. Workload mix per warehouse
```sql
WITH p AS (SELECT 14 AS days, CURRENT_DATE() AS end_date)
SELECT warehouse_name, query_type, COUNT(*) AS queries,
       APPROX_PERCENTILE(total_elapsed_time, 0.5) / 1000 AS p50_s,
       APPROX_PERCENTILE(total_elapsed_time, 0.95) / 1000 AS p95_s
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY, p
WHERE warehouse_name IS NOT NULL
  AND start_time >= DATEADD(day, -p.days, p.end_date) AND start_time < p.end_date
GROUP BY 1, 2
ORDER BY 1, queries DESC;
```
- Read: BI dashboards (many short SELECTs) and batch loads (few long DML) on one warehouse → split them: sizes and auto-suspend differ.

### W10. Warehouses that billed but nobody used much
```sql
WITH p AS (SELECT 30 AS days, CURRENT_DATE() AS end_date),
m AS (SELECT warehouse_name, SUM(credits_used) AS credits
      FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY, p
      WHERE start_time >= DATEADD(day, -p.days, p.end_date) AND start_time < p.end_date GROUP BY 1),
q AS (SELECT warehouse_name, COUNT(*) AS queries, COUNT(DISTINCT user_name) AS users
      FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY, p
      WHERE start_time >= DATEADD(day, -p.days, p.end_date) AND start_time < p.end_date GROUP BY 1)
SELECT m.warehouse_name, m.credits, COALESCE(q.queries, 0) AS queries, COALESCE(q.users, 0) AS users,
       m.credits / NULLIF(q.queries, 0) AS credits_per_query
FROM m LEFT JOIN q ON q.warehouse_name = m.warehouse_name
ORDER BY credits_per_query DESC NULLS FIRST;
```
- Read: credits with almost no queries → a keep-alive, a monitoring ping, or a forgotten `auto_suspend` setting.
- Pitfall: joins on name (both views carry it); a renamed warehouse splits into two rows - use `warehouse_id` where both sides have it.

### W11. What-if: one size down
- Estimate only: compute credits / 2 if runtime stays equal; queries that spill or scan heavily get slower and may not save. Test by running the top shapes (`cost.md` C8) on the smaller size for a week and comparing W2 and W8. Resizing is a change → user-run.
