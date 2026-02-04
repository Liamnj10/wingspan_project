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

st.subheader("Last game")

query = """
SELECT *
FROM v_game_player_score_ranked
WHERE game_id = (
    SELECT game_id
    FROM games
    ORDER BY played_at DESC, game_id DESC
    LIMIT 1
);"""

conn = db.get_connection()
df = pd.read_sql(query, conn)
conn.close()

if df.empty:
    st.info("No games found.")
    st.stop()
    
game_summary = db.build_game_summary(df)
final_table = db.build_game_scorecard(df)

st.table(game_summary)

# Identify winner (rank = 1)
winner = (
    df[df["rank"] == 1]["player_name"]
    .iloc[0]
)

# Highlight winner column
styled_table = final_table.style.apply(
    lambda col: ["background-color: #d4edda" if col.name == winner else "" for _ in col],
    axis=0
)

st.dataframe(styled_table)
