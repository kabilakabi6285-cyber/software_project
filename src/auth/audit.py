import sqlite3
import json
from datetime import datetime
from pathlib import Path


class AuditLogger:
    """Append-only audit log of every tool call."""

    def __init__(self, db_path: str = "audit.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                action TEXT NOT NULL,
                user TEXT NOT NULL,
                resource TEXT,
                result TEXT NOT NULL,
                details TEXT
            )
        """)
        conn.commit()
        conn.close()

    def log(self, action: str, user: str, result: str,
            resource: str = "", details: dict = None):
        """Record a tool call."""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """INSERT INTO audit_log
               (timestamp, action, user, resource, result, details)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                datetime.utcnow().isoformat(),
                action,
                user,
                resource,
                result,
                json.dumps(details or {}),
            ),
        )
        conn.commit()
        conn.close()

    def recent(self, limit: int = 20) -> list:
        """Return recent audit entries."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM audit_log ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]