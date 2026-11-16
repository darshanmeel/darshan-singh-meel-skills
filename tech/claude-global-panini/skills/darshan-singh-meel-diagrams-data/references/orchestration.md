# Orchestration: `airflow-dag`, `airflow-overview`, `orchestration`

All default to the base `airflow` style (task box, type as tag, state as border colour and text, legend). `plain` drops the states' look. Shared base fields: `collapse`, `view`, `group_layout`, `direction`, `legend`, `states`, `edge_kinds`, `select`.

## `airflow-dag` - one DAG (Graph view)
```json
{"id": "warehouse-load", "type": "airflow-dag", "collapse": ["quality"],
 "groups": [{"id": "extract", "label": "extract"}],
 "tasks": [{"id": "dbt_build", "operator": "BashOperator", "state": "scheduled",
            "upstream": ["load_orders"], "outlets": ["warehouse.marts"], "trigger_rule": "all_done", "group": "extract"}]}
```
- `state`: an Airflow task instance state (`success`, `failed`, `upstream_failed`, `up_for_retry`, `running`, `queued`, `scheduled`, `skipped`, `deferred`, ...). When any task has a state, tasks without one (or `none`) show "no status", as in a run.
- `upstream` lists the task ids before it (`edges` also work).
- `trigger_rule` other than `all_success` is written in the box ("rule one_failed").
- `outlets` → an asset box (dashed purple) and a dashed "updates asset" arrow leaving the task's top.
- `groups` = TaskGroups, one level (nested groups are refused - flatten or collapse); `collapse` draws a group as one bold box with its worst state and counts per state.
- Groups lay out as columns along the flow, as bands when they run in parallel.

## `airflow-overview` - many DAGs
```json
{"id": "platform-dags", "type": "airflow-overview",
 "dags": [{"id": "dbt_build", "schedule": ["raw.crm", "raw.erp"], "tasks": 14, "state": "queued", "outlets": ["marts.core"]}],
 "links": [{"from": "dbt_build", "to": "finance_export", "kind": "trigger", "label": "TriggerDagRunOperator"}]}
```
- `schedule`: a cron or preset string (`"@daily"`, `"0 2 * * *"`), `null` (manual / external trigger), a list of assets (all must update) or `{"any": [...]}` (any one). Mixed conditions such as `a | (b & c)` have no field: list every asset in `any` and write the expression in `sub` (`"sub": "a | (b & c)"`).
- Asset arrows are inferred: a DAG whose `outlets` hold an asset → every DAG scheduled on it, labelled with the asset name(s). An asset nobody produces becomes an "asset · external" box. Asset, trigger and sensor arrows from one DAG leave on different sides.
- `show_assets: true` draws each asset as its own box between producer and consumers.
- `state` = last DAG run state (`queued`, `running`, `success`, `failed`).
- `links` kinds: `trigger` (TriggerDagRunOperator, dashed blue), `sensor` (ExternalTaskSensor, dotted grey), `asset`.
- Box tag "DAG · <schedule>", sub = state and task count; `groups` (team, domain) optional.

## `orchestration` - ADF or any pipeline tool
```json
{"id": "daily-sales-adf", "type": "orchestration", "collapse": ["each_table"],
 "triggers": [{"id": "tr_daily", "label": "daily 02:00 UTC", "type": "schedule", "starts": ["get_tables"]}],
 "containers": [{"id": "each_table", "label": "each source table", "type": "ForEach"}],
 "activities": [{"id": "alert_teams", "type": "WebActivity", "state": "succeeded",
                 "depends_on": [{"activity": "each_table", "on": "failed"}]},
                {"id": "publish", "type": "ExecutePipeline", "depends_on": ["transform"], "calls": "pl_publish_marts"}]}
```
- `type` = activity type (Copy, Lookup, Notebook, StoredProcedure, ...), shown as the tag.
- `depends_on`: activity ids (on success) or `{activity, on}` with `on` = `succeeded` (neutral line), `failed` (red), `completed` (dashed blue), `skipped` (dotted grey). Mixed conditions from one activity leave on separate sides.
- `state`: `succeeded`, `failed`, `in_progress`, `queued`, `cancelled`, `skipped` (Airflow states also accepted).
- `containers` = ForEach / If / Until / Switch activities, drawn as frames ("ForEach · each source table"). A dependency on a container attaches to its first inner activities (incoming) or last ones (outgoing); for the true container-level picture `collapse` it.
- `triggers` = pills with "trigger · <type>" and dashed arrows to `starts`.
- `calls` = Execute Pipeline target, drawn as a dashed "pipeline" box.
- Generic tools (Databricks Workflows, Step Functions, Glue): same fields; `type` holds the task type.
