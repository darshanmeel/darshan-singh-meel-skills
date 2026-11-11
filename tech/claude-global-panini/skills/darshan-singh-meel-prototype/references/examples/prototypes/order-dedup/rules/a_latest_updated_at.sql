-- A: keep the rows that carry the latest updated_at per order
SELECT o.*
FROM raw_orders o
JOIN (SELECT order_id, max(updated_at) AS updated_at FROM raw_orders GROUP BY order_id) m
  USING (order_id, updated_at)
ORDER BY order_id, load_seq
