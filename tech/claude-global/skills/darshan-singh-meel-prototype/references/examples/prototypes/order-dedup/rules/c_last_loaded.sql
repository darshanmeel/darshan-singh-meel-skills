-- C: the row loaded last wins
SELECT *
FROM raw_orders
QUALIFY row_number() OVER (PARTITION BY order_id ORDER BY load_seq DESC) = 1
ORDER BY order_id
