# Prototype: order-dedup
Status: done
Branch: Data
Run: `python prototypes/order-dedup/run.py`

## Question
Which rule leaves exactly one correct row per order when the feed delivers the same row twice, an older change after a newer one, and two changes in the same second?

## Assumptions
- Grain of the target: one row per `order_id`, holding the order's latest state.
- `updated_at` is the source's change time, to the second; `load_seq` rises with arrival order.
- Two changes in the same second: the one that arrived later is the later state.
- Rows are synthetic, written in `run.py`; no warehouse, no file on disk (in-memory DuckDB).

## Files outside prototypes/
none

## Answer
Rule B (`updated_at DESC, load_seq DESC`, first row) is the only one that passes both checks. A returns 6 rows for 4 orders: the duplicate delivery and the same-second pair both survive. C returns 4 rows but ends order 3 on `paid`, the older change that arrived late.

## Keep
- Absorb `rules/b_updated_at_then_load_seq.sql` into the staging model for orders, with a `unique` + `not_null` test on `order_id`.
- Delete the rest of `prototypes/order-dedup/`.
