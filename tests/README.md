# Tests

Two layers: fast pure-math unit tests, plus browser smoke tests that drive the
real app in headless Chromium for the behaviours unit tests can't reach (DOM
wiring, canvas work, focus, downloads).

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

## 3. Colour picker + main-flow smoke test (browser, end-to-end)

Guards the in-page colour picker (`static/js/colorpicker.js`) that replaced the
native `<input type="color">` — the native dialog's built-in **EyeDropper** was
the freeze, so the picker must never touch that API. Drives the real app: checks
that every colour input is enhanced with a `.cp-trigger` and the native dialog is
suppressed, that the popover opens, that an arbitrary hex applies, that "Pick
from image" samples the pixel under the pointer, and — via a constructor spy —
that `EyeDropper` is never constructed. Then runs the main flow end-to-end:
waits for removal, applies a custom background *through the picker*, and exports
a fixed-size PNG.

```bash
# same prereqs as the crop smoke test (dev server + Playwright/Chromium + network)
python tests/smoke_colorpicker.py
```

Other browser smoke tests follow the same pattern: `smoke_crop_page.py` (the
standalone crop page) and `smoke_instagram.py` (the Instagram editor).

`tests/fixtures/sample.png` is the input image every layer uses.
