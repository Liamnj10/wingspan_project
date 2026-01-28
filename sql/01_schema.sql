-- ============================================
-- Wingspan Project
-- Database Schema
-- ============================================
-- This schema models:
--  - players and their score breakdowns over multiple games
--  - games played at a point in time
--  - scores linking players to games 
--  - number of wins for each player
--
-- Designed for fun analytics for competetive players
-- ============================================

-- ---------- players ----------
CREATE TABLE players (
    player_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);


-- ---------- game_versions ----------
CREATE TABLE game_versions (
    game_version_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

-- ---------- games -----------
CREATE TABLE games (
    game_id SERIAL PRIMARY KEY,
    game_no INTEGER NOT NULL UNIQUE,
    game_verion_id INTEGER NOT NULL 
    played_at TIMESTAMP NOT NULL DEFAULT NOW()
);


-- ---------- score_types ---------
CREATE TABLE score_types (
    score_type_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

-- ---------- scores -----------
CREATE TABLE scores ( 
    game_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    score_type_id INTEGER NOT NULL,
    points INTEGER NOT NULL CHECK (points >= 0),

    PRIMARY KEY (game_id, player_id, score_type_id)

    CONSTRAINT fk_scores_game
        FOREIGN KEY (game_id)
        REFERENCES games (game_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_scores_player
        FOREIGN KEY (player_id)
        REFERENCES players (player_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_scores_type
        FOREIGN KEY (score_type_id)
        REFERENCES score_types (score_type_id)
);