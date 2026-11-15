# Example review: `analysis/dbt-cost-rise/` (Snowflake, synthetic)

Reviewed: `00_connection.ipynb` (template) and `01_cost_by_model_week.ipynb`, question "why did dbt cost rise last week and who caused it". Four errors in it; the first three only a reader finds, the fourth `check_queries.py` reports.

## Cells under review (excerpt)
```python
# cell 4 — credits per node and week
df1 = q(r"""select d.node_id, sum(iff(d.wk = :last_wk, a.credits_used_compute, 0)) as credits_last_wk ...
left join snowflake.account_usage.query_attribution_history a on a.query_id = d.query_id ...""", ...)
# cell 6 — credits per role
df2 = q(r"""... left join snowflake.account_usage.query_attribution_history a on a.warehouse_name = d.warehouse_name ...""", ...)
# cell 8 — warehouse bill per week
df3 = q(r"""... from snowflake.account_usage.warehouse_metering_history
where start_time >= dateadd(week, -104, date_trunc('week', :as_of)) ...""", ...)
# cell 9 — no markdown cell before it
stmt = "create or replace table analytics.scratch.cost_wk as select * from ..."
q(stmt)
```

## Report (`reviews/dbt-review-2026-11-12-1440.md`)

**Verdict:** Not ready — two queries return wrong numbers, one fails, and one cell writes to the warehouse.

**Scripts:** `check_queries.py analysis/dbt-cost-rise` → 3 ERROR (cell 9: SQL through a variable, no markdown, not read-only).

### Must
1. **Column does not exist in the view** — `01_cost_by_model_week.ipynb` cell 4
   - Why: `credits_used_compute` is a `WAREHOUSE_METERING_HISTORY` column; `QUERY_ATTRIBUTION_HISTORY` has `CREDITS_ATTRIBUTED_COMPUTE` (performance-cost.md view table). The query fails with invalid identifier.
   - Fix: `a.credits_attributed_compute`.
2. **Fan-out: attribution joined on `warehouse_name`** — cell 6
   - Why: each dbt query matches every attributed query on that warehouse; credits per role are multiplied.
   - Fix: `on a.query_id = d.query_id`, after the one-row-per-`query_id` guard (performance-cost.md S1).
3. **Window longer than retention** — cell 8
   - Why: 104 weeks on a 365-day view; older weeks come back empty and read as zero cost.
   - Fix: `dateadd(week, -2, date_trunc('week', :as_of))`.
4. **Write in an analysis notebook** — cell 9
   - Why: `create or replace table` is DDL, passed through a variable and without a markdown cell.
   - Fix: delete the cell; a write goes in a user-run `dbt-cost-rise-changes.ipynb`.

### Should
1. **`invocations` read as runs** — cell 4
   - Why: the default query comment has no `invocation_id`; the column is NULL.
   - Fix: use `run_hours`, or state the JSON query tag it needs.

### Re-derived answers
| Question | Reviewed answer | Re-derived | Match? |
|---|---|---|---|
| Credits per node, last two weeks | `credits_used_compute` | S1/S10: `credits_attributed_compute` on `query_id` | No → Must 1 |
| Credits per role and target | join on `warehouse_name` | S13: join on `query_id` | No → Must 2 |
