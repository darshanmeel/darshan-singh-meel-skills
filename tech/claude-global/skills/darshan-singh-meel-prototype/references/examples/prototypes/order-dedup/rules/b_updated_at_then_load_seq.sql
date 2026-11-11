-- B: latest updated_at wins; same updated_at -> the row loaded last wins
SELECT *
FROM raw_orders
QUALIFY row_number() OVER (PARTITION BY order_id ORDER BY updated_at DESC, load_seq DESC) = 1
ORDER BY order_id
