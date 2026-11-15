# Compute: clusters, pools, SQL warehouses

## Rules
- `compute.clusters` covers classic compute only: `cluster_source` `UI`/`API` = all-purpose, `JOB` = job compute, `PIPELINE`/`PIPELINE_MAINTENANCE` = pipelines. Serverless and SQL warehouses are not in it.
- Auto-termination matters on all-purpose clusters only; job and pipeline clusters end with their run.
- `data_security_mode`: `USER_ISOLATION` = Standard, `SINGLE_USER` = Dedicated; `NONE` and `LEGACY_*` = no isolation or legacy (flag them); NULL on some system-created clusters.
- `node_timeline` = one row per node-minute, classic only; nodes shorter than 10 min may be missing → "no telemetry" is not "idle".
- Warehouse state comes from `warehouse_events`; query activity from `query.history` (`compute.type = 'WAREHOUSE'`). `SCALING_UP`/`SCALING_DOWN` appear in a docs sample but are not documented event types: ignore them.
- Sizing logic: **queueing** (`waiting_at_capacity_duration_ms`) → more clusters (`max_clusters`); **spill / slow single queries** (`spilled_local_bytes`) → larger size; **cold starts** (`waiting_for_compute_duration_ms`) → serverless or a longer auto-stop; **idle uptime** → shorter auto-stop.

## Questions
### K1 Current config of every live cluster
```sql
SELECT workspace_id, cluster_id, cluster_name, cluster_source, owned_by, dbr_version, data_security_mode,
       policy_id, driver_node_type, worker_node_type, worker_count, min_autoscale_workers, max_autoscale_workers,
       auto_termination_minutes
FROM system.compute.clusters
QUALIFY ROW_NUMBER() OVER (PARTITION BY workspace_id, cluster_id ORDER BY change_time DESC) = 1
  AND delete_time IS NULL;
```
- Read: filter the latest row first, then `delete_time` (filtering earlier returns a deleted cluster's last live state).

### K2 All-purpose clusters with no or long auto-termination
- K1 with `cluster_source IN ('UI','API') AND (auto_termination_minutes IS NULL OR auto_termination_minutes = 0 OR auto_termination_minutes > :max_minutes)`; join C6 cost to rank.

### K3 Clusters without a policy, on old runtimes, or without isolation
- K1 with `policy_id IS NULL`, `data_security_mode IN ('NONE') OR data_security_mode LIKE 'LEGACY%'`, `dbr_version` below the oldest supported LTS (check: Databricks Runtime support lifecycle page).

### K4 How busy are a cluster's nodes?
```sql
SELECT workspace_id, cluster_id, driver,
       percentile_approx(cpu_user_percent + cpu_system_percent, 0.9) AS cpu_p90,
       MAX(mem_used_percent) AS mem_peak, MAX(mem_swap_percent) AS swap_peak,
       COUNT(*) AS node_minutes
FROM system.compute.node_timeline
WHERE start_time >= date_sub(current_date(), :days)
GROUP BY ALL ORDER BY node_minutes DESC LIMIT 100;
```
- Read: workers (`driver = false`) with CPU p90 < ~30 % and memory peak < ~40 % without swap over several runs → oversized; any sustained swap → memory pressure, do not shrink. Thresholds are heuristics, not vendor numbers.

### K5 Oversized job clusters
- `job_task_run_timeline` → `explode(compute_ids)` → `node_timeline.cluster_id` (same workspace) → K4 per `job_id`; price with cost C3. No compute id or no telemetry → NOT_ASSESSED (serverless, or older rows: check `MIN(period_start_time)` of rows with `compute_ids` set), never "not oversized".

### K6 Current config of every live SQL warehouse
```sql
SELECT workspace_id, warehouse_id, warehouse_name, warehouse_type, warehouse_channel, warehouse_size,
       min_clusters, max_clusters, auto_stop_minutes, tags
FROM system.compute.warehouses
QUALIFY ROW_NUMBER() OVER (PARTITION BY workspace_id, warehouse_id ORDER BY change_time DESC) = 1
  AND delete_time IS NULL;
```
- Values: type `CLASSIC`/`PRO`/`SERVERLESS`; channel `CURRENT`/`PREVIEW`; size `2X_SMALL` … `5X_LARGE` (5X_LARGE Beta, PRO/SERVERLESS).

### K7 Warehouse uptime vs query activity (idle time)
```sql
WITH ev AS (
  SELECT workspace_id, warehouse_id, event_type, cluster_count, event_time,
         LEAD(event_time) OVER (PARTITION BY workspace_id, warehouse_id ORDER BY event_time) AS next_time
  FROM system.compute.warehouse_events
  WHERE event_time >= date_sub(current_date(), :days) AND event_time < current_date())
SELECT workspace_id, warehouse_id,
       SUM(CASE WHEN event_type IN ('STARTING','RUNNING','SCALED_UP','SCALED_DOWN') AND cluster_count > 0
                THEN timestampdiff(SECOND, event_time, COALESCE(next_time, current_date())) END) / 60 AS up_minutes
FROM ev GROUP BY ALL ORDER BY up_minutes DESC;
```
- Busy minutes: distinct minutes covered by statements per warehouse.
```sql
SELECT workspace_id, compute.warehouse_id AS warehouse_id, COUNT(DISTINCT m) AS busy_minutes
FROM system.query.history
LATERAL VIEW explode(sequence(date_trunc('MINUTE', start_time), date_trunc('MINUTE', end_time), INTERVAL 1 MINUTE)) t AS m
WHERE compute.type = 'WAREHOUSE' AND start_time >= date_sub(current_date(), :days) AND start_time < current_date()
  AND end_time IS NOT NULL
GROUP BY ALL;
```
- `idle = up − busy` per warehouse (join the two results on `workspace_id, warehouse_id`). State at window start comes from the last event before it (read a day earlier and clip).
- Pitfalls: events sharing a timestamp → order STARTING, RUNNING, SCALED_*, STOPPING, STOPPED; activity query history does not record (some API or catalog calls) can keep a warehouse up.

### K8 Queueing → add clusters?
```sql
SELECT workspace_id, compute.warehouse_id AS warehouse_id, date_trunc('HOUR', start_time) AS hour_utc,
       COUNT(*) AS statements,
       SUM(waiting_at_capacity_duration_ms) / 1000 AS queued_s,
       SUM(waiting_for_compute_duration_ms) / 1000 AS cold_start_s,
       percentile_approx(total_duration_ms, 0.95) / 1000 AS p95_s
FROM system.query.history
WHERE compute.type = 'WAREHOUSE' AND start_time >= date_sub(current_date(), :days)
GROUP BY ALL ORDER BY queued_s DESC LIMIT 100;
```
- Read: queued seconds concentrated in busy hours while `max_clusters` is reached → raise `max_clusters`; cold-start seconds → auto-stop too short or move to serverless.
- Pitfall: NULL + NULL is NULL; wrap sums in `COALESCE` before comparing, or a non-measured warehouse reads "fine".

### K9 Spill → size up?
- `query.history` per warehouse: share of statements with `spilled_local_bytes > 0`, top statements by `spilled_local_bytes`; heavy spill on a small size → next size; spill on one statement only → fix the query first (performance.md).

### K10 Dormant warehouses and clusters
```sql
WITH wh AS (SELECT workspace_id, warehouse_id, warehouse_name, warehouse_type, warehouse_size, min_clusters
            FROM system.compute.warehouses
            QUALIFY ROW_NUMBER() OVER (PARTITION BY workspace_id, warehouse_id ORDER BY change_time DESC) = 1
                AND delete_time IS NULL),
q AS (SELECT DISTINCT workspace_id, compute.warehouse_id AS warehouse_id FROM system.query.history
      WHERE compute.type = 'WAREHOUSE' AND start_time >= date_sub(current_date(), :days)),
ev AS (SELECT DISTINCT workspace_id, warehouse_id FROM system.compute.warehouse_events
       WHERE event_time >= date_sub(current_date(), :days))
SELECT wh.workspace_id, wh.warehouse_id, wh.warehouse_name, wh.warehouse_type, wh.warehouse_size,
       ev.warehouse_id IS NOT NULL AS had_state_changes
FROM wh
LEFT JOIN q ON q.workspace_id = wh.workspace_id AND q.warehouse_id = wh.warehouse_id
LEFT JOIN ev ON ev.workspace_id = wh.workspace_id AND ev.warehouse_id = wh.warehouse_id
WHERE q.warehouse_id IS NULL;
```
- Read: no statement in `:days` (≤ 365, query history retention); `had_state_changes = true` → it still starts (API or catalog calls, K7 pitfall) and costs money. Starts from the config (K6), so a warehouse with no events still shows.
- Clusters: live all-purpose clusters (K1, `cluster_source IN ('UI','API')`) LEFT JOIN `billing.usage` rows with that `usage_metadata.cluster_id` in `:days`; no usage → dormant.

### K11 Autoscale churn on warehouses
- `warehouse_events` `SCALED_UP`/`SCALED_DOWN` between running clusters only (exclude the 0→1 start and 1→0 stop: `cluster_count` before/after via `LAG`). Many changes per hour → `min_clusters` too low for the steady load.

### K12 Auto-stops and restarts
- `STOPPED` events per warehouse per day; restarts within minutes of a stop → `auto_stop_minutes` shorter than the gaps between workloads (cold-start cost on classic/pro).

### K13 Jobs running on all-purpose clusters
- `job_task_run_timeline` → `explode(compute_ids)` → latest `clusters` row with `cluster_source IN ('UI','API')`. These runs pay all-purpose rates and their cost is not on the job (cost C3 pitfall).

### K14 Instance pool idle capacity
- Latest `instance_pools` row (`min_idle_instances`, `idle_instance_autotermination_minutes`, `max_capacity`); `instance_events` `INSTANCE_READY` (idle) vs `INSTANCE_PLACED` (in use) time per pool. High idle with `min_idle_instances > 0` → paying for warm nodes nobody uses.

### K15 Node types in use and their size
- Latest clusters' `worker_node_type`/`driver_node_type` joined to `compute.node_types` (`core_count`, `memory_mb`, `gpu_count`); GPU nodes idle in K4 are the costliest finding.

## Tuning playbook (proposals; changes run by the user)
- **Warehouse:** serverless for bursty or interactive BI; one warehouse per workload class (BI vs ETL); size for the largest common query, clusters for concurrency; auto-stop short on serverless, longer on classic/pro where start-up is slow (check: SQL warehouse sizing and auto-stop page for current minimums).
- **Clusters:** job compute for scheduled work; policies enforce auto-termination, node types and tags; autoscale with a sane max; Photon for SQL-heavy work; Standard access mode unless a feature needs Dedicated.
