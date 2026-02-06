import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import db

load_dotenv()

st.title("Wingspan Scoring App")

st.subheader("Leaderboard")

query = """
SELECT *
FROM v_player_leaderboard;
"""

conn = db.get_connection()
df = pd.read_sql(query, conn)
conn.close()

st.dataframe(df)

st.subheader("Top Scores")

query = """
SELECT *
FROM v_game_player_score_ranked
WHERE all_time <= 10"""

conn = db.get_connection()
df = pd.read_sql(query, conn)
conn.close()

leaderboard = db.build_leaderboard_scorecard(df)

st.dataframe(leaderboard)