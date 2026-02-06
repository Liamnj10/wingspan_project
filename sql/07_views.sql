-- Pull all required data fields into one view, 
-- Shows breakdown of player scores over all recorded games

CREATE OR REPLACE VIEW v_game_player_score_breakdown AS
SELECT
    g.game_id,
    g.game_version_id,
    gv.name AS game_version,
    p.player_id,
    p.name AS player_name,
    st.score_type_code,
    st.name AS score_type,
    s.points
FROM scores s
JOIN games g
    ON s.game_id = g.game_id
JOIN players p
    ON s.player_id = p.player_id
JOIN score_types st
    ON s.score_type_id = st.score_type_id
JOIN game_versions gv
    ON g.game_version_id = gv.version_id;

-- total scores per player per game

CREATE OR REPLACE VIEW v_game_player_totals AS
SELECT
    game_id,
    game_version,
    player_id,
    player_name,
    SUM(points) AS total_points
FROM v_game_player_score_breakdown
GROUP BY
    game_id,
    game_version,
    player_id,
    player_name
ORDER BY 
    game_id,
    player_id;


-- winners list
CREATE OR REPLACE VIEW v_winners AS
SELECT 
	game_id,
    player_id,
	player_name,
	total_points
FROM(
	SELECT 
		game_id, 
        player_id,
		player_name, 
		total_points,
		RANK() OVER(PARTITION BY game_id ORDER BY total_points DESC)AS rnk
	FROM v_game_player_totals
)
WHERE rnk=1
ORDER BY game_id;



-- Leaderboard
CREATE OR REPLACE VIEW v_player_leaderboard AS

-- Pre-aggregate the games played and wins 
WITH games_played AS (
    SELECT
        player_id,
        COUNT(DISTINCT game_id) AS games_played
    FROM v_game_player_totals
    GROUP BY player_id
),
wins AS (
    SELECT
        player_id,
        COUNT(DISTINCT game_id) AS wins
    FROM v_winners
    GROUP BY player_id
)

SELECT
    t.player_id,
    t.player_name,
    gp.games_played,
	COALESCE(w.wins,0) AS wins,
    ROUND(AVG(t.total_points), 2) AS avg_score,
    MAX(t.total_points) AS best_score,
    MIN(t.total_points) AS worst_score
FROM v_game_player_totals t
JOIN games_played gp
	ON t.player_id = gp.player_id
LEFT JOIN wins w
    ON t.player_id = w.player_id
GROUP BY
    t.player_id,
    t.player_name,
    gp.games_played,
    w.wins	
ORDER BY
	wins DESC,
	avg_score DESC;

CREATE OR REPLACE VIEW v_game_player_score_table AS
SELECT
    game_id,
    game_version_id,
    game_version,
    player_id,
    player_name,
    points
FROM v_game_player_score_breakdown

-- Ranked score breakdowns for more detailed game views in streamlit

CREATE OR REPLACE VIEW v_game_player_score_ranked AS
WITH ranked_players AS (
    SELECT
        game_id,
        player_id,
        total_points,
        RANK() OVER (
            PARTITION BY game_id
            ORDER BY total_points DESC
        ) AS rank,
        RANK() OVER (
            ORDER BY total_points DESC
        ) AS all_time
    FROM v_game_player_totals
)
SELECT
    b.game_id,
    b.game_version_id,
    b.game_version,
    b.player_id,
    b.player_name,
    b.score_type_code,
    b.score_type,
    b.points,
    rp.total_points,
    rp.rank,
    rp.all_time
FROM v_game_player_score_breakdown b
JOIN ranked_players rp
    ON b.game_id = rp.game_id
   AND b.player_id = rp.player_id;
