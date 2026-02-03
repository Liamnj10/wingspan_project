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

def get_players():
    conn = get_connection()
    df = pd.read_sql(
        "SELECT player_id, name FROM players ORDER BY name;",
        conn
    )
    conn.close()
    return df

def get_score_types():
    conn = get_connection()
    df = pd.read_sql(
        "SELECT score_type_id, score_type_code FROM score_types ORDER BY score_type_ID;",
        conn
    )
    conn.close()
    return df

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

st.subheader("Play New Game")

players_df = get_players()
score_types_df = get_score_types()

with st.form("game_with_scores_form"):
    played_at = st.date_input("Game Date")
    version_code = st.selectbox(
        "Game Version",
        ["BASE","OCEANIA"]
    )

    selected_players = st.multiselect(
        "players",
        players_df["name"].tolist()
    )

    scores = {}

    for player in selected_players:
        st.markdown(f"## Scores for {player}")
        scores[player] = {}

        for _, row in score_types_df.iterrows():
            points = st.number_input(
                f"{player} - {row['score_type_code']}",
                min_value=0,
                step=1,
                key=f"{player}_{row['score_type_code']}"
            )
            scores[player][row["score_type_code"]] = points

    confirm = st.checkbox("I confirm all scores are final")
    submitted = st.form_submit_button("Save game")

if submitted and not confirm:
    st.warning("Please confirm all scores before saving.")
    st.stop()

if submitted:
    conn = get_connection()
    cur = conn.cursor()

    try:
        #Create game
        cur.execute(
            """
            INSERT INTO games (played_at, game_version_id)
            SELECT %s, gv.version_id
            FROM game_versions gv
            WHERE gv.version_code = %s
            RETURNING game_id;
            """,
            (played_at, version_code)
        )

        game_id = cur.fetchone()[0]

        #2. Insert scores
        for player_name, player_scores in scores.items():
            cur.execute(
                "SELECT player_id FROM players WHERE name = %s;",
                (player_name,)
            )
            player_id = cur.fetchone()[0]

            for score_code, points in player_scores.items():
                cur.execute(
                    """
                    INSERT INTO scores (game_id, player_id, score_type_id, points)
                    SELECT %s, %s, st.score_type_id, %s
                    FROM score_types st
                    WHERE st.score_type_code = %s;
                    """,
                    (game_id, player_id, points, score_code)
                )

            conn.commit()
            st.success("Game and scores saved successfully")
    
    #if an error occurs and table conditions are not met then all changes are rolled back
    #This prevents games being created without scores or other partial updates
    except Exception as e:
        conn.rollback()
        st.error(f"Error saving game: {e}")

    #Closes off connection
    finally:
        cur.close()
        conn.close()