"""Demo 3 - Targeted control: one dimension, or one locked-in theme.

    uv run demo_3_isolated_prompts.py typography   # fonts only, same SaaS page
    uv run demo_3_isolated_prompts.py solarpunk    # theme lock, energy dashboard

Smaller prompt = narrower change and more predictable output.
"""

import sys

from common import (BASE_SYSTEM_PROMPT, SOLARPUNK_THEME_PROMPT, TYPOGRAPHY_PROMPT, USER_PROMPT,
                    fingerprint, generate_page, print_fingerprint)

MODES = {
    "typography": (TYPOGRAPHY_PROMPT, USER_PROMPT),
    "solarpunk": (SOLARPUNK_THEME_PROMPT, "Create a dashboard for renewable energy monitoring"),
}

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "typography"
    if mode not in MODES:
        sys.exit(f"Pick one of: {', '.join(MODES)}")
    extra, user_prompt = MODES[mode]
    path = generate_page(f"3_{mode}", BASE_SYSTEM_PROMPT + "\n\n" + extra, user_prompt)
    print_fingerprint(fingerprint(path))
