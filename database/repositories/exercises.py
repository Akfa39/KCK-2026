from database.repositories.base import BaseRepository


class ExerciseRepository(BaseRepository):

    def get_all(self, user_id: int = None) -> list[dict]:
        if user_id is not None:
            rows = self._execute(
                "SELECT * FROM TBL_Exercises WHERE user_id = ? OR user_id IS NULL", (user_id,)
            ).fetchall()
        else:
            rows = self._execute("SELECT * FROM TBL_Exercises").fetchall()
        return [self._row_to_dict(r) for r in rows]

    def get_by_id(self, exercise_id: int) -> dict | None:
        row = self._execute(
            "SELECT * FROM TBL_Exercises WHERE id = ?", (exercise_id,)
        ).fetchone()
        return self._row_to_dict(row)

    def get_by_name(self, name: str) -> dict | None:
        row = self._execute(
            "SELECT * FROM TBL_Exercises WHERE name = ?", (name,)
        ).fetchone()
        return self._row_to_dict(row)

    def add(self, name: str, description: str = None, muscle_group: str = None,
            equipment: str = None, difficulty: int = None, user_id: int = None,
            image_url: str = None, video_url: str = None) -> int:
        cursor = self._execute(
            """INSERT INTO TBL_Exercises
               (name, description, muscle_group, equipment, difficulty, user_id, image_url, video_url)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (name, description, muscle_group, equipment, difficulty, user_id, image_url, video_url)
        )
        self._conn.commit()
        return cursor.lastrowid

    def delete(self, exercise_id: int) -> bool:
        cursor = self._execute(
            "DELETE FROM TBL_Exercises WHERE id = ?", (exercise_id,)
        )
        self._conn.commit()
        return cursor.rowcount > 0
