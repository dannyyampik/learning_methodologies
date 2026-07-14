# cafe sales pipeline
# by Dave (2023) -- ask me on slack if something breaks
# UPDATE 2024: dave left. do not touch this file, it works. -- ops team
#
# run from the repo root:  python modules/00-orientation/project/pipeline.py

import csv
import glob
import sys

import duckdb

con = duckdb.connect("data/warehouse.duckdb")

# stores
con.execute("CREATE OR REPLACE TABLE stores (store_id INT, store_name VARCHAR, city VARCHAR, opened_date DATE)")
f = open("data/raw/stores.csv")
r = csv.reader(f)
next(r)
for row in r:
    con.execute("INSERT INTO stores VALUES (?, ?, ?, ?)", row)

# products  (copy pasted from stores, seems fine)
con.execute("CREATE OR REPLACE TABLE products (product_id INT, product_name VARCHAR, category VARCHAR, unit_price DOUBLE)")
f = open("data/raw/products.csv")
r = csv.reader(f)
next(r)
for row in r:
    con.execute("INSERT INTO products VALUES (?, ?, ?, ?)", row)

# sales
con.execute("""CREATE TABLE IF NOT EXISTS sales (
    sale_id VARCHAR, store_id INT, product_id INT, quantity INT,
    unit_price DOUBLE, revenue DOUBLE, sold_at TIMESTAMP, payment_method VARCHAR)""")

total = 0
for fname in sorted(glob.glob("data/raw/sales/*.csv")):
    rows = []
    f = open(fname)
    r = csv.reader(f)
    next(r)
    for row in r:
        try:
            qty = int(row[3])
            price = float(row[4])
            # marketing wants revenue incl. VAT
            rev = qty * price * 1.17
            # if qty > 100: continue  # ??? dave why
            rows.append((row[0], row[1] or None, row[2], qty, price, rev, row[5], row[6]))
        except:
            # bad row, whatever
            continue
    con.executemany("INSERT INTO sales VALUES (?, ?, ?, ?, ?, ?, ?, ?)", rows)
    total = total + len(rows)
    print("loaded", fname, len(rows))

# daily revenue for the dashboard (finance uses this!!)
con.execute("""CREATE OR REPLACE TABLE daily_revenue AS
    SELECT CAST(sold_at AS DATE) AS day, s.store_id, st.store_name, st.city,
           SUM(s.revenue) AS revenue, COUNT(*) AS transactions
    FROM sales s LEFT JOIN stores st ON s.store_id = st.store_id
    GROUP BY 1, 2, 3, 4""")

# top products (marketing asked for this in 2023, not sure anyone still looks at it)
con.execute("""CREATE OR REPLACE TABLE top_products AS
    SELECT p.product_name, p.category, SUM(s.quantity) AS units,
           SUM(s.quantity * s.unit_price * 1.17) AS revenue
    FROM sales s JOIN products p ON s.product_id = p.product_id
    GROUP BY 1, 2 ORDER BY revenue DESC""")

print("done!", total, "rows loaded")
sys.exit(0)
