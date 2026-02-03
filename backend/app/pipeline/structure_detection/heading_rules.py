"""
Heading Detection Rules - Text and style heuristics for identifying headings.

This module contains rule-based logic to detect heading candidates based on:
- Keyword matching (common section names)
- Numbering patterns (1., 1.1, I., etc.)
- Font size (outliers compared to body text)
- Text styling (bold, font size)
- Text properties (short lines, capitalization)
"""

import re
from typing import Optional, Dict, Any, Tuple
from app.models import Block


# Common academic section headings (case-insensitive)
COMMON_SECTION_KEYWORDS = {
    # Front matter
    "abstract", "keywords", "key words",
    
    # Main sections (level 1)
    "introduction", "background", "related work", "literature review",
    "methods", "methodology", "materials and methods", "experimental setup",
    "results", "findings", "experimental results",
    "discussion", "results and discussion",
    "conclusion", "conclusions", "summary",
    "acknowledgments", "acknowledgements", "funding",
    "references", "bibliography", "works cited",
    "appendix", "appendices", "supplementary material",
    
    # Common subsections (level 2+)
    "motivation", "contributions", "objectives",
    "dataset", "data collection", "participants",
    "procedure", "analysis", "evaluation",
    "limitations", "future work", "implications",
}


def detect_numbering_pattern(text: str) -> Optional[Dict[str, Any]]:
    """
    Detect if text starts with a heading numbering pattern.
    
    Patterns recognized:
    - "1." or "1.1" or "1.1.1" (decimal)
    - "I." or "II." or "III." (Roman numerals)
    - "(a)" or "(1)" (parenthetical)
    - "A." or "B." (letters)
    
    Args:
        text: Block text (should be trimmed)
    
    Returns:
        Dict with pattern info if detected, None otherwise
        {
            "pattern_type": "decimal" | "roman" | "letter" | "parenthetical",
            "number": "1.1",
            "level": 2,  # inferred from decimal depth
            "remainder": "Introduction"  # text after number
        }
    """
    text = text.strip()
    
    # Decimal numbering: 1., 1.1, 1.1.1, etc.
    decimal_match = re.match(r'^(\d+(?:\.\d+)*)\.\s+(.+)$', text)
    if decimal_match:
        number = decimal_match.group(1)
        remainder = decimal_match.group(2)
        level = number.count('.') + 1  # 1. = level 1, 1.1 = level 2
        return {
            "pattern_type": "decimal",
            "number": number,
            "level": level,
            "remainder": remainder
        }
    
    # Roman numerals: I., II., III., IV., etc.
    roman_match = re.match(r'^([IVX]+)\.\s+(.+)$', text)
    if roman_match:
        number = roman_match.group(1)
        remainder = roman_match.group(2)
        # Roman numerals are typically level 1 or 2
        return {
            "pattern_type": "roman",
            "number": number,
            "level": 1,  # Assume level 1 for Roman
            "remainder": remainder
        }
    
    # Letter numbering: A., B., C., etc.
    letter_match = re.match(r'^([A-Z])\.\s+(.+)$', text)
    if letter_match:
        number = letter_match.group(1)
        remainder = letter_match.group(2)
        return {
            "pattern_type": "letter",
            "number": number,
            "level": 2,  # Assume level 2 for letters
            "remainder": remainder
        }
    
    # Parenthetical: (a), (1), etc.
    paren_match = re.match(r'^\(([a-z0-9])\)\s+(.+)$', text)
    if paren_match:
        number = paren_match.group(1)
        remainder = paren_match.group(2)
        return {
            "pattern_type": "parenthetical",
            "number": number,
            "level": 3,  # Assume level 3 for parenthetical
            "remainder": remainder
        }
    
    return None


def matches_section_keyword(text: str) -> bool:
    """
    Check if text matches a common section heading keyword.
    
    Args:
        text: Block text (normalized)
    
    Returns:
        True if text matches a known section keyword
    """
    # Normalize: lowercase, strip numbering
    text_clean = text.strip().lower()
    
    # Remove leading numbering if present
    text_clean = re.sub(r'^\d+(?:\.\d+)*\.\s*', '', text_clean)
    text_clean = re.sub(r'^[IVX]+\.\s*', '', text_clean)
    text_clean = re.sub(r'^[A-Z]\.\s*', '', text_clean)
    
    # Check exact match
    if text_clean in COMMON_SECTION_KEYWORDS:
        return True
    
    # Check if it starts with a keyword (e.g., "Introduction and Background")
    for keyword in COMMON_SECTION_KEYWORDS:
        if text_clean.startswith(keyword):
            return True
    
    return False


def is_likely_heading_by_style(block: Block, avg_font_size: Optional[float] = None) -> Tuple[bool, float]:
    """
    Determine if a block is likely a heading based on styling.
    
    Heuristics:
    - Bold text
    - Larger font size than average
    - Short text (< 100 chars typically)
    - No punctuation at end (headings rarely end with .)
    
    Args:
        block: Block to analyze
        avg_font_size: Average font size in document (for comparison)
    
    Returns:
        Tuple of (is_likely_heading, confidence_score)
        confidence_score: 0.0-1.0
    """
    score = 0.0
    text = block.text.strip()
    
    # Empty or very short text is unlikely to be a heading
    if len(text) < 2:
        return False, 0.0
    
    # Check bold
    if block.style.bold:
        score += 0.3
    
    # Check font size
    if block.style.font_size and avg_font_size:
        if block.style.font_size > avg_font_size * 1.1:  # 10% larger
            score += 0.3
        elif block.style.font_size > avg_font_size * 1.3:  # 30% larger
            score += 0.4
    
    # Check text length (headings are usually short)
    if len(text) < 100:
        score += 0.2
    if len(text) < 50:
        score += 0.1
    
    # Check for lack of sentence-ending punctuation
    # Headings typically don't end with periods (except for numbering)
    if not text.endswith('.') or detect_numbering_pattern(text):
        score += 0.1
    
    # Check for ALL CAPS (common for headings)
    if text.isupper() and len(text) > 2:
        score += 0.2
    
    # Check for title case (each word capitalized)
    words = text.split()
    if len(words) >= 2:
        capitalized_words = sum(1 for w in words if w and w[0].isupper())
        if capitalized_words / len(words) > 0.7:  # 70%+ capitalized
            score += 0.1
    
    # Confidence threshold
    is_likely = score >= 0.4
    
    return is_likely, min(score, 1.0)


def infer_heading_level(block: Block, numbering_info: Optional[Dict] = None) -> int:
    """
    Infer the heading level (1, 2, 3, or 4).
    
    Level inference:
    - If numbering detected, use numbering depth
    - If font size available, larger = higher level (lower number)
    - Otherwise, default to level 2
    
    Args:
        block: Block to analyze
        numbering_info: Output from detect_numbering_pattern()
    
    Returns:
        Heading level (1-4)
    """
    # If we have numbering, use that
    if numbering_info and "level" in numbering_info:
        return min(numbering_info["level"], 4)  # Cap at level 4
    
    # Use font size as a heuristic
    # Larger font = higher level (level 1 is biggest)
    if block.style.font_size:
        font_size = block.style.font_size
        if font_size >= 18:
            return 1
        elif font_size >= 16:
            return 1
        elif font_size >= 14:
            return 2
        elif font_size >= 12:
            return 3
        else:
            return 4
    
    # Check if it matches a major section keyword (Introduction, Methods, etc.)
    text_lower = block.text.strip().lower()
    major_sections = {"introduction", "methods", "results", "discussion", "conclusion", "abstract", "references"}
    if text_lower in major_sections:
        return 1
    
    # Default to level 2
    return 2


def analyze_heading_candidate(
    block: Block,
    avg_font_size: Optional[float] = None
) -> Optional[Dict[str, Any]]:
    """
    Comprehensive analysis of whether a block is a heading candidate.
    
    This combines all heuristics to produce a single result.
    
    Args:
        block: Block to analyze
        avg_font_size: Average font size in document
    
    Returns:
        Dict with heading info if it's a candidate, None otherwise
        {
            "is_heading": bool,
            "confidence": float,
            "level": int,
            "has_numbering": bool,
            "numbering_info": dict or None,
            "matches_keyword": bool,
            "reasons": list of strings
        }
    """
    text = block.text.strip()
    
    # Skip empty blocks
    if not text:
        return None
    
    reasons = []
    confidence = 0.0
    
    # Check numbering
    numbering_info = detect_numbering_pattern(text)
    has_numbering = numbering_info is not None
    if has_numbering:
        reasons.append(f"Has numbering pattern: {numbering_info['pattern_type']}")
        confidence += 0.4
    
    # Check keyword matching
    matches_keyword = matches_section_keyword(text)
    if matches_keyword:
        reasons.append("Matches section keyword")
        confidence += 0.3
    
    # Check style
    style_likely, style_score = is_likely_heading_by_style(block, avg_font_size)
    if style_likely:
        reasons.append(f"Style suggests heading (score: {style_score:.2f})")
        confidence += style_score * 0.5  # Weight style at 50%
    
    # Decision: is this a heading?
    is_heading = confidence >= 0.4 or has_numbering or matches_keyword
    
    if not is_heading:
        return None
    
    # Infer level
    level = infer_heading_level(block, numbering_info)
    
    return {
        "is_heading": True,
        "confidence": min(confidence, 1.0),
        "level": level,
        "has_numbering": has_numbering,
        "numbering_info": numbering_info,
        "matches_keyword": matches_keyword,
        "reasons": reasons
    }
