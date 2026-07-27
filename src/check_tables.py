import pandas as pd
from database import get_connection

conn = get_connection()

print(pd.read_sql_query(
    "SELECT COUNT(*) FROM players",
    conn
))

print(pd.read_sql_query(
    "PRAGMA table_info(players);",
    conn
))