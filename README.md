# Escape the AI-Slop Look: Prompting Claude for Distinctive Frontends

A walkthrough of the Claude Cookbook recipe [Prompting for frontend aesthetics](https://platform.claude.com/cookbook/coding-prompting-for-frontend-aesthetics) in 4 small Python scripts, run with **uv**.

Without direction, Claude builds safe, generic pages: Inter, purple gradients, cookie-cutter layouts. The fix is a block of **system prompt** that steers four design dimensions (typography, colour, motion, backgrounds), names inspirations, and calls out the usual defaults. This lab streams real pages from the Messages API, saves them as HTML, and scores each one with a small local **"slop detector"** so you can compare pages with numbers. It also adds the newer Opus 5.5 advice: **name the exact defaults to avoid**.

## Project layout

```
frontend-aesthetics/
├── pyproject.toml                # uv project + dependencies
├── .env.example                  # copy to .env and add your key
├── common.py                     # prompts, generate_page(), fingerprint() slop detector
├── demo_1_the_default.py         # no design guidance: the baseline
├── demo_2_aesthetics_prompt.py   # + the cookbook <frontend_aesthetics> block
├── demo_3_isolated_prompts.py    # typography-only, or a locked Solarpunk theme
├── demo_4_name_the_defaults.py   # turn the last page's fingerprint into a "do not use" list
├── compare.py                    # no key: score every page + side-by-side gallery
└── html_outputs/                 # generated pages land here
```

## Setup

1. Install [uv](https://docs.astral.sh/uv/):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
2. Add your API key:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and set `ANTHROPIC_API_KEY=sk-ant-...`. Optional: `CLAUDE_MODEL` (default `claude-opus-5-5`) and `CLAUDE_EFFORT` (default `medium`).
3. Install dependencies:
   ```bash
   uv sync
   ```

> **Conda users:** if a conda env is active, uv may pick conda's Python (wrong architecture on Apple Silicon).
> Run `conda deactivate` first, or prefix commands with `env -u CONDA_PREFIX`.

## Run the lab (in order)

Each generating demo takes about 2 minutes and opens the page in your browser. Set `NO_BROWSER=1` to skip that.

| # | Command | API key? | What you'll see |
|---|---|---|---|
| 1 | `uv run demo_1_the_default.py` | yes | The generic page + its fingerprint (fonts, colours, motion, 7 default flags) |
| 2 | `uv run demo_2_aesthetics_prompt.py` | yes | Same request with the aesthetics block, plus a before/after line |
| 3 | `uv run demo_3_isolated_prompts.py typography` | yes | Fonts-only prompt |
| 3b | `uv run demo_3_isolated_prompts.py solarpunk` | yes | Theme-locked energy dashboard |
| 4 | `uv run demo_4_name_the_defaults.py` | yes (needs demo 2's page) | The auto-built "Do not use…" rule and the regenerated page |
| ★ | `uv run compare.py` | **no** | A score table + `html_outputs/index.html` gallery |

Demos 1 and 2 accept your own request: `uv run demo_1_the_default.py "Build a blog post layout with author bio"`.

### Real results (`claude-opus-5-5`, effort medium)

| Page | Fonts | Palette | Animations | Defaults flagged |
|---|---|---|---|---|
| 1 default | Inter | indigo scale `#eef2ff → #818cf8` | 0 | **4 / 7** |
| 2 aesthetics block | Bricolage Grotesque, Instrument Serif, IBM Plex Mono | ink `#15140f`, cream `#efe9dc`, mustard, rust | 4 | **4 / 7** (different four: cream, italic accent, mono, pill) |
| 3 typography only | Bricolage Grotesque, JetBrains Mono | ink, orange `#ff5a1f`, cream | 1 | 5 / 7 |
| 3 solarpunk | Righteous, Space Grotesk, JetBrains Mono | greens + gold | 4 | 3 / 7 |
| 4 named defaults | Unbounded, Manrope | deep teal `#07181a`, vermilion `#ff5a36`, sky, mint | 3 | **1 / 7** |

Each page took 100-133 s and 12k-17k output tokens. Claude Haiku 5.5 on demo 1 gave the same indigo + Inter look in 62 s.

## How it works (the lines that matter)

```python
system = BASE_SYSTEM_PROMPT + "\n\n" + DISTILLED_AESTHETICS_PROMPT          # the cookbook technique
rule = "Do not use " + ", ".join(avoid[:-1]) + ", or " + avoid[-1] + "."    # demo 4: name the defaults
with client.beta.messages.stream(model=MODEL, max_tokens=64_000, system=system, ...) as stream:
```

## Cost

Opus 5.5 is $4 / $20 per million input / output tokens. A page is about 16k output tokens, roughly **$0.30**, so the full lab (5 pages) is about **$1.50**. For a cheap run, set `CLAUDE_MODEL=claude-haiku-5-5` in `.env` (about 2 cents a page) or `CLAUDE_EFFORT=low`. `compare.py` is free.

## Differences from the original

- **Model:** `claude-opus-5-5` (overridable) instead of `claude-sonnet-4-6`, with an explicit `effort` setting.
- **Plain scripts instead of a notebook:** a progress line every 5,000 characters replaces the IPython streaming widget.
- **Refusal fallback:** requests opt into server-side fallbacks (`fallbacks="default"`) and check `stop_reason == "refusal"`.
- **New: the slop detector** (`fingerprint()` in `common.py`). It's a heuristic regex scan for fonts, colours, keyframes, gradients and 7 known defaults. It is not a design judge.
- **New: demo 4.** The current Claude docs say that on Opus 5.5 a vague "avoid a generic AI look" mostly swaps one default for another, and that naming specific patterns works. We saw exactly that: demo 2 changed which defaults it used but not how many. Demo 4 names them and gets 1 of 7.
- **Observed:** the isolated prompts weren't faster in our runs (126-133 s vs 118-128 s for the full block).

---

From **TechieTalksAI** by [Schogini](http://schogini.com). Want an AI agent for your business? Book a free demo at http://schogini.com.
