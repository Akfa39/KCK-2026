from datetime import datetime

from database.repositories.base import BaseRepository


class WorkoutRepository(BaseRepository):

    def start(self, user_id: int, plan_id: int = None) -> int:
        cursor = self._execute(
            "INSERT INTO TBL_Workouts (user_id, plan_id, started_at) VALUES (?, ?, ?)",
            (user_id, plan_id, datetime.now().isoformat())
        )
        self._conn.commit()
        return cursor.lastrowid

    def finish(self, workout_id: int, calories_burned: int = None) -> bool:
        cursor = self._execute(
            """UPDATE TBL_Workouts
               SET ended_at = ?, calories_burned = ?
               WHERE id = ?""",
            (datetime.now().isoformat(), calories_burned, workout_id)
        )
        self._conn.commit()
        return cursor.rowcount > 0

    def log_exercise(self, workout_id: int, exercise_id: int, set_number: int = 1,
                     reps_completed: int = None, duration_seconds: int = None) -> int:
        cursor = self._execute(
            """INSERT INTO TBL_Workout_Exercises
               (workout_id, exercise_id, set_number, reps_completed, duration_seconds)
               VALUES (?, ?, ?, ?, ?)""",
            (workout_id, exercise_id, set_number, reps_completed, duration_seconds)
        )
        self._conn.commit()
        return cursor.lastrowid

    def get_history(self, user_id: int, limit: int = 20) -> list[dict]:
        rows = self._execute(
            """SELECT * FROM TBL_Workouts
               WHERE user_id = ?
               ORDER BY started_at DESC
               LIMIT ?""",
            (user_id, limit)
        ).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def get_by_id(self, workout_id: int) -> dict | None:
        row = self._execute(
            "SELECT * FROM TBL_Workouts WHERE id = ?", (workout_id,)
        ).fetchone()
        if not row:
            return None
        workout = self._row_to_dict(row)
        exercises = self._execute(
            """SELECT we.*, e.name, e.muscle_group
               FROM TBL_Workout_Exercises we
               JOIN TBL_Exercises e ON e.id = we.exercise_id
               WHERE we.workout_id = ?""",
            (workout_id,)
        ).fetchall()
        workout["exercises"] = [self._row_to_dict(e) for e in exercises]
        return workout
