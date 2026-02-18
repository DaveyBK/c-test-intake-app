"""
SQLite database layer for C-Test Intake App.

Local database for C-test results and templates.
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Generator, Dict

from config import DB_PATH
from models import CTestItem, CTestResult, Student


# =============================================================================
# SCHEMA
# =============================================================================

SCHEMA = """
-- C-test results (local storage)
CREATE TABLE IF NOT EXISTS c_test_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    test_version TEXT NOT NULL,
    test_date DATETIME NOT NULL,
    num_items INTEGER NOT NULL,
    num_correct INTEGER NOT NULL,
    percentage REAL NOT NULL,
    score INTEGER NOT NULL,
    placement_level TEXT,
    completed BOOLEAN DEFAULT 1,
    synced_to_inventory BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- C-test result items (item-level details)
CREATE TABLE IF NOT EXISTS c_test_result_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    result_id INTEGER NOT NULL,
    item_number INTEGER NOT NULL,
    correct_word TEXT NOT NULL,
    student_answer TEXT,
    is_correct BOOLEAN NOT NULL,
    FOREIGN KEY (result_id) REFERENCES c_test_results(id) ON DELETE CASCADE
);

-- C-test templates/versions
CREATE TABLE IF NOT EXISTS c_test_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT NOT NULL UNIQUE,
    text_with_fragments TEXT NOT NULL,
    answer_key TEXT NOT NULL,
    num_items INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Students cache (local copy from inventory.db)
CREATE TABLE IF NOT EXISTS students_cache (
    id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    current_level TEXT,
    last_synced DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""


# =============================================================================
# DATABASE CLASS
# =============================================================================

class Database:
    """SQLite database manager for C-Test app."""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self._init_db()
    
    def _init_db(self):
        """Create tables if they don't exist."""
        with self._connect() as conn:
            conn.executescript(SCHEMA)
        print(f"C-Test database initialized at {self.db_path}")
    
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
    # C-TEST RESULT OPERATIONS
    # =========================================================================
    
    def add_c_test_result(self, result: CTestResult) -> int:
        """
        Add a C-test result with items.
        
        Args:
            result: CTestResult object
            
        Returns:
            Result ID
        """
        with self._connect() as conn:
            # Insert result
            cursor = conn.execute(
                """INSERT INTO c_test_results
                   (student_id, test_version, test_date, num_items, num_correct,
                    percentage, score, placement_level, completed, synced_to_inventory)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (result.student_id, result.test_version, 
                 result.test_date.isoformat() if result.test_date else None,
                 result.num_items, result.num_correct, result.percentage,
                 result.score, result.placement_level, result.completed,
                 result.synced_to_inventory)
            )
            result_id = cursor.lastrowid
            
            # Insert items
            for item in result.items:
                conn.execute(
                    """INSERT INTO c_test_result_items
                       (result_id, item_number, correct_word, student_answer, is_correct)
                       VALUES (?, ?, ?, ?, ?)""",
                    (result_id, item.item_number, item.original_word,
                     item.student_answer, item.is_correct)
                )
            
            return result_id
    
    def get_c_test_result(self, result_id: int) -> Optional[CTestResult]:
        """
        Get a C-test result by ID.
        
        Args:
            result_id: Result ID
            
        Returns:
            CTestResult object or None
        """
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM c_test_results WHERE id = ?", (result_id,)
            ).fetchone()
            
            if not row:
                return None
            
            # Get items
            item_rows = conn.execute(
                """SELECT * FROM c_test_result_items 
                   WHERE result_id = ? ORDER BY item_number""",
                (result_id,)
            ).fetchall()
            
            items = [
                CTestItem(
                    item_number=r["item_number"],
                    original_word=r["correct_word"],
                    fragment_shown="",
                    student_answer=r["student_answer"] or "",
                    is_correct=bool(r["is_correct"])
                )
                for r in item_rows
            ]
            
            test_date = None
            if row["test_date"]:
                if isinstance(row["test_date"], str):
                    test_date = datetime.fromisoformat(row["test_date"])
                else:
                    test_date = row["test_date"]
            
            return CTestResult(
                id=row["id"],
                student_id=row["student_id"],
                test_version=row["test_version"],
                test_date=test_date,
                num_items=row["num_items"],
                num_correct=row["num_correct"],
                percentage=row["percentage"],
                score=row["score"],
                placement_level=row["placement_level"] or "",
                items=items,
                completed=bool(row["completed"]),
                synced_to_inventory=bool(row["synced_to_inventory"])
            )
    
    def get_student_results(self, student_id: int) -> List[CTestResult]:
        """
        Get all C-test results for a student.
        
        Args:
            student_id: Student ID
            
        Returns:
            List of CTestResult objects
        """
        with self._connect() as conn:
            rows = conn.execute(
                """SELECT id FROM c_test_results 
                   WHERE student_id = ? 
                   ORDER BY test_date DESC""",
                (student_id,)
            ).fetchall()
            
            return [self.get_c_test_result(row["id"]) for row in rows]
    
    def mark_result_synced(self, result_id: int) -> None:
        """Mark a result as synced to inventory.db."""
        with self._connect() as conn:
            conn.execute(
                "UPDATE c_test_results SET synced_to_inventory = 1 WHERE id = ?",
                (result_id,)
            )
    
    # =========================================================================
    # C-TEST TEMPLATE OPERATIONS
    # =========================================================================
    
    def add_c_test_template(self, version: str, text: str, answer_key: str, num_items: int) -> int:
        """
        Add a C-test template.
        
        Args:
            version: Template version identifier (e.g., "A", "B")
            text: Text with fragments (e.g., "The wea____ was col____")
            answer_key: JSON string of answer key
            num_items: Number of items in the test
        
        Returns:
            Template ID
        """
        with self._connect() as conn:
            cursor = conn.execute(
                """INSERT INTO c_test_templates
                   (version, text_with_fragments, answer_key, num_items)
                   VALUES (?, ?, ?, ?)""",
                (version, text, answer_key, num_items)
            )
            return cursor.lastrowid
    
    def get_c_test_template(self, version: str) -> Optional[Dict]:
        """
        Get a C-test template by version.
        
        Args:
            version: Template version identifier
        
        Returns:
            Dictionary with template data or None
        """
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM c_test_templates WHERE version = ?",
                (version,)
            ).fetchone()
            if row:
                return {
                    "id": row["id"],
                    "version": row["version"],
                    "text_with_fragments": row["text_with_fragments"],
                    "answer_key": row["answer_key"],
                    "num_items": row["num_items"],
                    "created_at": row["created_at"],
                }
            return None
    
    def list_c_test_templates(self) -> List[Dict]:
        """List all available C-test templates."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT version, num_items FROM c_test_templates ORDER BY version"
            ).fetchall()
            return [{"version": r["version"], "num_items": r["num_items"]} for r in rows]
    
    # =========================================================================
    # STUDENT CACHE OPERATIONS
    # =========================================================================
    
    def cache_student(self, student: Student) -> None:
        """Cache a student from inventory.db."""
        with self._connect() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO students_cache
                   (id, first_name, last_name, email, current_level, last_synced)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (student.id, student.first_name, student.last_name,
                 student.email, student.current_level, datetime.now().isoformat())
            )
    
    def get_cached_student(self, student_id: int) -> Optional[Student]:
        """Get a cached student."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM students_cache WHERE id = ?", (student_id,)
            ).fetchone()
            
            if row:
                return Student(
                    id=row["id"],
                    first_name=row["first_name"],
                    last_name=row["last_name"],
                    email=row["email"] or "",
                    current_level=row["current_level"] or ""
                )
            return None
    
    def get_all_cached_students(self) -> List[Student]:
        """Get all cached students."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM students_cache ORDER BY last_name, first_name"
            ).fetchall()
            
            return [
                Student(
                    id=r["id"],
                    first_name=r["first_name"],
                    last_name=r["last_name"],
                    email=r["email"] or "",
                    current_level=r["current_level"] or ""
                )
                for r in rows
            ]


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
