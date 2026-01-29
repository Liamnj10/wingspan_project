BEGIN;

-- =========================
-- Game versions / expansions
-- =========================
INSERT INTO game_versions (version_code, name)
VALUES
    ('BASE', 'Base Game'),
    ('OCEANIA', 'Oceania Expansion')
ON CONFLICT (version_code) DO NOTHING;

-- =========================
-- Seed score types
-- =========================

INSERT INTO score_types (score_type_code, name)
VALUES
    ('BIRD','Birds'),
    ('BONUS','Bonus Cards'),
    ('ROUND_GOAL','End of Round Goals'),
    ('EGGS','Eggs'),
    ('FOOD','Food on Cards'),
    ('TUCK','Tucked Cards'),
    ('NECTAR','Nectar')
ON CONFLICT (score_type_id) DO NOTHING;

COMMIT;
