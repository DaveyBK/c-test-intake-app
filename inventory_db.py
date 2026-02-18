"""
Inventory database integration for C-Test Intake App.

This module provides functions to read from and write to the shared
inventory.db database used by the Zone B teacher assistant portal.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import List, Optional, Generator

from models import Student, CTestResult


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
    
    # =========================================================================
    # STUDENT OPERATIONS
    # =========================================================================
    
    def get_students(self) -> List[Student]:
        """
        Get all students from inventory database.
        
        Returns:
            List of Student objects
        """
        if not self.is_available():
            return []
        
        with self._connect() as conn:
            # TODO: Update this query once you provide the actual schema
            rows = conn.execute(
                """SELECT student_id, first_name, last_name, email, current_level
                   FROM students 
                   ORDER BY last_name, first_name"""
            ).fetchall()
            
            return [
                Student(
                    id=row["student_id"],
                    first_name=row["first_name"],
                    last_name=row["last_name"],
                    email=row.get("email", ""),
                    current_level=row.get("current_level", "")
                )
                for row in rows
            ]
    
    def get_student(self, student_id: int) -> Optional[Student]:
        """
        Get a specific student by ID.
        
        Args:
            student_id: Student ID
            
        Returns:
            Student object or None
        """
        if not self.is_available():
            return None
        
        with self._connect() as conn:
            # TODO: Update this query once you provide the actual schema
            row = conn.execute(
                """SELECT student_id, first_name, last_name, email, current_level
                   FROM students 
                   WHERE student_id = ?""",
                (student_id,)
            ).fetchone()
            
            if row:
                return Student(
                    id=row["student_id"],
                    first_name=row["first_name"],
                    last_name=row["last_name"],
                    email=row.get("email", ""),
                    current_level=row.get("current_level", "")
                )
            return None
    
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
            # TODO: Update this schema once you provide the actual table structure
            # This is a placeholder based on typical assessment tracking
            
            cursor = conn.execute(
                """INSERT INTO c_test_results
                   (student_id, test_version, test_date, num_items, num_correct,
                    percentage, score, placement_level, completed)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (result.student_id, result.test_version,
                 result.test_date.isoformat() if result.test_date else None,
                 result.num_items, result.num_correct, result.percentage,
                 result.score, result.placement_level, result.completed)
            )
            result_id = cursor.lastrowid
            
            # Save item-level details if table exists
            try:
                for item in result.items:
                    conn.execute(
                        """INSERT INTO c_test_result_items
                           (result_id, item_number, correct_word, student_answer, is_correct)
                           VALUES (?, ?, ?, ?, ?)""",
                        (result_id, item.item_number, item.original_word,
                         item.student_answer, item.is_correct)
                    )
            except sqlite3.OperationalError:
                # Table doesn't exist - that's okay, just save summary
                pass
            
            return result_id
    
    def get_student_c_test_history(self, student_id: int) -> List[dict]:
        """
        Get C-test history for a student from inventory.db.
        
        Args:
            student_id: Student ID
            
        Returns:
            List of test result dictionaries
        """
        if not self.is_available():
            return []
        
        with self._connect() as conn:
            try:
                rows = conn.execute(
                    """SELECT test_version, test_date, score, placement_level
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
                        "level": row.get("placement_level", "")
                    }
                    for row in rows
                ]
            except sqlite3.OperationalError:
                # Table doesn't exist yet
                return []


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
