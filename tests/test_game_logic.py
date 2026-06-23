"""Pytest cases for game logic in logic_utils.py.

These tests target specific bugs found in Phase 1 of the project.
Run with: python -m pytest
"""

import pytest
from logic_utils import (
    get_range_for_difficulty,
    parse_guess,
    check_guess,
    update_score,
)


# --- Starter tests (updated to unpack the (outcome, message) tuple) ---

def test_winning_guess():
    """If the secret is 50 and guess is 50, it should be a win."""
    outcome, _ = check_guess(50, 50)
    assert outcome == "Win"


def test_guess_too_high():
    """If secret is 50 and guess is 60, hint should be 'Too High'."""
    outcome, _ = check_guess(60, 50)
    assert outcome == "Too High"


def test_guess_too_low():
    """If secret is 50 and guess is 40, hint should be 'Too Low'."""
    outcome, _ = check_guess(40, 50)
    assert outcome == "Too Low"


# --- Regression test for the flipped-hint bug ---

def test_check_guess_handles_string_secret_without_crashing():
    """Even if upstream code accidentally passes a string secret,
    the fix coerces both sides to int so the answer is still correct.
    This regression test targets the original bug where check_guess
    fell into a string-comparison branch on even-numbered attempts.
    """
    outcome, _ = check_guess(99, "32")
    assert outcome == "Too High"


# --- get_range_for_difficulty: range display bug ---

def test_easy_range():
    assert get_range_for_difficulty("Easy") == (1, 20)


def test_normal_range():
    assert get_range_for_difficulty("Normal") == (1, 100)


def test_hard_range_is_wider_than_normal():
    """Hard should be harder than Normal, meaning a wider number range."""
    low, high = get_range_for_difficulty("Hard")
    assert (high - low) > 100


# --- parse_guess: input validation ---

def test_parse_guess_empty_input():
    ok, value, err = parse_guess("")
    assert ok is False
    assert value is None
    assert err is not None


def test_parse_guess_valid_integer():
    ok, value, err = parse_guess("42")
    assert ok is True
    assert value == 42
    assert err is None


def test_parse_guess_decimal_input():
    """Decimals like '42.7' should be coerced to int (42)."""
    ok, value, err = parse_guess("42.7")
    assert ok is True
    assert value == 42


def test_parse_guess_invalid_text():
    ok, value, err = parse_guess("hello")
    assert ok is False
    assert value is None


# --- update_score: asymmetric scoring bug ---

def test_wrong_guess_always_loses_points():
    """Regression test: Too High should never reward points.
    Original code added +5 on even attempts, which is wrong.
    """
    # Attempt 2 (even) — was the broken case in the original code
    assert update_score(current_score=10, outcome="Too High", attempt_number=2) == 5
    # Attempt 3 (odd)
    assert update_score(current_score=10, outcome="Too High", attempt_number=3) == 5


def test_too_low_loses_points():
    assert update_score(current_score=10, outcome="Too Low", attempt_number=1) == 5


def test_win_awards_more_points_on_early_attempts():
    """Winning on attempt 1 should give more points than winning on attempt 5."""
    early = update_score(0, "Win", 1)
    late = update_score(0, "Win", 5)
    assert early > late