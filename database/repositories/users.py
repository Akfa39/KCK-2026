from database.repositories.base import BaseRepository


class UserRepository(BaseRepository):

    def get_all(self) -> list[dict]:
        rows = self._execute("SELECT * FROM TBL_Users").fetchall()
        return [self._row_to_dict(r) for r in rows]

    def get_by_id(self, user_id: int) -> dict | None:
        row = self._execute(
            "SELECT * FROM TBL_Users WHERE id = ?", (user_id,)
        ).fetchone()
        return self._row_to_dict(row)

    def get_by_name(self, username: str) -> dict | None:
        row = self._execute(
            "SELECT * FROM TBL_Users WHERE user = ?", (username,)
        ).fetchone()
        return self._row_to_dict(row)

    def add(self, username: str, role: str = "user") -> int:
        cursor = self._execute(
            "INSERT INTO TBL_Users (user, role) VALUES (?, ?)", (username, role)
        )
        self._conn.commit()
        return cursor.lastrowid

    def delete(self, user_id: int) -> bool:
        cursor = self._execute(
            "DELETE FROM TBL_Users WHERE id = ?", (user_id,)
        )
        self._conn.commit()
        return cursor.rowcount > 0
