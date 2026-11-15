-- what: <the question this query answers, one line>
-- views: <system.schema.table, ...>
-- joins: <left.key = right.key, ...; latest row for SCD tables>
-- grain: one row = <...>
-- params: :days (window in whole UTC days, today excluded)
-- look for: <good vs bad value; which row to open next>
SELECT usage_date, billing_origin_product, SUM(usage_quantity) AS quantity
FROM system.billing.usage
WHERE usage_date >= date_sub(current_date(), :days) AND usage_date < current_date()
GROUP BY ALL
ORDER BY usage_date, quantity DESC;
