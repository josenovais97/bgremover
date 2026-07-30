"""Regenerate the demo artwork for the QR, Palette and Base64 tool cards.

These three were the only tools on the homepage grid with no demo image, so they
rendered as icon-only cards among thirty that show a result. The other demos are
hand-made illustrations rather than UI screenshots — a source on the left, the
result on the right, on a soft neutral backdrop — so these follow that language:
composed as HTML and shot at the same 820x616 as the rest.

The *content* is real, not mocked up. The QR code is encoded by the actual
generator on /qr-code-generator/, and the palette hexes come from running the
actual extractor on /color-palette/ over one of the existing demo photos. So the
cards promise what the tools deliver.

Requires the dev server (it drives the real tool pages):
    venv/bin/python manage.py runserver 127.0.0.1:8877
    /home/jpn/nonius_docker/venv/bin/python scripts/make-tool-demos.py

Then regenerate the grid thumbnails, which are derived from these:
    venv/bin/python scripts/make-tool-thumbs.py
"""
import base64
import pathlib
import sys

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8877"
OUT = pathlib.Path("static/img")
SIZE = {"width": 820, "height": 616}   # matches every other demo-*.webp
PALETTE_SOURCE = "static/img/demo-blur-before.webp"

# Per-tool signature colours, mirroring TOOL_ACCENTS in context_processors.py.
ACCENT = {"qr": "#475569", "palette": "#a21caf", "base64": "#52525b"}

SHELL = """
<style>
  @import url('{base}/static/css/inter.css');
  * {{ box-sizing: border-box; margin: 0; }}
  body {{
    width: {w}px; height: {h}px; display: grid; place-items: center;
    font-family: Inter, system-ui, sans-serif;
    background: linear-gradient(140deg, #f2efec 0%, #e7e2dc 55%, #ded8d1 100%);
  }}
  .row {{ display: flex; align-items: center; gap: 34px; }}
  .card {{
    background: #fff; border-radius: 20px; padding: 22px;
    box-shadow: 0 18px 40px rgba(31, 27, 24, .16), 0 2px 6px rgba(31, 27, 24, .08);
  }}
  .arrow {{ width: 58px; height: 12px; flex: none; position: relative; }}
  .arrow::before {{
    content: ''; position: absolute; top: 5px; left: 0; width: 42px; height: 3px;
    background: #6b6560; border-radius: 2px;
  }}
  .arrow::after {{
    content: ''; position: absolute; top: 0; right: 0;
    border: 6px solid transparent; border-left-color: #6b6560;
  }}
  .cap {{
    font-size: 12px; font-weight: 700; letter-spacing: .09em; text-transform: uppercase;
    color: #8a827a; margin-bottom: 12px;
  }}
</style>
<div class="row">{body}</div>
"""


def data_uri(path):
    ext = pathlib.Path(path).suffix.lstrip(".")
    mime = {"webp": "image/webp", "png": "image/png", "jpg": "image/jpeg"}[ext]
    return f"data:{mime};base64," + base64.b64encode(pathlib.Path(path).read_bytes()).decode()


def qr_body(qr_png):
    """A link on the left, the code the generator actually produced on the right."""
    return f"""
    <div class="card" style="width:270px">
      <div class="cap">Your link</div>
      <div style="display:flex;align-items:center;gap:10px;padding:13px 15px;border-radius:12px;
                  background:#f4f5f7;border:1px solid #e6e8ec">
        <span style="width:9px;height:9px;border-radius:50%;background:{ACCENT['qr']};flex:none"></span>
        <span style="font-size:17px;font-weight:600;color:#1f2937">clearbg.pt</span>
      </div>
      <div style="margin-top:14px;height:9px;width:78%;border-radius:5px;background:#eceef1"></div>
      <div style="margin-top:8px;height:9px;width:54%;border-radius:5px;background:#eceef1"></div>
    </div>
    <div class="arrow"></div>
    <div class="card" style="text-align:center">
      <div class="cap">Scannable code</div>
      <!-- Native 320px, 1:1: scaling a QR resamples its modules and
           costs scannability for nothing. -->
      <img src="{qr_png}" width="320" height="320" style="display:block">
    </div>"""


def palette_body(photo, hexes):
    chips = "".join(
        f"""<div style="display:flex;align-items:center;gap:11px">
              <span style="width:38px;height:38px;border-radius:10px;background:{h};
                           border:1px solid rgba(0,0,0,.08);flex:none"></span>
              <span style="font-size:14px;font-weight:600;color:#3f3a35;
                           font-family:ui-monospace,Menlo,monospace">{h}</span>
            </div>"""
        for h in hexes
    )
    return f"""
    <div class="card" style="padding:14px">
      <img src="{photo}" width="286" height="358" style="display:block;border-radius:12px;object-fit:cover">
    </div>
    <div class="arrow"></div>
    <div class="card" style="width:214px">
      <div class="cap">Palette</div>
      <div style="display:flex;flex-direction:column;gap:12px">{chips}</div>
    </div>"""


def base64_body(photo, snippet):
    """The payload is the real PNG encoding of the photo shown beside it, so the
    `image/png` prefix and the bytes after it actually agree — a reader who knows
    what a PNG header looks like in base64 will not be told a fib by our own art."""
    return f"""
    <div class="card" style="padding:14px">
      <img src="{photo}" width="228" height="285" style="display:block;border-radius:12px;object-fit:cover">
    </div>
    <div class="arrow"></div>
    <div class="card" style="width:330px">
      <div class="cap">Data URI</div>
      <div style="padding:14px;border-radius:12px;background:#1f2229;overflow:hidden">
        <div style="font-family:ui-monospace,Menlo,monospace;font-size:12.5px;line-height:1.65;
                    word-break:break-all;color:#c9d1d9">
          <span style="color:#7ee787">data:image/png;base64,</span>{snippet}<span
            style="color:#6b7280">…</span>
        </div>
      </div>
      <div style="margin-top:14px;display:inline-flex;align-items:center;gap:8px;padding:9px 15px;
                  border-radius:10px;background:{ACCENT['base64']};color:#fff;
                  font-size:13.5px;font-weight:600">Copy data URI</div>
    </div>"""


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()

        # Real QR, encoded by the tool itself.
        page = browser.new_page()
        page.goto(f"{BASE}/qr-code-generator/", wait_until="networkidle")
        page.fill("#qr-text", "https://clearbg.pt")
        page.wait_for_timeout(1200)
        qr_png = page.evaluate("()=>document.querySelector('#qr-canvas').toDataURL('image/png')")
        if not qr_png:
            sys.exit("QR canvas was empty — is the dev server up?")

        # Real palette, extracted by the tool itself.
        page.goto(f"{BASE}/color-palette/", wait_until="networkidle")
        page.set_input_files("#pl-input", PALETTE_SOURCE)
        page.wait_for_timeout(2000)
        hexes = page.evaluate(
            """()=>[...new Set([...document.querySelectorAll('#pl-swatches *')]
                 .map(e=>e.textContent.trim()).filter(t=>/^#[0-9a-f]{6}$/.test(t)))]"""
        )[:6]
        if len(hexes) < 6:
            sys.exit(f"expected 6 palette swatches, got {hexes}")

        photo = data_uri(PALETTE_SOURCE)
        b64_photo = data_uri("static/img/demo-crop-before.webp")
        # Genuine PNG bytes for the very image the card displays, encoded in the
        # browser so the prefix and the payload cannot disagree.
        snippet = page.evaluate(
            """async (src) => {
                const img = new Image();
                img.src = src;
                await img.decode();
                const c = document.createElement('canvas');
                c.width = 64; c.height = Math.round(64 * img.height / img.width);
                c.getContext('2d').drawImage(img, 0, 0, c.width, c.height);
                return c.toDataURL('image/png').split(',')[1];
            }""",
            b64_photo,
        )[:150]

        shots = {
            "demo-qr-after.webp": qr_body(qr_png),
            "demo-palette-after.webp": palette_body(photo, hexes),
            "demo-base64-after.webp": base64_body(b64_photo, snippet),
        }
        shot = browser.new_page(viewport=SIZE, device_scale_factor=1)
        for name, body in shots.items():
            shot.set_content(SHELL.format(base=BASE, w=SIZE["width"], h=SIZE["height"], body=body))
            shot.wait_for_timeout(700)   # let the webfont settle before capture
            png = shot.screenshot(type="png")
            # Playwright only writes PNG/JPEG, and the Playwright env has no
            # Pillow — so re-encode to WebP in the browser, which has an encoder
            # already. Keeps this a single command against one interpreter.
            webp = shot.evaluate(
                """async (b64) => {
                    const img = new Image();
                    img.src = 'data:image/png;base64,' + b64;
                    await img.decode();
                    const c = document.createElement('canvas');
                    c.width = img.width; c.height = img.height;
                    c.getContext('2d').drawImage(img, 0, 0);
                    return c.toDataURL('image/webp', 0.88).split(',')[1];
                }""",
                base64.b64encode(png).decode(),
            )
            path = OUT / name
            path.write_bytes(base64.b64decode(webp))
            print(f"wrote {name}  ({path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
