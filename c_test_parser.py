"""
C-test answer parser for C-test Intake App.

Extracts student answers from various submission formats.
"""

import re
from typing import Dict


def extract_c_test_answers(text: str, num_items: int) -> Dict[int, str]:
    """
    Extract C-test answers from student submission text.
    
    Supports multiple formats:
    - Numbered list: "1. weather" or "1) weather" or "1. weather\n2. cold"
    - Bracket format: "The wea[weather] was col[cold]"
    
    Args:
        text: The submission text
        num_items: Expected number of items
    
    Returns:
        Dictionary mapping item numbers to answers
    """
    answers = {}
    
    # Try numbered list format first (most common)
    numbered_answers = _parse_numbered_list(text, num_items)
    if numbered_answers:
        return numbered_answers
    
    # Try bracket format
    bracket_answers = _parse_bracket_format(text, num_items)
    if bracket_answers:
        return bracket_answers
    
    return answers


def _parse_numbered_list(text: str, num_items: int) -> Dict[int, str]:
    """
    Parse numbered list format.
    
    Examples:
        1. weather
        2. cold
        
        1) weather
        2) cold
    
    Args:
        text: The submission text
        num_items: Expected number of items
    
    Returns:
        Dictionary of answers or empty dict if not this format
    """
    answers = {}
    
    # Pattern matches: "1. word" or "1) word" or "1 word"
    # Captures number and word
    pattern = r'^\s*(\d+)[\.\)]\s*([a-zA-Z]+)'
    
    lines = text.split('\n')
    for line in lines:
        match = re.match(pattern, line.strip())
        if match:
            item_num = int(match.group(1))
            answer = match.group(2).strip()
            if 1 <= item_num <= num_items:
                answers[item_num] = answer
    
    # Only return if we found a reasonable number of answers
    if len(answers) >= num_items / 2:  # At least half
        return answers
    
    return {}


def _parse_bracket_format(text: str, num_items: int) -> Dict[int, str]:
    """
    Parse bracket format.
    
    Example:
        The wea[weather] was col[cold] yest[yesterday]
    
    Args:
        text: The submission text
        num_items: Expected number of items
    
    Returns:
        Dictionary of answers or empty dict if not this format
    """
    answers = {}
    
    # Pattern matches: [word] or (word)
    pattern = r'\[([a-zA-Z]+)\]'
    
    matches = re.findall(pattern, text)
    
    for i, match in enumerate(matches, start=1):
        if i <= num_items:
            answers[i] = match.strip()
    
    # Only return if we found a reasonable number of answers
    if len(answers) >= num_items / 2:  # At least half
        return answers
    
    return {}


def parse_c_test_with_template(text: str, template: str) -> Dict[int, str]:
    """
    Parse C-test answers by comparing with a template.
    
    The template contains the text with fragments marked, like:
    "The wea____ was col____ yesterday"
    
    The student submission should have completions in brackets or as numbered list.
    
    Args:
        text: Student submission text
        template: Template text with fragments
    
    Returns:
        Dictionary mapping item numbers to answers
    """
    # First try to count fragments in template
    fragment_pattern = r'___+'
    fragments = re.findall(fragment_pattern, template)
    num_items = len(fragments)
    
    # Try to extract answers
    return extract_c_test_answers(text, num_items)


def normalize_answer(answer: str) -> str:
    """
    Normalize an answer for comparison.
    
    Args:
        answer: The answer string
    
    Returns:
        Normalized answer
    """
    return answer.strip().lower()


def validate_answers(answers: Dict[int, str], num_items: int) -> bool:
    """
    Validate that we have a complete set of answers.
    
    Args:
        answers: Dictionary of answers
        num_items: Expected number of items
    
    Returns:
        True if answers are complete enough (at least 50%)
    """
    if not answers:
        return False
    
    # Check we have at least half the expected answers
    if len(answers) < num_items / 2:
        return False
    
    # Check all answers are non-empty strings
    for answer in answers.values():
        if not answer or not isinstance(answer, str):
            return False
    
    return True
