"""Prototype: which dedup rule leaves one correct row per order? Run: python prototypes/order-dedup/run.py
Shell only: synthetic rows in, every rule in rules/ run on in-memory DuckDB, full result printed."""
import pathlib

import duckdb

# synthetic feed rows: order_id, status, amount, updated_at, load_seq (order of arrival)
ROWS = [
    (1, "new", 40.00, "2026-03-01 09:00:00", 1),        # delivered once
    (2, "new", 15.50, "2026-03-01 09:05:00", 2),        # same row delivered twice
    (2, "new", 15.50, "2026-03-01 09:05:00", 2),
    (3, "new", 99.00, "2026-03-01 10:00:00", 3),
    (3, "shipped", 99.00, "2026-03-02 08:00:00", 4),
    (3, "paid", 99.00, "2026-03-01 12:00:00", 5),       # older change arrives late
    (4, "new", 20.00, "2026-03-03 07:00:00", 6),        # two changes in the same second
    (4, "cancelled", 20.00, "2026-03-03 07:00:00", 7),
]
WANT = {1: "new", 2: "new", 3: "shipped", 4: "cancelled"}  # status each order must end with


def show(rows):
    for r in rows:
        print("   ", *r, sep="  ")


con = duckdb.connect(":memory:")
con.execute("CREATE TABLE raw_orders (order_id INT, status TEXT, amount DECIMAL(9,2), updated_at TIMESTAMP, load_seq INT)")
con.executemany("INSERT INTO raw_orders VALUES (?, ?, ?, ?, ?)", ROWS)
print(f"raw_orders: {len(ROWS)} rows, {len(WANT)} orders")
show(con.execute("SELECT * FROM raw_orders ORDER BY load_seq").fetchall())

for rule in sorted((pathlib.Path(__file__).parent / "rules").glob("*.sql")):
    rows = con.execute(rule.read_text(encoding="utf-8")).fetchall()
    got = {r[0]: r[1] for r in rows}
    one_row = len(rows) == len(WANT)
    print(f"\n{rule.name}: {len(rows)} rows")
    show(rows)
    print(f"    one row per order: {'PASS' if one_row else 'FAIL'}  |  final status: {'PASS' if got == WANT else 'FAIL'}")
