BEGIN;

INSERT INTO games (played_at, game_version_id)
SELECT 
    DATE '2025-12-30',
    gv.version_id
FROM game_versions gv
WHERE gv.version_code = 'BASE';

COMMIT;