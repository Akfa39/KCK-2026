from database.repositories.base import BaseRepository


class TrainingPlanRepository(BaseRepository):

    def get_all(self, user_id: int) -> list[dict]:
        rows = self._execute(
            "SELECT * FROM TBL_Training_Plans WHERE user_id = ?", (user_id,)
        ).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def get_by_id(self, plan_id: int) -> dict | None:
        row = self._execute(
            "SELECT * FROM TBL_Training_Plans WHERE id = ?", (plan_id,)
        ).fetchone()
        if not row:
            return None
        plan = self._row_to_dict(row)
        exercises = self._execute(
            """SELECT tpe.*, e.name, e.muscle_group, e.difficulty
               FROM TBL_Training_Plan_Exercises tpe
               JOIN TBL_Exercises e ON e.id = tpe.exercise_id
               WHERE tpe.plan_id = ?
               ORDER BY tpe.order_index""",
            (plan_id,)
        ).fetchall()
        plan["exercises"] = [self._row_to_dict(e) for e in exercises]
        return plan

    def create(self, user_id: int, name: str) -> int:
        cursor = self._execute(
            "INSERT INTO TBL_Training_Plans (user_id, name) VALUES (?, ?)", (user_id, name)
        )
        self._conn.commit()
        return cursor.lastrowid

    def add_exercise(self, plan_id: int, exercise_id: int, order_index: int,
                     sets: int = 1, target_reps: int = None,
                     target_duration_seconds: int = None) -> int:
        cursor = self._execute(
            """INSERT INTO TBL_Training_Plan_Exercises
               (plan_id, exercise_id, order_index, sets, target_reps, target_duration_seconds)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (plan_id, exercise_id, order_index, sets, target_reps, target_duration_seconds)
        )
        self._conn.commit()
        return cursor.lastrowid

    def delete(self, plan_id: int) -> bool:
        cursor = self._execute(
            "DELETE FROM TBL_Training_Plans WHERE id = ?", (plan_id,)
        )
        self._conn.commit()
        return cursor.rowcount > 0
