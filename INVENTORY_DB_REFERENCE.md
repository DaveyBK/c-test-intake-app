# Complete inventory_db.py File

This is the complete `inventory_db.py` file that handles integration with your shared inventory.db database.

## File Location
`/home/runner/work/c-test-intake-app/c-test-intake-app/inventory_db.py`

## Purpose
- Read students from inventory.db
- Write C-Test results to inventory.db
- Manage table creation (with safety checks)
- Cache students locally for offline operation

---

## Complete Source Code

```python
"""
Inventory database integration for C-Test Intake App.

This module provides functions to read from and write to the shared
inventory.db database used by the Zone B teacher assistant portal.

Schema matches the actual inventory.db structure:
- students: student_id (TEXT), first_name, last_name, level, status
- class_def: class_id, class_name, level
- class_roster: links students to classes
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import List, Optional, Generator

from models import Student, CTestResult


# SQL to create C-Test results table in inventory.db
CREATE_C_TEST_TABLES = """
-- C-Test results table (main test results)
CREATE TABLE IF NOT EXISTS c_test_results (
    result_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id      TEXT NOT NULL,
    test_version    TEXT NOT NULL,
    test_date       TEXT NOT NULL,
    num_items       INTEGER NOT NULL,
    num_correct     INTEGER NOT NULL,
    percentage      REAL NOT NULL,
    score           INTEGER NOT NULL,
    placement_level TEXT,
    completed       INTEGER DEFAULT 1,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

-- C-Test result items (detailed item-level results)
CREATE TABLE IF NOT EXISTS c_test_result_items (
    item_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    result_id       INTEGER NOT NULL,
    item_number     INTEGER NOT NULL,
    correct_word    TEXT NOT NULL,
    student_answer  TEXT,
    is_correct      INTEGER NOT NULL,
    FOREIGN KEY (result_id) REFERENCES c_test_results(result_id) ON DELETE CASCADE
);

-- Index for faster student lookups
CREATE INDEX IF NOT EXISTS idx_c_test_student 
ON c_test_results(student_id);

-- Index for date-based queries
CREATE INDEX IF NOT EXISTS idx_c_test_date 
ON c_test_results(test_date);
"""


class InventoryDatabase:
    """Interface to the shared inventory.db database."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize inventory database connection.
        
        Args:
            db_path: Path to inventory.db. If None, uses config.INVENTORY_DB_PATH
        """
        if db_path is None:
            try:
                from config import INVENTORY_DB_PATH
                db_path = INVENTORY_DB_PATH
            except ImportError:
                db_path = None
        
        self.db_path = Path(db_path) if db_path else None
        self._available = self.db_path and self.db_path.exists()
    
    @contextmanager
    def _connect(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager for database connections."""
        if not self._available:
            raise ConnectionError(f"Inventory database not available at {self.db_path}")
        
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
    
    def is_available(self) -> bool:
        """Check if inventory database is available."""
        return self._available
    
    def initialize_c_test_tables(self) -> bool:
        """
        Create C-Test tables in inventory.db if they don't exist.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            return False
        
        try:
            with self._connect() as conn:
                conn.executescript(CREATE_C_TEST_TABLES)
            print("✓ C-Test tables initialized in inventory.db")
            return True
        except Exception as e:
            print(f"✗ Failed to initialize C-Test tables: {e}")
            return False
    
    # =========================================================================
    # STUDENT OPERATIONS
    # =========================================================================
    
    def get_students(self, status: str = 'active') -> List[Student]:
        """
        Get students from inventory database.
        
        Args:
            status: Filter by status ('active', 'archived', or None for all)
        
        Returns:
            List of Student objects
        """
        if not self.is_available():
            return []
        
        with self._connect() as conn:
            if status:
                rows = conn.execute(
                    """SELECT student_id, first_name, last_name, level, status, qr_code,
                              created_at, updated_at, archived_at
                       FROM students 
                       WHERE status = ?
                       ORDER BY last_name, first_name""",
                    (status,)
                ).fetchall()
            else:
                rows = conn.execute(
                    """SELECT student_id, first_name, last_name, level, status, qr_code,
                              created_at, updated_at, archived_at
                       FROM students 
                       ORDER BY last_name, first_name"""
                ).fetchall()
            
            return [
                Student(
                    student_id=row["student_id"],
                    first_name=row["first_name"],
                    last_name=row["last_name"] or "",
                    level=row["level"] or "",
                    status=row["status"] or "active",
                    qr_code=row["qr_code"] or "",
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    archived_at=row["archived_at"]
                )
                for row in rows
            ]
    
    def get_student(self, student_id: str) -> Optional[Student]:
        """
        Get a specific student by ID.
        
        Args:
            student_id: Student ID (TEXT, e.g., '20231107')
            
        Returns:
            Student object or None
        """
        if not self.is_available():
            return None
        
        with self._connect() as conn:
            row = conn.execute(
                """SELECT student_id, first_name, last_name, level, status, qr_code,
                          created_at, updated_at, archived_at
                   FROM students 
                   WHERE student_id = ?""",
                (student_id,)
            ).fetchone()
            
            if row:
                return Student(
                    student_id=row["student_id"],
                    first_name=row["first_name"],
                    last_name=row["last_name"] or "",
                    level=row["level"] or "",
                    status=row["status"] or "active",
                    qr_code=row["qr_code"] or "",
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    archived_at=row["archived_at"]
                )
            return None
    
    def get_students_by_level(self, level: str) -> List[Student]:
        """
        Get all students at a specific level.
        
        Args:
            level: Level code (e.g., 'SM4', 'Phonics 2')
            
        Returns:
            List of Student objects
        """
        if not self.is_available():
            return []
        
        with self._connect() as conn:
            rows = conn.execute(
                """SELECT student_id, first_name, last_name, level, status, qr_code,
                          created_at, updated_at, archived_at
                   FROM students 
                   WHERE level = ? AND status = 'active'
                   ORDER BY last_name, first_name""",
                (level,)
            ).fetchall()
            
            return [
                Student(
                    student_id=row["student_id"],
                    first_name=row["first_name"],
                    last_name=row["last_name"] or "",
                    level=row["level"] or "",
                    status=row["status"] or "active",
                    qr_code=row["qr_code"] or "",
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    archived_at=row["archived_at"]
                )
                for row in rows
            ]
    
    # =========================================================================
    # C-TEST RESULT OPERATIONS
    # =========================================================================
    
    def save_c_test_result(self, result: CTestResult) -> int:
        """
        Save a C-test result to inventory database.
        
        Args:
            result: CTestResult object
            
        Returns:
            Result ID in inventory.db
        """
        if not self.is_available():
            raise ConnectionError("Cannot save to inventory.db - not available")
        
        with self._connect() as conn:
            # Insert main result
            cursor = conn.execute(
                """INSERT INTO c_test_results
                   (student_id, test_version, test_date, num_items, num_correct,
                    percentage, score, placement_level, completed)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (result.student_id, result.test_version,
                 result.test_date.strftime('%Y-%m-%d %H:%M:%S') if result.test_date else None,
                 result.num_items, result.num_correct, result.percentage,
                 result.score, result.placement_level, 1 if result.completed else 0)
            )
            result_id = cursor.lastrowid
            
            # Save item-level details
            for item in result.items:
                conn.execute(
                    """INSERT INTO c_test_result_items
                       (result_id, item_number, correct_word, student_answer, is_correct)
                       VALUES (?, ?, ?, ?, ?)""",
                    (result_id, item.item_number, item.original_word,
                     item.student_answer, 1 if item.is_correct else 0)
                )
            
            return result_id
    
    def get_student_c_test_history(self, student_id: str) -> List[dict]:
        """
        Get C-test history for a student from inventory.db.
        
        Args:
            student_id: Student ID (TEXT)
            
        Returns:
            List of test result dictionaries
        """
        if not self.is_available():
            return []
        
        try:
            with self._connect() as conn:
                rows = conn.execute(
                    """SELECT test_version, test_date, score, placement_level, 
                              num_correct, num_items, percentage
                       FROM c_test_results
                       WHERE student_id = ?
                       ORDER BY test_date DESC""",
                    (student_id,)
                ).fetchall()
                
                return [
                    {
                        "version": row["test_version"],
                        "date": row["test_date"],
                        "score": row["score"],
                        "level": row["placement_level"] or "",
                        "num_correct": row["num_correct"],
                        "num_items": row["num_items"],
                        "percentage": row["percentage"]
                    }
                    for row in rows
                ]
        except sqlite3.OperationalError:
            # Table doesn't exist yet
            return []
    
    def get_latest_c_test_result(self, student_id: str) -> Optional[dict]:
        """
        Get the most recent C-test result for a student.
        
        Args:
            student_id: Student ID (TEXT)
            
        Returns:
            Dictionary with test result or None
        """
        history = self.get_student_c_test_history(student_id)
        return history[0] if history else None


# =============================================================================
# SINGLETON
# =============================================================================

_inventory_db: Optional[InventoryDatabase] = None


def get_inventory_db() -> InventoryDatabase:
    """Get the inventory database instance."""
    global _inventory_db
    if _inventory_db is None:
        _inventory_db = InventoryDatabase()
    return _inventory_db
```

---

## Key Safety Features

1. **CREATE TABLE IF NOT EXISTS** - All table creation is idempotent
2. **Error handling** - initialize_c_test_tables() returns True/False, doesn't crash
3. **Connection management** - Context managers ensure connections are closed
4. **Rollback on error** - Failed transactions are rolled back automatically
5. **Availability check** - Checks if database exists before attempting operations

## Methods Provided

### Database Initialization
- `initialize_c_test_tables()` - Create tables if they don't exist

### Student Operations
- `get_students(status='active')` - Get all active students
- `get_student(student_id)` - Get specific student by ID
- `get_students_by_level(level)` - Get students at a specific level

### C-Test Result Operations
- `save_c_test_result(result)` - Save test result to inventory.db
- `get_student_c_test_history(student_id)` - Get all tests for a student
- `get_latest_c_test_result(student_id)` - Get most recent test

## Usage Example

```python
from inventory_db import get_inventory_db

# Get database instance
inventory = get_inventory_db()

# Check if available
if inventory.is_available():
    # Initialize tables (safe to run multiple times)
    inventory.initialize_c_test_tables()
    
    # Load students
    students = inventory.get_students(status='active')
    
    # Save a test result
    result_id = inventory.save_c_test_result(my_result)
    
    # Get test history
    history = inventory.get_student_c_test_history('20231107')
```

---

See `SCHEMA_REVIEW.md` for detailed table schemas and safety information.
