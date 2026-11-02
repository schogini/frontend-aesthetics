"""Demo 2 - The fix: append the cookbook's <frontend_aesthetics> block.

Same user prompt as demo 1. The only change is the system prompt, which now
guides four design dimensions (typography, colour, motion, backgrounds),
suggests inspirations and calls out the usual defaults.

    uv run demo_2_aesthetics_prompt.py
"""

import sys

from common import (BASE_SYSTEM_PROMPT, DISTILLED_AESTHETICS_PROMPT, OUT_DIR, USER_PROMPT,
                    fingerprint, generate_page, print_fingerprint)

if __name__ == "__main__":
    user_prompt = sys.argv[1] if len(sys.argv) > 1 else USER_PROMPT
    path = generate_page("2_aesthetics", BASE_SYSTEM_PROMPT + "\n\n" + DISTILLED_AESTHETICS_PROMPT, user_prompt)
    after = fingerprint(path)
    print_fingerprint(after)

    before_path = OUT_DIR / "1_default.html"
    if before_path.exists():
        before = fingerprint(before_path)
        print(f"\nBEFORE (demo 1): {before['flag_count']} defaults | fonts {before['fonts'][:2]} | {before['keyframes']} animations")
        print(f"AFTER  (demo 2): {after['flag_count']} defaults | fonts {after['fonts'][:2]} | {after['keyframes']} animations")
