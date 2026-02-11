"""
Data models for C-test Intake App.

Dataclasses for homework submissions, scores, and C-test specific data.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class Homework:
    """A homework submission."""
    id: Optional[int] = None
    hw_number: int = 0
    file_name: str = ""
    file_path: str = ""
    extracted_text: str = ""
    status: str = "pending"  # pending, scored, confirmed
    submitted_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    # Scores (0-5 each)
    reading_score: Optional[int] = None
    writing_score: Optional[int] = None
    listening_score: Optional[int] = None  # Manual entry
    
    # Teacher feedback
    comment: str = ""
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.submitted_at is None:
            self.submitted_at = datetime.now()


@dataclass
class GeneratedHomework:
    """A generated homework assignment."""
    id: Optional[int] = None
    hw_number: int = 0
    reading_file: str = ""
    writing_file: str = ""
    reading_text: str = ""
    writing_prompts: str = ""
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class CTestItem:
    """A single C-test completion item."""
    item_number: int
    original_word: str
    fragment_shown: str
    student_answer: str
    is_correct: bool = False


@dataclass
class CTestSubmission:
    """A complete C-test submission."""
    homework_id: int
    test_version: str
    items: List[CTestItem]
    num_correct: int
    percentage: float
    score: int
