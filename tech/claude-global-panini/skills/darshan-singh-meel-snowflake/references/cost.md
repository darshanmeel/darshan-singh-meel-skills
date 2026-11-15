# Cost and credits

Money rules first, then the question catalogue. Every query uses the `p` window CTE (`account-usage-map.md`).

## Money rules
- **Used is not billed.** `CREDITS_USED` in `METERING_HISTORY`, `WAREHOUSE_METERING_HISTORY` and `QUERY_HISTORY.CREDITS_USED_CLOUD_SERVICES` is before the cloud services adjustment. Billed = `METERING_DAILY_HISTORY.CREDITS_BILLED` = compute + cloud services + `CREDITS_ADJUSTMENT_CLOUD_SERVICES` (negative).
- **Cloud services 10%:** each day, cloud services up to 10% of that day's warehouse compute are free. Hourly or per-warehouse figures: price compute in full and cloud services times the day's billed share (C4). Example: compute 100, cloud services 15 → adjustment -10, billed 105.
- **Totals by service:** sum `CREDITS_BILLED` from `METERING_DAILY_HISTORY` by `SERVICE_TYPE`. Per-feature views (clustering, MVs, search optimization, serverless tasks, pipes, Cortex) only split those totals; never add them to it.
- **Attribution is not a total.** `QUERY_ATTRIBUTION_HISTORY` leaves out idle time, queries of about 100 ms or less, adaptive warehouses, cloud services, serverless and AI tokens; lags 8 h; complete from mid-Aug 2024. Its sum < warehouse compute; the gap is idle.
- **Currency** comes only from OU: `USAGE_IN_CURRENCY_DAILY` (actual amounts, 72 h lag, can change until month end) and `RATE_SHEET_DAILY` (`EFFECTIVE_RATE`). Classify by `SERVICE_TYPE`, `RATING_TYPE`, `BILLING_TYPE`, `IS_ADJUSTMENT`; `USAGE_TYPE` is legacy. Stored values are upper case: compare with `LOWER(...)`.
- **No OU access** → one list price given by the user, every $ labelled "estimate at $X/credit", or credits only. Never invent a price; an unknown price is NULL, never 0.
- **One price, joined once:** reduce a rate table to one row per key (account, service type, date) before joining, or paste the price as a literal in `p`. A rate join that repeats rows multiplies spend.
- **AI credits** can have their own rate (`RATING_TYPE = 'AI_COMPUTE'`). Live accounts have billed AI under service types other than `AI_SERVICES` (seen: `AI_INFERENCE`): group AI service types by pattern, and take the larger per day if two names cover one day. check: metering_daily_history (service type list).
- **Storage** is currency per TB-month on the daily average bytes; transfer is currency per TB by route. Neither is in credits in AU.
- **Zero days count:** a day with no rows is a 0 day in averages, medians and spike baselines (spine pattern in `account-usage-map.md`).
- **Kinds stay apart:** spend, change, waste, saving and balance are separate columns; never sum change with spend, or waste with spend.
- **dbt cost:** dbt-snowflake sets `QUERY_TAG` when the model config has `query_tag`; without it, models are found by the comment dbt adds to the query text, which these queries never read. check: docs.getdbt.com snowflake-configs (query_tag).

## Catalogue

### C1. Billed credits per day and service
```sql
WITH p AS (SELECT 30 AS days, CURRENT_DATE() AS end_date)
SELECT usage_date, service_type,
       SUM(credits_used_compute) AS compute_credits,
       SUM(credits_used_cloud_services) AS cs_used_credits,
       SUM(credits_adjustment_cloud_services) AS cs_adjustment,
       SUM(credits_billed) AS billed_credits
FROM SNOWFLAKE.ACCOUNT_USAGE.METERING_DAILY_HISTORY, p
WHERE usage_date >= DATEADD(day, -p.days, p.end_date) AND usage_date < p.end_date
GROUP BY usage_date, service_type
ORDER BY usage_date, billed_credits DESC;
```
- Read: one row = day x service; `billed_credits` is what the invoice counts. The last day can be partial (3 h latency; cloud services 6 h).
- Pitfall: hourly views summed for the same window come out higher by the cloud services adjustment.

### C2. Why did cost jump? (service level first)
```sql
WITH p AS (SELECT 7 AS days, CURRENT_DATE() AS end_date),
d AS (
  SELECT service_type,
         SUM(IFF(usage_date >= DATEADD(day, -p.days, p.end_date), credits_billed, 0)) AS cur_credits,
         SUM(IFF(usage_date <  DATEADD(day, -p.days, p.end_date), credits_billed, 0)) AS prev_credits
  FROM SNOWFLAKE.ACCOUNT_USAGE.METERING_DAILY_HISTORY, p
  WHERE usage_date >= DATEADD(day, -2 * p.days, p.end_date) AND usage_date < p.end_date
  GROUP BY service_type
)
SELECT service_type, prev_credits, cur_credits, cur_credits - prev_credits AS change_credits,
       ROUND(100 * (cur_credits - prev_credits) / NULLIF(prev_credits, 0), 1) AS change_pct
FROM d
ORDER BY ABS(cur_credits - prev_credits) DESC;
```
- Read: the top row is the service that moved. `change_pct` NULL = new service in this window.
- Next: warehouse → C2b; a serverless service → C9; `AI_*` → C12; storage → `storage.md` S1.
- Pitfall: equal-length windows; a window that ends today is partial; month boundaries shift contract rates, not credits.

### C2b. Which warehouse or entity moved
```sql
WITH p AS (SELECT 7 AS days, CURRENT_DATE() AS end_date)
SELECT service_type, entity_id, MAX(name) AS name,
       SUM(IFF(start_time >= DATEADD(day, -p.days, p.end_date), credits_used, 0)) AS cur_credits_used,
       SUM(IFF(start_time <  DATEADD(day, -p.days, p.end_date), credits_used, 0)) AS prev_credits_used
FROM SNOWFLAKE.ACCOUNT_USAGE.METERING_HISTORY, p
WHERE start_time >= DATEADD(day, -2 * p.days, p.end_date) AND start_time < p.end_date
GROUP BY service_type, entity_id
ORDER BY ABS(cur_credits_used - prev_credits_used) DESC
LIMIT 50;
```
- Read: used credits (before adjustment) per entity; good for ranking, not for the bill.
- Next for a warehouse: C2c (query shapes) and `warehouses.md` W3 (idle).

### C2c. New or grown query shapes on one warehouse
```sql
WITH p AS (SELECT 7 AS days, CURRENT_DATE() AS end_date, 'WH_NAME' AS wh),
a AS (
  SELECT query_parameterized_hash AS shape,
         SUM(IFF(start_time >= DATEADD(day, -p.days, p.end_date), credits_attributed_compute, 0)) AS cur_credits,
         SUM(IFF(start_time <  DATEADD(day, -p.days, p.end_date), credits_attributed_compute, 0)) AS prev_credits,
         COUNT(DISTINCT IFF(start_time >= DATEADD(day, -p.days, p.end_date), query_id, NULL)) AS cur_queries,
         MAX_BY(query_id, credits_attributed_compute) AS costliest_query_id,
         MAX(user_name) AS a_user
  FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_ATTRIBUTION_HISTORY, p
  WHERE warehouse_name = p.wh
    AND start_time >= DATEADD(day, -2 * p.days, p.end_date) AND start_time < p.end_date
  GROUP BY 1
)
SELECT shape, prev_credits, cur_credits, cur_credits - prev_credits AS change_credits, cur_queries,
       costliest_query_id, a_user
FROM a
ORDER BY change_credits DESC
LIMIT 20;
```
- Read: `prev_credits = 0` → a new workload; same shape with more queries → a schedule or caller changed; fewer queries but more credits → data growth or a plan change (`performance.md` P1).
- Pitfall: excludes idle time; a jump that does not show here is idle or a size change (`warehouses.md` W3, W6).

### C3. Daily spike against a median baseline
```sql
WITH p AS (SELECT 60 AS days, CURRENT_DATE() AS end_date),
days AS (SELECT DATEADD(day, -ROW_NUMBER() OVER (ORDER BY SEQ4()), p.end_date) AS d
         FROM TABLE(GENERATOR(ROWCOUNT => 60)), p),
c AS (SELECT usage_date, SUM(credits_billed) AS credits
      FROM SNOWFLAKE.ACCOUNT_USAGE.METERING_DAILY_HISTORY, p
      WHERE usage_date >= DATEADD(day, -p.days, p.end_date) AND usage_date < p.end_date
      GROUP BY usage_date),
s AS (SELECT days.d, COALESCE(c.credits, 0) AS credits FROM days LEFT JOIN c ON c.usage_date = days.d)
SELECT d, credits, MEDIAN(credits) OVER () AS median_day,
       ROUND(credits / NULLIF(MEDIAN(credits) OVER (), 0), 2) AS x_median
FROM s
ORDER BY x_median DESC NULLS LAST
LIMIT 15;
```
- Read: `x_median` above about 2 marks a spike day; run C2 with that day as the current window.
- Pitfall: keep `ROWCOUNT` = `days`; `ANOMALIES_DAILY` is a second opinion only (docs do not say if it is used or billed credits).

### C4. Billed credits per warehouse (cloud services adjusted)
```sql
WITH p AS (SELECT 30 AS days, CURRENT_DATE() AS end_date),
r AS (
  SELECT usage_date,
         GREATEST(SUM(credits_used_cloud_services + credits_adjustment_cloud_services), 0)
           / NULLIF(SUM(credits_used_cloud_services), 0) AS billed_ratio
  FROM SNOWFLAKE.ACCOUNT_USAGE.METERING_DAILY_HISTORY, p
  WHERE service_type = 'WAREHOUSE_METERING'
    AND usage_date >= DATEADD(day, -p.days, p.end_date) AND usage_date < p.end_date
  GROUP BY usage_date
)
SELECT w.warehouse_id, MAX(w.warehouse_name) AS warehouse_name,
       SUM(w.credits_used_compute) AS compute_credits,
       SUM(w.credits_used_cloud_services * COALESCE(r.billed_ratio, 1)) AS cs_billed_credits,
       SUM(w.credits_used_compute + w.credits_used_cloud_services * COALESCE(r.billed_ratio, 1)) AS billed_credits
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY w
JOIN p ON w.start_time >= DATEADD(day, -p.days, p.end_date) AND w.start_time < p.end_date
LEFT JOIN r ON r.usage_date = CAST(CONVERT_TIMEZONE('UTC', w.start_time) AS DATE)
GROUP BY w.warehouse_id
ORDER BY billed_credits DESC;
```
- Read: `billed_credits` summed over warehouses ≈ C1's `WAREHOUSE_METERING` billed credits. `START_TIME` is `TIMESTAMP_LTZ`: convert it to UTC before matching `USAGE_DATE` (UTC days), whatever the session time zone.
- Pitfall: a day without a daily row reads ratio 1 (full cloud services billed), never 0.

### C5. Cloud services: billed amount and drivers
```sql
WITH p AS (SELECT 30 AS days, CURRENT_DATE() AS end_date)
SELECT query_type, warehouse_name IS NULL AS no_warehouse,
       COUNT(*) AS queries, SUM(credits_used_cloud_services) AS cs_used_credits,
       SUM(compilation_time) / 1000 / 3600 AS compile_hours
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY, p
WHERE start_time >= DATEADD(day, -p.days, p.end_date) AND start_time < p.end_date
GROUP BY 1, 2
ORDER BY cs_used_credits DESC
LIMIT 30;
```
- Read: billed cloud services per day = C1 `cs_used_credits + cs_adjustment` (warehouse service). Drivers: many tiny queries, `SHOW`/metadata calls, heavy compilation, frequent DDL or `COPY` listing many files.
- Pitfall: per-query cloud services are before adjustment; most days bill nothing if they stay under 10%.

### C6. Cost per user, role or query tag
```sql
WITH p AS (SELECT 30 AS days, CURRENT_DATE() AS end_date),
a AS (
  SELECT query_id, SUM(credits_attributed_compute) AS credits,
         SUM(COALESCE(credits_used_query_acceleration, 0)) AS qas_credits,
         MAX(user_name) AS user_name, MAX(query_tag) AS query_tag
  FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_ATTRIBUTION_HISTORY, p
  WHERE start_time >= DATEADD(day, -p.days, p.end_date) AND start_time < p.end_date
  GROUP BY query_id
),
q AS (
  SELECT query_id, role_name
  FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY, p
  WHERE start_time >= DATEADD(day, -p.days - 1, p.end_date) AND start_time < p.end_date
)
SELECT a.user_name, COALESCE(q.role_name, '(no query history row)') AS role_name,
       NULLIF(a.query_tag, '') AS query_tag,
       COUNT(*) AS queries, SUM(a.credits) AS compute_credits, SUM(a.qas_credits) AS qas_credits
FROM a LEFT JOIN q ON q.query_id = a.query_id
GROUP BY 1, 2, 3
ORDER BY compute_credits DESC
LIMIT 100;
```
- Read: attributed compute only; add the warehouse's idle share (C7) if the question is "full cost per team".
- Pitfall: aggregate per `QUERY_ID` before the join; a stored procedure's work sits on child queries (group by `COALESCE(ROOT_QUERY_ID, QUERY_ID)` to roll it up; `ROOT_QUERY_ID` is NULL for a query without a parent). Users are personal data: aggregate when results go to the model.

### C6b. Who caused the rise: attributed credits per warehouse and user, this window vs the previous
```sql
WITH p AS (SELECT 7 AS days, DATE_TRUNC(week, CURRENT_DATE()) AS end_date)
SELECT warehouse_id, MAX(warehouse_name) AS warehouse_name, user_name,
       SUM(IFF(start_time <  DATEADD(day, -p.days, p.end_date), credits_attributed_compute, 0)) AS prev_credits,
       SUM(IFF(start_time >= DATEADD(day, -p.days, p.end_date), credits_attributed_compute, 0)) AS cur_credits,
       cur_credits - prev_credits AS change_credits,
       COUNT(DISTINCT IFF(start_time >= DATEADD(day, -p.days, p.end_date), query_id, NULL)) AS cur_queries,
       COUNT(DISTINCT IFF(start_time >= DATEADD(day, -p.days, p.end_date), query_parameterized_hash, NULL)) AS cur_shapes
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_ATTRIBUTION_HISTORY, p
WHERE start_time >= DATEADD(day, -2 * p.days, p.end_date) AND start_time < p.end_date
GROUP BY warehouse_id, user_name
ORDER BY change_credits DESC
LIMIT 50;
```
- Read: the rows with the largest `change_credits` are who caused the rise; `prev_credits = 0` = new on that warehouse. Then C2c on that warehouse for the shapes. `end_date` = this Monday: two complete weeks.
- Pitfall: attributed compute leaves out idle time (C7), so the rows sum to less than C2b's change. Users are personal data: aggregate or keep local.

### C7. Idle credits per warehouse
```sql
WITH p AS (SELECT 30 AS days, CURRENT_DATE() AS end_date)
SELECT warehouse_id, MAX(warehouse_name) AS warehouse_name,
       SUM(credits_used_compute) AS compute_credits,
       SUM(credits_attributed_compute_queries) AS attributed_credits,
       SUM(credits_used_compute) - SUM(credits_attributed_compute_queries) AS idle_credits,
       ROUND(100 * (1 - SUM(credits_attributed_compute_queries) / NULLIF(SUM(credits_used_compute), 0)), 1) AS idle_pct
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY, p
WHERE start_time >= DATEADD(day, -p.days, p.end_date) AND start_time < p.end_date
  AND start_time < DATEADD(hour, -8, CURRENT_TIMESTAMP())        -- attribution lag
  AND credits_attributed_compute_queries IS NOT NULL             -- NULL on adaptive warehouses
GROUP BY warehouse_id
ORDER BY idle_credits DESC;
```
- Read: `idle_pct` above about 40% on a busy warehouse → auto-suspend too long or many short gaps (`warehouses.md` W3).
- Pitfall: an adaptive warehouse drops out (NULL): report it as "not assessed", never as 0 idle.

### C8. Costliest query shapes
```sql
WITH p AS (SELECT 30 AS days, CURRENT_DATE() AS end_date)
SELECT query_parameterized_hash AS shape, COUNT(DISTINCT query_id) AS queries,
       SUM(credits_attributed_compute) AS credits,
       SUM(credits_attributed_compute) / NULLIF(COUNT(DISTINCT query_id), 0) AS credits_per_query,
       ARRAY_TO_STRING(ARRAY_SLICE(ARRAY_AGG(DISTINCT warehouse_name), 0, 3), ', ') AS warehouses,
       MAX_BY(query_id, credits_attributed_compute) AS sample_query_id
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_ATTRIBUTION_HISTORY, p
WHERE start_time >= DATEADD(day, -p.days, p.end_date) AND start_time < p.end_date
GROUP BY 1
ORDER BY credits DESC
LIMIT 25;
```
- Read: high `queries` x low `credits_per_query` → schedule or caching fix; low `queries` x high `credits_per_query` → tune the query (`performance.md` with `sample_query_id`).

### C9. Serverless features split
```sql
WITH p AS (SELECT 30 AS days, CURRENT_DATE() AS end_date)
SELECT 'AUTO_CLUSTERING' AS feature, database_name || '.' || schema_name || '.' || table_name AS object,
       SUM(credits_used) AS credits
FROM SNOWFLAKE.ACCOUNT_USAGE.AUTOMATIC_CLUSTERING_HISTORY, p
WHERE start_time >= DATEADD(day, -p.days, p.end_date) AND start_time < p.end_date GROUP BY 1, 2
UNION ALL
SELECT 'MATERIALIZED_VIEW', database_name || '.' || schema_name || '.' || table_name,
       SUM(TRY_TO_DOUBLE(credits_used))
FROM SNOWFLAKE.ACCOUNT_USAGE.MATERIALIZED_VIEW_REFRESH_HISTORY, p
WHERE start_time >= DATEADD(day, -p.days, p.end_date) AND start_time < p.end_date GROUP BY 1, 2
UNION ALL
SELECT 'SERVERLESS_TASK', database_name || '.' || schema_name || '.' || task_name,
       SUM(TRY_TO_DOUBLE(credits_used))
FROM SNOWFLAKE.ACCOUNT_USAGE.SERVERLESS_TASK_HISTORY, p
WHERE start_time >= DATEADD(day, -p.days, p.end_date) AND start_time < p.end_date GROUP BY 1, 2
UNION ALL
SELECT 'PIPE', COALESCE(pipe_name, '(auto-refresh or streaming)'), SUM(credits_used)
FROM SNOWFLAKE.ACCOUNT_USAGE.PIPE_USAGE_HISTORY, p
WHERE start_time >= DATEADD(day, -p.days, p.end_date) AND start_time < p.end_date GROUP BY 1, 2
ORDER BY credits DESC
LIMIT 50;
```
- Read: credits used per object; the service total stays C1. Search optimization: `SEARCH_OPTIMIZATION_HISTORY` grouped by `BASE_TABLE_ID` (Enterprise).
- Pitfall: MV and serverless task credits are VARCHAR; MV `TABLE_NAME` is the MV itself; `PIPE_NAME` NULL = external or directory table auto-refresh, or Snowpipe Streaming.

### C10. Storage cost per month
```sql
WITH p AS (SELECT 90 AS days, CURRENT_DATE() AS end_date, 23.0 AS usd_tb_month)   -- price from the contract
SELECT DATE_TRUNC(month, usage_date) AS month,
       AVG(storage_bytes + stage_bytes + failsafe_bytes + COALESCE(hybrid_table_storage_bytes, 0)) / POWER(1024, 4) AS avg_tb,
       AVG(failsafe_bytes) / POWER(1024, 4) AS avg_failsafe_tb, COUNT(*) AS days_in_month,
       AVG(storage_bytes + stage_bytes + failsafe_bytes + COALESCE(hybrid_table_storage_bytes, 0)) / POWER(1024, 4) * MAX(p.usd_tb_month) AS est_usd
FROM SNOWFLAKE.ACCOUNT_USAGE.STORAGE_USAGE, p
WHERE usage_date >= DATEADD(day, -p.days, p.end_date) AND usage_date < p.end_date
GROUP BY 1 ORDER BY 1;
```
- Read: TB-month = average daily bytes over the month; `days_in_month` shows how many days the average covers. Partial first and last months are averages over the days present, not full months. Archive tiers have their own rate: leave them unpriced.
- Pitfall: `STORAGE_USAGE` does not reconcile with the bill; OU `STORAGE_DAILY_HISTORY` is closest. Per database: `storage.md` S1.

### C11. Data transfer by route
```sql
WITH p AS (SELECT 30 AS days, CURRENT_DATE() AS end_date)
SELECT source_cloud, source_region, target_cloud, target_region, transfer_type,
       SUM(TRY_TO_DOUBLE(TO_VARCHAR(bytes_transferred))) / POWER(1024, 4) AS tb
FROM SNOWFLAKE.ACCOUNT_USAGE.DATA_TRANSFER_HISTORY, p
WHERE start_time >= DATEADD(day, -p.days, p.end_date) AND start_time < p.end_date
GROUP BY 1, 2, 3, 4, 5
ORDER BY tb DESC;
```
- Read: bytes only; same-region transfer is free and has no row. Currency per route: OU `USAGE_IN_CURRENCY_DAILY` with `SERVICE_TYPE = 'DATA_TRANSFER'`. check: usage_in_currency_daily (service type value).

### C12. AI and Cortex spend
```sql
WITH p AS (SELECT 30 AS days, CURRENT_DATE() AS end_date)
SELECT function_name, COALESCE(NULLIF(model_name, ''), '(none)') AS model_name,
       COUNT(DISTINCT query_id) AS queries, SUM(credits) AS credits
FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AI_FUNCTIONS_USAGE_HISTORY, p
WHERE is_completed
  AND start_time >= DATEADD(day, -p.days, p.end_date) AND start_time < p.end_date
GROUP BY 1, 2
ORDER BY credits DESC;
```
- Read: AI function credits only; the reconciled total is C1 for the AI service types. Also: `CORTEX_ANALYST_USAGE_HISTORY`, `CORTEX_SEARCH_DAILY_USAGE_HISTORY`, `CORTEX_DOCUMENT_PROCESSING_USAGE_HISTORY`, `CORTEX_FINE_TUNING_USAGE_HISTORY`, `CORTEX_AGENT_USAGE_HISTORY`.
- Pitfall: filter `IS_COMPLETED` (in-progress rows); data from 2026-01-05; `USER_ID` and `ROLE_NAMES` (ARRAY) from 2026-02-16 (join `USER_ID` to `USERS.USER_ID` for the name); the warehouse that ran the query bills separately.

### C13. Spend in currency per account and service (org)
```sql
WITH p AS (SELECT 30 AS days, DATEADD(day, -3, CURRENT_DATE()) AS end_date)   -- 72 h billing lag
SELECT account_name, service_type, LOWER(rating_type) AS rating_type, LOWER(billing_type) AS billing_type,
       currency, SUM(usage) AS usage_units, SUM(usage_in_currency) AS amount
FROM SNOWFLAKE.ORGANIZATION_USAGE.USAGE_IN_CURRENCY_DAILY, p
WHERE usage_date >= DATEADD(day, -p.days, p.end_date) AND usage_date < p.end_date
GROUP BY 1, 2, 3, 4, 5
ORDER BY amount DESC;
```
- Read: actual invoice currency; `usage_units` mixes credits and TB across rating types, so read it per row only.
- Pitfall: needs `ORGANIZATION_BILLING_VIEWER`; error or no rows → "no org billing access", fall back to credits. Rows with `IS_ADJUSTMENT` are corrections, keep them for totals and leave them out of rates.

### C14. Effective price per credit
```sql
SELECT service_type, LOWER(rating_type) AS rating_type, currency,
       MAX_BY(effective_rate, "DATE") AS latest_rate, MAX("DATE") AS as_of
FROM SNOWFLAKE.ORGANIZATION_USAGE.RATE_SHEET_DAILY
WHERE account_locator = CURRENT_ACCOUNT()
  AND LOWER(billing_type) = 'consumption' AND NOT COALESCE(is_adjustment, FALSE)
GROUP BY 1, 2, 3
ORDER BY 1;
```
- Read: one rate per service type; compute, cloud services, each serverless type and AI can differ. No rate sheet → 90-day `SUM(usage_in_currency) / SUM(usage)` from C13 with `billing_type = 'consumption'`, no adjustments, no `balance_source = 'overage'`.
- Pitfall: `"DATE"` is a reserved word: quote it.

### C15. Contract balance and burn
```sql
SELECT "DATE", currency, capacity_balance, rollover_balance, free_usage_balance,
       on_demand_consumption_balance
FROM SNOWFLAKE.ORGANIZATION_USAGE.REMAINING_BALANCE_DAILY
WHERE "DATE" >= DATEADD(day, -90, CURRENT_DATE())
ORDER BY "DATE" DESC
LIMIT 90;
```
- Read: slope of `capacity_balance` = burn per day; days left = balance / average burn. Negative `on_demand_consumption_balance` = on-demand charges owed.
- Pitfall: funding org only; 72 h lag.

### C16. Resource monitor coverage
```sql
SHOW WAREHOUSES ->> SELECT "name", "size", "resource_monitor", "auto_suspend" FROM $1
                    WHERE "resource_monitor" = 'null' ORDER BY "name";
```
- Read: warehouses with no monitor; quotas in `RESOURCE_MONITORS` (`CREDIT_QUOTA`, `USED_CREDITS` are VARIANT, the account-level monitor has `LEVEL = 'ACCOUNT'`).
- Pitfall: SHOW and `RESOURCE_MONITORS` are role-filtered; `resource_monitor` is the text `'null'` when none.

### C17. Month-end forecast
```sql
WITH p AS (SELECT CURRENT_DATE() AS end_date),
m AS (
  SELECT usage_date, SUM(credits_billed) AS credits
  FROM SNOWFLAKE.ACCOUNT_USAGE.METERING_DAILY_HISTORY, p
  WHERE usage_date >= DATE_TRUNC(month, p.end_date) AND usage_date < p.end_date
  GROUP BY usage_date
)
SELECT SUM(m.credits) AS month_to_date, COUNT(*) AS days_with_rows,
       SUM(m.credits) / NULLIF(DATEDIFF(day, DATE_TRUNC(month, MAX(p.end_date)), MAX(p.end_date)), 0)
         * DAY(LAST_DAY(MAX(p.end_date))) AS forecast_credits
FROM m, p;
```
- Read: run rate x days in month; divide by calendar days so quiet days count. Weekly patterns make it rough; say "estimate".

### C18. Spend by account (org, credits)
```sql
WITH p AS (SELECT 30 AS days, CURRENT_DATE() AS end_date)
SELECT account_name, service_type, SUM(credits_billed) AS billed_credits
FROM SNOWFLAKE.ORGANIZATION_USAGE.METERING_DAILY_HISTORY, p
WHERE usage_date >= DATEADD(day, -p.days, p.end_date) AND usage_date < p.end_date
GROUP BY 1, 2
ORDER BY billed_credits DESC;
```
- Read: credits across accounts with 2 h latency (faster than currency). Needs `ORGANIZATION_USAGE_VIEWER`.

### C19. Chargeback by warehouse tag
```sql
WITH p AS (SELECT 30 AS days, CURRENT_DATE() AS end_date)
SELECT t.tag_name, t.tag_value, SUM(w.credits_used) AS credits_used
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY w
JOIN p ON w.start_time >= DATEADD(day, -p.days, p.end_date) AND w.start_time < p.end_date
JOIN SNOWFLAKE.ACCOUNT_USAGE.TAG_REFERENCES t
  ON t.domain = 'WAREHOUSE' AND t.object_id = w.warehouse_id AND t.object_deleted IS NULL
GROUP BY 1, 2
ORDER BY credits_used DESC;
```
- Read: used credits per tag value; untagged warehouses drop out, so also report the untagged total (LEFT JOIN, `tag_value IS NULL`).
- Pitfall: a warehouse with two tags counts twice across tags: filter one `tag_name` per query. Enterprise; role-filtered.
