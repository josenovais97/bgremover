"""Build the Chrome Web Store listing images into dist/store/.

Produces, at the exact canvas sizes the dashboard demands:

  shot-1-right-click.png    1280x800   composed: the menu over a page
  shot-2-in-the-tool.png    1280x800   real capture of the app doing the work
  shot-3-nothing-uploaded.png 1280x800 composed: the privacy claim
  tile-small.png             440x280   small promo tile
  tile-marquee.png          1400x560   marquee promo tile
  store-icon-128.png         128x128   store icon

Every one of these is written as **24-bit PNG with no alpha channel**, because the
store silently rejects an upload carrying transparency. Playwright always
screenshots with an alpha channel, so `flatten()` is not optional tidying — it is
the step that makes the file acceptable. The store icon keeps its alpha: icons
are the one asset where transparency is wanted.

Shot 2 is a genuine screenshot: the script runs the real removal on the real page
and captures the result, so the "avg 18.1s" style figures in it are true. Shots 1
and 3 are compositions, and shot 1 in particular draws its own copy of the
context menu — a native OS menu cannot be captured by any screenshot API, since
it is not part of the page. Its seven entries are generated from the same TOOLS
list that `extension/background.js` declares, so the picture cannot drift from
the menu a user actually sees.

Run:  venv/bin/python scripts/make-store-assets.py
      (needs the dev server up: venv/bin/python manage.py runserver 127.0.0.1:8877)
"""
import base64
import io
import pathlib
import re
import time

from PIL import Image
from playwright.sync_api import sync_playwright

OUT = pathlib.Path("dist/store")
DEV = "http://127.0.0.1:8877/"
PHOTO = pathlib.Path("static/img/demo-crop-before.webp")
ICON_SRC = pathlib.Path("static/img/icon-512.png")
BRAND = "#4F46E5"       # --color-primary
BRAND_DARK = "#4338CA"  # --color-primary-hover
FONT = "'Ubuntu Sans', 'DejaVu Sans', system-ui, sans-serif"


def tools():
    """The menu entries, read out of background.js so the two cannot disagree."""
    src = pathlib.Path("extension/background.js").read_text()
    block = src.split("const TOOLS = [", 1)[1].split("];", 1)[0]
    return re.findall(r"title:\s*'([^']+)'", block)


def data_uri(path):
    mime = "image/webp" if path.suffix == ".webp" else "image/png"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def trim_alpha(uri):
    """Crop a cutout to its subject.

    The cutout keeps the original's full canvas, so most of it is empty
    transparency. Dropped into the marquee's tall frame with object-fit:contain
    that renders the dog at half the size of the "before" beside it, which reads
    as a worse result rather than the same subject. Cropping to the alpha
    bounding box makes the two panels match.
    """
    raw = base64.b64decode(uri.split(",", 1)[1])
    im = Image.open(io.BytesIO(raw)).convert("RGBA")
    # Threshold first: the matte carries a wash of alpha=1..5 noise across the
    # whole canvas, and getbbox() counts any non-zero pixel, so the raw alpha
    # channel's bounding box is the entire image and the crop does nothing.
    alpha = im.split()[3].point(lambda a: 255 if a > 12 else 0)
    box = alpha.getbbox()
    if box:
        im = im.crop(box)
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def flatten(path, size):
    """Drop the alpha channel and assert the canvas is exactly right."""
    im = Image.open(path)
    if im.size != size:
        raise SystemExit(f"{path}: is {im.size}, must be {size}")
    # Composite onto white rather than just discarding alpha: discarding leaves
    # whatever garbage sat under transparent pixels.
    bg = Image.new("RGB", im.size, "white")
    bg.paste(im.convert("RGBA"), mask=im.convert("RGBA").split()[3])
    bg.save(path, optimize=True)


def render(pg, html, size, out):
    pg.set_viewport_size({"width": size[0], "height": size[1]})
    pg.set_content(html, wait_until="load")
    pg.wait_for_timeout(400)  # let fonts settle before capturing
    pg.screenshot(path=str(out))
    flatten(out, size)
    print(f"  {out.name:28} {size[0]}x{size[1]}")


# --------------------------------------------------------------------------- #
# shared chrome for the compositions

BASE_CSS = f"""
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family:{FONT}; -webkit-font-smoothing:antialiased; }}
  .stage {{ width:100vw; height:100vh; display:flex; flex-direction:column;
            align-items:center; overflow:hidden; position:relative; }}
  .checker {{ background-image:
      conic-gradient(#e9e9ef 25%, #fff 0 50%, #e9e9ef 0 75%, #fff 0);
      background-size:22px 22px; }}
"""


def shot_right_click(photo):
    """The one shot that explains the product: the menu open over a real page."""
    items = "".join(f"<div class='mi'>{t}</div>" for t in tools())
    return f"""<style>{BASE_CSS}
  .stage {{ background:linear-gradient(150deg,#EEF0FF 0%,#F7F5FF 45%,#FDF6FF 100%); }}
  .cap {{ padding:52px 0 30px; text-align:center; }}
  .cap h1 {{ font-size:42px; font-weight:800; letter-spacing:-1.1px; color:#15162B; }}
  .cap p  {{ font-size:20px; color:#5A5B76; margin-top:10px; font-weight:400; }}
  .win {{ width:1080px; height:560px; background:#fff; border-radius:14px 14px 0 0;
          box-shadow:0 34px 70px -18px rgba(28,26,72,.42); overflow:hidden;
          border:1px solid rgba(20,20,60,.09); position:relative; }}
  .bar {{ height:44px; background:#F4F4F8; display:flex; align-items:center;
          gap:8px; padding:0 16px; border-bottom:1px solid #E6E6EF; }}
  .dot {{ width:11px; height:11px; border-radius:50%; }}
  .url {{ flex:1; margin-left:12px; height:26px; border-radius:13px; background:#fff;
          border:1px solid #E2E2ED; display:flex; align-items:center; padding:0 12px;
          font-size:12.5px; color:#75768C; }}
  .page {{ padding:34px 44px; display:flex; gap:34px; }}
  .col  {{ flex:1; }}
  .kicker {{ font-size:11px; letter-spacing:1.6px; color:{BRAND};
             font-weight:700; text-transform:uppercase; }}
  .col h2 {{ font-size:25px; color:#1B1C33; margin:10px 0 16px; letter-spacing:-.5px; }}
  .ln {{ height:9px; border-radius:5px; background:#EBEBF2; margin-bottom:11px; }}
  .photo {{ width:430px; height:322px; border-radius:9px; object-fit:cover;
            box-shadow:0 2px 10px rgba(20,20,60,.13); }}
  /* Chrome's own menu, redrawn: it is an OS surface, not page content — which is
     also why it lives on .stage and not inside .win, so it can overhang the
     window edge the way a real menu does instead of being clipped by it. */
  .menu {{ position:absolute; left:575px; top:290px; width:236px; background:#fff;
           border-radius:9px; padding:6px; font-size:13.5px; color:#1F1F27;
           box-shadow:0 2px 6px rgba(0,0,0,.10),0 12px 34px rgba(0,0,0,.24);
           border:1px solid rgba(0,0,0,.07); }}
  .mi {{ padding:7px 11px; border-radius:5px; white-space:nowrap; }}
  .sep {{ height:1px; background:#E7E7EE; margin:6px 9px; }}
  .on {{ background:{BRAND}; color:#fff; font-weight:600;
         display:flex; justify-content:space-between; align-items:center; }}
  .sub {{ position:absolute; left:228px; top:130px; width:222px; background:#fff;
          border-radius:9px; padding:6px; font-size:13.5px; color:#1F1F27;
          box-shadow:0 2px 6px rgba(0,0,0,.10),0 12px 34px rgba(0,0,0,.24);
          border:1px solid rgba(0,0,0,.07); }}
  .sub .mi:first-child {{ background:#F1F1F7; font-weight:600; }}
  .ic {{ width:17px; height:17px; vertical-align:-4px; margin-right:9px;
         border-radius:4px; }}
</style>
<div class="stage">
  <div class="cap">
    <h1>Right-click any image on the web</h1>
    <p>It opens in the tool you picked, already loaded.</p>
  </div>
  <div class="win">
    <div class="bar">
      <div class="dot" style="background:#FF5F57"></div>
      <div class="dot" style="background:#FEBC2E"></div>
      <div class="dot" style="background:#28C840"></div>
      <div class="url">someblog.com/best-dog-photos</div>
    </div>
    <div class="page">
      <div class="col">
        <div class="kicker">Photography</div>
        <h2>The good boy of the week</h2>
        <div class="ln" style="width:100%"></div><div class="ln" style="width:94%"></div>
        <div class="ln" style="width:97%"></div><div class="ln" style="width:72%"></div>
        <div class="ln" style="width:88%"></div><div class="ln" style="width:45%"></div>
      </div>
      <img class="photo" src="{photo}">
    </div>
  </div>
  <div class="menu">
    <div class="mi">Open image in new tab</div>
    <div class="mi">Save image as&hellip;</div>
    <div class="mi">Copy image</div>
    <div class="mi">Copy image address</div>
    <div class="sep"></div>
    <div class="mi on"><span><img class="ic" src="{{icon}}">ClearBG</span><span>&#9656;</span></div>
    <div class="mi">Inspect</div>
    <div class="sub">{items}</div>
  </div>
</div>"""


def shot_nothing_uploaded(photo, icon):
    return f"""<style>{BASE_CSS}
  .stage {{ background:#0E0F1C; justify-content:center; color:#fff; }}
  .glow {{ position:absolute; width:900px; height:900px; border-radius:50%;
           background:radial-gradient(circle,rgba(79,70,229,.42),transparent 68%);
           top:-330px; }}
  h1 {{ font-size:47px; font-weight:800; letter-spacing:-1.3px; z-index:1;
        text-align:center; line-height:1.15; }}
  .sub {{ font-size:20px; color:#A9AAC6; margin-top:16px; z-index:1;
          text-align:center; max-width:720px; line-height:1.5; }}
  .flow {{ display:flex; align-items:center; gap:26px; margin-top:56px; z-index:1; }}
  .box {{ background:rgba(255,255,255,.055); border:1px solid rgba(255,255,255,.12);
          border-radius:16px; padding:20px 22px; text-align:center; }}
  .box img {{ width:118px; height:88px; object-fit:cover; border-radius:8px; }}
  .box .lbl {{ font-size:13px; color:#B9BAD4; margin-top:12px; font-weight:600; }}
  .dev {{ border-color:rgba(129,140,248,.5); background:rgba(79,70,229,.14); }}
  .dev .t {{ font-size:17px; font-weight:700; }}
  .dev .d {{ font-size:13px; color:#A9AAC6; margin-top:5px; }}
  .arrow {{ font-size:26px; color:#6C6E93; }}
  .cross {{ font-size:30px; color:#F0505C; font-weight:700; }}
  .off {{ opacity:.42; border-style:dashed; }}
  .cloud {{ font-size:40px; line-height:1; }}
  .foot {{ margin-top:52px; font-size:15px; color:#8C8EAE; z-index:1; }}
</style>
<div class="stage">
  <div class="glow"></div>
  <h1>Your images never leave your computer</h1>
  <div class="sub">There is no upload. The AI runs on your own device, in your
    browser &mdash; we don't receive your files, so we can't do anything with them.</div>
  <div class="flow">
    <div class="box"><img src="{photo}"><div class="lbl">The image on the page</div></div>
    <div class="arrow">&#8594;</div>
    <div class="box dev">
      <img src="{icon}" style="width:52px;height:52px;object-fit:contain">
      <div class="t" style="margin-top:8px">Processed on your device</div>
      <div class="d">Background removal, crop, compress</div>
    </div>
    <div class="cross">&#10005;</div>
    <div class="box off"><div class="cloud">&#9729;</div>
      <div class="lbl" style="margin-top:14px">Never sent to a server</div></div>
  </div>
  <div class="foot">Free &middot; no account &middot; no sign-up</div>
</div>"""


def tile_small(icon):
    return f"""<style>{BASE_CSS}
  .stage {{ background:linear-gradient(135deg,{BRAND} 0%,{BRAND_DARK} 55%,#6D28D9 100%);
            justify-content:center; color:#fff; }}
  img {{ width:74px; height:74px; }}
  h1 {{ font-size:34px; font-weight:800; letter-spacing:-.9px; margin-top:14px; }}
  p {{ font-size:14.5px; color:#DCDBFB; margin-top:9px; text-align:center;
       line-height:1.45; max-width:330px; }}
</style>
<div class="stage">
  <img src="{icon}">
  <h1>ClearBG</h1>
  <p>Right-click any image &mdash; remove the background, crop, compress</p>
</div>"""


def tile_marquee(photo, cutout, icon):
    return f"""<style>{BASE_CSS}
  .stage {{ background:linear-gradient(115deg,#1B1A3F 0%,{BRAND_DARK} 58%,#6D28D9 100%);
            flex-direction:row; align-items:center; justify-content:center;
            gap:66px; color:#fff; }}
  .left {{ width:600px; }}
  .brand {{ display:flex; align-items:center; gap:13px; }}
  .brand img {{ width:44px; height:44px; }}
  .brand span {{ font-size:26px; font-weight:800; letter-spacing:-.5px; }}
  h1 {{ font-size:44px; font-weight:800; letter-spacing:-1.2px; margin-top:24px;
        line-height:1.13; }}
  p {{ font-size:18px; color:#CFCEF6; margin-top:16px; line-height:1.5; }}
  .pills {{ display:flex; gap:8px; margin-top:24px; flex-wrap:wrap; }}
  .pill {{ font-size:13px; padding:6px 13px; border-radius:20px;
           background:rgba(255,255,255,.13); border:1px solid rgba(255,255,255,.2); }}
  .pair {{ display:flex; gap:16px; }}
  figure {{ text-align:center; }}
  figure img {{ width:236px; height:300px; object-fit:cover; border-radius:13px;
                box-shadow:0 22px 44px -12px rgba(0,0,0,.55); }}
  figcaption {{ font-size:12.5px; color:#BDBCEB; margin-top:11px;
                letter-spacing:1.3px; text-transform:uppercase; font-weight:700; }}
</style>
<div class="stage">
  <div class="left">
    <div class="brand"><img src="{icon}"><span>ClearBG</span></div>
    <h1>Cut out any image on the web in one right-click</h1>
    <p>No downloading, no re-uploading. The AI runs on your device &mdash;
       your images never leave your computer.</p>
    <div class="pills">
      <div class="pill">Remove background</div><div class="pill">Crop</div>
      <div class="pill">Compress</div><div class="pill">Convert</div>
      <div class="pill">Resize</div><div class="pill">Strip EXIF</div>
    </div>
  </div>
  <div class="pair">
    <figure><img src="{photo}"><figcaption>Right-click</figcaption></figure>
    <figure><img class="checker" src="{cutout}" style="object-fit:contain">
      <figcaption>Done</figcaption></figure>
  </div>
</div>"""


def capture_tool_page(pg):
    """Run the real removal on the real page; return the cutout as a data URI."""
    pg.set_viewport_size({"width": 1280, "height": 800})
    pg.goto(DEV, wait_until="domcontentloaded")
    pg.set_input_files("input[type=file]", str(PHOTO))
    for _ in range(150):
        if pg.evaluate("()=>document.querySelector('#results-grid .card')?.dataset.state") == "done":
            break
        time.sleep(1)
    else:
        raise SystemExit("removal never finished — is the CDN reachable?")

    # Leave the comparison slider at its default half-and-half: original on the
    # left, cutout on the right is the frame that shows what the tool did. (Its
    # scale runs the other way from what you would guess — 100 is *all original*,
    # so driving it "fully across" hides the result entirely.) Only the just-done
    # flourish has to go: it drops a green tick over the middle of the image.
    pg.evaluate("""()=>{
      document.querySelector('#results-grid .card')?.classList.remove('just-done');
    }""")
    # Frame it by hand. scrollIntoView({block:'center'}) centres the whole card,
    # which is tall enough that the preview leaves the top of the viewport and the
    # shot becomes a picture of the controls panel.
    pg.evaluate("""()=>{
      const c=document.querySelector('#results-grid .card');
      window.scrollTo(0, Math.max(0, c.getBoundingClientRect().top + window.scrollY - 110));
    }""")
    pg.wait_for_timeout(1800)

    out = OUT / "shot-2-in-the-tool.png"
    pg.screenshot(path=str(out))
    flatten(out, (1280, 800))
    print(f"  {out.name:28} 1280x800  (real capture)")

    return pg.evaluate("""async ()=>{
      const img=document.querySelector('#results-grid .card .processed-img');
      const c=document.createElement('canvas');
      c.width=img.naturalWidth; c.height=img.naturalHeight;
      c.getContext('2d').drawImage(img,0,0);
      return c.toDataURL('image/png');
    }""")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    photo = data_uri(PHOTO)
    icon = data_uri(ICON_SRC)

    # The store icon: 128x128 exactly, and the only asset that keeps its alpha.
    Image.open(ICON_SRC).convert("RGBA").resize((128, 128), Image.LANCZOS).save(
        OUT / "store-icon-128.png", optimize=True)
    print(f"  {'store-icon-128.png':28} 128x128   (alpha kept)")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        pg = browser.new_page(device_scale_factor=1)
        pg.on("pageerror", lambda e: print("PAGEERROR", e))

        cutout = trim_alpha(capture_tool_page(pg))

        render(pg, shot_right_click(photo).replace("{icon}", icon),
               (1280, 800), OUT / "shot-1-right-click.png")
        render(pg, shot_nothing_uploaded(photo, icon),
               (1280, 800), OUT / "shot-3-nothing-uploaded.png")
        render(pg, tile_small(icon), (440, 280), OUT / "tile-small.png")
        render(pg, tile_marquee(photo, cutout, icon), (1400, 560), OUT / "tile-marquee.png")

        browser.close()

    print(f"\n{len(list(OUT.iterdir()))} assets in {OUT}/")


if __name__ == "__main__":
    main()
