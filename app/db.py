import streamlit as st
import psycopg2
import pandas as pd
import os 

#Connect to db
def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
    )

#retrieve players from the db
def get_players():
    conn = get_connection()
    df = pd.read_sql(
        "SELECT player_id, name FROM players ORDER BY name;",
        conn
    )
    conn.close()
    return df

#retrieve score types from the db
def get_score_types():
    conn = get_connection()
    df = pd.read_sql(
        "SELECT score_type_id, score_type_code FROM score_types ORDER BY score_type_ID;",
        conn
    )
    conn.close()
    return df

#Insert a player into the db from app view
def add_player(player_name):
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO players (name)
                VALUES (%s)
                ON CONFLICT (name) DO NOTHING;
                """
                ,
                (player_name,)
            )
            conn.commit()
        finally:
            cur.close()
            conn.close()


def build_game_scorecard(df):

# Builds a pivoted scorecard for a single game.

# Rows:
#     - Rank
#     - Score types (ordered)
#     - Total

# Columns:
#     - Player names

# Enforced score order (consider adding score_type_id into the Viewto order by or add new types in case of expansions)
    score_order = [
        "Birds",
        "Bonus Cards",
        "End of Round Goals",
        "Eggs",
        "Food on Cards",
        "Tucked Cards",
        "Nectar",
    ]
#pivot score breakdown
    score_df = df.pivot(
        index="score_type",
        columns="player_name",
        values="points"
    )

# Keep only known score types, in correct order
    score_df = score_df.loc[
        score_df.index.intersection(score_order)
    ]

#Rank row
    rank_row = (
        df[["player_name","rank"]]
        .drop_duplicates()
        .set_index("player_name")
        .T
    )

    rank_row.index = ["Rank"]

#Totals row
    totals_row = (
        df[["player_name","total_points"]]
        .drop_duplicates()
        .set_index("player_name")
        .T
    )

    totals_row.index = ["Total"]

    final_table = pd.concat(
        [rank_row, score_df, totals_row]
    )

    return final_table
    

def build_game_summary(df):

    #Builds a one-row summary table for a game.
    
    summary = {
        "Game ID": df["game_id"].iloc[0],
        "Game Version": df["game_version"].iloc[0],
        #"Played At": df["played_at"].iloc[0],
        #above isn't pulled through in the underlying view review
    }

    return pd.DataFrame([summary])


#retrieve games from the db
def get_games():
     conn = get_connection()
     df = pd.read_sql("""
        SELECT
            g.game_id,
            g.played_at,
            gv.name AS game_version
        FROM games g
        JOIN game_versions gv 
            ON g.game_version_id = gv.version_id
        ORDER BY g.played_at DESC, g.game_id DESC;
    """, conn)
     conn.close()
     return df

#delete game, can be used in case of error in data entry
def delete_game(game_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM games WHERE game_id = %s;",
        (game_id,)
    )
    conn.commit()
    cur.close()
    conn.close()

# retrieve game breakdown for set game_id
def get_game_breakdown(game_id):
    conn = get_connection()
    query = """
        SELECT *
        FROM v_game_player_score_ranked
        WHERE game_id = %s
        ORDER BY rank, player_name, score_type;
    """

    df = pd.read_sql(query, conn, params=(game_id,))
    conn.close()

    return df

def build_leaderboard_scorecard(df):

# Builds a pivoted scorecard for a single game.

# Rows:
#     - all_time rank
#     - game_version
#     - Score types (ordered)
#     - Total

# Columns:
#     - Player names

# Enforced score order (consider adding score_type_id into the Viewto order by or add new types in case of expansions)
    score_order = [
        "Birds",
        "Bonus Cards",
        "End of Round Goals",
        "Eggs",
        "Food on Cards",
        "Tucked Cards",
        "Nectar",
    ]
#pivot score breakdown
    score_df = df.pivot(
        index="score_type",
        columns="all_time",
        values="points"
    )

# Keep only known score types, in correct order
    score_df = score_df.loc[
        score_df.index.intersection(score_order)
    ]

#Rank row
    player_row = (
        df[["all_time","player_name"]]
        .drop_duplicates()
        .set_index("all_time")
    )

    player_row.index = ["Player"]

#Rank row
    version_row = (
        df[["all_time","version_played"]]
        .drop_duplicates()
        .set_index("all_time")
    )

    player_row.index = ["Version"]

#Totals row
    totals_row = (
        df[["all_time","total_points"]]
        .drop_duplicates()
        .set_index("all_time")
        .T
    )

    totals_row.index = ["Total"]

    final_table = pd.concat(
        [player_row, version_row, score_df, totals_row]
    )

    return final_table