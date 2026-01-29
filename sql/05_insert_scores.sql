BEGIN;

WITH latest_game AS (
    SELECT game_id
    FROM games
    ORDER BY game_id DESC
    LIMIT 1
),
player AS (
    SELECT player_id
    FROM players
    WHERE name = 'Amelia'
),
score_values AS (
    SELECT *
    FROM (
        VALUES
        ('BIRD', 49),
        ('BONUS', 13),
        ('ROUND_GOAL', 12),
        ('EGGS', 0),
        ('FOOD', 3),
        ('TUCK', 4),
        ('NECTAR', 0)
    )AS v(score_type_code, points)
)
INSERT INTO scores (game_id, player_id, score_type_id, points)
SELECT
    lg.game_id,
    p.player_id,
    st.score_type_id,
    sv.points
FROM latest_game lg
CROSS JOIN player p
CROSS JOIN score_values sv
JOIN score_types st
    ON st.score_type_code = sv.score_type_code;

COMMIT;