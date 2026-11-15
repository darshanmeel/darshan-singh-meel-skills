-- what: <one line: what this query answers>
-- reads: <view> (<col_a>, <col_b>), <view_b> (<key>)
-- joins: <view>.<key> = <view_b>.<key> (1:1 | 1:n, aggregated first)
-- grain: one row = <one dbt node>
-- look for: <good value> vs <bad value>; empty = not assessed, not zero
-- latency: <view> up to <45 min>; retention <365 days>; window ends at :as_of
-- params: :days (window), :as_of (fixed timestamp, set once per topic)
select date_trunc('day', start_time) as day,
       count(*) as dbt_queries
from snowflake.account_usage.query_history
where start_time >= dateadd(day, -:days, :as_of)
  and start_time < :as_of
  and (query_tag ilike '%dbt%' or query_text ilike '%"app":%"dbt"%')
group by 1
order by 1;
