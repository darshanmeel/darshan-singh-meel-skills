# Sources

Official pages behind the facts in this skill (read 2026-11). Paths are the AWS docs; Azure and GCP have the same pages under `/azure/` and `/gcp/` and can differ in retention and availability.

| Page | Used for |
|---|---|
| https://docs.databricks.com/aws/en/admin/system-tables/ | table list (incl. the "Also exists" tables), retention, `st_retention` setting, streaming, regional/global, Preview status, enabling and grants, VACUUM 7 days, skipChangeCommits |
| https://docs.databricks.com/aws/en/admin/system-tables/billing | `billing.usage` columns, `billing_origin_product` values (`INTERACTIVE`, `PREDICTIVE_OPTIMIZATION`, `GENIE`, `AI_FUNCTIONS`), `usage_policy_id` (`budget_policy_id` deprecated), `record_type`, `usage_type`, `usage_metadata`, `product_features`, `identity_metadata`, 12 h latency, corrections |
| https://docs.databricks.com/aws/en/admin/system-tables/pricing | `list_prices` columns, `pricing.default` / `promotional` / `effective_list` |
| https://docs.databricks.com/aws/en/admin/usage/system-tables | usage × list price join, tag filter, owner as-of join to clusters, job names from latest `jobs` row |
| https://docs.databricks.com/aws/en/admin/system-tables/query-history | `query.history` columns, compute types, redaction, 1 h latency |
| https://docs.databricks.com/aws/en/admin/system-tables/jobs | lakeflow SCD tables, pipeline `result_state` `COMPLETED` / `FAILED` / `CANCELED`, columns not populated before early Dec 2025, no task queue column, latest-row query, hourly slicing, `result_state`, `run_type`, duration columns, limitations |
| https://docs.databricks.com/aws/en/admin/system-tables/compute | clusters, node types, node timeline, instance events and pools, `cluster_source`, `data_security_mode` |
| https://docs.databricks.com/aws/en/admin/system-tables/warehouses | warehouse columns, type/channel/size values, latest-row query |
| https://docs.databricks.com/aws/en/admin/system-tables/warehouse-events | event types, `cluster_count` |
| https://docs.databricks.com/aws/en/admin/system-tables/lineage | lineage columns, entity and source types, gaps, `direct_access`, retention |
| https://docs.databricks.com/aws/en/admin/system-tables/audit-logs | audit columns, account events `workspace_id = 0`, hidden `request_params` keys |
| https://docs.databricks.com/aws/en/admin/system-tables/predictive-optimization | operation types, statuses, metrics keys, ESTIMATED_DBU, 12 h latency |
| https://docs.databricks.com/aws/en/ai-gateway/configure-ai-gateway-endpoints#usage-tracking-table-schemas | `serving.endpoint_usage` and `served_entities` columns, account-admin only, ≤ 1 h latency, `served_entity_id` join |
| https://docs.databricks.com/aws/en/admin/system-tables/network | inbound and outbound network columns, `policy_outcome` `DENY` / `DENY_DRY_RUN`, ≤ 1 h latency |
| https://docs.databricks.com/aws/en/admin/system-tables/pipeline-events | `pipeline_events` columns, `level`, `error` struct, Beta schema name |
| Table metrics history page (linked from the system tables index) | `table_metrics_history` columns, 13 months |
| Data classification system table page (linked from the system tables index) | `data_classification.results` columns, `samples` (up to five raw values) |
| https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-qry-select-cte | `WITH RECURSIVE` (Databricks SQL, Runtime 17.0+), depth 100, 1,000,000 rows, `MAX RECURSION LEVEL` |
| https://docs.databricks.com/aws/en/sql/language-manual/information-schema/views | `view_definition` NULL unless the caller owns the view |
| https://docs.databricks.com/aws/en/sql/language-manual/information-schema/column_masks and `.../row_filters` | `catalog_name`, `schema_name`, `mask_col_usage`, `filter_col_usage` |
| https://docs.databricks.com/aws/en/error-messages/unsupported-feature-error-class | `LATERAL_COLUMN_ALIAS_IN_GROUP_BY` |
| https://docs.databricks.com/aws/en/dev-tools/python-sql-connector | connector auth, named parameters, `fetchall_arrow()` with the `[pyarrow]` extra (4.x) |

## Not found on official pages (marked `check:` where used)
- `system.billing.attributed_usage` (not in the system tables index; columns from a `DESCRIBE` of the system catalog).
- `system.ai_gateway.usage` and `external_model_spend` columns (names from `DESCRIBE`).
- Latency of audit, lineage, classification, AI gateway, pipeline events and table metrics tables.
- Exact audit action names (`updatePermissions`, login, token), `response.status_code` (the docs example shows `statusCode`), all-users principal name.
- Whether `total_duration_ms` equals waits + compilation + execution; minimum runtime for streaming reads of system tables.
- Spark defaults on Databricks compute (`autoBroadcastJoinThreshold`), file size targets, auto-stop minimums, Apps on-behalf-of-user auth.
