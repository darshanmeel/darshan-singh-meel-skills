# Model serving, AI gateway, vector search, Genie

## Rules
- Money comes only from `billing.usage` (cost.md base CTE): serving rows carry `usage_metadata.endpoint_id` / `endpoint_name`, `product_features.serving_type`, `product_features.model_serving.offering_type`; `usage_type` can be TOKEN or GPU_TIME as well as COMPUTE_TIME, and those rows can still be DBU-priced → price by `usage_unit`, never assume.
- `serving.served_entities` = config history (SCD): latest row per `workspace_id, served_entity_id` by `change_time`; roll up to one row per endpoint before joining to billing (an endpoint has many entities over time → fan-out).
- `serving.endpoint_usage` = one row per request (`request_time`, `requester`, `status_code`, token and character counts, `served_entity_id`); filled only when usage tracking is on for the endpoint; no `endpoint_id` column → join via `served_entity_id`. Both serving tables are visible to account admins only.
- Empty `system.serving.*` = not measured (no tracking, no grant), never "no traffic".
- `ai_gateway.usage` (Public Preview, global): per request `endpoint_name`, `destination_model`, `requester`, `requester_type`, `input_tokens`, `output_tokens`, `total_tokens`, `latency_ms`, `status_code`, `request_tags`.
- `requester` (and any IP column) is people's data → `COUNT(DISTINCT)` or `sha2(concat(:k, requester), 256)` with `k=PII_KEY`.

## Questions
### S1 Serving cost per endpoint per day
```sql
-- priced CTE (cost.md)
SELECT usage_date, workspace_id, usage_metadata.endpoint_id AS endpoint_id, usage_metadata.endpoint_name AS endpoint_name,
       product_features.serving_type AS serving_type, usage_type, ROUND(SUM(usd_list), 2) AS usd_list
FROM priced WHERE usage_metadata.endpoint_id IS NOT NULL
GROUP BY ALL ORDER BY usage_date, usd_list DESC;
```
- Read: keep `usage_date` in the grain when comparing with per-day thresholds.

### S2 Current config of served entities
```sql
SELECT workspace_id, endpoint_id, endpoint_name, served_entity_id, served_entity_name, entity_type,
       entity_name, entity_version, task, foundation_model_config, custom_model_config, endpoint_delete_time
FROM system.serving.served_entities
QUALIFY ROW_NUMBER() OVER (PARTITION BY workspace_id, served_entity_id ORDER BY change_time DESC) = 1;
```
- Read: provisioned throughput or minimum concurrency in the config structs → paying while idle; `endpoint_delete_time` set → gone.

### S3 Requests and tokens per endpoint
```sql
WITH se AS (SELECT workspace_id, served_entity_id, endpoint_id, endpoint_name FROM system.serving.served_entities
            QUALIFY ROW_NUMBER() OVER (PARTITION BY workspace_id, served_entity_id ORDER BY change_time DESC) = 1)
SELECT se.workspace_id, se.endpoint_name, date_trunc('DAY', u.request_time) AS day_utc, COUNT(*) AS requests,
       COUNT_IF(u.status_code >= 400) AS errors, SUM(u.input_token_count) AS in_tokens, SUM(u.output_token_count) AS out_tokens
FROM system.serving.endpoint_usage u
JOIN se ON se.workspace_id = u.workspace_id AND se.served_entity_id = u.served_entity_id
WHERE u.request_time >= date_sub(current_date(), :days)
GROUP BY ALL ORDER BY day_utc, requests DESC;
```

### S4 Dormant endpoints (cost, no traffic)
```sql
-- priced CTE (cost.md)
, cost AS (SELECT workspace_id, usage_metadata.endpoint_id AS endpoint_id, MAX(usage_metadata.endpoint_name) AS endpoint_name,
                  ROUND(SUM(usd_list), 2) AS usd_list
           FROM priced WHERE usage_metadata.endpoint_id IS NOT NULL GROUP BY 1, 2)
, se AS (SELECT DISTINCT workspace_id, endpoint_id, served_entity_id FROM system.serving.served_entities)
, req AS (SELECT se.workspace_id, se.endpoint_id, COUNT(*) AS requests
          FROM system.serving.endpoint_usage u
          JOIN se ON se.workspace_id = u.workspace_id AND se.served_entity_id = u.served_entity_id
          WHERE u.request_time >= date_sub(current_date(), :days) GROUP BY 1, 2)
SELECT c.workspace_id, c.endpoint_id, c.endpoint_name, c.usd_list, COALESCE(r.requests, 0) AS requests
FROM cost c LEFT JOIN req r ON r.workspace_id = c.workspace_id AND r.endpoint_id = c.endpoint_id
WHERE r.requests IS NULL
ORDER BY c.usd_list DESC;
```
- Read: `se` holds distinct entity → endpoint pairs, so no fan-out. Zero requests is dormant only where usage tracking is on for that endpoint; otherwise NOT_ASSESSED. Check `endpoint_usage` history reaches back `:days` (`MIN(request_time)`).

### S5 Cost per 1k requests or per million tokens
- S1 dollars ÷ S3 counts per endpoint-day; compare pay-per-token vs provisioned endpoints at their real volume.

### S6 AI gateway usage by model and requester
```sql
SELECT endpoint_name, destination_model, requester_type, date_trunc('DAY', event_time) AS day_utc,
       COUNT(*) AS requests, SUM(total_tokens) AS tokens,
       percentile_approx(latency_ms, 0.95) AS p95_latency_ms, COUNT_IF(status_code >= 400) AS errors
FROM system.ai_gateway.usage
WHERE event_time >= date_sub(current_date(), :days)
GROUP BY ALL ORDER BY tokens DESC LIMIT 200;
```
- Read: top requesters (masked) and models; cache reads in `token_details` lower cost (check: field names on the gateway reference).

### S7 Rate-limit and error hot spots
- S6 `status_code = 429` grouped by endpoint and hour → raise limits or spread load; 5xx → provider or model issue.

### S8 Vector search spend
- `priced` where `billing_origin_product = 'VECTOR_SEARCH'` by `usage_metadata.endpoint_name` and day; traffic via `access.audit` vector search events (key on `request_params['index_name']`; `endpoint_name` is often absent).

### S9 Genie and AI functions spend
- `priced` where `billing_origin_product IN ('GENIE', 'AI_FUNCTIONS')` (billing page; list `SELECT DISTINCT billing_origin_product` first for newer values; check: Genie cost page for the `usage_metadata` fields); SKUs containing `FREE` are free tier at $0.

### S10 Serving GPU hours
- `priced` where `usage_type = 'GPU_TIME'` (and `product_features.serverless_gpu.workload_type`) per endpoint; idle GPU endpoints are the largest serving waste.

### S11 Apps cost
- `priced` with `usage_metadata.app_id` / `app_name` and `product_features.apps.compute_size`; an app runs (and bills) while started, not only when used.
