"""
C-test grading module for C-test Intake App.

Provides proper C-test grading based on exact matches with answer keys.
"""

from typing import Dict, List, Tuple
from models import CTestItem

# Spelling variants (British/American)
SPELLING_VARIANTS = {
    "colour": "color",
    "honour": "honor",
    "favour": "favor",
    "labour": "labor",
    "neighbour": "neighbor",
    "behaviour": "behavior",
    "flavour": "flavor",
    "harbour": "harbor",
    "humour": "humor",
    "rumour": "rumor",
    "centre": "center",
    "metre": "meter",
    "theatre": "theater",
    "fibre": "fiber",
    "litre": "liter",
    "defence": "defense",
    "licence": "license",
    "offence": "offense",
    "pretence": "pretense",
    "organise": "organize",
    "realise": "realize",
    "recognise": "recognize",
    "analyse": "analyze",
    "paralyse": "paralyze",
    "travelled": "traveled",
    "travelling": "traveling",
    "cancelled": "canceled",
    "cancelling": "canceling",
    "jewellery": "jewelry",
    "grey": "gray",
    "fulfil": "fulfill",
}


class CTestGrader:
    """Grades C-test submissions based on exact match with answer key."""
    
    def __init__(self, answer_key: Dict[int, str], accept_variants: bool = True):
        """
        Initialize the C-test grader.
        
        Args:
            answer_key: Dictionary mapping item numbers to correct answers
            accept_variants: If True, accept British/American spelling variants
        """
        self.answer_key = answer_key
        self.accept_variants = accept_variants
    
    def grade_submission(self, student_answers: Dict[int, str]) -> Tuple[int, List[CTestItem], str]:
        """
        Grade a C-test submission.
        
        Args:
            student_answers: Dictionary mapping item numbers to student answers
        
        Returns:
            Tuple of (score, items, feedback) where:
            - score is 0-5 based on percentage correct
            - items is a list of CTestItem objects with grading details
            - feedback is a string with detailed grading explanation
        """
        items = []
        num_correct = 0
        
        # Grade each item
        for item_num, correct_answer in self.answer_key.items():
            student_answer = student_answers.get(item_num, "")
            is_correct = self._check_answer(student_answer, correct_answer)
            
            if is_correct:
                num_correct += 1
            
            # Create item result
            item = CTestItem(
                item_number=item_num,
                original_word=correct_answer,
                fragment_shown="",  # Not needed for grading
                student_answer=student_answer,
                is_correct=is_correct
            )
            items.append(item)
        
        # Calculate percentage and score
        total_items = len(self.answer_key)
        percentage = (num_correct / total_items * 100) if total_items > 0 else 0
        score = self._percentage_to_score(percentage)
        
        # Generate feedback
        feedback = self._generate_feedback(num_correct, total_items, percentage, score, items)
        
        return score, items, feedback
    
    def _check_answer(self, student_answer: str, correct_answer: str) -> bool:
        """
        Check if a student answer matches the correct answer.
        
        Args:
            student_answer: The student's answer
            correct_answer: The correct answer
        
        Returns:
            True if the answer is correct, False otherwise
        """
        # Normalize both answers
        student = student_answer.strip().lower()
        correct = correct_answer.strip().lower()
        
        # Direct match
        if student == correct:
            return True
        
        # Check spelling variants if enabled
        if self.accept_variants:
            # Check if student used variant of correct answer
            if student in SPELLING_VARIANTS and SPELLING_VARIANTS[student] == correct:
                return True
            if correct in SPELLING_VARIANTS and SPELLING_VARIANTS[correct] == student:
                return True
            
            # Reverse check - if correct answer is a variant key
            for variant, standard in SPELLING_VARIANTS.items():
                if correct == variant and student == standard:
                    return True
                if correct == standard and student == variant:
                    return True
        
        return False
    
    def _percentage_to_score(self, percentage: float) -> int:
        """
        Convert percentage to 0-5 score scale.
        
        Args:
            percentage: Percentage correct (0-100)
        
        Returns:
            Score from 0 to 5
        """
        if percentage >= 90:
            return 5
        elif percentage >= 75:
            return 4
        elif percentage >= 60:
            return 3
        elif percentage >= 45:
            return 2
        elif percentage >= 30:
            return 1
        else:
            return 0
    
    def _generate_feedback(self, num_correct: int, total_items: int, 
                          percentage: float, score: int, items: List[CTestItem]) -> str:
        """
        Generate detailed feedback for the grading.
        
        Args:
            num_correct: Number of correct answers
            total_items: Total number of items
            percentage: Percentage correct
            score: Final score (0-5)
            items: List of graded items
        
        Returns:
            Formatted feedback string
        """
        lines = [
            f"C-test Grading Results",
            f"=" * 50,
            f"Correct answers: {num_correct}/{total_items}",
            f"Percentage: {percentage:.1f}%",
            f"Score: {score}/5",
            f"",
            f"Item-by-Item Results:",
            f"-" * 50,
        ]
        
        # Add individual item results
        for item in items:
            status = "✓" if item.is_correct else "✗"
            if item.is_correct:
                lines.append(f"{status} Item {item.item_number}: '{item.student_answer}' - Correct")
            else:
                lines.append(f"{status} Item {item.item_number}: '{item.student_answer}' - Expected: '{item.original_word}'")
        
        return "\n".join(lines)


def grade_c_test(answer_key: Dict[int, str], student_answers: Dict[int, str], 
                 accept_variants: bool = True) -> Tuple[int, List[CTestItem], str]:
    """
    Convenience function to grade a C-test submission.
    
    Args:
        answer_key: Dictionary mapping item numbers to correct answers
        student_answers: Dictionary mapping item numbers to student answers
        accept_variants: If True, accept British/American spelling variants
    
    Returns:
        Tuple of (score, items, feedback)
    """
    grader = CTestGrader(answer_key, accept_variants)
    return grader.grade_submission(student_answers)
