import sqlite3

from database.repositories.users import UserRepository
from database.repositories.settings import UserSettingsRepository
from database.repositories.exercises import ExerciseRepository
from database.repositories.training_plans import TrainingPlanRepository
from database.repositories.workouts import WorkoutRepository


class DatabaseConnector:
    def __init__(self, db_path: str):
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")

        self.users = UserRepository(self._conn)
        self.settings = UserSettingsRepository(self._conn)
        self.exercises = ExerciseRepository(self._conn)
        self.training_plans = TrainingPlanRepository(self._conn)
        self.workouts = WorkoutRepository(self._conn)

    def close(self):
        self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
