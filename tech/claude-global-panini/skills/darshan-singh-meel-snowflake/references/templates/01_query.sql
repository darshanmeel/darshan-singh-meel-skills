-- 01. <Query title>
-- What: <what the query computes, per what grain, over which window>.
-- Reads: <views> (<grain of each>); join on <key>.
-- Look for: <columns that answer the question, units, normal vs bad values, pitfalls>.
WITH p AS (SELECT 30 AS days, CURRENT_DATE() AS end_date)   -- end_date is exclusive
SELECT <columns>
FROM SNOWFLAKE.ACCOUNT_USAGE.<VIEW> v, p
WHERE v.<time_column> >= DATEADD(day, -p.days, p.end_date) AND v.<time_column> < p.end_date
GROUP BY <keys>
ORDER BY <measure> DESC
LIMIT 1000;
