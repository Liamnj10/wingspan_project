import streamlit as st
import psycopg2
import pandas as pd
import os 

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