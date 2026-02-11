"""
Unit tests for c_test_grader.py

Tests the C-test grading functionality including:
- Exact match grading
- Spelling variants
- Percentage calculation
- Score conversion
- Edge cases
"""

import unittest
from c_test_grader import CTestGrader, grade_c_test
from models import CTestItem


class TestCTestGrader(unittest.TestCase):
    """Test cases for CTestGrader class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.answer_key = {
            1: "weather",
            2: "cold",
            3: "yesterday",
            4: "morning",
            5: "walked",
            6: "school",
            7: "because",
            8: "late",
        }
        self.grader = CTestGrader(self.answer_key, accept_variants=True)
    
    def test_perfect_score(self):
        """Test grading with all correct answers."""
        student_answers = {
            1: "weather",
            2: "cold",
            3: "yesterday",
            4: "morning",
            5: "walked",
            6: "school",
            7: "because",
            8: "late",
        }
        
        score, items, feedback = self.grader.grade_submission(student_answers)
        
        self.assertEqual(score, 5)
        self.assertEqual(len(items), 8)
        self.assertTrue(all(item.is_correct for item in items))
    
    def test_zero_score(self):
        """Test grading with all incorrect answers."""
        student_answers = {
            1: "wrong",
            2: "wrong",
            3: "wrong",
            4: "wrong",
            5: "wrong",
            6: "wrong",
            7: "wrong",
            8: "wrong",
        }
        
        score, items, feedback = self.grader.grade_submission(student_answers)
        
        self.assertEqual(score, 0)
        self.assertEqual(len(items), 8)
        self.assertTrue(all(not item.is_correct for item in items))
    
    def test_partial_score(self):
        """Test grading with partial correct answers."""
        student_answers = {
            1: "weather",
            2: "cold",
            3: "yesterday",
            4: "morning",
            5: "walked",
            6: "school",
            7: "wrong",  # Incorrect
            8: "wrong",  # Incorrect
        }
        
        score, items, feedback = self.grader.grade_submission(student_answers)
        
        # 6/8 = 75% -> score 4
        self.assertEqual(score, 4)
        self.assertEqual(sum(1 for item in items if item.is_correct), 6)
    
    def test_case_insensitive(self):
        """Test that grading is case-insensitive."""
        student_answers = {
            1: "WEATHER",
            2: "Cold",
            3: "YeStErDaY",
            4: "morning",
            5: "walked",
            6: "school",
            7: "because",
            8: "late",
        }
        
        score, items, feedback = self.grader.grade_submission(student_answers)
        
        self.assertEqual(score, 5)
        self.assertTrue(all(item.is_correct for item in items))
    
    def test_whitespace_handling(self):
        """Test that extra whitespace is handled correctly."""
        student_answers = {
            1: "  weather  ",
            2: " cold ",
            3: "yesterday",
            4: "morning",
            5: "walked",
            6: "school",
            7: "because",
            8: "late",
        }
        
        score, items, feedback = self.grader.grade_submission(student_answers)
        
        self.assertEqual(score, 5)
        self.assertTrue(all(item.is_correct for item in items))
    
    def test_spelling_variants_british_to_american(self):
        """Test British to American spelling variant acceptance."""
        answer_key = {
            1: "color",  # American
            2: "center", # American
        }
        grader = CTestGrader(answer_key, accept_variants=True)
        
        student_answers = {
            1: "colour",  # British
            2: "centre",  # British
        }
        
        score, items, feedback = grader.grade_submission(student_answers)
        
        self.assertEqual(score, 5)  # 100% = score 5
        self.assertTrue(all(item.is_correct for item in items))
    
    def test_spelling_variants_american_to_british(self):
        """Test American to British spelling variant acceptance."""
        answer_key = {
            1: "colour",  # British
            2: "centre",  # British
        }
        grader = CTestGrader(answer_key, accept_variants=True)
        
        student_answers = {
            1: "color",   # American
            2: "center",  # American
        }
        
        score, items, feedback = grader.grade_submission(student_answers)
        
        self.assertEqual(score, 5)  # 100% = score 5
        self.assertTrue(all(item.is_correct for item in items))
    
    def test_spelling_variants_disabled(self):
        """Test that spelling variants are rejected when disabled."""
        answer_key = {
            1: "color",
            2: "center",
        }
        grader = CTestGrader(answer_key, accept_variants=False)
        
        student_answers = {
            1: "colour",  # Should be wrong when variants disabled
            2: "centre",  # Should be wrong when variants disabled
        }
        
        score, items, feedback = grader.grade_submission(student_answers)
        
        self.assertEqual(score, 0)  # 0% = score 0
        self.assertTrue(all(not item.is_correct for item in items))
    
    def test_percentage_to_score_conversion(self):
        """Test percentage to score conversion thresholds."""
        test_cases = [
            (100, 5),  # 100% -> 5
            (95, 5),   # 95% -> 5
            (90, 5),   # 90% -> 5
            (85, 4),   # 85% -> 4
            (75, 4),   # 75% -> 4
            (70, 3),   # 70% -> 3
            (60, 3),   # 60% -> 3
            (55, 2),   # 55% -> 2
            (45, 2),   # 45% -> 2
            (40, 1),   # 40% -> 1
            (30, 1),   # 30% -> 1
            (25, 0),   # 25% -> 0
            (0, 0),    # 0% -> 0
        ]
        
        for percentage, expected_score in test_cases:
            with self.subTest(percentage=percentage):
                actual_score = self.grader._percentage_to_score(percentage)
                self.assertEqual(actual_score, expected_score,
                               f"Expected {percentage}% to convert to score {expected_score}, got {actual_score}")
    
    def test_empty_submission(self):
        """Test grading with empty student answers."""
        student_answers = {}
        
        score, items, feedback = self.grader.grade_submission(student_answers)
        
        self.assertEqual(score, 0)
        self.assertEqual(len(items), 8)
        self.assertTrue(all(not item.is_correct for item in items))
        self.assertTrue(all(item.student_answer == "" for item in items))
    
    def test_partial_submission(self):
        """Test grading with some missing answers."""
        student_answers = {
            1: "weather",
            2: "cold",
            3: "yesterday",
            # 4, 5, 6, 7, 8 missing
        }
        
        score, items, feedback = self.grader.grade_submission(student_answers)
        
        # 3/8 = 37.5% -> score 1
        self.assertEqual(score, 1)
        self.assertEqual(sum(1 for item in items if item.is_correct), 3)
    
    def test_feedback_generation(self):
        """Test that feedback is generated correctly."""
        student_answers = {
            1: "weather",
            2: "cold",
            3: "wrong",
            4: "morning",
            5: "walked",
            6: "school",
            7: "because",
            8: "late",
        }
        
        score, items, feedback = self.grader.grade_submission(student_answers)
        
        self.assertIn("7/8", feedback)
        self.assertIn("87.5%", feedback)
        self.assertIn("Score: 4/5", feedback)
        self.assertIn("✓", feedback)  # Correct items
        self.assertIn("✗", feedback)  # Incorrect items
    
    def test_grade_c_test_convenience_function(self):
        """Test the convenience function grade_c_test."""
        answer_key = {1: "test", 2: "answer"}
        student_answers = {1: "test", 2: "answer"}
        
        score, items, feedback = grade_c_test(answer_key, student_answers)
        
        self.assertEqual(score, 5)
        self.assertEqual(len(items), 2)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""
    
    def test_single_item_correct(self):
        """Test with a single item that is correct."""
        answer_key = {1: "test"}
        student_answers = {1: "test"}
        
        score, items, feedback = grade_c_test(answer_key, student_answers)
        
        self.assertEqual(score, 5)
        self.assertEqual(len(items), 1)
        self.assertTrue(items[0].is_correct)
    
    def test_single_item_incorrect(self):
        """Test with a single item that is incorrect."""
        answer_key = {1: "test"}
        student_answers = {1: "wrong"}
        
        score, items, feedback = grade_c_test(answer_key, student_answers)
        
        self.assertEqual(score, 0)
        self.assertEqual(len(items), 1)
        self.assertFalse(items[0].is_correct)
    
    def test_large_number_of_items(self):
        """Test with a large number of items."""
        answer_key = {i: f"word{i}" for i in range(1, 51)}  # 50 items
        student_answers = {i: f"word{i}" for i in range(1, 51)}
        
        score, items, feedback = grade_c_test(answer_key, student_answers)
        
        self.assertEqual(score, 5)
        self.assertEqual(len(items), 50)
    
    def test_non_sequential_item_numbers(self):
        """Test with non-sequential item numbers."""
        answer_key = {1: "first", 5: "fifth", 10: "tenth"}
        student_answers = {1: "first", 5: "fifth", 10: "tenth"}
        
        score, items, feedback = grade_c_test(answer_key, student_answers)
        
        self.assertEqual(score, 5)
        self.assertEqual(len(items), 3)


if __name__ == "__main__":
    unittest.main()
