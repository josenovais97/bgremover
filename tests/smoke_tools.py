#!/usr/bin/env python3
"""
End-to-end smoke test for the 1.10 tools, driven with Playwright/Chromium.

Covers what the Django suite can't: that the client-side pipelines actually run
in a browser — the HEIC decoder decodes, pdf.js renders a page, Tesseract reads
text, the SVG rasteriser exports, the diffusion fill erases, pica upscales, the
filters export downloads, and the compress hero collapses on upload.

Prereqs:
  - The dev server running:  python manage.py runserver 127.0.0.1:8877
  - Playwright + Chromium:    pip install playwright && playwright install chromium
  - Network access (heic2any / pdf.js / tesseract / pica load from the CDN on
    first use; the OCR check also downloads a language pack).

Env:
  BASE_URL   default http://127.0.0.1:8877

Run:  python tests/smoke_tools.py     (exit code 0 = pass; each check reports)
"""
import os
import sys
import tempfile
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = os.environ.get("BASE_URL", "http://127.0.0.1:8877")
FIXTURES = Path(__file__).parent / "fixtures"
PNG_FIXTURE = str(FIXTURES / "sample.png")
HEIC_FIXTURE = str(FIXTURES / "sample.heic")

failures = []


def check(name):
    def deco(fn):
        fn._check_name = name
        return fn
    return deco


def make_pdf(path):
    """A minimal one-page PDF with real text — no library needed."""
    objs = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R "
        b"/Resources << /Font << /F1 5 0 R >> >> >>",
    ]
    stream = b"BT /F1 36 Tf 72 700 Td (Hello ClearBG PDF) Tj ET"
    objs.append(b"<< /Length %d >>\nstream\n%s\nendstream" % (len(stream), stream))
    objs.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    out = b"%PDF-1.4\n"
    offsets = []
    for i, o in enumerate(objs, 1):
        offsets.append(len(out))
        out += b"%d 0 obj\n%s\nendobj\n" % (i, o)
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1)
    for off in offsets:
        out += b"%010d 00000 n \n" % off
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF" % (len(objs) + 1, xref)
    Path(path).write_bytes(out)


def make_svg(path):
    Path(path).write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="100" viewBox="0 0 200 100">'
        '<rect width="200" height="100" rx="12" fill="#4f46e5"/>'
        '<circle cx="60" cy="50" r="30" fill="#f59e0b"/></svg>'
    )


def make_text_png(path):
    """Text rendered onto a canvas by the browser itself, saved as a PNG —
    keeps this script free of any imaging dependency."""
    return path  # generated in-browser; see ocr()


@check("remove-object: brush + erase enables undo")
def remove_object(pg):
    pg.goto(f"{BASE}/remove-object/", wait_until="networkidle")
    pg.set_input_files("#ro-input", PNG_FIXTURE)
    pg.wait_for_selector("#ro-editor:not(.hidden)", timeout=8000)
    box = pg.locator("#ro-overlay").bounding_box()
    cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    pg.mouse.move(cx - 40, cy)
    pg.mouse.down()
    pg.mouse.move(cx + 40, cy, steps=8)
    pg.mouse.up()
    pg.click("#ro-apply")
    pg.wait_for_function(
        "() => document.querySelector('#ro-busy').classList.contains('hidden')"
        " && !document.querySelector('#ro-undo').disabled",
        timeout=30000,
    )


@check("upscale: pica run enables download")
def upscale(pg):
    pg.goto(f"{BASE}/upscale/", wait_until="networkidle")
    pg.set_input_files("#up-input", PNG_FIXTURE)
    pg.wait_for_selector("#up-editor:not(.hidden)", timeout=8000)
    pg.click("#up-run")
    pg.wait_for_selector("#up-download:not([disabled])", timeout=60000)


@check("heic: real .heic decodes to a downloadable card")
def heic(pg):
    pg.goto(f"{BASE}/heic-to-jpg/", wait_until="networkidle")
    pg.set_input_files("#hc-input", HEIC_FIXTURE)
    pg.wait_for_selector("#hc-grid .card .download-btn:not([disabled])", timeout=90000)


@check("pdf-to-image: page renders and downloads")
def pdf_to_image(pg, tmp):
    pdf = str(Path(tmp) / "sample.pdf")
    make_pdf(pdf)
    pg.goto(f"{BASE}/pdf-to-image/", wait_until="networkidle")
    pg.set_input_files("#p2i-input", pdf)
    pg.wait_for_selector("#p2i-grid .card .download-btn:not([disabled])", timeout=90000)


@check("ocr: tesseract reads canvas-rendered text")
def ocr(pg, tmp):
    # Render clean text to a PNG with the browser itself, so this script needs
    # no imaging library.
    pg.goto(f"{BASE}/image-to-text/", wait_until="domcontentloaded")
    data_url = pg.evaluate(
        """() => {
            const c = document.createElement('canvas');
            c.width = 900; c.height = 240;
            const x = c.getContext('2d');
            x.fillStyle = '#fff'; x.fillRect(0, 0, 900, 240);
            x.fillStyle = '#000'; x.font = '48px sans-serif';
            x.fillText('The quick brown fox', 40, 100);
            x.fillText('jumps over the lazy dog', 40, 180);
            return c.toDataURL('image/png');
        }"""
    )
    import base64
    png = str(Path(tmp) / "ocr.png")
    Path(png).write_bytes(base64.b64decode(data_url.split(",", 1)[1]))
    pg.goto(f"{BASE}/image-to-text/", wait_until="networkidle")
    pg.set_input_files("#oc-input", png)
    for _ in range(120):
        value = pg.evaluate("() => document.querySelector('#oc-text').value")
        if "quick brown fox" in value.lower():
            return
        time.sleep(1)
    raise AssertionError("OCR never produced the expected text")


@check("svg-to-png: export downloads a PNG at the chosen size")
def svg_to_png(pg, tmp):
    svg = str(Path(tmp) / "sample.svg")
    make_svg(svg)
    pg.goto(f"{BASE}/svg-to-png/", wait_until="networkidle")
    pg.set_input_files("#sv-input", svg)
    pg.wait_for_selector("#sv-editor:not(.hidden)", timeout=8000)
    assert "200×100" in pg.locator("#sv-size").text_content()
    with pg.expect_download(timeout=15000) as dl:
        pg.click("#sv-download")
    assert dl.value.suggested_filename.endswith(".png"), dl.value.suggested_filename


@check("photo-filters: look + export downloads")
def photo_filters(pg):
    pg.goto(f"{BASE}/photo-filters/", wait_until="networkidle")
    pg.set_input_files("#pf-input", PNG_FIXTURE)
    pg.wait_for_selector("#pf-editor:not(.hidden)", timeout=8000)
    pg.click("text=Vivid")
    pg.wait_for_timeout(400)
    with pg.expect_download(timeout=15000) as dl:
        pg.click("#pf-download")
    assert dl.value.suggested_filename.endswith(".jpg"), dl.value.suggested_filename


@check("compress: hero collapses on upload; summary appears")
def compress_collapse(pg):
    pg.goto(f"{BASE}/compress/", wait_until="networkidle")
    pg.set_input_files("#cmp-input", PNG_FIXTURE)
    pg.wait_for_function(
        "() => document.querySelector('#cmp-dropzone').closest('section').classList.contains('hidden')",
        timeout=15000,
    )
    pg.wait_for_function(
        "() => (document.querySelector('#cmp-summary').textContent || '').length > 0",
        timeout=15000,
    )


CHECKS = [remove_object, upscale, heic, pdf_to_image, ocr, svg_to_png,
          photo_filters, compress_collapse]


def main():
    with sync_playwright() as p, tempfile.TemporaryDirectory() as tmp:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1440, "height": 1000})
        pg = ctx.new_page()
        errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        for fn in CHECKS:
            name = fn._check_name
            errors.clear()
            try:
                if fn.__code__.co_argcount == 2:
                    fn(pg, tmp)
                else:
                    fn(pg)
                print(f"PASS  {name}" + (f"  (pageerrors: {errors})" if errors else ""))
            except Exception as exc:  # noqa: BLE001 — report and continue
                failures.append(name)
                print(f"FAIL  {name}: {type(exc).__name__}: {exc}  pageerrors={errors}")
        browser.close()
    if failures:
        print(f"\n{len(failures)} of {len(CHECKS)} checks failed")
        sys.exit(1)
    print(f"\nAll {len(CHECKS)} checks passed")


if __name__ == "__main__":
    main()
