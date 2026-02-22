"""
Data models for C-Test Intake App.

Dataclasses for C-test specific data and student information.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class Student:
    """A student in the system (matches inventory.db schema)."""
    student_id: str = ""  # TEXT primary key (e.g., '20231107')
    first_name: str = ""
    last_name: str = ""
    level: str = ""  # e.g., 'SM4', 'Phonics 2'
    status: str = "active"  # 'active' or 'archived'
    qr_code: str = ""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    archived_at: Optional[str] = None
    
    @property
    def full_name(self) -> str:
        """Get full name."""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def id(self) -> str:
        """Alias for student_id for compatibility."""
        return self.student_id


@dataclass
class CTestItem:
    """A single C-test completion item."""
    item_number: int
    original_word: str
    fragment_shown: str
    student_answer: str
    is_correct: bool = False


@dataclass
class CTestResult:
    """A complete C-test result for a student."""
    id: Optional[int] = None
    student_id: str = ""  # TEXT to match inventory.db schema
    test_version: str = ""
    test_date: Optional[datetime] = None
    num_items: int = 0
    num_correct: int = 0
    percentage: float = 0.0
    score: int = 0  # 0-5 scale
    placement_level: str = ""
    items: List[CTestItem] = field(default_factory=list)
    completed: bool = True
    synced_to_inventory: bool = False
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.test_date is None:
            self.test_date = datetime.now()
