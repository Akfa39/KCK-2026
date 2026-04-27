PRAGMA foreign_keys = ON;

INSERT INTO TBL_Users (user, role) VALUES
    ('oskar',        	    'admin'),
    ('kacper',              'admin'),
    ('piotrek',		    'admin'),

    ('katarzyna_wojcik',     'user'),
    ('michal_kowalczyk',     'user'),
    ('magdalena_kaminska',   'user'),
    ('tomasz_lewandowski',   'user'),
    ('agnieszka_zielinska',  'user'),
    ('pawel_szymanski',      'user'),
    ('joanna_wozniak',       'user'),
    ('marcin_dabrowski',     'user'),
    ('karolina_kozlowska',   'user'),
    ('adam_jankowski',       'user'),
    ('monika_mazur',         'user'),
    ('krzysztof_krawczyk',   'user'),
    ('beata_piotrowska',     'user'),
    ('lukasz_grabowski',     'user'),
    ('natalia_pawlowska',    'user');


INSERT INTO TBL_User_Settings
    (user_id, language, unit_system, weight_kg, height_cm, birth_date, gender)
VALUES
    -- Admini
    (1,  'pl', 'metric',   82.5, 180.0, '1985-03-12', 'M'),
    (2,  'pl', 'metric',   65.0, 168.0, '1990-07-24', 'M'),
    (3,  'en', 'metric',   78.3, 175.5, '1988-11-05', 'M'),

    -- Zwykli użytkownicy
    (4,  'pl', 'metric',   58.0, 165.0, '1995-01-18', 'F'),
    (5,  'pl', 'metric',   88.4, 182.0, '1992-05-30', 'M'),
    (6,  'en', 'imperial', 62.5, 170.0, '1998-09-14', 'F'),
    (7,  'pl', 'metric',   95.0, 188.0, '1980-12-02', 'M'),
    (8,  'pl', 'metric',   54.2, 162.0, '2001-04-21', 'F'),
    (9,  'pl', 'metric',   76.8, 178.0, '1993-08-09', 'M'),
    (10, 'en', 'metric',   68.0, 172.0, '1996-02-15', 'F'),
    (11, 'pl', 'metric',   84.5, 185.0, '1987-10-27', 'M'),
    (12, 'pl', 'metric',   60.3, 167.0, '1999-06-11', 'F'),
    (13, 'de', 'metric',   90.1, 190.0, '1984-03-08', 'M'),
    (14, 'pl', 'metric',   55.7, 160.0, '2000-11-19', 'F'),
    (15, 'pl', 'metric',   80.0, 183.0, '1991-07-04', 'M'),
    (16, 'pl', 'imperial', 63.4, 169.0, '1997-09-23', 'F'),
    (17, 'pl', 'metric',   72.5, 176.0, '1994-12-31', 'M'),
    (18, 'en', 'metric',   59.8, 164.0, '2002-05-06', 'F');

