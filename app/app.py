import streamlit as st
import psycopg2
import pandas as pd
import os 
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
    )

st.title("Wingspan Scoring App")

st.subheader("Leaderboard")

query = """
SELECT *
FROM v_player_leaderboard;
"""

conn = get_connection()
df = pd.read_sql(query, conn)
conn.close()

st.dataframe(df)