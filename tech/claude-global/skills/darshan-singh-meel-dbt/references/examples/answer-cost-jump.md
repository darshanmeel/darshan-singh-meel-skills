# Example answer: "Why did our dbt cost jump last week?" (Snowflake, synthetic values)

Delivery chosen: Notebook → `analysis/dbt-cost-jump/00_connection.ipynb`, `01_cost_by_model_week.ipynb`.

**Answer:** `fct_sessions` went from 41 to 312 credits per week after it changed from `incremental` to `table` on Monday; the other 180 models moved less than 5%. Restoring the incremental config (with a 3-day lookback) takes dbt back to about 520 credits per week.

## Query 1 — credits per dbt model, last two full weeks
Markdown cell before it:
- **What:** credits per dbt node and week.
- **Reads:** `QUERY_HISTORY` (`query_id`, `query_tag`, `query_text` → `node_id` only, `start_time`) + `QUERY_ATTRIBUTION_HISTORY` (`credits_attributed_compute`).
- **Joins:** `query_id`, one attribution row per query (guard cell before this one: `count(*) = count(distinct query_id)`).
- **Grain:** one row = node × week.
- **Latency:** attribution up to 8 h → `AS_OF` = now − 8 h (UTC, pinned in `ANALYSIS_AS_OF`); retention 365 days. Weeks start per `WEEK_START` (default Monday).
- **Look for:** one node with a large week-over-week rise, or many small rises (warehouse change).

```sql
with q as (
  select query_id, date_trunc('week', start_time) as wk,
         coalesce(try_parse_json(query_tag):node_id::string,
                  try_parse_json(regexp_substr(query_text,
                    '/\\*\\s*(\\{[^*]*"app"\\s*:\\s*"dbt"[^*]*\\})\\s*\\*/', 1, 1, 'e', 1)):node_id::string,
                  '(dbt, no node)') as node_id
  from snowflake.account_usage.query_history
  where start_time >= dateadd(week, -2, date_trunc('week', :as_of)) and start_time < date_trunc('week', :as_of)
    and (query_tag ilike '%dbt%' or query_text ilike '%"app":%"dbt"%')
)
select node_id,
       sum(iff(wk = dateadd(week, -1, date_trunc('week', :as_of)), a.credits_attributed_compute, 0)) as credits_last_wk,
       sum(iff(wk = dateadd(week, -2, date_trunc('week', :as_of)), a.credits_attributed_compute, 0)) as credits_prev_wk,
       credits_last_wk - credits_prev_wk as delta
from q
left join snowflake.account_usage.query_attribution_history a on a.query_id = q.query_id
group by node_id
order by delta desc
limit 20;
```

Result (synthetic):

| node_id | credits_last_wk | credits_prev_wk | delta |
|---|---|---|---|
| model.shop.fct_sessions | 312.4 | 41.0 | 271.4 |
| model.shop.int_events_sessionized | 88.1 | 85.9 | 2.2 |
| test.shop.unique_fct_sessions_session_id | 9.7 | 2.1 | 7.6 |

## How to read it
- `credits` are compute credits per query; warehouse idle time and queries ≤ ~100 ms are not included, so the sum is below the warehouse bill.
- The test on `fct_sessions` rose too: it now scans the full rebuilt table every run.
- `(dbt, no node)` absent → every dbt query carried the node id; a large value there would mean the comment was stripped and the split is incomplete.
- Credits × one price per credit for the window (`RATE_SHEET_DAILY`, list or contract — say which) gives currency; never join the rate per query.

## Confirm in the project (offline)
- `git log -p models/marts/fct_sessions.sql` → `materialized='table'` replaced the incremental config.
- `python <skill>/scripts/dbt_inventory.py target/manifest.json impact fct_sessions` → 6 children, 1 exposure: the change is safe to revert.

## Caveats
- Last 8 hours not included (attribution latency).
- Without IMPORTED PRIVILEGES (or `USAGE_VIEWER`) the views return an error → not assessed, not zero.

In the notebook the SQL sits in `q(r"""…""")` so the regex backslashes stay as written.

**Next query:** S13 (role, target, warehouse) to confirm no other job changed, then S3 (spill and pruning) for `fct_sessions` after the revert, to check the merge prunes on `session_start`.
