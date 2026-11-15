# System tables map

All in catalog `system`; read-only; free to store, you pay for the compute that queries them. Needs a Unity Catalog workspace; access = `USE CATALOG` on `system` + `USE SCHEMA` and `SELECT` per schema (account admins that are also metastore admins see them by default). Retention and status below are the AWS reference page; other clouds can differ (check: system tables reference for your cloud). 395 d is the default: an account admin can set 30–3,650 d with the `st_retention` account setting (Beta; no backfill; tables with 365-day or indefinite retention and the `data_classification`, `data_quality_monitoring`, `lakebase` schemas keep their own) → read `MIN(time)` before trusting a long window.

## Tables

| Table | One row = | Key | Time column | Latency (typical) | Retention | Shape · scope |
|---|---|---|---|---|---|---|
| `billing.usage` | one billed usage record (hourly or finer bucket, per SKU) | `record_id` | `usage_date`, `usage_start_time`, `usage_end_time` (UTC) | ≤ 12 h (ORIGINAL rows) | indefinite | events · global |
| `billing.list_prices` | one price period of one SKU | `sku_name, cloud, usage_unit, currency_code, price_start_time` | `price_start_time` / `price_end_time` (NULL = current) | – | indefinite | history · global |
| `billing.attributed_usage` | SQL-warehouse DBUs attributed to one statement (`usage_metadata.dbsql_statement_id`, `active_usage_quantity`) | `record_id` | `usage_date` | check | check | events (check: not in the reference page; confirm it exists on the account) |
| `compute.clusters` | one config version of a classic cluster | `workspace_id, cluster_id, change_time` | `change_time`, `delete_time` | ≤ 1 h | indefinite | SCD · regional; no serverless, no warehouses; clusters deleted before 2023-10-23 missing |
| `compute.warehouses` | one config version of a SQL warehouse | `workspace_id, warehouse_id, change_time` | `change_time`, `delete_time` | ≤ 1 h | 395 d | SCD · regional |
| `compute.warehouse_events` | one state change (`STARTING, RUNNING, SCALED_UP, SCALED_DOWN, STOPPING, STOPPED`) | `workspace_id, warehouse_id, event_time` | `event_time` | ≤ 1 h | 395 d | events · regional |
| `compute.node_timeline` | one node for one minute (CPU, memory, swap, network) | `workspace_id, cluster_id, instance_id, start_time` | `start_time` | ≤ 1 h | 395 d | events · classic only; nodes < 10 min may be missing |
| `compute.node_types` | one node type (`core_count, memory_mb, gpu_count`) | `node_type` | – | – | indefinite | reference |
| `compute.instance_events` / `instance_pools` | instance state change / pool config version | `instance_id, event_time` / `instance_pool_id, change_time` | `event_time` / `change_time` | ≤ 1 h | 395 d | Public Preview |
| `query.history` | one statement on a warehouse, serverless notebook/job, or pipeline | `statement_id` | `start_time`, `end_time` | ≤ 1 h | 365 d | events · regional |
| `lakeflow.jobs` / `job_tasks` / `pipelines` | one config version of a job / task / pipeline | `workspace_id, job_id[, task_key]` / `workspace_id, pipeline_id` + `change_time` | `change_time`, `delete_time` | ≤ 1 h | 395 d (pipelines indefinite; latest row kept beyond retention) | SCD · regional |
| `lakeflow.job_run_timeline` | one slice (≤ 1 clock hour) of a job run | `workspace_id, job_id, run_id, period_start_time` | `period_start_time` | ≤ 1 h after `period_end_time` | 395 d | events · `result_state` only on the final slice |
| `lakeflow.job_task_run_timeline` | one slice of a task run (`run_id` = task run, `job_run_id` = parent) | `workspace_id, job_id, run_id, period_start_time` | `period_start_time` | ≤ 1 h | 395 d | events |
| `lakeflow.pipeline_update_timeline` | one slice of a pipeline update | `workspace_id, pipeline_id, update_id, period_start_time` | `period_start_time` | ≤ 1 h | 395 d | events |
| `access.audit` | one audit event | `event_id` | `event_date` (partition), `event_time` | check | 395 d | Public Preview · workspace events regional, account events global (`workspace_id = '0'`) |
| `access.table_lineage` / `column_lineage` | one read/write event between tables, paths or columns | `record_id` | `event_date` (partition), `event_time` | check | 395 d | events · only when lineage can be inferred |
| `access.workspaces_latest` | one workspace, current state | `workspace_id` | – | – | indefinite | Public Preview · global |
| `access.inbound_network` / `outbound_network` | one denied request (inbound: `policy_outcome` `DENY` or `DENY_DRY_RUN`; outbound has no outcome column) | `event_id` | `event_time` | ≤ 1 h | 395 d | Public Preview · regional |
| `serving.served_entities` | one config version of a served entity | `workspace_id, served_entity_id, change_time` | `change_time` | ≤ 1 h | 395 d | SCD · Public Preview · regional · account admins only |
| `serving.endpoint_usage` | one request to an endpoint with usage tracking on | `databricks_request_id` | `request_time` | ≤ 1 h | 395 d (other clouds less: check) | events · regional · account admins only |
| `ai_gateway.usage` | one request through the AI gateway (tokens, latency, requester) | `request_id` | `event_time` | check | 395 d | Public Preview · global (columns: check: `DESCRIBE`) |
| `ai_gateway.external_model_spend` | estimated USD spend of external-model requests | check | check | check | 395 d | Beta · regional (columns: check: `DESCRIBE`; an estimate, not `billing.usage`) |
| `lakeflow_pipeline_events_preview.pipeline_events` | one pipeline event-log entry (`event_type`, `level` INFO/WARN/ERROR/METRICS, `message`, `error` struct, `details` variant, `origin`) | `pipeline_event_id` | `event_time` | check | 395 d | Beta · regional · moves to `lakeflow.pipeline_events` at GA |
| `storage.predictive_optimization_operations_history` | one maintenance operation (or part) on a managed table | `operation_id` | `start_time` | ≤ 12 h | 395 d (other clouds less: check) | Public Preview · `usage_unit = 'ESTIMATED_DBU'` |
| `storage.table_metrics_history` | one table on one snapshot day (`active_bytes, active_files, predictive_optimization_enabled`) | `table_id, snapshot_date` | `snapshot_date` | check | 13 months | Public Preview · managed tables · `table_dropped_time` set once dropped |
| `data_classification.results` | one detected class on one column (`class_tag, confidence, frequency`) | `catalog_name, schema_name, table_name, column_name, class_tag` | `latest_detected_time` | check | 395 d | Public Preview · detections only, no "scanned, clean" row · `samples` holds up to five raw matched values: never select it |
| `information_schema.*` (in `system` = all catalogs; in `<catalog>` = that catalog) | objects, grants, tags, masks, filters | object names | `last_altered` | live | live | privilege-aware: shows only what the caller can see |

## Also exists (no catalogue entry yet; `DESCRIBE` before use)
All 395 d and regional unless noted (system tables index).
- `data_quality_monitoring.table_results`: freshness and completeness check results and incidents.
- `mlflow.experiments_latest`, `mlflow.runs_latest`, `mlflow.run_metrics_history`: experiments, runs, logged metrics (Public Preview).
- `alert.alerts` (SCD config) and `alert.alert_evaluation_history` (one row per evaluation, state and notification delivery).
- `access.assistant_events` (Genie Code messages; people's data) and `access.clean_room_events` (Public Preview).
- `sharing.materialization_history`: materializations for shared views, materialized views, streaming tables.
- `storage.table_auto_upgrade_operations_history`: automatic feature enablement on managed tables (Public Preview).
- `tags.governed_tags`: governed tag definitions (Beta, global, indefinite).
- `replication.states`: managed disaster-recovery replication status (global).
- `lakebase.*`: Lakebase Postgres telemetry (Beta, 7 d).
- `marketplace.listing_funnel_events`, `marketplace.listing_access_events` (Public Preview; consumer data).
- `lakeflow.zerobus_stream`, `lakeflow.zerobus_ingest`: Zerobus Ingest streams and records (Beta).
- Other Private Preview tables can appear, empty by default.

## People's data in `system.*` (the PII discovery for these tables)
Columns: `executed_by`, `executed_as`, `statement_text`, `error_message` (query history) · `created_by` (lineage) · `run_as`, `owned_by`, `creator_user_name`, `run_as_user_name` (compute, jobs, pipelines) · `identity_metadata.run_as`, `.run_by`, `.owned_by` (billing, audit) · `usage_metadata.notebook_path` · `requester` (serving, AI gateway), `ip_address` (check: `DESCRIBE`) · `user_identity.email`, `source_ip_address`, `user_agent`, `request_params` (audit) · `authenticated_as`, `source` (inbound network) · `private_ip` (node timeline) · `message`, `details` (pipeline events) · `samples` (classification: raw values, never select it) · grantee and owner names that are emails.
- In outputs: `COUNT(DISTINCT col)`, or the keyed hash `sha2(concat(:k, col), 256) AS col_key` with `k=PII_KEY` bound (notebook skill §6; HMAC form there where `hmac()` exists). Never plain `sha2(col)`, never the raw value.
- Text columns (`statement_text`, `error_message`, `message`): only derived values leave the query (error class, fingerprint hash, regex-extracted column names), never the text.

## Join map
| From → to | Keys | Watch |
|---|---|---|
| `usage` → `list_prices` | `sku_name` (+ `cloud`, `usage_unit`, `currency_code = 'USD'`) and `usage_end_time >= price_start_time AND (price_end_time IS NULL OR usage_end_time < price_end_time)` | the docs sample joins on `sku_name` only; adding cloud/unit/currency prevents fan-out; dropping the `IS NULL` branch zeroes current usage |
| `usage` → `clusters` | `workspace_id`, `usage_metadata.cluster_id` | latest row, or as-of `change_time <= usage_start_time` for the owner at the time |
| `usage` → `warehouses` | `workspace_id`, `usage_metadata.warehouse_id` | latest row |
| `usage` → `jobs` | `workspace_id`, `usage_metadata.job_id` | latest row; one-time runs (`SUBMIT_RUN`) have no `jobs` row |
| `usage` → `job_run_timeline` | `workspace_id`, `usage_metadata.job_id`, `usage_metadata.job_run_id = run_id` | jobs on all-purpose clusters carry no `job_id` on the bill |
| `usage` → `pipelines` | `workspace_id`, `usage_metadata.dlt_pipeline_id = pipeline_id` | latest row |
| `usage` → `served_entities` | `workspace_id`, `usage_metadata.endpoint_id = endpoint_id` | roll entities up per endpoint first (fan-out) |
| `query.history` → `warehouses` | `workspace_id`, `compute.warehouse_id` | only `compute.type = 'WAREHOUSE'` has it; `cluster_id` never populated |
| `query.history` → jobs / dashboards / notebooks | `query_source.job_info.job_id`, `.dashboard_id`, `.notebook_id`, `.genie_space_id`, `.sql_query_id` | several ids can be set at once |
| `query.history` → lineage | `workspace_id`, `statement_id` | lineage carries `statement_id` only for SQL warehouse and serverless statements |
| `query.history` → `attributed_usage` | `workspace_id`, `statement_id = usage_metadata.dbsql_statement_id` | check: confirm ids match on the account |
| `job_run_timeline` → `job_task_run_timeline` | `workspace_id, job_id`, run `run_id` = task `job_run_id` | |
| `job_task_run_timeline` → `clusters`, `node_timeline` | `workspace_id`, `explode(compute_ids)` = `cluster_id` | empty for serverless; for older rows check: jobs page (it dates `compute`, `termination_type`, duration columns, `timeout_seconds`, `health_rules` to early Dec 2025, not `compute_ids`) |
| `job_tasks` → `jobs` | `workspace_id, job_id` | both SCD |
| `endpoint_usage` → `served_entities` | `workspace_id, served_entity_id` | no `endpoint_id` on `endpoint_usage` |
| lineage `entity_id` → job / pipeline / dashboard | `entity_type = 'JOB'` → `job_id`; `entity_run_id` → run | `entity_type` NULL = no Databricks entity (JDBC, sample tab) |
| `predictive_optimization_operations_history`, `table_metrics_history` → `information_schema.tables` | `table_id`, or `catalog_name, schema_name, table_name` | names change on rename; prefer `table_id` |

## Visibility probe (Q0, run first)
```sql
-- what this principal can see in system (privilege-aware: missing = not enabled OR no grant)
SELECT table_schema, table_name
FROM system.information_schema.tables
WHERE table_catalog = 'system' AND table_schema <> 'information_schema'
ORDER BY table_schema, table_name;
```
```sql
-- freshness of one source (one statement per table: a missing table fails the whole statement)
SELECT MAX(usage_date) AS latest_day, COUNT(*) AS rows_7d
FROM system.billing.usage
WHERE usage_date >= date_sub(current_date(), 7);
```
- Read: a needed table absent → "not visible to this principal" (schema not enabled, no grant, or another region), never "zero". `latest_day` older than the latency above → ingestion gap.
- Error classes: `SCHEMA_NOT_FOUND` / "not enabled" → schema off; `TABLE_OR_VIEW_NOT_FOUND` → table absent or invisible; `INSUFFICIENT_PERMISSIONS` / `PERMISSION_DENIED` → grant missing.

## Universal pitfalls
- **UTC everywhere.** Day buckets are UTC; say so when the user thinks in local time.
- **Regional tables** show only the region of the workspace you query from; billing, list prices, workspaces and `ai_gateway.usage` are global.
- **SCD fan-out:** joining a change-history table without the latest-row or as-of filter multiplies rows and money.
- **Ids are per workspace:** `job_id`, `cluster_id`, `warehouse_id`, `pipeline_id`, `task_key` → join with `workspace_id`.
- **Retention:** a window longer than retention silently truncates; compare `MIN(time)` with the window start before calling a trend.
- **Two spellings:** jobs use `CANCELLED`; query history and pipeline updates (`COMPLETED`, `FAILED`, `CANCELED`) use `CANCELED`.
- **Redaction:** `statement_text` is `<REDACTED>` unless the caller is an account admin or in `databricks_pii_access`; FedRAMP workspaces show `__REDACTED__` in billing identities; customer-managed keys encrypt `statement_text` and `error_message`.
- **Columns added later** (e.g. job `compute`, `termination_type`, duration columns, `timeout_seconds`) are NULL on older rows: NULL = "not reported", not 0.
- **Function differences:** `dayofweek()` is Sunday=1; regex is Java syntax (escape `[`); `QUALIFY` works on Databricks SQL.
- **Streaming reads** of system tables need `skipChangeCommits = true`; a stream more than 7 days behind can break (7-day VACUUM).

## Columns (appendix, for offline name checks)
Columns the catalogue uses, from the pages in `sources.md`; not complete (`DESCRIBE <table>` for the rest). A name not here and not in the docs → `check:`.
| Table | Columns |
|---|---|
| `billing.usage` | `record_id, account_id, workspace_id, sku_name, cloud, usage_start_time, usage_end_time, usage_date, usage_unit, usage_quantity, usage_type, record_type, ingestion_date, billing_origin_product, custom_tags` · `usage_metadata.{cluster_id, warehouse_id, job_id, job_run_id, dlt_pipeline_id, endpoint_id, endpoint_name, notebook_id, notebook_path, app_id, app_name, usage_policy_id}` (`budget_policy_id` deprecated; no `sql_warehouse_id`) · `identity_metadata.{run_as, owned_by}` · `product_features.{is_serverless, is_photon, performance_target, serving_type, model_serving.offering_type}` |
| `billing.list_prices` | `sku_name, cloud, currency_code, usage_unit, price_start_time, price_end_time, pricing.{default, promotional.default, effective_list.default}` |
| `query.history` | `workspace_id, statement_id, executed_by, executed_as, execution_status (FINISHED, FAILED, CANCELED), statement_text, statement_type, error_message, client_application, start_time, end_time, total_duration_ms, compilation_duration_ms, execution_duration_ms, waiting_for_compute_duration_ms, waiting_at_capacity_duration_ms, result_fetch_duration_ms, total_task_duration_ms, read_bytes, read_rows, produced_rows, read_files, pruned_files, read_io_cache_percent, from_result_cache, spilled_local_bytes, shuffle_read_bytes` · `compute.{type, warehouse_id}` · `query_source.{job_info.job_id, dashboard_id, notebook_id, genie_space_id, sql_query_id}` |
| `compute.clusters` | `workspace_id, cluster_id, cluster_name, cluster_source, owned_by, dbr_version, data_security_mode, policy_id, driver_node_type, worker_node_type, worker_count, min_autoscale_workers, max_autoscale_workers, auto_termination_minutes, tags, change_time, delete_time` |
| `compute.warehouses` | `workspace_id, warehouse_id, warehouse_name, warehouse_type, warehouse_channel, warehouse_size, min_clusters, max_clusters, auto_stop_minutes, tags, change_time, delete_time` |
| `compute.warehouse_events` | `workspace_id, warehouse_id, event_type, cluster_count, event_time` |
| `compute.node_timeline` | `workspace_id, cluster_id, instance_id, start_time, end_time, driver, cpu_user_percent, cpu_system_percent, mem_used_percent, mem_swap_percent` |
| `lakeflow.jobs` / `job_tasks` | `workspace_id, job_id, name, run_as, creator_user_name, paused, timeout_seconds, health_rules, change_time, delete_time` / `+ task_key, depends_on_keys` |
| `lakeflow.job_run_timeline` | `workspace_id, job_id, run_id, run_type, trigger_type, period_start_time, period_end_time, result_state, termination_code, compute, termination_type, setup_ / queue_ / run_ / execution_ / cleanup_duration_seconds` |
| `lakeflow.job_task_run_timeline` | `workspace_id, job_id, run_id, job_run_id, task_key, period_start_time, period_end_time, result_state, termination_code, compute_ids, setup_ / execution_ / cleanup_duration_seconds` (no queue column) |
| `lakeflow.pipeline_update_timeline` | `workspace_id, pipeline_id, update_id, update_type, period_start_time, period_end_time, result_state (COMPLETED, FAILED, CANCELED), full_refresh_selection` |
| `access.table_lineage` / `column_lineage` | `workspace_id, record_id, statement_id, event_time, event_date, entity_type, entity_id, entity_run_id, entity_metadata, created_by, direct_access, source_type, source_table_full_name, source_table_catalog, source_path, target_type, target_table_full_name, target_path` / `+ source_column_name, target_column_name` |
| `access.audit` | `workspace_id, event_id, event_time, event_date, service_name, action_name, request_params, user_identity.email, source_ip_address, user_agent, response.status_code (check: `DESCRIBE`; the docs example shows `statusCode`), identity_metadata.{run_by, run_as}` |
| `access.inbound_network` | `account_id, workspace_id, event_id, request_path, source, authenticated_as, event_time, policy_outcome, rule_label` |
| `access.outbound_network` | `account_id, workspace_id, event_id, destination_type, destination, dns_event, storage_event, event_time, access_type, network_source_type` |
| `serving.endpoint_usage` | `account_id, workspace_id, client_request_id, databricks_request_id, requester, status_code, request_time, input_token_count, output_token_count, input_character_count, output_character_count, usage_context, request_streaming, served_entity_id` |
| `lakeflow_pipeline_events_preview.pipeline_events` | `account_id, workspace_id, pipeline_id, update_id, pipeline_event_id, event_type, origin, message, level, maturity_level, error.{fatal, exceptions[].error_class, exceptions[].sql_state}, details, event_time` |
| `storage.predictive_optimization_operations_history` | `operation_id, catalog_name, schema_name, table_name, operation_type, operation_status, start_time, usage_quantity, usage_unit` |
| `storage.table_metrics_history` | `table_id, catalog_name, schema_name, table_name, snapshot_date, active_bytes, active_files, predictive_optimization_enabled, table_dropped_time` |
| `data_classification.results` | `catalog_name, schema_name, table_name, column_name, class_tag, confidence, frequency, latest_detected_time, samples (never select)` |
