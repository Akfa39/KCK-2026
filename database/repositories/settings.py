from database.repositories.base import BaseRepository


class UserSettingsRepository(BaseRepository):

    def get(self, user_id: int) -> dict | None:
        row = self._execute(
            "SELECT * FROM TBL_User_Settings WHERE user_id = ?", (user_id,)
        ).fetchone()
        return self._row_to_dict(row)

    def save(self, user_id: int, language: str = "pl", unit_system: str = "metric",
             weight_kg: float = None, height_cm: float = None,
             birth_date: str = None, gender: str = None):
        self._execute(
            """INSERT INTO TBL_User_Settings
               (user_id, language, unit_system, weight_kg, height_cm, birth_date, gender)
               VALUES (?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(user_id) DO UPDATE SET
                   language    = excluded.language,
                   unit_system = excluded.unit_system,
                   weight_kg   = excluded.weight_kg,
                   height_cm   = excluded.height_cm,
                   birth_date  = excluded.birth_date,
                   gender      = excluded.gender""",
            (user_id, language, unit_system, weight_kg, height_cm, birth_date, gender)
        )
        self._conn.commit()

    def update(self, user_id: int, **kwargs):
        allowed = {"language", "unit_system", "weight_kg", "height_cm", "birth_date", "gender"}
        fields = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            return
        assignments = ", ".join(f"{k} = ?" for k in fields)
        values = list(fields.values()) + [user_id]
        self._execute(
            f"UPDATE TBL_User_Settings SET {assignments} WHERE user_id = ?", values
        )
        self._conn.commit()
