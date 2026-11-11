import sqlite3

SCHEMA = """
CREATE TABLE orders (
    order_id     TEXT PRIMARY KEY,
    status       TEXT NOT NULL,
    amount_cents INTEGER NOT NULL,
    updated_at   TEXT NOT NULL
)
"""

UPSERT = """
INSERT INTO orders (order_id, status, amount_cents, updated_at)
VALUES (:order_id, :status, :amount_cents, :updated_at)
ON CONFLICT (order_id) DO UPDATE SET
    status       = excluded.status,
    amount_cents = excluded.amount_cents,
    updated_at   = excluded.updated_at
WHERE excluded.updated_at > orders.updated_at
"""


def load(con, batch):
    with con:
        con.executemany(UPSERT, batch)


def show(con, label):
    print(label)
    for row in con.execute("SELECT * FROM orders ORDER BY order_id"):
        print("  ", row)


def order(order_id, status, amount_cents, updated_at):
    return {
        "order_id": order_id,
        "status": status,
        "amount_cents": amount_cents,
        "updated_at": updated_at,
    }


monday = [
    order("A-1", "new", 4000, "2026-03-02T09:00:00Z"),
    order("A-2", "new", 1550, "2026-03-02T09:05:00Z"),
    order("A-3", "paid", 9900, "2026-03-02T09:10:00Z"),
]
tuesday = [
    order("A-2", "shipped", 1550, "2026-03-03T08:00:00Z"),  # newer: update
    order("A-3", "new", 9900, "2026-03-02T09:07:00Z"),  # older: keep stored row
    order("A-4", "new", 700, "2026-03-03T08:30:00Z"),  # unknown key: insert
]

con = sqlite3.connect(":memory:")
print("SQLite", sqlite3.sqlite_version)
con.execute(SCHEMA)

load(con, monday)
show(con, "monday batch")
load(con, monday)
show(con, "monday batch, rerun")
load(con, tuesday)
show(con, "tuesday batch")
load(con, tuesday)
show(con, "tuesday batch, rerun")
