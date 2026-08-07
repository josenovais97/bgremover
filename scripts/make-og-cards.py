"""Regenerate static/img/og/ — the per-tool Open Graph share cards (1200x630).

Every tool gets a card carrying its own name, its own one-line blurb, its own
demo artwork and its own accent colour, so a link pasted into WhatsApp, Slack or
a tweet says what the page does. Tools with no card of their own fall back to the
site-wide og-image.png, which says only "ClearBG" — fine for the homepage,
wasted on 30 different tools.

This also fixes the hand-made cards it replaces. Those were laid out with an
unconstrained text column, so any title longer than about eleven characters ran
underneath the artwork panel: the old pdf-to-image card read "PDF to Imag", and
the privacy pill disappeared behind the picture on several others. Here the left
column is a fixed width and the title auto-shrinks to fit inside it, so a long
label wraps instead of colliding.

`index` is deliberately skipped: the homepage keeps the purpose-built site-wide
card rather than a generated one.

Run:  venv/bin/python scripts/make-og-cards.py
"""
import base64
import io
import json
import os
import pathlib
import sys

import django
from PIL import Image
from playwright.sync_api import sync_playwright

OUT = pathlib.Path("static/img/og")
SIZE = (1200, 630)
SKIP = {"index"}
FONT = "'Ubuntu Sans', 'DejaVu Sans', system-ui, sans-serif"


def og_name(url_name):
    """'pdf_to_image' -> 'pdf-to-image.png', matching the existing filenames."""
    return url_name.replace("_", "-") + ".png"


def data_uri(rel):
    """Embed a static image; the CSP forbids nothing here but file:// would."""
    path = pathlib.Path("static") / rel
    mime = {".webp": "image/webp", ".png": "image/png",
            ".jpg": "image/jpeg", ".gif": "image/gif"}[path.suffix]
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def card_html(label, blurb, art, icon, accent, accent_dark):
    return f"""<style>
  *{{margin:0;padding:0;box-sizing:border-box}}
  body{{width:1200px;height:630px;font-family:{FONT};overflow:hidden;
       background:linear-gradient(135deg,rgb({accent}) 0%,rgb({accent_dark}) 100%);
       color:#fff;display:flex;align-items:center;-webkit-font-smoothing:antialiased}}
  /* Fixed width is the whole point: the artwork starts at x=592, so the text
     column must never be allowed to grow past it. */
  .left{{width:496px;margin-left:64px;flex:0 0 496px}}
  .brand{{display:flex;align-items:center;gap:16px;margin-bottom:58px}}
  .brand img{{width:52px;height:52px;border-radius:12px}}
  .brand span{{font-size:31px;font-weight:800;letter-spacing:-.4px}}
  h1{{font-size:60px;font-weight:800;letter-spacing:-1.6px;line-height:1.06;
      overflow-wrap:break-word}}
  .sub{{font-size:26px;color:rgba(255,255,255,.86);margin-top:18px;line-height:1.32}}
  .pill{{display:inline-flex;align-items:center;gap:11px;margin-top:44px;
        padding:14px 24px;border-radius:40px;background:rgba(255,255,255,.16);
        border:1px solid rgba(255,255,255,.25);font-size:20px;font-weight:600;
        white-space:nowrap}}
  .art{{position:absolute;left:592px;top:44px;width:552px;height:542px;
       border-radius:28px;overflow:hidden;box-shadow:0 26px 60px -14px rgba(0,0,0,.5)}}
  .art img{{width:100%;height:100%;object-fit:cover}}
</style>
<div class="left">
  <div class="brand"><img src="{icon}"><span>ClearBG</span></div>
  <h1 id="t">{label}</h1>
  <div class="sub">{blurb}</div>
  <div class="pill">&#128274; Runs in your browser &middot; nothing uploaded</div>
</div>
<div class="art"><img src="{art}"></div>"""


def main():
    sys.path.insert(0, ".")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
    django.setup()
    from remover.context_processors import TOOL_NAV, TOOL_ACCENTS, _DEFAULT_ACCENT

    icon = data_uri("img/icon-512.png")
    jobs = []
    for tool in TOOL_NAV:
        name = tool["name"]
        if name in SKIP:
            continue
        accent = TOOL_ACCENTS.get(name, _DEFAULT_ACCENT)
        jobs.append({
            "name": name,
            "file": og_name(name),
            "html": card_html(
                tool["label"], tool["blurb"],
                data_uri(tool["demo"]),
                icon,
                ",".join(accent[0].split()), ",".join(accent[1].split()),
            ),
        })

    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        pg = browser.new_page(viewport={"width": SIZE[0], "height": SIZE[1]},
                              device_scale_factor=1)
        for job in jobs:
            pg.set_content(job["html"], wait_until="load")
            # Shrink the title until it fits the column's two-line allowance. Doing
            # this by measurement rather than by picking a size per tool means a
            # tool renamed later still produces a correct card.
            pg.evaluate("""()=>{
              const h=document.getElementById('t');
              for (let s=60; s>28 && h.scrollHeight>150; s-=2) h.style.fontSize=s+'px';
            }""")
            pg.wait_for_timeout(120)
            raw = pg.screenshot()
            # Flatten to RGB: the crawlers that render these want plain 24-bit,
            # and the existing cards are RGB too.
            im = Image.open(io.BytesIO(raw)).convert("RGB")
            im.save(OUT / job["file"], optimize=True)
            print(f"  {job['file']:28} {(OUT / job['file']).stat().st_size // 1024:4} KB")
        browser.close()

    print(f"\n{len(jobs)} cards in {OUT}/")
    # Hand the caller the mapping to paste into OG_IMAGES.
    mapping = {j["name"]: f"img/og/{j['file']}" for j in jobs}
    pathlib.Path("dist/og-images.json").parent.mkdir(exist_ok=True)
    pathlib.Path("dist/og-images.json").write_text(json.dumps(mapping, indent=2))
    print("mapping written to dist/og-images.json")


if __name__ == "__main__":
    main()
