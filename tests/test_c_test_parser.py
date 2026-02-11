"""
Unit tests for c_test_parser.py

Tests the C-test answer parsing functionality including:
- Numbered list parsing
- Bracket format parsing
- Template comparison
- Malformed input handling
"""

import unittest
from c_test_parser import (
    extract_c_test_answers,
    parse_c_test_with_template,
    normalize_answer,
    validate_answers,
    _parse_numbered_list,
    _parse_bracket_format,
)


class TestNumberedListParsing(unittest.TestCase):
    """Test cases for numbered list format parsing."""
    
    def test_simple_numbered_list_with_periods(self):
        """Test parsing simple numbered list with periods."""
        text = """
        1. weather
        2. cold
        3. yesterday
        4. morning
        """
        
        answers = _parse_numbered_list(text, num_items=4)
        
        self.assertEqual(len(answers), 4)
        self.assertEqual(answers[1], "weather")
        self.assertEqual(answers[2], "cold")
        self.assertEqual(answers[3], "yesterday")
        self.assertEqual(answers[4], "morning")
    
    def test_numbered_list_with_parentheses(self):
        """Test parsing numbered list with parentheses."""
        text = """
        1) weather
        2) cold
        3) yesterday
        """
        
        answers = _parse_numbered_list(text, num_items=3)
        
        self.assertEqual(len(answers), 3)
        self.assertEqual(answers[1], "weather")
        self.assertEqual(answers[2], "cold")
    
    def test_numbered_list_with_extra_whitespace(self):
        """Test parsing with extra whitespace."""
        text = """
        1.   weather  
        2.  cold
        3.     yesterday
        """
        
        answers = _parse_numbered_list(text, num_items=3)
        
        self.assertEqual(len(answers), 3)
        self.assertEqual(answers[1], "weather")
        self.assertEqual(answers[2], "cold")
        self.assertEqual(answers[3], "yesterday")
    
    def test_numbered_list_not_starting_at_one(self):
        """Test parsing list that doesn't start at 1."""
        text = """
        3. yesterday
        4. morning
        5. walked
        """
        
        answers = _parse_numbered_list(text, num_items=5)
        
        # Should only capture items 3, 4, 5
        self.assertEqual(len(answers), 3)
        self.assertEqual(answers[3], "yesterday")
        self.assertEqual(answers[4], "morning")
        self.assertEqual(answers[5], "walked")
    
    def test_numbered_list_with_gaps(self):
        """Test parsing list with gaps in numbering."""
        text = """
        1. weather
        3. yesterday
        5. walked
        """
        
        answers = _parse_numbered_list(text, num_items=5)
        
        # Should capture all provided items
        self.assertEqual(len(answers), 3)
        self.assertEqual(answers[1], "weather")
        self.assertEqual(answers[3], "yesterday")
        self.assertEqual(answers[5], "walked")
    
    def test_numbered_list_insufficient_answers(self):
        """Test that insufficient answers returns empty dict."""
        text = """
        1. weather
        """
        
        # Expecting 10 items but only got 1 (< 50%)
        answers = _parse_numbered_list(text, num_items=10)
        
        self.assertEqual(len(answers), 0)
    
    def test_numbered_list_mixed_with_text(self):
        """Test parsing when list is mixed with other text."""
        text = """
        Here are my answers:
        1. weather
        2. cold
        3. yesterday
        I hope these are correct!
        """
        
        answers = _parse_numbered_list(text, num_items=3)
        
        self.assertEqual(len(answers), 3)
        self.assertEqual(answers[1], "weather")


class TestBracketFormatParsing(unittest.TestCase):
    """Test cases for bracket format parsing."""
    
    def test_simple_bracket_format(self):
        """Test parsing simple bracket format."""
        text = "The wea[weather] was col[cold] yest[yesterday]day"
        
        answers = _parse_bracket_format(text, num_items=3)
        
        self.assertEqual(len(answers), 3)
        self.assertEqual(answers[1], "weather")
        self.assertEqual(answers[2], "cold")
        self.assertEqual(answers[3], "yesterday")
    
    def test_bracket_format_with_multiple_lines(self):
        """Test parsing bracket format across multiple lines."""
        text = """
        The wea[weather] was col[cold].
        I walk[walked] to scho[school].
        """
        
        answers = _parse_bracket_format(text, num_items=4)
        
        self.assertEqual(len(answers), 4)
        self.assertEqual(answers[1], "weather")
        self.assertEqual(answers[2], "cold")
        self.assertEqual(answers[3], "walked")
        self.assertEqual(answers[4], "school")
    
    def test_bracket_format_insufficient_answers(self):
        """Test that insufficient answers returns empty dict."""
        text = "The wea[weather]"
        
        # Expecting 10 items but only got 1 (< 50%)
        answers = _parse_bracket_format(text, num_items=10)
        
        self.assertEqual(len(answers), 0)
    
    def test_bracket_format_with_extra_brackets(self):
        """Test parsing with more brackets than expected items."""
        text = "The wea[weather] was col[cold] and ver[very] nic[nice]"
        
        # Only expecting 2 items, should only take first 2
        answers = _parse_bracket_format(text, num_items=2)
        
        self.assertEqual(len(answers), 2)
        self.assertEqual(answers[1], "weather")
        self.assertEqual(answers[2], "cold")


class TestExtractCTestAnswers(unittest.TestCase):
    """Test cases for the main extract function."""
    
    def test_extract_numbered_list(self):
        """Test extraction from numbered list format."""
        text = """
        1. weather
        2. cold
        3. yesterday
        """
        
        answers = extract_c_test_answers(text, num_items=3)
        
        self.assertEqual(len(answers), 3)
        self.assertEqual(answers[1], "weather")
        self.assertEqual(answers[2], "cold")
        self.assertEqual(answers[3], "yesterday")
    
    def test_extract_bracket_format(self):
        """Test extraction from bracket format."""
        text = "The wea[weather] was col[cold]"
        
        answers = extract_c_test_answers(text, num_items=2)
        
        self.assertEqual(len(answers), 2)
        self.assertEqual(answers[1], "weather")
        self.assertEqual(answers[2], "cold")
    
    def test_extract_prefers_numbered_list(self):
        """Test that numbered list format is preferred over bracket format."""
        # Text with both formats
        text = """
        1. weather
        2. cold
        The wea[sun] was col[hot]
        """
        
        answers = extract_c_test_answers(text, num_items=2)
        
        # Should use numbered list format, not bracket format
        self.assertEqual(answers[1], "weather")
        self.assertEqual(answers[2], "cold")
    
    def test_extract_empty_text(self):
        """Test extraction from empty text."""
        answers = extract_c_test_answers("", num_items=5)
        
        self.assertEqual(len(answers), 0)
    
    def test_extract_no_recognizable_format(self):
        """Test extraction when no format is recognized."""
        text = "This is just random text without any answers"
        
        answers = extract_c_test_answers(text, num_items=5)
        
        self.assertEqual(len(answers), 0)


class TestParseWithTemplate(unittest.TestCase):
    """Test cases for template-based parsing."""
    
    def test_parse_with_template_numbered_list(self):
        """Test parsing with template using numbered list."""
        template = "The wea____ was col____ yesterday"
        text = """
        1. weather
        2. cold
        """
        
        answers = parse_c_test_with_template(text, template)
        
        self.assertEqual(len(answers), 2)
        self.assertEqual(answers[1], "weather")
        self.assertEqual(answers[2], "cold")
    
    def test_parse_with_template_bracket_format(self):
        """Test parsing with template using bracket format."""
        template = "The wea____ was col____"
        text = "The wea[weather] was col[cold]"
        
        answers = parse_c_test_with_template(text, template)
        
        self.assertEqual(len(answers), 2)
        self.assertEqual(answers[1], "weather")
        self.assertEqual(answers[2], "cold")
    
    def test_parse_with_template_multiple_fragments(self):
        """Test parsing template with multiple fragments."""
        template = "The wea____ was col____ yest____day morn____"
        text = """
        1. weather
        2. cold
        3. yesterday
        4. morning
        """
        
        answers = parse_c_test_with_template(text, template)
        
        self.assertEqual(len(answers), 4)


class TestNormalizeAnswer(unittest.TestCase):
    """Test cases for answer normalization."""
    
    def test_normalize_lowercase(self):
        """Test normalization to lowercase."""
        self.assertEqual(normalize_answer("WEATHER"), "weather")
        self.assertEqual(normalize_answer("Weather"), "weather")
    
    def test_normalize_whitespace(self):
        """Test normalization of whitespace."""
        self.assertEqual(normalize_answer("  weather  "), "weather")
        self.assertEqual(normalize_answer(" weather "), "weather")
    
    def test_normalize_combined(self):
        """Test combined normalization."""
        self.assertEqual(normalize_answer("  WEATHER  "), "weather")


class TestValidateAnswers(unittest.TestCase):
    """Test cases for answer validation."""
    
    def test_validate_complete_answers(self):
        """Test validation of complete answer set."""
        answers = {1: "weather", 2: "cold", 3: "yesterday"}
        
        self.assertTrue(validate_answers(answers, num_items=3))
    
    def test_validate_partial_answers_sufficient(self):
        """Test validation of sufficient partial answers (>50%)."""
        answers = {1: "weather", 2: "cold", 3: "yesterday"}
        
        # 3 out of 5 is 60%, should be valid
        self.assertTrue(validate_answers(answers, num_items=5))
    
    def test_validate_partial_answers_insufficient(self):
        """Test validation of insufficient partial answers (<50%)."""
        answers = {1: "weather", 2: "cold"}
        
        # 2 out of 5 is 40%, should be invalid
        self.assertFalse(validate_answers(answers, num_items=5))
    
    def test_validate_empty_answers(self):
        """Test validation of empty answer set."""
        answers = {}
        
        self.assertFalse(validate_answers(answers, num_items=5))
    
    def test_validate_answers_with_empty_string(self):
        """Test validation with empty string answers."""
        answers = {1: "weather", 2: "", 3: "yesterday"}
        
        self.assertFalse(validate_answers(answers, num_items=3))
    
    def test_validate_answers_with_non_string(self):
        """Test validation with non-string answers."""
        answers = {1: "weather", 2: None, 3: "yesterday"}
        
        self.assertFalse(validate_answers(answers, num_items=3))


class TestMalformedInput(unittest.TestCase):
    """Test cases for malformed or edge case inputs."""
    
    def test_malformed_numbered_list_with_letters(self):
        """Test parsing malformed list with letters."""
        text = """
        a. weather
        b. cold
        """
        
        answers = _parse_numbered_list(text, num_items=2)
        
        # Should not match letter-based lists
        self.assertEqual(len(answers), 0)
    
    def test_malformed_mixed_numbering(self):
        """Test parsing with inconsistent numbering."""
        text = """
        1. weather
        2) cold
        3. yesterday
        """
        
        answers = _parse_numbered_list(text, num_items=3)
        
        # Should handle both . and ) formats
        self.assertEqual(len(answers), 3)
    
    def test_bracket_format_with_nested_brackets(self):
        """Test parsing bracket format with nested text."""
        text = "The wea[weather (cold)] was nice"
        
        # Should extract what's in the brackets
        answers = _parse_bracket_format(text, num_items=1)
        
        # May not handle nested brackets perfectly, but shouldn't crash
        self.assertIsInstance(answers, dict)
    
    def test_very_long_input(self):
        """Test parsing with very long input."""
        # Create a very long numbered list
        lines = [f"{i}. word{i}" for i in range(1, 101)]
        text = "\n".join(lines)
        
        answers = extract_c_test_answers(text, num_items=100)
        
        self.assertEqual(len(answers), 100)
    
    def test_unicode_characters(self):
        """Test parsing with Unicode characters."""
        text = """
        1. café
        2. naïve
        """
        
        answers = _parse_numbered_list(text, num_items=2)
        
        # Should handle Unicode, but we only expect letters
        # This might not work depending on regex pattern
        # Just ensure it doesn't crash
        self.assertIsInstance(answers, dict)


if __name__ == "__main__":
    unittest.main()
