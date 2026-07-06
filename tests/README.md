# Tests

Two layers, matching where the crop logic's risk actually lives.

## 1. Geometry unit tests (fast, no browser)

Pure-math checks for the shared `cropGeometry()` helper — the code the live
preview and the final export both depend on. The test pulls the function
straight out of `static/js/app.js`, so it always exercises the shipped code.

```bash
node tests/crop-geometry.test.mjs
# or
npm test
```

No dependencies beyond Node. Exit code `0` = pass.

## 2. Crop smoke test (browser, end-to-end)

Drives the real app in headless Chromium: uploads an image, opens the crop
dialog *before* background removal finishes, checks the Original/Cut-out source
toggle, applies crops, and downloads. Covers what unit tests can't (DOM wiring,
canvas masking, focus, downloads).

```bash
# 1. start the app
python manage.py runserver 127.0.0.1:8877

# 2. one-time setup
pip install playwright && playwright install chromium

# 3. run it (needs network — the removal model loads from a CDN on first use)
python tests/smoke_crop.py
```

Override the target with `BASE_URL=https://… python tests/smoke_crop.py`.

`tests/fixtures/sample.png` is the input image both layers use.
