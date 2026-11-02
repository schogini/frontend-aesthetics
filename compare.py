"""Bonus (no API key): fingerprint every page and build a side-by-side gallery.

    uv run compare.py           # prints a table, writes html_outputs/index.html and opens it
"""

import os
import webbrowser

from common import OUT_DIR, fingerprint

if __name__ == "__main__":
    pages = sorted(p for p in OUT_DIR.glob("*.html") if p.name != "index.html")
    if not pages:
        raise SystemExit("No pages yet. Run demo 1 first.")

    print(f"{'page':<20} {'defaults':>8}  {'anims':>5}  fonts")
    cards = []
    for p in pages:
        fp = fingerprint(p)
        fonts = ", ".join(fp["fonts"][:2]) or "(default)"
        print(f"{p.stem:<20} {fp['flag_count']:>5}/{len(fp['flags'])}  {fp['keyframes']:>5}  {fonts}")
        hits = "".join(f"<li>{k}</li>" for k, v in fp["flags"].items() if v) or "<li>none</li>"
        swatches = "".join(f'<i style="background:{c}"></i>' for c in fp["top_colors"])
        cards.append(f"""<figure><iframe src="{p.name}" loading="lazy"></iframe>
<figcaption><b>{p.stem}</b> · {fp['flag_count']} defaults · {fonts}<div class="sw">{swatches}</div>
<ul>{hits}</ul></figcaption></figure>""")

    index = OUT_DIR / "index.html"
    index.write_text(f"""<!doctype html><meta charset="utf-8"><title>Gallery</title><style>
body{{margin:0;padding:24px;background:#111;color:#eee;font:14px/1.4 sans-serif}}
main{{display:grid;grid-template-columns:repeat(auto-fill,minmax(560px,1fr));gap:24px}}
figure{{margin:0;background:#1c1c1c;border-radius:10px;overflow:hidden}}
iframe{{width:1280px;height:800px;border:0;transform:scale(.4375);transform-origin:0 0;margin-bottom:-450px}}
figcaption{{padding:12px}} .sw i{{display:inline-block;width:22px;height:14px;margin:6px 4px 0 0}}
ul{{margin:6px 0 0;padding-left:18px;color:#f99}}</style><main>{''.join(cards)}</main>""")
    print(f"\nGallery: {index}")
    if not os.getenv("NO_BROWSER"):
        webbrowser.open(index.resolve().as_uri())
