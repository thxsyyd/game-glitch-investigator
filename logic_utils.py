"""Pure game logic functions for Game Glitch Investigator.

All functions here are stateless and easy to test with pytest.
Refactored from app.py to separate logic from UI.
"""


def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        # FIX: Hard should have a wider range than Normal, not narrower.
        # Original code returned 1, 50 which made Hard easier than Normal.
        return 1, 200
    return 1, 100


def parse_guess(raw: str):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    if raw is None or raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except (ValueError, TypeError):
        return False, None, "That is not a number."

    return True, value, None


def check_guess(guess, secret):
    """
    Compare guess to secret and return (outcome, message).

    outcome examples: "Win", "Too High", "Too Low"

    FIX: Original code had a fragile try/except TypeError fallback that
    compared strings lexicographically when secret was accidentally cast
    to str upstream. Removed the except branch so type errors surface
    instead of silently producing wrong hints.
    """
    # Coerce both sides to int to make the function robust to upstream bugs.
    guess = int(guess)
    secret = int(secret)

    if guess == secret:
        return "Win", "🎉 Correct!"
    if guess > secret:
        return "Too High", "📉 Go LOWER!"
    return "Too Low", "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update score based on outcome and attempt number.

    FIX: Original code rewarded wrong guesses (+5) on even attempts for
    Too High, and only penalized Too Low. New rule: any wrong guess loses
    5 points; correct guess earns points that decay with attempt number.
    """
    if outcome == "Win":
        points = max(10, 100 - 10 * (attempt_number - 1))
        return current_score + points

    if outcome in ("Too High", "Too Low"):
        return current_score - 5

    return current_score