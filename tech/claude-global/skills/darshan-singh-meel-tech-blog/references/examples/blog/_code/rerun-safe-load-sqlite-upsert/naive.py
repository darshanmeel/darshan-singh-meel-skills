import sqlite3

batch = [("A-1", "new", 4000), ("A-2", "new", 1550), ("A-3", "paid", 9900)]
INSERT = "INSERT INTO orders VALUES (?, ?, ?)"
COUNT = "SELECT count(*) FROM orders"

con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE orders (order_id TEXT, status TEXT, cents INTEGER)")
con.executemany(INSERT, batch)
con.executemany(INSERT, batch)  # the retry
print("no key:", con.execute(COUNT).fetchone()[0], "rows")

con.execute("DROP TABLE orders")
con.execute(
    "CREATE TABLE orders "
    "(order_id TEXT PRIMARY KEY, status TEXT, cents INTEGER)"
)
con.executemany(INSERT, batch)
try:
    con.executemany(INSERT, batch)  # the retry
except sqlite3.IntegrityError as error:
    print("with key:", type(error).__name__, "-", error)
