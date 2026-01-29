BEGIN; 

INSERT INTO players (name)
VALUES 
    ('Amelia'),
    ('Liam')
ON CONFLICT (name) DO NOTHING;

COMMIT;