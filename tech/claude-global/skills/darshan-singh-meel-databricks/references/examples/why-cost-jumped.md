# Example answer: "Why did our Databricks cost jump last week?"

Delivery: on screen. All values synthetic.

**Answer:** list-price spend rose from $8,410 to $12,960 (+$4,550) week over week; $3,900 of it is one workspace's serverless SQL, driven by one warehouse that stopped auto-stopping after its auto-stop was raised from 10 to 120 minutes. Run Q1–Q3 to confirm on the account.

## Queries
Q1 — Is billing complete for both weeks? (one row; billing lands within ~12 h) Look for: `first_day` 14 days back, `latest_day` yesterday.
```sql
SELECT MIN(usage_date) AS first_day, MAX(usage_date) AS latest_day
FROM system.billing.usage
WHERE usage_date >= date_sub(current_date(), 14) AND usage_date < current_date();
```
Q2 — Which workspace, product and SKU moved? (one row = workspace × product × SKU; list USD) Look for: the top `delta_usd` rows; `unpriced_qty` > 0 → that row's dollars are a floor.
```sql
WITH priced AS (
  SELECT u.workspace_id, u.billing_origin_product, u.sku_name, u.usage_date,
         u.usage_quantity * CAST(p.pricing.effective_list.default AS DOUBLE) AS usd_list,
         CASE WHEN p.sku_name IS NULL THEN u.usage_quantity END AS unpriced_quantity
  FROM system.billing.usage u
  LEFT JOIN system.billing.list_prices p   -- LEFT: unpriced usage stays visible as NULL usd_list
    ON p.sku_name = u.sku_name AND p.cloud = u.cloud AND p.usage_unit = u.usage_unit AND p.currency_code = 'USD'
   AND u.usage_end_time >= p.price_start_time
   AND (p.price_end_time IS NULL OR u.usage_end_time < p.price_end_time)
  WHERE u.usage_date >= date_sub(current_date(), 14) AND u.usage_date < current_date())
SELECT workspace_id, billing_origin_product, sku_name,
       ROUND(SUM(CASE WHEN usage_date >= date_sub(current_date(), 7) THEN usd_list END), 2) AS usd_now,
       ROUND(SUM(CASE WHEN usage_date <  date_sub(current_date(), 7) THEN usd_list END), 2) AS usd_before,
       ROUND(COALESCE(SUM(CASE WHEN usage_date >= date_sub(current_date(), 7) THEN usd_list END), 0)
           - COALESCE(SUM(CASE WHEN usage_date <  date_sub(current_date(), 7) THEN usd_list END), 0), 2) AS delta_usd,
       SUM(unpriced_quantity) AS unpriced_qty
FROM priced GROUP BY workspace_id, billing_origin_product, sku_name
ORDER BY delta_usd DESC LIMIT 20;
```
Q3 — Which warehouse, and did its config change? (SCD history, one row per config version) Look for: a new row around the jump day and what changed in it.
```sql
SELECT warehouse_id, warehouse_name, warehouse_size, max_clusters, auto_stop_minutes, change_time
FROM system.compute.warehouses
WHERE workspace_id = :workspace_id AND change_time >= date_sub(current_date(), 30)
ORDER BY warehouse_id, change_time;
```

## How to read
- Q1: `first_day` must be 14 days back and `latest_day` yesterday; otherwise one week is partial and the delta is not a trend.
- Q2 (synthetic result):

| workspace_id | product | sku_name | usd_now | usd_before | delta_usd | unpriced_qty |
|---|---|---|---|---|---|---|
| 1001 | SQL | PREMIUM_SERVERLESS_SQL_COMPUTE_US_EAST | 5,120.00 | 1,220.00 | 3,900.00 | NULL |
| 1002 | JOBS | PREMIUM_JOBS_COMPUTE | 2,310.00 | 1,780.00 | 530.00 | NULL |

- Top row explains 86 % of the jump → drill into its warehouses (cost C5 by `usage_metadata.warehouse_id`).
- Q3 (synthetic): warehouse `wh-a` shows a new row on day −8 with `auto_stop_minutes` 10 → 120. Confirm idle time with compute K7: up 21 h/day vs busy 3 h/day.

## Caveats
- Dollars are list-price estimates (effective list price), not the invoice; contract discounts are not in system tables.
- Retractions and restatements are summed in; a late correction can shift a day after this run.
- Days are UTC.

## Next
- Compute K7 for `wh-a` (idle minutes per day), then propose `auto_stop_minutes = 10` in a changes notebook the owner runs.
