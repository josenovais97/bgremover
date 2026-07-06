---
name: run
description: Launch and drive the BG Remover app to verify a change works end-to-end. Use when asked to run/start/screenshot the app, or to confirm a UI change (crop tool, refine editor, background/format, converter) actually works in the browser rather than only in unit tests.
---

# Running BG Remover

A Django app whose real logic is **client-side JS** (`static/js/app.js`): background
removal, crop, refine, and export all run in the browser. So "running it" means
launching the dev server and driving the page in a headless browser — not hitting
an API.

## 1. Start the dev server

```bash
venv/bin/python manage.py runserver 127.0.0.1:8877 >/tmp/dj.log 2>&1 &
# wait until it answers
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8877/   # expect 200
```

Settings default to `config.settings.development` (DEBUG=True), which serves
`static/` directly — no `collectstatic` needed. After editing `templates/` the
StatReloader picks it up; after editing `static/**` just reload the page. After
editing Tailwind classes, rebuild the CSS: `npm run build:css`.

## 2. Drive it in Chromium (Playwright)

A Playwright Chromium is already cached on this machine; use the Python at
`/home/jpn/nonius_docker/venv/bin/python` (has `playwright` installed). Network
is required — the removal model loads from a CDN on first use and takes a few
seconds.

Minimal driver — upload the fixture, wait for a blob result, screenshot:

```python
from playwright.sync_api import sync_playwright
import time
with sync_playwright() as p:
    pg = p.chromium.launch().new_page()
    pg.on("pageerror", lambda e: print("PAGEERROR", e))
    pg.goto("http://127.0.0.1:8877/", wait_until="domcontentloaded")
    pg.set_input_files("input[type=file]", "tests/fixtures/sample.png")
    for _ in range(90):
        if pg.evaluate("()=>document.querySelector('.card')?.dataset.state==='done'"):
            break
        time.sleep(1)
    pg.screenshot(path="/tmp/app.png")   # then Read the screenshot
```

Key selectors: upload `input[type=file]`; card state `.card[data-state]`
(`processing`|`done`|`error`); actions `.crop-btn` `.edit-btn` `.download-btn`;
crop dialog `#crop-modal`, `.crop-source[data-source=original|cutout]`,
`.crop-shape[data-crop=circle|square|rounded|4:5|16:9|9:16]`, `#crop-apply`.

**Always Read the screenshot** — a blank frame means it didn't launch.

## 3. Or just run the smoke test

For crop changes, `tests/smoke_crop.py` already drives the whole flow with
assertions (see `tests/README.md`). Start the server, then:

```bash
BASE_URL=http://127.0.0.1:8877 /home/jpn/nonius_docker/venv/bin/python tests/smoke_crop.py
```

## Cleanup

```bash
pkill -f "manage.py runserver 127.0.0.1:8877"
```
