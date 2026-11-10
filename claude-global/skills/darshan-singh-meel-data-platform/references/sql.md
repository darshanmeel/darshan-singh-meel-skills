# SQL (any engine)

## Correctness
- State the grain of every table and CTE when not obvious ("one row per order_id per day").
- Check every join for fan-out. Aggregate or dedupe *before* joining.
- Never use `DISTINCT` to hide duplicates from a bad join — fix the join.
- NULL traps: `NOT IN` with a nullable subquery (use `NOT EXISTS`); `=` never matches NULL; `COUNT(col)` skips NULLs.
- `LEFT JOIN` + `WHERE` filter on the right table = inner join. Put the filter in `ON`.
- `UNION ALL` unless dedup is intended.
- Be explicit with integer division, decimal precision, and timezones.
- Dedupe with `QUALIFY ROW_NUMBER() OVER (PARTITION BY key ORDER BY updated_at DESC, <tiebreaker>) = 1`.

## Minimal & readable
- Explicit column lists; `SELECT *` only as a pass-through from the CTE above.
- CTEs named for their content (`orders_deduped`), one step each, top to bottom.
- No subqueries nested 3 deep — flatten into CTEs.
- No redundant casts, no `ORDER BY` in intermediate steps, no unused columns carried along.
- Match the project's keyword case and comma style.

## Performance
- Filter and select columns early.
- No functions on filter/join columns (`WHERE DATE(ts) = …`); use ranges so pruning works.
- Avoid cross / non-equi joins on large tables unless required.
- Prefer `GROUP BY key` over `DISTINCT` / `COUNT(DISTINCT)` on huge tables when equivalent.
- Partition window functions on the narrowest correct key.

## Security
- Never build SQL from external input with string formatting — bind parameters or framework quoting.
