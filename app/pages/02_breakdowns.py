import streamlit as st
import pandas as pd
import db

st.header("Game Breakdown")

games_df = db.get_games()

selected_game_id = st.selectbox(
    "Select Game",
    games_df["game_id"],
    format_func=lambda x: (
        f"Game {x} | "
        f"{games_df.loc[games_df.game_id == x, 'game_version'].iloc[0]} | "
        f"{games_df.loc[games_df.game_id == x, 'played_at'].iloc[0].strftime('%d %b %Y')}"    
    )
)

st.divider()

df = db.get_game_breakdown(selected_game_id)

if df.empty:
    st.info("No games found.")
    st.stop()
    
game_summary = db.build_game_summary(df)
final_table = db.build_game_scorecard(df)

# Identify winner (rank = 1)
# winner = (
#     df[df["rank"] == 1]["player_name"]
#     .iloc[0]
# )

# Highlight winner column
#styled_table = final_table.style.apply(
#    lambda col: ["background-color: #d4edda" 
#                 if col.name == winner else "" 
#                 for _ in col
    # # ],
    # axis=0
# )

st.dataframe(final_table)

confirm_delete = st.checkbox(
    f"I understand this will permanently delete Game {selected_game_id}"
)

if st.button("Delete Game", disabled=not confirm_delete):
    db.delete_game(selected_game_id)
    st.success("Game deleted")
    st.rerun()

