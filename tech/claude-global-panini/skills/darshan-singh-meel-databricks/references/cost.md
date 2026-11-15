# Cost and DBUs

## Rules
- **DBU is not money.** Dollars = `usage_quantity × pricing.effective_list.default` (the list price after promotions; the price the docs say is used to calculate cost). `pricing.default` is the pre-promotion rate: never mix the two.
- **List, not invoice:** no system table holds negotiated or committed rates. Label every dollar "list-price estimate"; a discount is a separate what-if column (`× (1 - :discount)`), never a change to the stored figure.
- **Corrections:** `record_type` ORIGINAL, RETRACTION (negative quantity), RESTATEMENT. Sum all of them and drop groups that net to 0; never filter to ORIGINAL for totals. Count billed hours on ORIGINAL rows only.
- **Unpriced ≠ $0:** keep `unpriced_quantity` when the price join misses, grouped by `usage_unit` wherever it is shown (quantities of different units never add up); `*_FREE_USAGE`-style SKUs have no price by design (price_basis `free`).
- **Latency:** billing lands within ~12 h; the trailing day is provisional → end windows at `current_date()` (exclusive) unless asked.
- **Units:** `usage_unit` is not always DBU (`usage_type` COMPUTE_TIME, STORAGE_SPACE, NETWORK_BYTE, NETWORK_HOUR, API_OPERATION, TOKEN, GPU_TIME, ANSWER); price each by its own unit, sum dollars, never quantities, across units.
- **Account-level rows:** `workspace_id` NULL → account-level usage; keep them as their own group.
- **Out of scope:** the cloud provider's VM, storage and egress bill (check: `system.billing.cloud_infra_cost` availability on your cloud).

## Base CTE (reuse in every priced query)
```sql
WITH priced AS (
  SELECT u.record_id, u.workspace_id, u.usage_date, u.usage_start_time, u.sku_name, u.usage_unit, u.billing_origin_product,
         u.usage_metadata, u.custom_tags, u.product_features, u.identity_metadata, u.record_type,
         u.usage_quantity,
         u.usage_quantity * CAST(p.pricing.effective_list.default AS DOUBLE) AS usd_list,
         CASE WHEN p.sku_name IS NULL THEN u.usage_quantity END              AS unpriced_quantity
  FROM system.billing.usage u
  LEFT JOIN system.billing.list_prices p
    ON  p.sku_name = u.sku_name AND p.cloud = u.cloud AND p.usage_unit = u.usage_unit
    AND p.currency_code = 'USD'
    AND u.usage_end_time >= p.price_start_time
    AND (p.price_end_time IS NULL OR u.usage_end_time < p.price_end_time)
  WHERE u.usage_date >= date_sub(current_date(), :days) AND u.usage_date < current_date()
)
```
- Check once that the join does not fan out: `SELECT COUNT(*)` of `priced` = `COUNT(*)` of usage in the same window. Overlapping price rows → cap each `price_end_time` at the next row's `price_start_time`.

## Questions
### C1 How much did we spend per day and product?
```sql
-- priced CTE
SELECT usage_date, billing_origin_product, usage_unit, ROUND(SUM(usd_list), 2) AS usd_list, SUM(unpriced_quantity) AS unpriced_qty
FROM priced GROUP BY ALL HAVING SUM(usage_quantity) <> 0 ORDER BY usage_date, usd_list DESC;
```
- Read: one row = UTC day × product × unit. A non-zero `unpriced_qty` → the dollar total is a floor.

### C2 Why did cost jump? (start here)
```sql
-- priced CTE with :days = 2 × :window
SELECT workspace_id, billing_origin_product, sku_name,
       SUM(CASE WHEN usage_date >= date_sub(current_date(), :window) THEN usd_list END) AS usd_now,
       SUM(CASE WHEN usage_date <  date_sub(current_date(), :window) THEN usd_list END) AS usd_before,
       SUM(CASE WHEN usage_date >= date_sub(current_date(), :window) THEN usd_list ELSE 0 END)
     - SUM(CASE WHEN usage_date <  date_sub(current_date(), :window) THEN usd_list ELSE 0 END) AS delta_usd
FROM priced GROUP BY workspace_id, billing_origin_product, sku_name ORDER BY delta_usd DESC LIMIT 50;
```
- Read: biggest `delta_usd` first; `usd_before` NULL = new SKU or product. Then drill the top row to its resource with C3–C6 (job, warehouse, cluster, endpoint, notebook) by `usage_metadata`.
- Pitfalls: compare equal-length windows; check billing history reaches back 2 × window (`MIN(usage_date)`); a restatement in the window shifts both periods.

**Who caused it** (next query after the top row): delta per resource and identity, each usage row in exactly one resource kind.
```sql
-- priced CTE with :days = 2 × :window
, k AS (
  SELECT workspace_id, usage_date, usd_list, identity_metadata,
         CASE WHEN usage_metadata.job_id IS NOT NULL THEN 'job'
              WHEN usage_metadata.dlt_pipeline_id IS NOT NULL THEN 'pipeline'
              WHEN usage_metadata.warehouse_id IS NOT NULL THEN 'warehouse'
              WHEN usage_metadata.endpoint_id IS NOT NULL THEN 'endpoint'
              WHEN usage_metadata.app_id IS NOT NULL THEN 'app'
              WHEN usage_metadata.cluster_id IS NOT NULL THEN 'cluster'
              WHEN usage_metadata.notebook_id IS NOT NULL THEN 'notebook'
              ELSE 'other' END AS kind,
         COALESCE(usage_metadata.job_id, usage_metadata.dlt_pipeline_id, usage_metadata.warehouse_id, usage_metadata.endpoint_id,
                  usage_metadata.app_id, usage_metadata.cluster_id, usage_metadata.notebook_id) AS resource_id
  FROM priced)
SELECT workspace_id, kind, resource_id,
       sha2(concat(:k, COALESCE(identity_metadata.run_as, identity_metadata.owned_by, '(none)')), 256) AS identity_key,
       SUM(CASE WHEN usage_date >= date_sub(current_date(), :window) THEN usd_list ELSE 0 END)
     - SUM(CASE WHEN usage_date <  date_sub(current_date(), :window) THEN usd_list ELSE 0 END) AS delta_usd
FROM k GROUP BY ALL ORDER BY delta_usd DESC LIMIT 50;
```
- Read: `identity_key` = keyed hash of `run_as` (serverless, jobs) or `owned_by` (`k=PII_KEY`); a warehouse shared by many people shows one key here → per-user split with C10. A job on an all-purpose cluster lands under `job` only when the bill carries its `job_id`.

### C3 Top jobs by cost (with names)
```sql
-- priced CTE
, jobs AS (SELECT workspace_id, job_id, name FROM system.lakeflow.jobs
           QUALIFY ROW_NUMBER() OVER (PARTITION BY workspace_id, job_id ORDER BY change_time DESC) = 1)
SELECT p.workspace_id, p.usage_metadata.job_id AS job_id, j.name, ROUND(SUM(p.usd_list), 2) AS usd_list,
       COUNT(DISTINCT p.usage_metadata.job_run_id) AS runs
FROM priced p LEFT JOIN jobs j ON j.workspace_id = p.workspace_id AND j.job_id = p.usage_metadata.job_id
WHERE p.usage_metadata.job_id IS NOT NULL GROUP BY ALL ORDER BY usd_list DESC LIMIT 50;
```
- Read: `name` NULL → one-time submit run (no `jobs` row). Serverless job usage is included (filter `product_features.is_serverless` to split).
- Pitfall: jobs on all-purpose clusters have no `job_id` on the bill; their cost sits on the cluster.

### C4 Cost per job run (which runs were expensive)
- Same as C3 grouped by `job_id, usage_metadata.job_run_id`; join `job_run_timeline` on `workspace_id, job_id, run_id = job_run_id` (final slice: `result_state IS NOT NULL`) for start time and outcome.
- Pitfall: rows with `job_id` but no `job_run_id` (older data) drop out; totals can be below C3.

### C5 Cost by SQL warehouse
```sql
-- priced CTE
, wh AS (SELECT workspace_id, warehouse_id, warehouse_name, warehouse_type, warehouse_size FROM system.compute.warehouses
         QUALIFY ROW_NUMBER() OVER (PARTITION BY workspace_id, warehouse_id ORDER BY change_time DESC) = 1)
SELECT p.workspace_id, p.usage_metadata.warehouse_id AS warehouse_id, w.warehouse_name, w.warehouse_type, w.warehouse_size,
       ROUND(SUM(p.usd_list), 2) AS usd_list,
       COUNT(DISTINCT CASE WHEN p.record_type = 'ORIGINAL' THEN date_trunc('HOUR', p.usage_start_time) END) AS billed_hours
FROM priced p LEFT JOIN wh w ON w.workspace_id = p.workspace_id AND w.warehouse_id = p.usage_metadata.warehouse_id
WHERE p.usage_metadata.warehouse_id IS NOT NULL
GROUP BY ALL ORDER BY usd_list DESC LIMIT 50;
```
- Read: `billed_hours` counts distinct hours, never summed durations (base and Photon/serverless rows share an hour). Name NULL → no config row inside the 395-day history.

### C6 Cost by all-purpose cluster and owner (owner at the time of use)
```sql
-- priced CTE
, u AS (SELECT record_id, workspace_id, usage_metadata.cluster_id AS cluster_id, usage_start_time, usd_list
        FROM priced
        WHERE usage_metadata.cluster_id IS NOT NULL AND usage_metadata.job_id IS NULL AND usage_metadata.dlt_pipeline_id IS NULL)
, owned AS (
  SELECT u.workspace_id, u.cluster_id, u.usd_list, c.owned_by
  FROM u LEFT JOIN system.compute.clusters c
    ON c.workspace_id = u.workspace_id AND c.cluster_id = u.cluster_id AND c.change_time <= u.usage_start_time
  QUALIFY ROW_NUMBER() OVER (PARTITION BY u.record_id ORDER BY c.change_time DESC) = 1)
SELECT workspace_id, cluster_id, sha2(concat(:k, owned_by), 256) AS owner_key, ROUND(SUM(usd_list), 2) AS usd_list
FROM owned GROUP BY ALL ORDER BY usd_list DESC LIMIT 50;
```
- Read: as-of join = the config row valid at the usage start, one per usage record (`record_id`), so no fan-out. `owner_key` NULL → cluster not in `compute.clusters` (deleted before 2023-10-23). Driver and worker can be separate records; summed per cluster.

### C7 Cost by tag value, and untagged share
```sql
-- priced CTE
SELECT workspace_id, COALESCE(custom_tags[:tag_key], '(untagged)') AS tag_value, ROUND(SUM(usd_list), 2) AS usd_list
FROM priced GROUP BY ALL ORDER BY usd_list DESC;
```
- Read: `custom_tags` holds compute tags plus serverless usage-policy tags. Map keys are case-sensitive: list variants first with `SELECT DISTINCT explode(map_keys(custom_tags))`.
- Pitfall: exploding all tags and summing double-counts a row with several tags; one key at a time.

### C8 Serverless vs classic, Photon vs not
- `product_features.is_serverless`, `product_features.is_photon` (NULL → not Photon), `product_features.performance_target`; group `priced` by them and by `billing_origin_product`.
- Pitfall: some managed products (model serving, vector search, apps) are Databricks-managed compute but may not set `is_serverless`; also treat SKU names containing `SERVERLESS` as serverless.

### C9 Serverless notebook cost by person
- `billing_origin_product = 'INTERACTIVE'` with `product_features.is_serverless`; group by `sha2(concat(:k, identity_metadata.run_as), 256)` and `sha2(concat(:k, usage_metadata.notebook_path), 256)` (paths hold user names) → keyed hashes only, `k=PII_KEY`.

### C10 Cost per SQL statement or per user on a warehouse
- With attribution: `billing.attributed_usage.active_usage_quantity` per `usage_metadata.dbsql_statement_id`, priced like C1 (check: table present). Idle and start-up time belong to no statement → statements sum below the warehouse bill.
- Without (estimate): split each billed warehouse hour by the statements' `total_task_duration_ms` share in that hour.
```sql
-- priced CTE
, wh AS (SELECT workspace_id, usage_metadata.warehouse_id AS warehouse_id, date_trunc('HOUR', usage_start_time) AS hour_utc,
                SUM(usd_list) AS usd_hour
         FROM priced WHERE usage_metadata.warehouse_id IS NOT NULL GROUP BY 1, 2, 3)
, st AS (SELECT workspace_id, compute.warehouse_id AS warehouse_id, date_trunc('HOUR', start_time) AS hour_utc,
                sha2(concat(:k, executed_by), 256) AS user_key, SUM(total_task_duration_ms) AS task_ms
         FROM system.query.history
         WHERE compute.type = 'WAREHOUSE' AND start_time >= date_sub(current_date(), :days) AND start_time < current_date()
         GROUP BY 1, 2, 3, 4 HAVING SUM(total_task_duration_ms) > 0)
, sh AS (SELECT workspace_id, warehouse_id, hour_utc, user_key, task_ms,
                SUM(task_ms) OVER (PARTITION BY workspace_id, warehouse_id, hour_utc) AS hour_task_ms
         FROM st)
SELECT w.workspace_id, w.warehouse_id, COALESCE(s.user_key, '(no statements: idle or start-up)') AS user_key,
       ROUND(SUM(w.usd_hour * COALESCE(s.task_ms / s.hour_task_ms, 1)), 2) AS usd_list_est
FROM wh w LEFT JOIN sh s ON s.workspace_id = w.workspace_id AND s.warehouse_id = w.warehouse_id AND s.hour_utc = w.hour_utc
GROUP BY ALL ORDER BY usd_list_est DESC LIMIT 100;
```
- Read: list-price estimate. Hours with statements give their whole cost to that hour's users (idle minutes inside the hour included); hours without statements show as the idle row. Rows sum to the warehouse total (C5): check it. A statement spanning hours counts in its start hour.
- Join to `query.history` on `workspace_id, statement_id` for user, source, tags (`query_tags`).

### C11 Monthly actuals and trend
- `date_trunc('MONTH', usage_date)` on `priced`; flag the current month and the first month of history as partial; never scale a partial month.

### C12 Daily spikes
- Per workspace × product: day `usd_list` vs median of the trailing 28 days (`percentile_approx(usd, 0.5)` over a window frame or a self-join); flag ratio ≥ 2 and `usd ≥ :floor`.
- Pitfall: days with no usage have no row → the median ignores zero days.

### C13 Usage and budget policy coverage
- Share of serverless dollars with `usage_metadata.usage_policy_id` NULL (`budget_policy_id` is the deprecated older field; read it only for old rows).

### C14 Which SKUs changed price
```sql
SELECT sku_name, cloud, usage_unit, price_start_time, price_end_time,
       pricing.default AS default_price, pricing.effective_list.default AS effective_list
FROM system.billing.list_prices
WHERE currency_code = 'USD' AND price_start_time >= date_sub(current_date(), :days)
ORDER BY price_start_time DESC;
```

### C15 Reconcile: do the parts add up to the bill?
- Total `priced` dollars for the window vs the sum of each cut (by workspace, by product, by SKU): every cut must equal the total; a cut that does not → filter or fan-out bug. Tag cuts overlap by design; reconcile them as tagged + untagged = total.

### C16 Storage, networking, other units
- `priced` where `usage_unit <> 'DBU'`, grouped by `usage_type, usage_unit, sku_name`; default storage and networking SKUs show here.

### C17 What did predictive optimization cost per table?
- `storage.predictive_optimization_operations_history` `SUM(usage_quantity)` (ESTIMATED_DBU) by `catalog_name, schema_name, table_name`; DBUs only (no SKU in the table). For dollars use the bill: `priced` where `billing_origin_product = 'PREDICTIVE_OPTIMIZATION'`, apportioned by the table's DBU share.
