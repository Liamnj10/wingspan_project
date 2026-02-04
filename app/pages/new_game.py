import streamlit as st
import pandas as pd
import db

st.subheader("Add New Player")

with st.form("add_player_form"):
    new_player_name = st.text_input("Player name")
    add_player_submit = st.form_submit_button("Add Player")

if add_player_submit:
    if new_player_name.strip() == "":
        st.warning("Player name can not be empty.")
        
    else:
        db.add_player(new_player_name.strip())
        st.success(f"Player '{new_player_name}' added.")


st.subheader("Play New Game")

players_df = db.get_players()
score_types_df = db.get_score_types()

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

#extra checkbox to prevent accidental submissions
if submitted and not confirm:
    st.warning("Please confirm all scores before saving.")
    st.stop()

# Wingspan is fo 2 to 5 players this checks the count of players is in bounds
if submitted and len(selected_players) < 2:
    st.warning("A game must have at least 2 players.")
    st.stop()

if submitted and len(selected_players) > 5:
    st.warning("A game can have at most 5 players.")
    st.stop()


if submitted:
    conn = db.get_connection()
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