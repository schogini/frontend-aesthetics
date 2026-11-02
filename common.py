"""Shared pieces for the frontend-aesthetics demos.

- The prompts from the Claude Cookbook recipe "Prompting for frontend aesthetics"
- generate_page(): stream one HTML page from Claude and save it
- fingerprint(): a small, local "AI-slop detector" that reads an HTML file
"""

import colorsys
import os
import re
import sys
import time
import webbrowser
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("CLAUDE_MODEL", "claude-opus-5-5")
EFFORT = os.getenv("CLAUDE_EFFORT", "medium")  # Opus 5.5 default; "low" is faster
OUT_DIR = Path("html_outputs")

USER_PROMPT = "Create a SaaS landing page for a project management tool"

# ---------------------------------------------------------------------------
# Prompts (copied from the cookbook)
# ---------------------------------------------------------------------------

BASE_SYSTEM_PROMPT = """
You are an expert frontend engineer skilled at crafting beautiful, performant frontend applications.
<tech_stack>
Use vanilla HTML, CSS, & Javascript. Use Tailwind CSS for your CSS variables.
</tech_stack>
<output>
Generate complete, self-contained HTML code for the requested frontend application. Include all CSS and JavaScript inline.
CRITICAL: You must wrap your HTML code in triple backticks with html language identifier like this:
```html
<!DOCTYPE html>
<html>
...
</html>
```
Our parser depends on this format - do not deviate from it!
</output>
"""

DISTILLED_AESTHETICS_PROMPT = """
<frontend_aesthetics>
You tend to converge toward generic, "on distribution" outputs. In frontend design, this creates what users call the "AI slop" aesthetic. Avoid this: make creative, distinctive frontends that surprise and delight. Focus on:
Typography: Choose fonts that are beautiful, unique, and interesting. Avoid generic fonts like Arial and Inter; opt instead for distinctive choices that elevate the frontend's aesthetics.
Color & Theme: Commit to a cohesive aesthetic. Use CSS variables for consistency. Dominant colors with sharp accents outperform timid, evenly-distributed palettes. Draw from IDE themes and cultural aesthetics for inspiration.
Motion: Use animations for effects and micro-interactions. Prioritize CSS-only solutions for HTML. Use Motion library for React when available. Focus on high-impact moments: one well-orchestrated page load with staggered reveals (animation-delay) creates more delight than scattered micro-interactions.
Backgrounds: Create atmosphere and depth rather than defaulting to solid colors. Layer CSS gradients, use geometric patterns, or add contextual effects that match the overall aesthetic.
Avoid generic AI-generated aesthetics:
- Overused font families (Inter, Roboto, Arial, system fonts)
- Clichéd color schemes (particularly purple gradients on white backgrounds)
- Predictable layouts and component patterns
- Cookie-cutter design that lacks context-specific character
Interpret creatively and make unexpected choices that feel genuinely designed for the context. Vary between light and dark themes, different fonts, different aesthetics. You still tend to converge on common choices (Space Grotesk, for example) across generations. Avoid this: it is critical that you think outside the box!
</frontend_aesthetics>
"""

TYPOGRAPHY_PROMPT = """
<use_interesting_fonts>
Typography instantly signals quality. Avoid using boring, generic fonts.
**Never use:** Inter, Roboto, Open Sans, Lato, default system fonts
**Impact choices:**
- Code aesthetic: JetBrains Mono, Fira Code, Space Grotesk
- Editorial: Playfair Display, Crimson Pro, Fraunces
- Startup: Clash Display, Satoshi, Cabinet Grotesk
- Technical: IBM Plex family, Source Sans 3
- Distinctive: Bricolage Grotesque, Obviously, Newsreader
**Pairing principle:** High contrast = interesting. Display + monospace, serif + geometric sans, variable font across weights.
**Use extremes:** 100/200 weight vs 800/900, not 400 vs 600. Size jumps of 3x+, not 1.5x.
Pick one distinctive font, use it decisively. Load from Google Fonts. State your choice before coding.
</use_interesting_fonts>
"""

SOLARPUNK_THEME_PROMPT = """
<always_use_solarpunk_theme>
Always design with Solarpunk aesthetic:
- Warm, optimistic color palettes (greens, golds, earth tones)
- Organic shapes mixed with technical elements
- Nature-inspired patterns and textures
- Bright, hopeful atmosphere
- Retro-futuristic typography
</always_use_solarpunk_theme>
"""

# ---------------------------------------------------------------------------
# Talking to Claude
# ---------------------------------------------------------------------------


def get_client():
    if not os.getenv("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY is missing. Run: cp .env.example .env  and paste your key.")
    import anthropic

    return anthropic.Anthropic()


def extract_html(text: str) -> str | None:
    match = re.search(r"```(?:html)?\s*(.*?)\s*```", text, re.DOTALL)
    return match.group(1) if match else None


def generate_page(name: str, system_prompt: str, user_prompt: str = USER_PROMPT) -> Path:
    """Stream one page from Claude, save it as html_outputs/<name>.html, open it."""
    client = get_client()
    print(f"[generate] {name}  model={MODEL} effort={EFFORT}")
    print(f"[prompt]   system {len(system_prompt):,} chars | user: {user_prompt!r}")

    text, next_mark, start = "", 5_000, time.time()
    with client.beta.messages.stream(
        model=MODEL,
        max_tokens=64_000,
        output_config={"effort": EFFORT},
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
        # If a safety classifier declines, the API retries on a fallback model for us
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    ) as stream:
        for chunk in stream.text_stream:
            text += chunk
            if len(text) >= next_mark:
                print(f"           ... {len(text):,} chars ({time.time() - start:.0f}s)")
                next_mark += 5_000
        final = stream.get_final_message()

    if final.stop_reason == "refusal":
        sys.exit("Claude declined this request (stop_reason=refusal).")
    html = extract_html(text)
    if html is None:
        sys.exit("Could not find a ```html block in the reply.")

    OUT_DIR.mkdir(exist_ok=True)
    path = OUT_DIR / f"{name}.html"
    path.write_text(html)
    print(f"[done]     {time.time() - start:.1f}s | output tokens {final.usage.output_tokens:,} | saved {path}")
    if not os.getenv("NO_BROWSER"):
        webbrowser.open(path.resolve().as_uri())
    return path


# ---------------------------------------------------------------------------
# The local "AI-slop detector" (no API key)
# ---------------------------------------------------------------------------

GENERIC_FONTS = {"inter", "roboto", "arial", "open sans", "lato", "helvetica",
                 "system-ui", "-apple-system", "segoe ui", "space grotesk"}
CSS_GENERIC = {"sans-serif", "serif", "monospace", "cursive", "inherit", "blinkmacsystemfont", "ui-monospace",
               "ui-sans-serif", "ui-serif", "sfmono-regular", "menlo", "consolas", "courier new", "georgia",
               "times new roman", "apple color emoji", "segoe ui emoji", "noto color emoji", "var"}


def _fonts(html: str) -> list[str]:
    found = []
    for fam in re.findall(r"fonts\.googleapis\.com/css2?\?([^\"'>]+)", html):
        found += [f.split(":")[0].replace("+", " ") for f in re.findall(r"family=([^&]+)", fam)]
    for decl in re.findall(r"font-family\s*:\s*([^;}\"]+)", html):
        found += [f.strip(" '\"") for f in decl.split(",")]
    for decl in re.findall(r"fontFamily\s*:\s*\{([^}]*)\}", html):  # tailwind.config
        found += re.findall(r"['\"]([A-Z][\w ]+)['\"]", decl)
    seen, out = set(), []
    for f in found:
        key = f.lower()
        if f and key not in seen and key not in CSS_GENERIC and not key.startswith("var("):
            seen.add(key)
            out.append(f)
    return out


def _hexes(html: str) -> Counter:
    colors = Counter()
    for h in re.findall(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b", html):
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        colors["#" + h.lower()] += 1
    return colors


def _is_purple(hex_color: str) -> bool:
    r, g, b = (int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return 0.68 <= h <= 0.82 and s > 0.35 and 0.2 < l < 0.85


def _is_cream(hex_color: str) -> bool:
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return min(r, g, b) > 200 and r >= g >= b and 6 <= r - b <= 50


def fingerprint(path: Path) -> dict:
    html = Path(path).read_text()
    colors = _hexes(html)
    fonts = _fonts(html)
    purple = sum(n for c, n in colors.items() if _is_purple(c)) + len(
        re.findall(r"\b(?:from|via|to|bg|text)-(?:purple|violet|indigo|fuchsia)-\d{2,3}", html))
    flags = {
        "generic font (Inter/Roboto/Arial/system/Space Grotesk)": any(f.lower() in GENERIC_FONTS for f in fonts) or not fonts,
        "purple / indigo gradient": purple >= 3 and "gradient" in html,
        "cream / off-white background": any(_is_cream(c) for c, _ in colors.most_common(4)),
        "pill-shaped buttons / badges": bool(re.search(r"rounded-full|border-radius\s*:\s*(9999|999|100|50)px", html)),
        "numbered 01/02/03 labels": len(re.findall(r">\s*0[1-6]\s*(?:<|[./—–-])", html)) >= 2,
        "italic accent words in headlines": bool(re.search(
            r"<h[12][^>]*>(?:(?!</h[12]>).)*(?:<(?:em|i)\b|class=\"[^\"]*\bitalic\b|font-style\s*:\s*italic)", html, re.DOTALL)),
        "monospace labels": bool(re.search(r"font-mono|monospace", html)),
    }
    return {
        "file": str(path),
        "size_kb": round(len(html) / 1024, 1),
        "fonts": fonts[:4],
        "top_colors": [c for c, _ in colors.most_common(5)],
        "keyframes": len(re.findall(r"@keyframes", html)),
        "animation_delays": len(re.findall(r"animation-delay", html)),
        "gradients": len(re.findall(r"(?:linear|radial|conic)-gradient", html)),
        "flags": flags,
        "flag_count": sum(flags.values()),
    }


def print_fingerprint(fp: dict) -> None:
    print(f"\n[fingerprint] {fp['file']}  ({fp['size_kb']} KB)")
    print(f"  fonts      : {', '.join(fp['fonts']) or '(none - browser default)'}")
    print(f"  top colours: {' '.join(fp['top_colors'])}")
    print(f"  motion     : {fp['keyframes']} @keyframes, {fp['animation_delays']} animation-delay")
    print(f"  backgrounds: {fp['gradients']} gradients")
    print("  generic-default flags:")
    for name, hit in fp["flags"].items():
        print(f"    {'[x]' if hit else '[ ]'} {name}")
    print(f"  => {fp['flag_count']} of {len(fp['flags'])} common defaults found")
