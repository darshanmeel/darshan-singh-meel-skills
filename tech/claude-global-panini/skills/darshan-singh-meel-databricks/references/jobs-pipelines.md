# Jobs and pipelines

## Rules
- `job_run_timeline` slices runs longer than an hour into hourly rows (clock-hour aligned for rows from 2026-01-19); `result_state` and `termination_code` are set only on the final slice → filter `result_state IS NOT NULL` for outcomes; take `MIN(period_start_time)` over all slices for the run start.
- A retried or repaired run writes one final row per attempt with the same `run_id` → dedupe to the last attempt (`ORDER BY period_end_time DESC`) for "final outcome"; count all final rows for "attempts".
- `result_state`: `SUCCEEDED`, `FAILED`, `SKIPPED`, `CANCELLED`, `TIMED_OUT`, `ERROR`, `BLOCKED`, NULL (intermediate). Failures = `FAILED`, `ERROR`, `TIMED_OUT`.
- `run_type`: `JOB_RUN` (normal) · `SUBMIT_RUN` (one-time, no `jobs` row) · `WORKFLOW_RUN` (notebook workflow, only in `job_run_timeline`, billed to the parent notebook).
- Run-level phase columns (`setup_`, `queue_`, `run_`, `execution_`, `cleanup_duration_seconds`) are filled only for legacy single-task jobs; multi-task runs show 0 → treat 0 as "not reported", use `job_task_run_timeline` per task, or wall clock `timestampdiff(SECOND, start, end)`.
- A run that never started has `period_start_time = period_end_time`.
- Several columns (`compute`, `termination_type`, the run duration columns, `timeout_seconds`, `health_rules`) are not populated for rows before early Dec 2025.
- Exclude the incomplete current day: `period_end_time < current_date()`.

## Base CTE: one row per run, final attempt
```sql
WITH runs AS (
  SELECT workspace_id, job_id, run_id, run_type, trigger_type,
         MIN(period_start_time) OVER (PARTITION BY workspace_id, job_id, run_id) AS run_start,
         period_end_time AS run_end, result_state, termination_code
  FROM system.lakeflow.job_run_timeline
  WHERE period_start_time >= date_sub(current_date(), :days + 7) AND period_end_time < current_date()
  QUALIFY result_state IS NOT NULL
      AND ROW_NUMBER() OVER (PARTITION BY workspace_id, job_id, run_id ORDER BY period_end_time DESC) = 1
)
```
- The +7 days read-back keeps the first slices of runs that started before the window; then filter `run_start >= date_sub(current_date(), :days)`.
- Window functions run before QUALIFY, so `run_start` spans every slice and attempt; attempts are counted in J4.
- Job names: `, jobs AS (SELECT workspace_id, job_id, name FROM system.lakeflow.jobs QUALIFY ROW_NUMBER() OVER (PARTITION BY workspace_id, job_id ORDER BY change_time DESC) = 1)`.

## Questions
### J1 Which jobs fail most?
```sql
-- runs CTE + jobs CTE
SELECT r.workspace_id, r.job_id, j.name, COUNT(*) AS runs,
       COUNT_IF(r.result_state IN ('FAILED','ERROR','TIMED_OUT')) AS failed,
       ROUND(100 * COUNT_IF(r.result_state IN ('FAILED','ERROR','TIMED_OUT')) / COUNT(*), 1) AS fail_pct
FROM runs r LEFT JOIN jobs j ON j.workspace_id = r.workspace_id AND j.job_id = r.job_id
WHERE r.run_start >= date_sub(current_date(), :days)
GROUP BY r.workspace_id, r.job_id, j.name
HAVING COUNT_IF(r.result_state IN ('FAILED','ERROR','TIMED_OUT')) > 0
ORDER BY failed DESC LIMIT 50;
```
- Aggregates are repeated on purpose: a select-list alias used in another expression under `GROUP BY ALL` fails (`UNSUPPORTED_FEATURE.LATERAL_COLUMN_ALIAS_IN_GROUP_BY`).

### J2 Latest run state per job, failures since the last success
```sql
-- runs CTE + jobs CTE
, per_job AS (
  SELECT workspace_id, job_id, MAX_BY(result_state, run_start) AS latest_state, MAX(run_start) AS latest_start,
         MAX(CASE WHEN result_state = 'SUCCEEDED' THEN run_start END) AS last_success
  FROM runs WHERE run_start >= date_sub(current_date(), :days) GROUP BY workspace_id, job_id)
SELECT p.workspace_id, p.job_id, j.name, p.latest_state, p.latest_start, p.last_success,
       COUNT_IF(r.result_state IN ('FAILED','ERROR','TIMED_OUT') AND (p.last_success IS NULL OR r.run_start > p.last_success)) AS failures_since_success
FROM per_job p
JOIN runs r ON r.workspace_id = p.workspace_id AND r.job_id = p.job_id AND r.run_start >= date_sub(current_date(), :days)
LEFT JOIN jobs j ON j.workspace_id = p.workspace_id AND j.job_id = p.job_id
GROUP BY p.workspace_id, p.job_id, j.name, p.latest_state, p.latest_start, p.last_success
ORDER BY failures_since_success DESC LIMIT 100;
```
- Read: `last_success` NULL → no success inside `:days` (not "never").

### J3 Why do runs fail? (termination codes)
- `runs` grouped by `termination_code` and job; `CLUSTER_ERROR`/`DRIVER_ERROR` → compute; `RUN_EXECUTION_ERROR` → code or data; `UNAUTHORIZED_ERROR` → permission; `MAX_CONCURRENT_RUNS_EXCEEDED` → schedule overlap. Task-level detail: `job_task_run_timeline.termination_code` per `task_key`.

### J4 Retries and repairs
```sql
SELECT workspace_id, job_id, run_id, COUNT(*) AS attempts,
       MAX_BY(result_state, period_end_time) AS final_state
FROM system.lakeflow.job_run_timeline
WHERE result_state IS NOT NULL AND period_start_time >= date_sub(current_date(), :days)
GROUP BY ALL HAVING attempts > 1 ORDER BY attempts DESC LIMIT 100;
```
- Task retries: same on `job_task_run_timeline` by `run_id` (task run) or by `job_run_id, task_key`.

### J5 Duration regression
```sql
-- runs CTE with :days = 28
, d AS (
  SELECT workspace_id, job_id,
         percentile_approx(CASE WHEN run_start >= date_sub(current_date(), 7) THEN timestampdiff(SECOND, run_start, run_end) END, 0.5) AS p50_recent_s,
         percentile_approx(CASE WHEN run_start <  date_sub(current_date(), 7) THEN timestampdiff(SECOND, run_start, run_end) END, 0.5) AS p50_before_s,
         COUNT_IF(run_start >= date_sub(current_date(), 7)) AS runs_recent,
         COUNT_IF(run_start <  date_sub(current_date(), 7)) AS runs_before
  FROM runs
  WHERE result_state = 'SUCCEEDED' AND run_start >= date_sub(current_date(), 28)
  GROUP BY workspace_id, job_id)
SELECT workspace_id, job_id, p50_recent_s, p50_before_s, runs_recent, runs_before
FROM d
WHERE runs_recent >= 3 AND runs_before >= 3 AND p50_recent_s >= 1.5 * p50_before_s
ORDER BY p50_recent_s - p50_before_s DESC;
```
- Read: last 7 days vs the 21 before, successful runs only; compare measured periods, never scale one.

### J6 Long-running runs right now or recently
- `runs` duration vs the job's own p90 of successful runs; running now = slices with `result_state IS NULL` and `period_end_time` within the last hour and no final row yet (latency up to 1 h).

### J7 Slow tasks and setup time
```sql
SELECT workspace_id, job_id, task_key, COUNT(*) AS task_runs,
       percentile_approx(execution_duration_seconds, 0.5) AS exec_p50_s,
       percentile_approx(setup_duration_seconds, 0.5) AS setup_p50_s
FROM system.lakeflow.job_task_run_timeline
WHERE result_state IS NOT NULL AND period_start_time >= date_sub(current_date(), :days)
GROUP BY ALL ORDER BY exec_p50_s DESC LIMIT 50;
```
- Read: large setup vs execution → cluster start dominates: pools, serverless, or one shared job cluster across tasks.

### J8 Queue time
- Run-level `queue_duration_seconds` (filled only for single-task legacy jobs); the task timeline has no queue column (setup, execution, cleanup only) → for SQL tasks use `query.history.waiting_at_capacity_duration_ms` / `waiting_for_compute_duration_ms`, else the gap between the run's first slice and its first task's `period_start_time`.

### J9 Jobs and tasks without a timeout
- Latest `jobs` and `job_tasks` rows with `timeout_seconds = 0` (no bound configured) vs NULL (not populated, older rows) — report the two separately; skip tasks of deleted jobs.

### J10 What did failed runs cost?
```sql
-- WITH priced AS (cost.md base CTE), runs AS (base CTE above), same :days
SELECT p.workspace_id, p.usage_metadata.job_id AS job_id, r.result_state,
       COUNT(DISTINCT r.run_id) AS runs, ROUND(SUM(p.usd_list), 2) AS usd_list
FROM priced p
JOIN runs r ON r.workspace_id = p.workspace_id AND r.job_id = p.usage_metadata.job_id
           AND r.run_id = p.usage_metadata.job_run_id
WHERE r.result_state IN ('FAILED','ERROR','TIMED_OUT')
GROUP BY ALL ORDER BY usd_list DESC LIMIT 50;
```
- Read: list-price waste estimate; `runs` is one row per run, so no fan-out. Failing before compute started costs ~0; runs on all-purpose clusters carry no `job_run_id` and drop out.

### J11 Pipeline update failures
```sql
SELECT workspace_id, pipeline_id, update_id,
       MAX_BY(update_type, period_end_time) AS update_type, MAX_BY(result_state, period_end_time) AS result_state,
       MIN(period_start_time) AS update_start, MAX(period_end_time) AS update_end
FROM system.lakeflow.pipeline_update_timeline
WHERE period_start_time >= date_sub(current_date(), :days)
GROUP BY workspace_id, pipeline_id, update_id
HAVING MAX_BY(result_state, period_end_time) IN ('FAILED', 'CANCELED')  -- values: COMPLETED, FAILED, CANCELED
ORDER BY update_start DESC LIMIT 200;
```
- Error detail: `lakeflow_pipeline_events_preview.pipeline_events` (Beta) with `level = 'ERROR'` on the same `workspace_id, pipeline_id, update_id` → `error.exceptions[0].error_class`, `.sql_state`, `error.fatal`; `message` can echo data → aggregate by error class.
- Name and settings: latest `lakeflow.pipelines` row (`name`, `pipeline_type`, `settings.photon`, `run_as`). Full refreshes (`full_refresh_selection`) are costly; frequent ones → check upstream schema changes.

### J12 Stale jobs (not run, not paused)
- Latest `jobs` rows (`paused = false`, live) with no run in `:days`, or whose last run start is older than retention can show → say "no run in history", not "never ran".

### J13 Jobs running as people
- Latest `jobs` rows: `run_as` / `run_as_user_name` looks like an email → runs as a person; recommended pattern is a service principal. `creator_user_name <> run_as_user_name` alone is not an orphan signal.

### J14 Never-started runs
- `job_run_timeline` rows with `period_start_time = period_end_time` and their `termination_code` (concurrency limits, invalid config, cluster errors).

### J15 When do jobs run? (load by hour)
- Active runs per UTC hour from slices; overlap with warehouse queueing (compute K8) explains slow BI hours.

### J16 Job health rules and notifications
- Latest `jobs.health_rules` (and `job_tasks.health_rules`): jobs with no duration rule are blind to regressions.

## Build rules: notebooks and deploy
- No leftover `display()`, test cells or hard-coded widget values in production notebooks.
- Reusable logic in Python modules, not copy-pasted cells.
- Deploy with Asset Bundles (`databricks bundle validate`, `databricks bundle deploy -t <env>`) or the project's CI; never edit jobs in the UI.
