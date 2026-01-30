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
    player_name;


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
		RANK() OVER(PARTITION BY player_name ORDER BY total_points DESC)AS rnk
	FROM v_game_player_totals
)
WHERE rnk=1
ORDER BY game_id;



-- Leaderboard

CREATE OR REPLACE VIEW v_player_leaderboard AS
SELECT
    t.player_id,
    t.player_name,
    COUNT(*) AS games_played,
	COUNT(w.player_id) AS wins,
    ROUND(AVG(t.total_points), 2) AS avg_score,
    MAX(t.total_points) AS best_score,
    MIN(t.total_points) AS worst_score
FROM v_game_player_totals t
JOIN v_winners w
	ON t.player_id = w.player_id
GROUP BY
    t.player_id,
    t.player_name
ORDER BY
	wins,
	avg_score;


