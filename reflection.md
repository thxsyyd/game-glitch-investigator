# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?

The game looked polished on the surface — it had a proper title, a difficulty selector in the sidebar, a developer debug panel, attempt counter, score display, and even balloons animation for wins. Everything visually suggested a finished product, which made the underlying logic bugs harder to spot at first glance. The footer caption ironically read "Built by an AI that claims this code is production-ready," which set the tone for what I was about to discover.

- List at least two concrete bugs you noticed at the start (for example: "the hints were backwards").

First, the hints were unreliable — guessing 50, 68, 77, 99 all returned "Go HIGHER" even though the actual secret was 32. Second, the attempts counter started at 1 instead of 0, so the player silently lost one attempt before guessing anything. Third, the range display was hardcoded to "Guess a number between 1 and 100" regardless of selected difficulty (Hard mode is actually 1–50).

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
| Guess of 99 when secret was 32 (on attempt 2) | "Go LOWER!" hint | "Go HIGHER!" displayed — hint reversed on even-numbered attempts | none (silent logic error from string comparison) |
| Game just started, no guesses made | Attempts left: 8 | Attempts left: 7 (counter initialized to 1 instead of 0) | none |
| Select "Hard" difficulty | "Guess a number between 1 and 50" | "Guess a number between 1 and 100" (hardcoded display) | none |
| Wrong guess on attempt 2 (e.g., Too High) | Score decreases | Score increases by +5 | none |
| Click "New Game" after losing | Score, status, history all reset | Only attempts and secret reset; score and status carry over | none |

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?

I used Claude (Claude.ai) as my primary AI coding assistant throughout this project. I attached the relevant files (`app.py`, `logic_utils.py`) to the chat so Claude had full project context rather than having to guess what code I was referring to.

- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).

When I described the symptom that hints flipped between odd and even attempts, Claude pointed me to the line `secret = str(st.session_state.secret)` inside the even-attempt branch in `app.py`. It explained that converting secret to a string triggers a TypeError when `check_guess` tries `guess > secret`, which then falls into the except block that compares two strings lexicographically — so "100" appears "less than" "32" because the character '1' is less than '3'. I verified this by reading the `check_guess` function line by line and confirming the except branch existed, and the diagnosis matched the alternating pattern I had observed in the app exactly.

- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).

Earlier in the same debugging session, Claude initially suggested the hint bug was a simple `>` vs `<` swap inside `check_guess`. That would have been a fast, plausible-looking fix, but it didn't explain why the bug only appeared on even-numbered attempts — if the operator were simply wrong, the hints would be wrong every time, not every other time. I verified by playing the game again and confirming the alternating pattern, then asked Claude to look upstream at how `secret` was being passed into the function. That conversation led to the real root cause in the caller, not the comparison logic itself.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?

I decided a bug was really fixed only when two conditions were both met: (1) the symptom no longer reproduced in the Streamlit app across multiple attempts and difficulty settings, and (2) I could explain in plain language *why* the fix worked, not just that it ran without throwing errors. The second condition matters because AI-generated patches can silence symptoms by accident without fixing the underlying logic.

- Describe at least one test you ran (manual or using pytest) and what it showed you about your code.

I wrote a pytest case in `tests/test_game_logic.py` that calls `check_guess(99, 32)` and asserts the outcome is "Too High" — this gave me a regression test I could rerun after future changes. I also wrote a test for `update_score` confirming that a "Too High" outcome decreases the score on every attempt (not just odd-numbered ones), which would have caught the original asymmetric scoring bug. Running `pytest` showed all tests passing in green, which gave me confidence that both the directional hint and the scoring logic were now consistent.

- Did AI help you design or understand any tests? How?

AI helped me with the pytest skeleton — imports, the `test_` naming convention, the structure of an `assert` line — because I was newer to pytest specifically. However, I chose the actual input/expected pairs myself based on the bugs I had reproduced and documented in the log, so the tests were targeting real failure modes I had observed rather than generic happy paths the AI might invent.

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

Streamlit reruns the entire Python script from top to bottom every time the user interacts with any widget — clicking a button, typing in a field, changing a dropdown. That means normal Python variables don't persist between interactions; they get rebuilt from scratch each time. To keep data across reruns (like the secret number, current score, or attempts so far), you store it in `st.session_state`, which is a special dictionary that survives reruns. So the "state" of the game lives in `session_state`, while the UI gets re-rendered fresh on every interaction — very different from a typical web app where the page only changes when you tell it to.

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?

The habit I most want to reuse is **reproducing the bug before fixing it**. Filling out the Bug Reproduction Log forced me to write down the exact input, expected output, and actual output for each issue — and several times that act of being specific revealed that two symptoms I thought were separate were actually the same root cause (the string-conversion bug caused both the flipped hints *and* the inconsistent scoring on even attempts). Without that table I would have chased two fixes instead of one.

- What is one thing you would do differently next time you work with AI on a coding task?

Next time I would **share more context upfront instead of describing symptoms in isolation**. Claude's first hypothesis was often a generic pattern match (swap `>` and `<`), and it only got to the real root cause once I attached the full `app.py` and asked about the upstream `secret` variable. Giving the AI the full file from the start would have saved a debugging cycle.

- In one or two sentences, describe how this project changed the way you think about AI generated code.

AI is excellent at producing code that **looks** complete — type hints, docstrings, expander panels, emojis, organized session_state initialization — while hiding real logic bugs underneath that polish. Looking convincing is not the same as being correct, and the verification responsibility belongs to me.