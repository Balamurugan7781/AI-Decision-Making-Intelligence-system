# this code is for checking the tables in the database....

import sqlite3
import os

# ======================================================
# DATABASE PATH
# ======================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE_PATH = os.path.join(
    BASE_DIR,
    "data",
    "business.db"
)

# ======================================================
# CONNECT TO DATABASE
# ======================================================

conn = sqlite3.connect(DATABASE_PATH)

cursor = conn.cursor()

# ======================================================
# FETCH TABLES
# ======================================================

cursor.execute("""
SELECT name
FROM sqlite_master
WHERE type='table';
""")

tables = cursor.fetchall()

# ======================================================
# PRINT TABLES
# ======================================================

print("\nTables in Database:\n")

for table in tables:
    print(table[0])

conn.close()