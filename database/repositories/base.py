import sqlite3


class BaseRepository:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def _execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        return self._conn.execute(sql, params)

    def _row_to_dict(self, row: sqlite3.Row) -> dict:
        return dict(row) if row else None
