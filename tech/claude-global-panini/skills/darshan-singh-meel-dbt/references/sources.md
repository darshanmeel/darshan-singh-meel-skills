# Sources (official pages)

Checked 2026-11; re-check version-gated items before relying on them.

## dbt (docs.getdbt.com)
- reference/commands/parse — `dbt parse` does not connect; manifest without compiled code or column types
- reference/commands/list — `dbt ls` reads the profile but does not connect; `--output json`, `--output-keys`, `--resource-type`
- docs/build/incremental-strategy — strategies per adapter
- docs/build/incremental-microbatch — `event_time`, `begin`, `batch_size`, `lookback`, `concurrent_batches`, event-time flags, retry (1.9+)
- docs/build/unit-tests — YAML keys, formats, warehouse needed, `test_type:unit`, `--exclude-resource-type` (1.8+)
- docs/build/snapshots — YAML snapshots, `hard_deletes`, `dbt_valid_to_current`, pitfalls (1.9+)
- reference/resource-properties/data-tests — `arguments` (1.10.5+), `config`
- reference/resource-properties/constraints — contracts, constraint enforcement per adapter; Databricks checks names and order, not types
- reference/resource-configs/snowflake-configs — transient default, `query_tag`, `snowflake_warehouse`, `cluster_by`, `copy_grants`, dynamic tables, incremental strategies, `tmp_relation_type`
- reference/resource-configs/databricks-configs — `liquid_clustered_by`, `auto_liquid_cluster`, `partition_by`, `databricks_compute`, strategies, merge options, `query_tags` (1.11+), `skip_optimize`
- reference/node-selection/methods — selector methods, `state:` sub-selectors, `selector:` method (1.12+)
- reference/node-selection/defer — `--defer`, `--state`, `--defer-state`, `--favor-state`
- reference/project-configs/query-comment — default comment keys (`app`, `dbt_version`, `profile_name`, `target_name`, `node_id`; no `invocation_id`), appended on Snowflake
- reference/artifacts/manifest-json — top-level keys, schema v12
- reference/artifacts/run-results-json — result fields, timing, which commands write it
- docs/fusion/supported-features — adapters, `dbt lint`, upgrade requirements

## Snowflake (docs.snowflake.com)
- sql-reference/account-usage/query_attribution_history — columns, 8 h latency, exclusions, data from mid-Aug 2024
- sql-reference/account-usage/query_history — columns, 45 min latency, 365 days
- sql-reference/account-usage/access_history — base/direct objects, `columns[].columnName`, 3 h latency, Enterprise edition
- sql-reference/account-usage/object_dependencies — columns, 3 h latency (retention not stated)

## Databricks (docs.databricks.com)
- aws/en/admin/system-tables/query-history — columns, coverage, ~1 h latency
- aws/en/admin/system-tables/lineage — table and column lineage columns, 395-day rolling retention (latency not stated)
- aws/en/views/materialized — created from a SQL warehouse, refreshed by a serverless pipeline

## Open `check:` items (in the references)
- dbt: freshness config placement; metadata-based freshness; data-test config keys page; grants `+` append; model versions alias view; project dependencies; MetricFlow commands; clone per adapter; platform CI deferral; Fusion naming and compile behaviour; `print()` in Fusion; `DBT_STATE` vs `DBT_ENGINE_STATE`.
- Snowflake: QUERY_ATTRIBUTION_HISTORY one row per query (not stated; guard in S1); OBJECT_DEPENDENCIES retention; WAREHOUSE_METERING_HISTORY and AUTOMATIC_CLUSTERING_HISTORY latency; TABLE_STORAGE_METRICS latency; ORGANIZATION_USAGE rate views and latency; dbt projects on Snowflake.
- Databricks: query.history retention; `statement_type` values (MERGE, OPTIMIZE); billing.usage latency and retention; table_lineage / column_lineage latency and `entity_type` values; materialized view compute requirements; tune file size properties; dbt task in Jobs.
- Python connectors in the template: `private_key_file` parameter of the Snowflake connector, native `:name` parameters of the Databricks SQL connector (check: docs.snowflake.com/en/developer-guide/python-connector, docs.databricks.com/aws/en/dev-tools/python-sql-connector).
