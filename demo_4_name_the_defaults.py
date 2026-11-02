"""Demo 4 - The newer-model twist: name the exact defaults to avoid.

Current Claude docs: on Claude Opus 5.5 a vague "avoid a generic AI look" mostly
swaps one default for another. What works is a list of SPECIFIC patterns -
and you grow that list from what the previous result actually used.

This script reads demo 2's page, turns its fingerprint into a "Do not use" line,
and generates again.

    uv run demo_4_name_the_defaults.py
"""

import sys

from common import (BASE_SYSTEM_PROMPT, DISTILLED_AESTHETICS_PROMPT, OUT_DIR, USER_PROMPT,
                    fingerprint, generate_page, print_fingerprint)

# The list the docs give for Opus 5.5's own house styles
KNOWN_DEFAULTS = ["a cream or off-white background", "italic accent words in headlines",
                  'numbered "01/02/03" section labels', "monospace labels", "pill-shaped buttons"]


def avoid_list(previous: dict) -> list[str]:
    """Known defaults + whatever the last page actually chose."""
    items = list(KNOWN_DEFAULTS)
    if previous["fonts"]:
        items.append("the fonts " + " or ".join(previous["fonts"][:3]))
    if previous["top_colors"]:
        items.append("the palette " + ", ".join(previous["top_colors"][:3]))
    return items


if __name__ == "__main__":
    prev_path = OUT_DIR / "2_aesthetics.html"
    if not prev_path.exists():
        sys.exit("Run demo 2 first: uv run demo_2_aesthetics_prompt.py")
    previous = fingerprint(prev_path)

    avoid = avoid_list(previous)
    rule = "Do not use " + ", ".join(avoid[:-1]) + ", or " + avoid[-1] + "."
    print("[avoid]    " + rule + "\n")

    system = BASE_SYSTEM_PROMPT + "\n\n" + DISTILLED_AESTHETICS_PROMPT + "\n<avoid>\n" + rule + "\n</avoid>"
    path = generate_page("4_named_defaults", system, USER_PROMPT)
    after = fingerprint(path)
    print_fingerprint(after)
    print(f"\nDemo 2 fonts {previous['fonts'][:2]}  ->  Demo 4 fonts {after['fonts'][:2]}")
    print(f"Demo 2 colours {previous['top_colors'][:3]}  ->  Demo 4 colours {after['top_colors'][:3]}")
