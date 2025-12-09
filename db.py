"""
SQLite database layer for 10-Minute Reading App (V1).

Simple schema for tracking homework submissions and scores.
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Generator

from config import DB_PATH
from models import Homework, GeneratedHomework


# =============================================================================
# SCHEMA
# =============================================================================

SCHEMA = """
-- Homework submissions
CREATE TABLE IF NOT EXISTS homeworks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hw_number INTEGER NOT NULL UNIQUE,
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    extracted_text TEXT,
    status TEXT DEFAULT 'pending',
    submitted_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    reading_score INTEGER,
    writing_score INTEGER,
    listening_score INTEGER,
    comment TEXT
);

-- Generated homework files
CREATE TABLE IF NOT EXISTS generated_homeworks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hw_number INTEGER NOT NULL,
    reading_file TEXT,
    writing_file TEXT,
    reading_text TEXT,
    writing_prompts TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Track which files we've already processed
CREATE TABLE IF NOT EXISTS processed_files (
    file_path TEXT PRIMARY KEY,
    processed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""


# =============================================================================
# DATABASE CLASS
# =============================================================================

class Database:
    """SQLite database manager."""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self._init_db()
    
    def _init_db(self):
        """Create tables if they don't exist."""
        with self._connect() as conn:
            conn.executescript(SCHEMA)
        print(f"Database initialized at {self.db_path}")
    
    @contextmanager
    def _connect(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager for database connections."""
        conn = None
        try:
            conn = sqlite3.connect(
                self.db_path,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            )
            conn.row_factory = sqlite3.Row
            yield conn
            conn.commit()
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    # =========================================================================
    # HOMEWORK OPERATIONS
    # =========================================================================
    
    def add_homework(self, hw: Homework) -> int:
        """Add a new homework. Returns the ID."""
        with self._connect() as conn:
            # Serialize datetime to ISO format string for consistent handling
            submitted_at_str = hw.submitted_at.isoformat() if hw.submitted_at else None

            cursor = conn.execute(
                """INSERT INTO homeworks
                   (hw_number, file_name, file_path, extracted_text, status,
                    submitted_at, reading_score, writing_score, comment)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (hw.hw_number, hw.file_name, hw.file_path, hw.extracted_text,
                 hw.status, submitted_at_str, hw.reading_score, hw.writing_score,
                 hw.comment)
            )
            return cursor.lastrowid
    
    def get_homework(self, hw_id: int) -> Optional[Homework]:
        """Get a homework by ID."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM homeworks WHERE id = ?", (hw_id,)
            ).fetchone()
            if row:
                return self._row_to_homework(row)
            return None
    
    def get_homework_by_number(self, hw_number: int) -> Optional[Homework]:
        """Get a homework by homework number."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM homeworks WHERE hw_number = ?", (hw_number,)
            ).fetchone()
            if row:
                return self._row_to_homework(row)
            return None
    
    def get_all_homeworks(self) -> List[Homework]:
        """Get all homeworks, newest first."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM homeworks ORDER BY hw_number DESC"
            ).fetchall()
            return [self._row_to_homework(row) for row in rows]
    
    def update_homework(self, hw: Homework) -> None:
        """Update an existing homework."""
        with self._connect() as conn:
            conn.execute(
                """UPDATE homeworks SET
                   status = ?, reading_score = ?, writing_score = ?,
                   listening_score = ?, comment = ?
                   WHERE id = ?""",
                (hw.status, hw.reading_score, hw.writing_score,
                 hw.listening_score, hw.comment, hw.id)
            )
    
    def get_next_hw_number(self) -> int:
        """Get the next homework number."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT MAX(hw_number) as max_num FROM homeworks"
            ).fetchone()
            max_num = row["max_num"] if row["max_num"] else 0
            return max_num + 1

    def delete_homework(self, hw_id: int) -> None:
        """Delete a homework by ID."""
        with self._connect() as conn:
            conn.execute("DELETE FROM homeworks WHERE id = ?", (hw_id,))

    def _row_to_homework(self, row: sqlite3.Row) -> Homework:
        """Convert a database row to Homework object."""
        # Deserialize datetime strings to datetime objects
        submitted_at = None
        if row["submitted_at"]:
            if isinstance(row["submitted_at"], str):
                submitted_at = datetime.fromisoformat(row["submitted_at"])
            else:
                submitted_at = row["submitted_at"]

        created_at = None
        if row["created_at"]:
            if isinstance(row["created_at"], str):
                created_at = datetime.fromisoformat(row["created_at"])
            else:
                created_at = row["created_at"]

        return Homework(
            id=row["id"],
            hw_number=row["hw_number"],
            file_name=row["file_name"],
            file_path=row["file_path"],
            extracted_text=row["extracted_text"] or "",
            status=row["status"],
            submitted_at=submitted_at,
            created_at=created_at,
            reading_score=row["reading_score"],
            writing_score=row["writing_score"],
            listening_score=row["listening_score"],
            comment=row["comment"] or "",
        )
    
    # =========================================================================
    # PROCESSED FILES TRACKING
    # =========================================================================
    
    def is_file_processed(self, file_path: str) -> bool:
        """Check if a file has already been processed."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM processed_files WHERE file_path = ?",
                (file_path,)
            ).fetchone()
            return row is not None
    
    def mark_file_processed(self, file_path: str) -> None:
        """Mark a file as processed."""
        with self._connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO processed_files (file_path) VALUES (?)",
                (file_path,)
            )
    
    # =========================================================================
    # GENERATED HOMEWORK OPERATIONS
    # =========================================================================
    
    def add_generated_homework(self, gen: GeneratedHomework) -> int:
        """Add a generated homework record. Returns the ID."""
        with self._connect() as conn:
            cursor = conn.execute(
                """INSERT INTO generated_homeworks
                   (hw_number, reading_file, writing_file, reading_text, writing_prompts)
                   VALUES (?, ?, ?, ?, ?)""",
                (gen.hw_number, gen.reading_file, gen.writing_file,
                 gen.reading_text, gen.writing_prompts)
            )
            return cursor.lastrowid


# =============================================================================
# SINGLETON
# =============================================================================

_db: Optional[Database] = None


def get_db() -> Database:
    """Get the database instance."""
    global _db
    if _db is None:
        _db = Database()
    return _db
