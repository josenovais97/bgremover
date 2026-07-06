#!/usr/bin/env python3
"""
End-to-end smoke test for the standalone crop tool (/crop/).

Verifies the editor opens without background removal, ratio presets change the
canvas aspect, the circle shape masks transparent corners and forces 1:1,
rotate swaps the aspect, and PNG/JPG exports download.

Prereqs (see tests/README.md): dev server running, Playwright + Chromium.
Run:  BASE_URL=http://127.0.0.1:8877 python tests/smoke_crop_page.py
"""
import os
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


def aspect(pg):
    return pg.evaluate("()=>{const c=document.querySelector('#cr-canvas');return c.width/c.height;}")


def main():
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.goto(f"{BASE_URL}/crop/", wait_until="domcontentloaded")

        pg.set_input_files("#cr-input", FIXTURE)
        time.sleep(0.5)
        check("editor opens on upload (no bg removal)",
              pg.evaluate("()=>!document.querySelector('#cr-editor').classList.contains('hidden')"))
        check("canvas is painted",
              pg.evaluate("()=>{const c=document.querySelector('#cr-canvas');return c.width>0&&c.height>0;}"))

        pg.click(".cr-ratio[data-ratio='1']")
        time.sleep(0.2)
        check("1:1 ratio makes a square canvas", abs(aspect(pg) - 1) < 0.02)

        pg.click(".cr-ratio[data-ratio='1.7778']")
        time.sleep(0.2)
        check("16:9 ratio sets a wide canvas", abs(aspect(pg) - 1.7778) < 0.03)

        # Circle shape: masks transparent corners and forces a 1:1 ratio.
        pg.click(".cr-shape[data-shape='circle']")
        time.sleep(0.2)
        check("circle shape forces a square canvas", abs(aspect(pg) - 1) < 0.02)
        corner_alpha = pg.evaluate(
            "()=>document.querySelector('#cr-canvas').getContext('2d').getImageData(0,0,1,1).data[3]"
        )
        check("circle masks transparent corners", corner_alpha == 0)

        # Rotate: on the Original ratio, a 90° turn swaps the aspect.
        pg.click(".cr-shape[data-shape='rect']")
        pg.click(".cr-ratio[data-ratio='free']")
        time.sleep(0.2)
        before = aspect(pg)
        pg.click("#cr-rotate-r")
        time.sleep(0.2)
        after = aspect(pg)
        check("rotate swaps the Original aspect", abs(after - 1 / before) < 0.03)

        # PNG export downloads a real PNG.
        pg.click(".cr-shape[data-shape='circle']")
        time.sleep(0.2)
        with pg.expect_download(timeout=8000) as dp:
            pg.click("#cr-download")
        pp = os.path.join(tempfile.gettempdir(), "crop.png")
        dp.value.save_as(pp)
        with open(pp, "rb") as fh:
            png_sig = fh.read(4)
        check("PNG export downloads a PNG", png_sig == b"\x89PNG")

        # JPG export downloads a real JPEG.
        pg.click(".cr-format[data-format='jpg']")
        time.sleep(0.1)
        with pg.expect_download(timeout=8000) as dj:
            pg.click("#cr-download")
        jp = os.path.join(tempfile.gettempdir(), "crop.jpg")
        dj.value.save_as(jp)
        with open(jp, "rb") as fh:
            jpg_sig = fh.read(2)
        check("JPG export downloads a JPEG", jpg_sig == b"\xff\xd8")

        check("no uncaught page errors", not errors)
        if errors:
            print("  page errors:", errors)
        b.close()

    failed = [n for n, ok in results if not ok]
    print(f"\n{len(failed)} FAILED" if failed else "\nAll crop-page smoke checks passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
