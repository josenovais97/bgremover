#!/usr/bin/env python3
"""
End-to-end smoke test for the standalone Instagram editor (/instagram/).

Verifies the editor opens without background removal, filters and adjustment
sliders repaint the canvas, format switching changes the aspect, Fit mode and
borders repaint, the carousel splitter previews a panorama and exports a ZIP,
and single exports come out at Instagram's exact pixel size.

Prereqs (see tests/README.md): dev server running, Playwright + Chromium.
Run:  BASE_URL=http://127.0.0.1:8877 python tests/smoke_instagram.py
"""
import os
import struct
import sys
import tempfile
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8877")
FIXTURE = str(Path(__file__).parent / "fixtures" / "sample.png")
results = []


def check(name, cond):
    results.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}")


def jpeg_size(path):
    """Read (width, height) from a JPEG's first SOF marker — no image library."""
    with open(path, "rb") as f:
        data = f.read()
    i = 2
    while i < len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
            h, w = struct.unpack(">HH", data[i + 5:i + 9])
            return (w, h)
        seg = struct.unpack(">H", data[i + 2:i + 4])[0]
        i += 2 + seg
    return None


def snap(pg):
    """Hash the whole canvas so a repaint anywhere is detected (a fixed byte
    slice can miss changes that only touch edges or flat regions, e.g. sharpen)."""
    return pg.evaluate(
        "()=>{const c=document.querySelector('#ig-canvas');"
        "const d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;"
        "let h=0;for(let i=0;i<d.length;i+=53){h=(h*31+d[i])>>>0;}return h;}"
    )


def main():
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.goto(f"{BASE_URL}/instagram/", wait_until="domcontentloaded")

        pg.set_input_files("#ig-input", FIXTURE)
        time.sleep(0.6)
        check("editor opens on upload (no bg removal needed)",
              pg.evaluate("()=>!document.querySelector('#ig-editor').classList.contains('hidden')"))
        check("canvas is painted",
              pg.evaluate("()=>{const c=document.querySelector('#ig-canvas');return c.width>0&&c.height>0;}"))

        base = snap(pg)
        pg.click(".ig-filter[data-filter='vivid']")
        time.sleep(0.3)
        check("filter preset repaints the canvas", snap(pg) != base)

        # Regression: a preset with sharpen>0 must STILL grade colour. Noir sets
        # saturate:0 — the whole canvas should go greyscale. If sharpen were mixed
        # into ctx.filter as a url(), the grade would silently void and colour stay.
        pg.click(".ig-filter[data-filter='noir']")
        time.sleep(0.3)
        max_chroma = pg.evaluate(
            "()=>{const c=document.querySelector('#ig-canvas');"
            "const d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let m=0;"
            "for(let i=0;i<d.length;i+=400){m=Math.max(m,Math.abs(d[i]-d[i+1]),Math.abs(d[i+1]-d[i+2]));}return m;}"
        )
        check("sharpen-bearing preset still grades colour (Noir desaturates)", max_chroma < 12)

        # Filter strength dials a look back toward the original.
        pg.click(".ig-filter[data-filter='vivid']")
        time.sleep(0.2)
        full = snap(pg)
        pg.eval_on_selector("#ig-strength",
                            "el=>{el.value=0;el.dispatchEvent(new Event('input',{bubbles:true}));}")
        time.sleep(0.3)
        check("filter strength repaints the canvas", snap(pg) != full)

        # Reset first: vivid clamps this flat-block fixture to 0/255, where a
        # brightness *increase* is a no-op. Darkening from a clean state always moves pixels.
        pg.click(".ig-filter[data-filter='original']")
        time.sleep(0.2)
        mid = snap(pg)
        pg.eval_on_selector(".ig-adj[data-adj='brightness']",
                            "el=>{el.value=60;el.dispatchEvent(new Event('input',{bubbles:true}));}")
        time.sleep(0.3)
        check("adjustment slider repaints the canvas", snap(pg) != mid)

        pg.click(".ig-format[data-key='story']")
        time.sleep(0.3)
        ar = pg.evaluate("()=>{const c=document.querySelector('#ig-canvas');return c.width/c.height;}")
        check("Story format sets a 9:16 canvas", abs(ar - 0.5625) < 0.02)

        with pg.expect_download(timeout=8000) as di:
            pg.click("#ig-download")
        out = os.path.join(tempfile.gettempdir(), "ig_story.jpg")
        di.value.save_as(out)
        check("Story export is exactly 1080x1920", jpeg_size(out) == (1080, 1920))

        # Fit mode: whole photo, no crop — repaints and hides reposition.
        pre_fit = snap(pg)
        pg.click(".ig-fit[data-fit='fit']")
        time.sleep(0.3)
        check("Fit mode repaints the canvas", snap(pg) != pre_fit)
        check("Fit mode hides reposition controls",
              pg.evaluate("()=>document.querySelector('#ig-zoom-row').classList.contains('hidden')"))
        pg.click(".ig-fit[data-fit='fill']")
        time.sleep(0.2)

        # Border repaints the canvas.
        pre_border = snap(pg)
        pg.eval_on_selector("#ig-border",
                            "el=>{el.value=10;el.dispatchEvent(new Event('input',{bubbles:true}));}")
        time.sleep(0.3)
        check("Border repaints the canvas", snap(pg) != pre_border)
        pg.eval_on_selector("#ig-border",
                            "el=>{el.value=0;el.dispatchEvent(new Event('input',{bubbles:true}));}")
        time.sleep(0.2)

        # Sharpen repaints the canvas — from a clean (unclamped) state so the
        # sharpen convolution actually shifts edge pixels rather than re-clamping.
        pg.click(".ig-format[data-key='post']")
        pg.click(".ig-filter[data-filter='original']")
        time.sleep(0.3)
        pre_sharpen = snap(pg)
        pg.eval_on_selector(".ig-adj[data-adj='sharpen']",
                            "el=>{el.value=80;el.dispatchEvent(new Event('input',{bubbles:true}));}")
        time.sleep(0.3)
        check("Sharpen repaints the canvas", snap(pg) != pre_sharpen)

        # Grain repaints the canvas.
        pg.click(".ig-filter[data-filter='original']")
        time.sleep(0.2)
        pre_grain = snap(pg)
        pg.eval_on_selector(".ig-adj[data-adj='grain']",
                            "el=>{el.value=80;el.dispatchEvent(new Event('input',{bubbles:true}));}")
        time.sleep(0.3)
        check("Grain repaints the canvas", snap(pg) != pre_grain)

        # Press-and-hold compare shows the (unedited) original, then restores.
        pg.click(".ig-filter[data-filter='vintage']")
        time.sleep(0.2)
        edited = snap(pg)
        pg.dispatch_event("#ig-compare", "pointerdown")
        time.sleep(0.25)
        original_view = snap(pg)
        pg.dispatch_event("#ig-compare", "pointerup")
        time.sleep(0.25)
        check("compare shows the original then restores",
              original_view != edited and snap(pg) == edited)

        # Safe-zone guides overlay the frame (Story format).
        pg.click(".ig-format[data-key='story']")
        pg.click(".ig-filter[data-filter='original']")
        time.sleep(0.3)
        pre_safe = snap(pg)
        pg.click("#ig-safezones")
        time.sleep(0.3)
        check("safe-zone guides repaint the canvas", snap(pg) != pre_safe)
        pg.click("#ig-safezones")  # toggle back off
        time.sleep(0.2)

        # Carousel: 2 tiles at Post format previews a 2:1 panorama and exports a ZIP.
        pg.click(".ig-format[data-key='post']")
        pg.click(".ig-carousel[data-n='2']")
        time.sleep(0.3)
        ar2 = pg.evaluate("()=>{const c=document.querySelector('#ig-canvas');return c.width/c.height;}")
        check("2-tile carousel previews a 2:1 panorama", abs(ar2 - 2) < 0.05)
        with pg.expect_download(timeout=15000) as dz:
            pg.click("#ig-download")
        zp = os.path.join(tempfile.gettempdir(), "ig_carousel.zip")
        dz.value.save_as(zp)
        with open(zp, "rb") as fh:
            sig = fh.read(2)
        check("carousel exports a ZIP", sig == b"PK")

        check("no uncaught page errors", not errors)
        if errors:
            print("  page errors:", errors)
        b.close()

    failed = [n for n, ok in results if not ok]
    print(f"\n{len(failed)} FAILED" if failed else "\nAll Instagram smoke checks passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
