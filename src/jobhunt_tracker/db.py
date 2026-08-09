from datetime import datetime
from pathlib import Path
import sqlite3
from typing import Any, Optional

from jobhunt_tracker.config import get_db_path
from jobhunt_tracker.models import ApplicationStatus, JobApplication


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    path = db_path or get_db_path()
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Optional[Path] = None) -> None:
    with get_connection(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                role TEXT NOT NULL,
                platform TEXT,
                status TEXT NOT NULL DEFAULT 'APPLIED',
                url TEXT,
                date_applied TEXT NOT NULL,
                salary TEXT,
                notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        columns = [row["name"] for row in conn.execute("PRAGMA table_info(applications)").fetchall()]
        if "platform" not in columns:
            conn.execute("ALTER TABLE applications ADD COLUMN platform TEXT")

        conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON applications(status)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_company ON applications(company)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_platform ON applications(platform)")
        conn.commit()


def add_application(app: JobApplication, db_path: Optional[Path] = None) -> int:
    init_db(db_path)
    now = datetime.now().isoformat()
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            """
            INSERT INTO applications (
                company, role, platform, status, url, date_applied, salary, notes, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                app.company,
                app.role,
                app.platform,
                app.status.value,
                app.url,
                app.date_applied,
                app.salary,
                app.notes,
                now,
                now,
            ),
        )
        conn.commit()
        return cursor.lastrowid or 0


def get_application(app_id: int, db_path: Optional[Path] = None) -> Optional[JobApplication]:
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.execute("SELECT * FROM applications WHERE id = ?", (app_id,))
        row = cursor.fetchone()
        return JobApplication.from_row(row) if row else None


def list_applications(
    status: Optional[str] = None,
    platform: Optional[str] = None,
    search: Optional[str] = None,
    db_path: Optional[Path] = None,
) -> list[JobApplication]:
    init_db(db_path)
    query = "SELECT * FROM applications WHERE 1=1"
    params: list[Any] = []

    if status:
        query += " AND status = ?"
        params.append(status.strip().upper())

    if platform:
        query += " AND platform LIKE ?"
        params.append(f"%{platform.strip()}%")

    if search:
        query += " AND (company LIKE ? OR role LIKE ? OR platform LIKE ? OR notes LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term, term])

    query += " ORDER BY date_applied DESC, id DESC"

    with get_connection(db_path) as conn:
        cursor = conn.execute(query, params)
        return [JobApplication.from_row(row) for row in cursor.fetchall()]


def update_application(
    app_id: int,
    db_path: Optional[Path] = None,
    **kwargs: Any,
) -> bool:
    init_db(db_path)
    allowed_fields = {"company", "role", "platform", "status", "url", "date_applied", "salary", "notes"}
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields and v is not None}

    if not updates:
        return False

    if "status" in updates and isinstance(updates["status"], ApplicationStatus):
        updates["status"] = updates["status"].value
    elif "status" in updates and isinstance(updates["status"], str):
        updates["status"] = ApplicationStatus.from_string(updates["status"]).value

    updates["updated_at"] = datetime.now().isoformat()

    set_clauses = [f"{field} = ?" for field in updates.keys()]
    values = list(updates.values()) + [app_id]

    with get_connection(db_path) as conn:
        cursor = conn.execute(
            f"UPDATE applications SET {', '.join(set_clauses)} WHERE id = ?",
            values,
        )
        conn.commit()
        return cursor.rowcount > 0



def delete_application(app_id: int, db_path: Optional[Path] = None) -> bool:
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.execute("DELETE FROM applications WHERE id = ?", (app_id,))
        conn.commit()
        return cursor.rowcount > 0


def get_status_counts(db_path: Optional[Path] = None) -> dict[str, int]:
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            "SELECT status, COUNT(*) as count FROM applications GROUP BY status"
        )
        counts = {status.value: 0 for status in ApplicationStatus}
        for row in cursor.fetchall():
            counts[row["status"]] = row["count"]
        return counts
