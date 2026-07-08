#!/usr/bin/env python3
"""
End-to-end smoke test for the in-page colour picker and the main bg-removal
flow (upload -> remove -> style -> export), driven with Playwright/Chromium.

The picker (static/js/colorpicker.js) replaced the native <input type="color">
because the native dialog's built-in EyeDropper hangs the browser on some
systems — that was the freeze. This test locks in the behaviours that guard
against a regression:

  - every colour input is enhanced with a `.cp-trigger` and the native dialog
    is suppressed (a click on the hidden input is preventDefault-ed);
  - clicking a trigger opens the popover;
  - typing an arbitrary hex applies it to the underlying input;
  - the EyeDropper API is never constructed, even during "Pick from image";
  - "Pick from image" samples the pixel under the pointer via getImageData.

It then exercises the real flow: waits for background removal, applies a custom
background *through the picker*, and exports a fixed-size PNG.

Prereqs:
  - The dev server running:  python manage.py runserver 127.0.0.1:8877
  - Playwright + Chromium:    pip install playwright && playwright install chromium
  - Network access (the background-removal model loads from a CDN on first use).

Env:
  BASE_URL   default http://127.0.0.1:8877

Run:  python tests/smoke_colorpicker.py     (exit code 0 = pass)
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

# Colour we paint onto an injected canvas and expect "Pick from image" to read back.
SAMPLE_HEX = "#3a7bd5"

results = []


def check(name, cond):
    results.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        pg = browser.new_page(viewport={"width": 1280, "height": 800})

        # Spy on the EyeDropper constructor before any app code runs. If the picker
        # ever touches it (the freeze), the flag flips and the test fails.
        pg.add_init_script(
            "window.__eyedropperUsed = false;"
            "window.EyeDropper = function () {"
            "  window.__eyedropperUsed = true;"
            "  return { open: function () { return Promise.resolve({ sRGBHex: '#000000' }); } };"
            "};"
        )

        errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.goto(BASE_URL, wait_until="domcontentloaded")
        pg.set_input_files("input[type=file]", FIXTURE)
        pg.wait_for_selector(".card .options-btn", timeout=5000)

        # Reveal the options panel so its colour inputs (and their triggers) exist.
        pg.click(".card .options-btn")
        pg.wait_for_selector(".custom-color + .cp-trigger", timeout=3000)

        # --- Progressive enhancement + native-dialog suppression -----------------
        check(
            "every colour input is hidden and gets a .cp-trigger",
            pg.evaluate(
                "() => [...document.querySelectorAll('.card input[type=color]')].every("
                "  i => getComputedStyle(i).display === 'none'"
                "    && i.nextElementSibling && i.nextElementSibling.classList.contains('cp-trigger'))"
            ),
        )
        check(
            "a click on the native colour input is preventDefault-ed",
            pg.evaluate(
                "() => {"
                "  const i = document.querySelector('.custom-color');"
                "  const ev = new MouseEvent('click', { cancelable: true, bubbles: true });"
                "  return i.dispatchEvent(ev) === false;"  # false == default prevented
                "}"
            ),
        )

        # --- Picker opens --------------------------------------------------------
        pg.click(".custom-color + .cp-trigger")
        time.sleep(0.2)
        check(
            "clicking the trigger opens the picker popover",
            pg.evaluate("() => { const p = document.querySelector('.cp-pop'); "
                        "return !!p && getComputedStyle(p).display !== 'none'; }"),
        )

        # --- Arbitrary hex applies to the underlying input -----------------------
        pg.fill(".cp-hex", "#123456")
        time.sleep(0.1)
        check(
            "typing an arbitrary hex updates the underlying colour input",
            pg.eval_on_selector(".custom-color", "i => i.value.toLowerCase()") == "#123456",
        )

        # --- No EyeDropper before we even touch "Pick from image" ----------------
        check("EyeDropper API not constructed by opening/using the picker",
              pg.evaluate("() => window.__eyedropperUsed === false"))

        # --- "Pick from image" samples the pixel under the pointer ---------------
        # Enter sample mode first (the button must be clickable), THEN paint a
        # full-viewport canvas a known colour so the sampled value is deterministic.
        pg.click(".cp-pick")
        pg.evaluate(
            "(hex) => {"
            "  const c = document.createElement('canvas');"
            "  c.id = '__probe'; c.width = window.innerWidth; c.height = window.innerHeight;"
            "  c.style.cssText = 'position:fixed;inset:0;z-index:99999';"
            "  const g = c.getContext('2d'); g.fillStyle = hex;"
            "  g.fillRect(0, 0, c.width, c.height);"
            "  document.body.appendChild(c);"
            "}",
            SAMPLE_HEX,
        )
        time.sleep(0.15)  # the sampler binds its click listener on a 0ms timeout
        pg.mouse.click(640, 400)
        time.sleep(0.2)
        check(
            "'Pick from image' reads the sampled pixel colour",
            pg.eval_on_selector(".custom-color", "i => i.value.toLowerCase()") == SAMPLE_HEX,
        )
        check("EyeDropper API still not constructed after sampling",
              pg.evaluate("() => window.__eyedropperUsed === false"))
        pg.evaluate("() => document.getElementById('__probe')?.remove()")
        pg.keyboard.press("Escape")  # sampling re-shows the popover; close it cleanly
        time.sleep(0.2)

        # --- Main flow: wait for removal, apply a custom bg via the picker, export
        done = False
        for _ in range(90):
            if pg.evaluate("() => document.querySelector('.card')?.dataset.state === 'done'"):
                done = True
                break
            time.sleep(1)
        check("background removal completes", done)

        # Re-open the picker and set a custom background through it — the picker's
        # dispatched `input` event is what drives setBackground() in the app.
        pg.click(".custom-color + .cp-trigger")
        time.sleep(0.2)
        pg.fill(".cp-hex", "#204060")
        time.sleep(0.5)  # setBackground() composites on the next frame (rafThrottle)
        check(
            "custom background from the picker composites into the preview",
            pg.evaluate("() => document.querySelector('.processed-img').src.startsWith('blob:')"),
        )

        # Export at a fixed size and confirm the PNG really is that size.
        pg.click(".size-btn[data-size='512x512']")
        time.sleep(0.2)
        try:
            with pg.expect_download(timeout=8000) as di:
                pg.click(".download-btn")
            out = os.path.join(tempfile.gettempdir(), "smoke_colorpicker.png")
            di.value.save_as(out)
            check("styled export is a 512x512 PNG", png_size(out) == (512, 512))
        except Exception as e:  # noqa: BLE001
            check(f"styled export is a 512x512 PNG ({e})", False)

        check("no uncaught page errors", not errors)
        if errors:
            print("  page errors:", errors)
        browser.close()

    failed = [n for n, ok in results if not ok]
    print(f"\n{len(failed)} FAILED" if failed else "\nAll smoke checks passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
