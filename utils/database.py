import duckdb
import os
import pandas as pd


def init_db():
    os.makedirs("database", exist_ok=True)

    conn = duckdb.connect("database/data.duckdb")
    return conn

def load_csv_to_db(conn, uploaded_file):
    df = pd.read_csv(uploaded_file)
    conn.execute("CREATE OR REPLACE TABLE sales AS SELECT * FROM df")
    return df
