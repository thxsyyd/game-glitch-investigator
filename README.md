# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable.

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the fixed app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.**
   - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

- **Game purpose:** A single-player number guessing game built with Streamlit. The player picks a difficulty (Easy / Normal / Hard), the app generates a secret number in the matching range, and the player has a limited number of attempts to guess it. After each guess the app gives a directional hint ("Go HIGHER" or "Go LOWER") and updates a running score. The game ends on a correct guess (win) or when attempts run out (loss).

- **Bugs found:**
  1. *Flipped hints on even-numbered attempts.* `app.py` cast `secret` to a string on every even attempt, which forced `check_guess` into a lexicographic string-comparison fallback. Result: "99" appeared less than "32" because '9' < '3' is false but '1' (in "100") sorts before '3' (in "32"), so the hint direction reversed every other guess.
  2. *Attempts counter off-by-one.* `st.session_state.attempts` was initialized to `1` instead of `0`, so the very first display showed "Attempts left: 7" out of 8 before the player guessed anything.
  3. *Hardcoded range message.* The info banner said "Guess a number between 1 and 100" regardless of difficulty. Hard mode (1–200 after the fix) and Easy mode (1–20) both displayed the wrong range.
  4. *Asymmetric, illogical scoring.* `update_score` awarded **+5 points** for a "Too High" guess on even-numbered attempts, while a "Too Low" guess always lost 5 points. Wrong guesses should never earn points.
  5. *Incomplete New Game reset.* Clicking "New Game" reset only `attempts` and `secret`. `score`, `status`, and `history` carried over from the previous round, and `secret` was always drawn from 1–100 ignoring difficulty.

- **Fixes applied:**
  1. Removed the offending `secret = str(...)` line in `app.py` so the integer secret is passed to `check_guess` directly. Also coerced both operands to `int` inside `check_guess` and deleted the `except TypeError` fallback that was silently producing wrong hints.
  2. Initialized `attempts` to `0` in `reset_game_state()` so the displayed "Attempts left" is correct on first load.
  3. Replaced the hardcoded "between 1 and 100" string with `f"Guess a number between {low} and {high}."` using the actual range from `get_range_for_difficulty(difficulty)`.
  4. Rewrote `update_score` so any wrong outcome ("Too High" or "Too Low") loses 5 points, and a win awards `max(10, 100 - 10 * (attempt_number - 1))` points — early wins are worth more, but a late win still earns at least 10.
  5. Extracted a `reset_game_state(low, high)` helper that clears all five state keys (`secret`, `attempts`, `score`, `status`, `history`) and uses the current difficulty's range when drawing a new secret. Both the initial load and the "New Game" button now call this helper, so behavior is consistent.
  6. **Refactored** all four logic functions (`get_range_for_difficulty`, `parse_guess`, `check_guess`, `update_score`) out of `app.py` and into `logic_utils.py`, so they are testable independently of the Streamlit UI.

## 📸 Demo Walkthrough

1. User opens the app and selects "Normal" difficulty. The sidebar shows "Range: 1 to 100" and "Attempts allowed: 8", and the main panel correctly reads "Attempts left: 8".
2. User enters a guess of `40` and clicks **Submit Guess**. The secret is `73`, so the game returns "📈 Go HIGHER!" and the score drops by 5 (from 0 to -5). Attempts left becomes 7.
3. User enters `90`. The hint shows "📉 Go LOWER!" — consistent and correct, no more flipping. Attempts left becomes 6.
4. User enters `73`. The game shows "🎉 Correct!", triggers the balloons animation, and awards points (100 - 10 * (3 - 1) = 80, added to the running score). Final score: 70.
5. User clicks **New Game**. Score resets to 0, status resets to "playing", history clears, and a new secret is drawn from the current difficulty's range. The game is fully replayable.
6. User switches to "Hard" difficulty. The sidebar updates to "Range: 1 to 200" and the main panel text also updates to "Guess a number between 1 and 200" — no longer hardcoded.

## 🧪 Test Results

(base) haoxuantang@Haoxuans-MacBook-Pro game-glitch-investigator % python -m pytest
===================================== test session starts =====================================
platform darwin -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/haoxuantang/Desktop/CodePath/AI110/20260618 W3/game-glitch-investigator
plugins: anyio-4.12.1
collected 14 items                                                                            

tests/test_game_logic.py ..............                                                 [100%]

===================================== 14 passed in 0.01s ======================================

## 🚀 Stretch Features

- Not attempted in this submission. Future work could include Challenge 1 (edge-case test suite for negative numbers, decimals, and out-of-range guesses) or Challenge 4 (color-coded "Hot/Cold" UI based on how close the guess is to the secret).