"""Demo 1 - The problem: what Claude builds with NO design guidance.

Only the base system prompt ("you are a frontend engineer, output one HTML file").
We save the page, open it, and run the local slop detector on it.

    uv run demo_1_the_default.py
    uv run demo_1_the_default.py "Build a blog post layout with author bio"
"""

import sys

from common import BASE_SYSTEM_PROMPT, USER_PROMPT, fingerprint, generate_page, print_fingerprint

if __name__ == "__main__":
    user_prompt = sys.argv[1] if len(sys.argv) > 1 else USER_PROMPT
    path = generate_page("1_default", BASE_SYSTEM_PROMPT, user_prompt)
    print_fingerprint(fingerprint(path))
