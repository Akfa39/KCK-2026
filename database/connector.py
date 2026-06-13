import sqlite3

from database.repositories.users import UserRepository
from database.repositories.settings import UserSettingsRepository
from database.repositories.exercises import ExerciseRepository
from database.repositories.training_plans import TrainingPlanRepository
from database.repositories.workouts import WorkoutRepository

_SCHEMA = """
CREATE TABLE IF NOT EXISTS TBL_Users (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT    NOT NULL,
    role TEXT    NOT NULL DEFAULT 'user'
);

CREATE TABLE IF NOT EXISTS TBL_User_Settings (
    user_id     INTEGER PRIMARY KEY,
    language    TEXT    DEFAULT 'pl',
    unit_system TEXT    DEFAULT 'metric',
    weight_kg   REAL,
    height_cm   REAL,
    birth_date  TEXT,
    gender      TEXT,
    FOREIGN KEY (user_id) REFERENCES TBL_Users(id)
);

CREATE TABLE IF NOT EXISTS TBL_Exercises (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT NOT NULL,
    description  TEXT,
    muscle_group TEXT,
    equipment    TEXT,
    difficulty   INTEGER,
    user_id      INTEGER,
    image_url    TEXT,
    video_url    TEXT
);

CREATE TABLE IF NOT EXISTS TBL_Training_Plans (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name    TEXT    NOT NULL,
    FOREIGN KEY (user_id) REFERENCES TBL_Users(id)
);

CREATE TABLE IF NOT EXISTS TBL_Training_Plan_Exercises (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id                 INTEGER NOT NULL,
    exercise_id             INTEGER NOT NULL,
    order_index             INTEGER NOT NULL,
    sets                    INTEGER DEFAULT 1,
    target_reps             INTEGER,
    target_duration_seconds INTEGER,
    FOREIGN KEY (plan_id)     REFERENCES TBL_Training_Plans(id),
    FOREIGN KEY (exercise_id) REFERENCES TBL_Exercises(id)
);

CREATE TABLE IF NOT EXISTS TBL_Workouts (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        INTEGER NOT NULL,
    plan_id        INTEGER,
    started_at     TEXT    NOT NULL,
    ended_at       TEXT,
    calories_burned INTEGER,
    FOREIGN KEY (user_id)  REFERENCES TBL_Users(id),
    FOREIGN KEY (plan_id)  REFERENCES TBL_Training_Plans(id)
);

CREATE TABLE IF NOT EXISTS TBL_Workout_Exercises (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    workout_id       INTEGER NOT NULL,
    exercise_id      INTEGER NOT NULL,
    set_number       INTEGER DEFAULT 1,
    reps_completed   INTEGER,
    duration_seconds INTEGER,
    FOREIGN KEY (workout_id)   REFERENCES TBL_Workouts(id),
    FOREIGN KEY (exercise_id)  REFERENCES TBL_Exercises(id)
);
"""


class DatabaseConnector:
    def __init__(self, db_path: str):
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

        self.users = UserRepository(self._conn)
        self.settings = UserSettingsRepository(self._conn)
        self.exercises = ExerciseRepository(self._conn)
        self.training_plans = TrainingPlanRepository(self._conn)
        self.workouts = WorkoutRepository(self._conn)

        self._seed_default_user()

    def _seed_default_user(self):
        row = self._conn.execute("SELECT id FROM TBL_Users WHERE id = 1").fetchone()
        if not row:
            self._conn.execute(
                "INSERT INTO TBL_Users (user, role) VALUES (?, ?)", ("default", "user")
            )
            self._conn.commit()

    def seed_exercises(self, exercise_classes: list) -> None:
        for cls in exercise_classes:
            existing = self._conn.execute(
                "SELECT id FROM TBL_Exercises WHERE name = ?", (cls.name,)
            ).fetchone()
            if not existing:
                self._conn.execute(
                    """INSERT INTO TBL_Exercises (name, description, muscle_group, equipment)
                       VALUES (?, ?, ?, ?)""",
                    (cls.name, getattr(cls, "description", None),
                     getattr(cls, "muscle_group", None), "hantel"),
                )
        self._conn.commit()

    def close(self):
        self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
