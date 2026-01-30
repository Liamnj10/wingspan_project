BEGIN;

WITH latest_game AS (
    SELECT game_id
    FROM games
    ORDER BY game_id DESC
    LIMIT 1
),

players_in_game AS (
    SELECT player_id, name
    FROM players
    WHERE name IN ('Amelia' , 'Liam')
),

score_values AS (
    SELECT *
    FROM (
        VALUES
        ('Amelia','BIRD', 40),
        ('Amelia','BONUS', 4),
        ('Amelia','ROUND_GOAL', 16),
        ('Amelia','EGGS', 20),
        ('Amelia','FOOD', 1),
        ('Amelia','TUCK', 5),
        ('Amelia','NECTAR', 0),

        ('Liam','BIRD', 42),
        ('Liam','BONUS', 4),
        ('Liam','ROUND_GOAL', 14),
        ('Liam','EGGS', 8),
        ('Liam','FOOD', 0),
        ('Liam','TUCK', 5),
        ('Liam','NECTAR', 0)
    )AS v(player_name, score_type_code, points)
)

INSERT INTO scores (game_id, player_id, score_type_id, points)
SELECT 
    lg.game_id,
    p.player_id,
    st.score_type_id,
    sv.points
FROM latest_game lg
JOIN score_values sv
    ON TRUE
JOIN player_in_game p
    ON p.name = sv.player_name
JOIN score_types st
    ON st.score_types_code = sv.score_types_code;

COMMIT;