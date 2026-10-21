"""SQLite Database Layer for EarlyCare User Accounts and Screening History.

Stores user profiles authenticated via Google OAuth and associates their
health screening reports for historical timeline tracking.
"""
import sqlite3
import os
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

DB_FILE = os.environ.get(
    "EARLYCARE_DB_PATH",
    str(Path(__file__).resolve().parent.parent.parent / "earlycare.db")
)


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initializes tables for users and saved screening records."""
    conn = get_db_connection()
    try:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    name TEXT,
                    picture TEXT,
                    google_id TEXT,
                    created_at TEXT NOT NULL,
                    last_login TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS saved_screenings (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    screening_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    overall_risk_tier TEXT NOT NULL,
                    highest_risk_condition TEXT NOT NULL,
                    anemia_risk_pct REAL NOT NULL,
                    prediabetes_risk_pct REAL NOT NULL,
                    micronutrients_risk_pct REAL NOT NULL,
                    urgent_consult_flag INTEGER NOT NULL,
                    intake_json TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_screenings_user ON saved_screenings(user_id, created_at DESC)
            """)
    finally:
        conn.close()


def get_or_create_user(
    email: str,
    name: Optional[str] = None,
    picture: Optional[str] = None,
    google_id: Optional[str] = None
) -> Dict[str, Any]:
    """Finds existing user by email or creates a new account record."""
    clean_email = email.strip().lower()
    conn = get_db_connection()
    now_iso = datetime.now(timezone.utc).isoformat()
    try:
        with conn:
            row = conn.execute("SELECT * FROM users WHERE email = ?", (clean_email,)).fetchone()
            if row:
                user_id = row["id"]
                conn.execute(
                    """
                    UPDATE users 
                    SET name = COALESCE(?, name), 
                        picture = COALESCE(?, picture),
                        google_id = COALESCE(?, google_id),
                        last_login = ?
                    WHERE id = ?
                    """,
                    (name, picture, google_id, now_iso, user_id)
                )
                updated = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
                return dict(updated)
            else:
                import uuid
                user_id = f"usr_{uuid.uuid4().hex[:12]}"
                user_name = name or clean_email.split("@")[0].capitalize()
                conn.execute(
                    """
                    INSERT INTO users (id, email, name, picture, google_id, created_at, last_login)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (user_id, clean_email, user_name, picture or "", google_id or "", now_iso, now_iso)
                )
                created = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
                return dict(created)
    finally:
        conn.close()


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a user profile by internal user ID."""
    conn = get_db_connection()
    try:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def save_screening_for_user(
    user_id: str,
    screening_id: str,
    intake_data: Dict[str, Any],
    result_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Persists a screening report linked to the user's account."""
    import uuid
    record_id = f"rec_{uuid.uuid4().hex[:12]}"
    now_iso = datetime.now(timezone.utc).isoformat()

    overall_tier = result_data.get("overall_risk_tier", "low")
    highest_cond = result_data.get("highest_risk_condition", "General Health")
    anemia_risk = float(result_data.get("conditions", {}).get("anemia", {}).get("calibrated_risk_pct", 0.0))
    prediab_risk = float(result_data.get("conditions", {}).get("prediabetes", {}).get("calibrated_risk_pct", 0.0))
    micro_risk = float(result_data.get("conditions", {}).get("micronutrients", {}).get("calibrated_risk_pct", 0.0))
    urgent_flag = 1 if result_data.get("urgent_consult_flag", False) else 0

    conn = get_db_connection()
    try:
        with conn:
            # Check if this exact screening_id was already saved for this user to prevent duplication
            existing = conn.execute(
                "SELECT id FROM saved_screenings WHERE user_id = ? AND screening_id = ?",
                (user_id, screening_id)
            ).fetchone()

            if existing:
                conn.execute(
                    """
                    UPDATE saved_screenings
                    SET created_at = ?, overall_risk_tier = ?, highest_risk_condition = ?,
                        anemia_risk_pct = ?, prediabetes_risk_pct = ?, micronutrients_risk_pct = ?,
                        urgent_consult_flag = ?, intake_json = ?, result_json = ?
                    WHERE id = ?
                    """,
                    (
                        now_iso, overall_tier, highest_cond, anemia_risk, prediab_risk,
                        micro_risk, urgent_flag, json.dumps(intake_data), json.dumps(result_data),
                        existing["id"]
                    )
                )
                return {"id": existing["id"], "status": "updated", "screening_id": screening_id}

            conn.execute(
                """
                INSERT INTO saved_screenings (
                    id, user_id, screening_id, created_at, overall_risk_tier,
                    highest_risk_condition, anemia_risk_pct, prediabetes_risk_pct,
                    micronutrients_risk_pct, urgent_consult_flag, intake_json, result_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record_id, user_id, screening_id, now_iso, overall_tier,
                    highest_cond, anemia_risk, prediab_risk, micro_risk,
                    urgent_flag, json.dumps(intake_data), json.dumps(result_data)
                )
            )
            return {"id": record_id, "status": "created", "screening_id": screening_id}
    finally:
        conn.close()


def get_user_screenings(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Returns a summarized list of screenings belonging to the user for timeline display."""
    conn = get_db_connection()
    try:
        rows = conn.execute(
            """
            SELECT id, screening_id, created_at, overall_risk_tier, highest_risk_condition,
                   anemia_risk_pct, prediabetes_risk_pct, micronutrients_risk_pct,
                   urgent_consult_flag
            FROM saved_screenings
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (user_id, limit)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_screening_by_id(user_id: str, screening_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves the full original payload and result for a specific screening."""
    conn = get_db_connection()
    try:
        row = conn.execute(
            """
            SELECT * FROM saved_screenings
            WHERE user_id = ? AND (screening_id = ? OR id = ?)
            """,
            (user_id, screening_id, screening_id)
        ).fetchone()
        if not row:
            return None
        d = dict(row)
        d["intake_data"] = json.loads(d["intake_json"])
        d["result_data"] = json.loads(d["result_json"])
        return d
    finally:
        conn.close()


def delete_user_screening(user_id: str, screening_id: str) -> bool:
    """Deletes a screening record belonging to the user."""
    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.execute(
                "DELETE FROM saved_screenings WHERE user_id = ? AND (screening_id = ? OR id = ?)",
                (user_id, screening_id, screening_id)
            )
            return cursor.rowcount > 0
    finally:
        conn.close()
