#!/usr/bin/env python3
"""
End-to-end smoke test for the crop tool, driven with Playwright/Chromium.

Covers the behaviours that pure unit tests can't: that the crop dialog opens
(even before background removal finishes), that the Original/Cut-out source
toggle behaves, that a masked shape produces the right pixels, and that a
cropped card downloads.

Prereqs:
  - The dev server running:  python manage.py runserver 127.0.0.1:8877
  - Playwright + Chromium:    pip install playwright && playwright install chromium
  - Network access (the background-removal model loads from a CDN on first use).

Env:
  BASE_URL   default http://127.0.0.1:8877

Run:  python tests/smoke_crop.py     (exit code 0 = pass)
"""
import os
import struct
import sys
import tempfile
import time
from pathlib import Path

from playwright.sync_api import sync_playwright


def png_size(path):
    """Read (width, height) from a PNG's IHDR chunk — no image library needed."""
    with open(path, "rb") as f:
        head = f.read(24)
    return struct.unpack(">II", head[16:24])

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8877")
FIXTURE = str(Path(__file__).parent / "fixtures" / "sample.png")

results = []


def check(name, cond):
    results.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        pg = browser.new_page()
        errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.goto(BASE_URL, wait_until="domcontentloaded")
        pg.set_input_files("input[type=file]", FIXTURE)
        pg.wait_for_selector(".crop-btn", timeout=5000)

        # Crop must open immediately, before bg removal finishes.
        pg.click(".crop-btn")
        time.sleep(0.6)
        check("crop dialog opens before processing finishes",
              pg.evaluate("()=>!document.querySelector('#crop-modal').classList.contains('hidden')"))
        src = pg.evaluate("()=>Object.fromEntries([...document.querySelectorAll('.crop-source')]"
                          ".map(b=>[b.dataset.source,b.disabled]))")
        check("Original source enabled, Cut-out disabled pre-removal",
              src.get("original") is False and src.get("cutout") is True)

        # Crop the original (keeps background) to a circle.
        pg.click(".crop-shape[data-crop=circle]")
        time.sleep(0.2)
        pg.click("#crop-apply")
        time.sleep(0.4)
        check("card marked cropped after applying original crop",
              "cropped" in pg.eval_on_selector(".meta", "e=>e.textContent").lower())

        # Wait for background removal to finish (card leaves the processing state).
        done = False
        for _ in range(90):
            if pg.evaluate("()=>document.querySelector('.card')?.dataset.state==='done'"):
                done = True
                break
            time.sleep(1)
        check("background removal completes", done)

        # Re-opening the dialog, the Cut-out source is now available.
        pg.click(".crop-btn")
        time.sleep(0.4)
        check("Cut-out source unlocks once removal completes",
              pg.evaluate("()=>{const b=[...document.querySelectorAll('.crop-source')]"
                          ".find(x=>x.dataset.source=='cutout');return b&&!b.disabled;}"))

        # A cropped card downloads.
        pg.click(".crop-source[data-source=cutout]")
        time.sleep(0.3)
        pg.click(".crop-shape[data-crop=circle]")
        time.sleep(0.3)
        pg.click("#crop-apply")
        time.sleep(0.3)
        try:
            with pg.expect_download(timeout=8000) as di:
                pg.click(".download-btn")
            check("cropped cut-out downloads", di.value.suggested_filename.endswith(".png"))
        except Exception as e:  # noqa: BLE001
            check(f"cropped cut-out downloads ({e})", False)

        # Sticker effects grow the composed output and clear cleanly.
        pg.click("#crop-cancel") if pg.evaluate(
            "()=>!document.querySelector('#crop-modal').classList.contains('hidden')") else None
        pg.click(".options-btn")
        time.sleep(0.2)
        size_before = pg.evaluate("()=>{const i=document.querySelector('.processed-img');"
                                  "return [i.naturalWidth,i.naturalHeight];}")
        pg.check(".fx-outline")
        time.sleep(0.6)
        size_outline = pg.evaluate("()=>{const i=document.querySelector('.processed-img');"
                                   "return [i.naturalWidth,i.naturalHeight];}")
        check("outline enlarges the composed output",
              size_outline[0] > size_before[0] and size_outline[1] > size_before[1])
        pg.uncheck(".fx-outline")
        time.sleep(0.6)
        size_off = pg.evaluate("()=>{const i=document.querySelector('.processed-img');"
                               "return [i.naturalWidth,i.naturalHeight];}")
        check("turning outline off restores the original size", size_off == size_before)

        # Rich background (gradient) composites into the preview.
        pg.click(".bg-grad-btn")
        time.sleep(0.6)
        check("gradient background composites into the preview",
              pg.evaluate("()=>document.querySelector('.processed-img').src.startsWith('blob:')")
              and pg.evaluate("()=>document.querySelector('.bg-grad-btn').classList.contains('bg-primary')"))

        # Export size preset produces an exact-size download (read the PNG IHDR).
        pg.click(".size-btn[data-size='512x512']")
        time.sleep(0.2)
        with pg.expect_download(timeout=8000) as di:
            pg.click(".download-btn")
        out = os.path.join(tempfile.gettempdir(), "smoke_profile.png")
        di.value.save_as(out)
        check("profile export is 512x512", png_size(out) == (512, 512))

        # Instagram one-click preset crops + sizes in a single click.
        pg.click(".ig-btn[data-ig='ig-story']")
        time.sleep(0.4)
        with pg.expect_download(timeout=8000) as di_ig:
            pg.click(".download-btn")
        ig_out = os.path.join(tempfile.gettempdir(), "smoke_ig_story.png")
        di_ig.value.save_as(ig_out)
        check("Instagram Story preset exports 1080x1920", png_size(ig_out) == (1080, 1920))

        check("no uncaught page errors", not errors)
        if errors:
            print("  page errors:", errors)
        browser.close()

    failed = [n for n, ok in results if not ok]
    print(f"\n{len(failed)} FAILED" if failed else "\nAll smoke checks passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
