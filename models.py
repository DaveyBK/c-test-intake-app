"""
Data models for C-Test Intake App.

Dataclasses for C-test specific data and student information.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class Student:
    """A student in the system."""
    id: Optional[int] = None
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    current_level: str = ""
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    @property
    def full_name(self) -> str:
        """Get full name."""
        return f"{self.first_name} {self.last_name}".strip()


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
    student_id: int = 0
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
