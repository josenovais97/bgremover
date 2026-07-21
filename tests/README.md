# Tests

Three layers:

1. **Django tests** (`remover/tests.py`) — fast, no browser, run in CI-style with
   `python manage.py test`.
2. **Geometry unit tests** — pure math, Node, no browser.
3. **Browser smoke tests** — Playwright + headless Chromium, for the behaviours the other
   two can't reach (DOM wiring, canvas work, focus, downloads).

---

## 1. Django tests (fast)

```bash
python manage.py test          # 62 tests
```

Covers page rendering, SEO endpoints (robots/sitemap/canonical/FAQ + Organization schema),
the use-case / country / landing page sets, i18n routing and hreflang, the PWA manifest and
service worker, ad gating, and the health check.

Three suites here are guard rails for things that break *silently*, so read the failure
before "fixing" the test:

- **`AccentContrastTests`** recomputes the WCAG contrast ratio of every entry in
  `TOOL_ACCENTS` (surface vs white, text pair vs the dark glass surface). A new accent that
  looks fine but dips under AA fails here.
- **`AccentWiringTests`** asserts gradient headlines use the *text* pair
  (`primaryText`/`primaryTextAlt`), not the surface pair — using `text-primary` is the bug
  this exists to catch.
- **`IconSubsetTests`** scans the templates for `fa-*` classes and fails on any glyph that
  isn't in the committed Font Awesome subset (`static/css/fontawesome.css`). Out-of-subset
  icons render as blank boxes in the browser with no error.

## 2. Geometry unit tests (fast, no browser)

Pure-math checks for the shared `cropGeometry()` helper — the code the live preview and the
final export both depend on. The test pulls the function straight out of
`static/js/app.js`, so it always exercises the shipped code.

```bash
node tests/crop-geometry.test.mjs
# or
npm test
```

No dependencies beyond Node. Exit code `0` = pass.

## 3. Browser smoke tests (end-to-end)

Common prerequisites:

```bash
# 1. start the app
python manage.py runserver 127.0.0.1:8877

# 2. one-time setup
pip install playwright && playwright install chromium
```

They need network access — the removal model and the CDN libraries load on first use.
Override the target with `BASE_URL=https://… python tests/<file>.py`.

| File | What it guards |
|------|----------------|
| `smoke_crop.py` | Uploads an image, opens the crop dialog *before* removal finishes, checks the Original/Cut-out source toggle, applies crops, downloads. |
| `smoke_colorpicker.py` | The in-page colour picker + the main flow (see below). |
| `smoke_crop_page.py` | The standalone `/crop/` page. |
| `smoke_instagram.py` | The Instagram editor. |

**Why `smoke_colorpicker.py` is worth the runtime:** the native `<input type="color">`
dialog's built-in **EyeDropper** froze the tab, which is why `static/js/colorpicker.js`
replaced it. The test checks that every colour input is enhanced with a `.cp-trigger` and
the native dialog is suppressed, that the popover opens, that an arbitrary hex applies,
that "Pick from image" samples the pixel under the pointer, and — via a constructor spy —
that `EyeDropper` is **never** constructed. It then runs the main flow end-to-end: waits
for removal, applies a custom background *through the picker*, and exports a fixed-size
PNG.

`tests/fixtures/sample.png` is the input image every layer uses.

---

## Not covered

Most tools have no automated coverage at all — compress, convert, resize, watermark, GIF,
QR, EXIF, redact, meme, favicon, sticker, passport, blur, eCommerce and text-behind are
verified by hand. The `run` skill (`.claude/skills/run/SKILL.md`) drives the app in a
browser for manual verification of a change.
