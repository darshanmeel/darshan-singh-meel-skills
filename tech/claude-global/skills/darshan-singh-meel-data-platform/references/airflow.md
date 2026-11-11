# Airflow

- **Idempotent tasks:** rerun for the same interval = same result (overwrite or `MERGE` that interval).
- Use `data_interval_start` / `data_interval_end` / `{{ ds }}` — never `datetime.now()` in task logic.
- Static `start_date`; `catchup` set on purpose (usually `False` unless backfilling).
- No heavy top-level code: no DB/API calls, `Variable.get()`, or big imports at module level (runs on every parse). Use templating (`{{ var.value.x }}`) or fetch inside the task.
- Credentials only via Connections / secrets backend.
- XCom carries small values (paths, IDs, table names), never datasets.
- Use provider operators/hooks (Snowflake, Databricks, dbt, S3, Azure) over custom wrappers. TaskFlow if the project uses it.
- Sensors: `mode="reschedule"` or deferrable, always with `timeout`.
- Set `retries` + `retry_delay`, `execution_timeout`, `max_active_runs`.
- One task = one retryable unit of work. Don't split trivial steps into many tasks.
- Clear DAG/task ids; `owner`, `tags`, alerting as the project does.

## Deploy & access
- DAGs deploy via CI (sync to the DAG bucket/repo or image build) — never edited on the server.
- Connections/variables created through the secrets backend or IaC, documented by name.
- Docs state: Airflow URL per environment, which roles can trigger/clear runs, how to backfill (3.x: `airflow backfill create --dag-id <id> --from-date … --to-date …`; 2.x: `airflow dags backfill -s … -e … <dag_id>`).
