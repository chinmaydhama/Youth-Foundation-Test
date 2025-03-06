import sqlite3
import pandas as pd

conn = sqlite3.connect("youth_impact_data.db")
query = "SELECT * FROM youth_impact where district = 'DHARWAD'"
df = pd.read_sql(query, conn)
conn.close()
print(df.head())







