import sqlite3
import pandas as pd

conn = sqlite3.connect("data/nba.db")

tables = pd.read_sql(
    """
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    ORDER BY name
    """,
    conn
)

print(tables)

conn.close()