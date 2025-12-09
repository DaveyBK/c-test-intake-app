"""
Simple rule-based grading for 10-Minute Reading App (V1).

Uses basic heuristics to suggest reading and writing scores.
Teacher can always adjust these manually.
"""

import re
from typing import Tuple

from config import MIN_SCORE, MAX_SCORE
from extractor import get_word_count, get_sentence_count


# =============================================================================
# SCORING HEURISTICS
# =============================================================================

# Keywords that suggest good reading comprehension
COMPREHENSION_PHRASES = [
    "the text was about",
    "the main idea",
    "according to the text",
    "the author",
    "this shows",
    "for example",
    "because",
    "therefore",
    "in conclusion",
    "i learned",
    "i think",
]

# Minimum word counts for different scores
WORD_COUNT_THRESHOLDS = {
    1: 20,   # At least 20 words for score 1
    2: 40,   # At least 40 words for score 2
    3: 60,   # At least 60 words for score 3
    4: 80,   # At least 80 words for score 4
    5: 100,  # At least 100 words for score 5
}


def grade_homework(text: str) -> Tuple[int, int]:
    """
    Grade a homework submission.
    
    Args:
        text: Extracted text from submission
    
    Returns:
        Tuple of (reading_score, writing_score) each 0-5
    """
    if not text or not text.strip():
        return (0, 0)
    
    reading_score = _calculate_reading_score(text)
    writing_score = _calculate_writing_score(text)
    
    return (reading_score, writing_score)


def _calculate_reading_score(text: str) -> int:
    """
    Calculate reading comprehension score (0-5).
    
    Based on:
    - Presence of comprehension-indicating phrases
    - Evidence of understanding main ideas
    """
    text_lower = text.lower()
    
    # Count how many comprehension phrases are present
    phrase_count = 0
    for phrase in COMPREHENSION_PHRASES:
        if phrase in text_lower:
            phrase_count += 1
    
    # Base score from phrase count
    if phrase_count >= 5:
        base_score = 5
    elif phrase_count >= 4:
        base_score = 4
    elif phrase_count >= 3:
        base_score = 3
    elif phrase_count >= 2:
        base_score = 2
    elif phrase_count >= 1:
        base_score = 1
    else:
        base_score = 0
    
    # Adjust based on length (short responses get penalized)
    word_count = get_word_count(text)
    if word_count < 30:
        base_score = max(0, base_score - 2)
    elif word_count < 50:
        base_score = max(0, base_score - 1)
    
    return _clamp(base_score)


def _calculate_writing_score(text: str) -> int:
    """
    Calculate writing quality score (0-5).
    
    Based on:
    - Word count
    - Sentence variety
    - Basic error indicators
    """
    word_count = get_word_count(text)
    sentence_count = get_sentence_count(text)
    
    # Start with score based on word count
    score = 0
    for threshold_score, threshold_words in sorted(WORD_COUNT_THRESHOLDS.items()):
        if word_count >= threshold_words:
            score = threshold_score
    
    # Bonus for sentence variety
    if sentence_count >= 5:
        score = min(5, score + 1)
    
    # Check for obvious errors (penalty)
    error_count = _count_basic_errors(text)
    if error_count >= 5:
        score = max(0, score - 2)
    elif error_count >= 3:
        score = max(0, score - 1)
    
    return _clamp(score)


def _count_basic_errors(text: str) -> int:
    """Count basic writing errors."""
    errors = 0
    
    # Missing capital at start of sentences
    sentences = re.split(r"[.!?]+\s*", text)
    for sent in sentences:
        sent = sent.strip()
        if sent and sent[0].islower():
            errors += 1
    
    # Lowercase 'i' as pronoun (not in contractions)
    if re.search(r"\bi\b(?!')", text):
        errors += 1
    
    # Multiple spaces
    if re.search(r"\s{3,}", text):
        errors += 1
    
    # No punctuation at all (if long enough)
    word_count = get_word_count(text)
    if word_count > 20 and not re.search(r"[.!?]", text):
        errors += 2
    
    return errors


def _clamp(score: int) -> int:
    """Clamp score to valid range."""
    return max(MIN_SCORE, min(MAX_SCORE, score))


def get_score_explanation(reading: int, writing: int, text: str) -> str:
    """
    Generate a brief explanation of the scores.
    
    Args:
        reading: Reading score (0-5)
        writing: Writing score (0-5)
        text: The graded text
    
    Returns:
        Explanation string
    """
    word_count = get_word_count(text)
    sentence_count = get_sentence_count(text)
    
    # Count comprehension phrases
    text_lower = text.lower()
    phrases_found = [p for p in COMPREHENSION_PHRASES if p in text_lower]
    
    lines = [
        f"Word count: {word_count}",
        f"Sentences: ~{sentence_count}",
        f"Comprehension phrases found: {len(phrases_found)}",
    ]
    
    if phrases_found:
        lines.append(f"  Examples: {', '.join(phrases_found[:3])}")
    
    return "\n".join(lines)
