import sqlite3
from datetime import datetime


class ReviewHistoryStore:
    """Stores past reviews to learn team conventions."""

    def __init__(self, db_path: str = "history.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                pr_number INTEGER,
                file TEXT,
                comment TEXT,
                accepted BOOLEAN DEFAULT 0,
                category TEXT,
                severity TEXT
            )
        """)
        conn.commit()
        conn.close()

    def store(
        self,
        pr_number: int,
        file: str,
        comment: str,
        category: str = "",
        severity: str = "",
        accepted: bool = False,
    ):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """INSERT INTO reviews
               (timestamp, pr_number, file, comment, accepted, category, severity)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                datetime.utcnow().isoformat(),
                pr_number,
                file,
                comment,
                accepted,
                category,
                severity,
            ),
        )
        conn.commit()
        conn.close()

    def get_few_shot_examples(self, limit: int = 5) -> list:
        """Return recent ACCEPTED reviews to use as examples."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """SELECT comment, category, severity FROM reviews
               WHERE accepted = 1
               ORDER BY id DESC LIMIT ?""",
            (limit,),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def mark_accepted(self, review_id: int, accepted: bool = True):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "UPDATE reviews SET accepted = ? WHERE id = ?",
            (accepted, review_id),
        )
        conn.commit()
        conn.close()