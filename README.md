# ClearBG — a free, private image toolkit that runs in your browser

**19 image tools that never upload your photos.** Background removal, conversion,
compression, resizing, image-to-PDF, passport photos, stickers, QR codes, metadata
stripping and more — all of it executes on the visitor's device. Django serves fast, SEO-optimised
HTML; the pixels never touch the server.

Live: **[clearbg.pt](https://clearbg.pt)**

> **Why client-side?** It makes the app truly free (no per-image API cost), private by
> design, and deployable to serverless hosts like **Vercel** — a server-side removal
> model would be far too large for a serverless function. "Nothing is uploaded" is also
> the product's one structural differentiator: no competitor that uploads can claim it.

---

## 🧰 The toolkit

Every tool is 100% client-side, free, unlimited, and watermark-free.

| Tool | URL | What it does |
|------|-----|--------------|
| **Background remover** | `/` | AI cut-out to a transparent PNG. Batch, refine brush, crop, backgrounds, effects, export sizes. |
| **Image converter** | `/convert/` | PNG / JPG / WEBP / **AVIF**, format auto-detected, batch + ZIP. |
| **Image compressor** | `/compress/` | Quality slider **or a target file size** (binary-searches quality to hit it), optional max-dimension downscale. |
| **Image resizer** | `/resize-image/` | Exact pixels or a percentage, aspect lock, export JPG/PNG/WEBP. |
| **Crop tool** | `/crop/` | Rectangle / rounded / circle at 1:1, 4:5, 3:4, 16:9, 9:16, custom or original ratio; rotate + flip. |
| **Instagram editor** | `/instagram/` | Exact IG sizes, fill-or-fit, 12 looks, adjustments, text layers, logo, carousel splitter. |
| **Sticker maker** | `/sticker-maker/` | Removes the background, adds a die-cut outline + caption, exports a 512×512 WebP for WhatsApp/Telegram. |
| **Text behind image** | `/text-behind-image/` | The viral effect: text layered between the photo and the subject cut-out. |
| **Watermark** | `/watermark-image/` | A single mark anchored to one of nine positions, or a tiled pattern that's hard to crop out. |
| **GIF maker** | `/gif-maker/` | Frames → animated GIF (gifenc), with a cheap live preview and on-demand encode. |
| **Meme generator** | `/meme-maker/` | Draggable top/bottom captions in Impact / Anton / Oswald, PNG/JPG or copy to clipboard. |
| **Passport & ID photos** | `/passport-photo/` | Exact biometric size at 300 DPI for 22 countries, guide lines, auto-fit, 6×4 print sheet. |
| **Product photos** | `/ecommerce/` | One click → product centred on pure white at Amazon / Etsy / Shopify sizes. Batch + ZIP. |
| **Background blur** | `/blur-background/` | Portrait-mode depth: the removal mask keeps the subject sharp and blurs the rest. |
| **Blur & redact** | `/redact-image/` | Drag boxes *or trace a freehand lasso* over faces/plates/text; blur, pixelate or black out. |
| **Favicon generator** | `/favicon-generator/` | A full icon set as a ZIP: multi-size `.ico`, PNGs, Apple touch, PWA + maskable, `site.webmanifest`, paste-ready HTML. |
| **QR code generator** | `/qr-code-generator/` | Styled static QR (square/rounded/dot modules, styled eyes, gradient, centre logo) → PNG or SVG. |
| **EXIF remover** | `/exif-remover/` | Reads GPS/camera/date metadata, then strips it — **losslessly** for JPEG (marker segments dropped, pixel data untouched). |
| **Image to PDF** | `/image-to-pdf/` | Combine photos or scans into one multi-page PDF; drag to reorder, A4/Letter/fit-image, margins. JPEG and PNG bytes are embedded as-is. |

Removed: the AI upscaler (`/upscale/`) — client-side super-resolution froze the tab. The
URL 301s to home so the indexed page never 404s.

**Batch** is supported by the remover, convert, compress, eCommerce, GIF and PDF
tools, plus resize, watermark and EXIF — for those three the first file is the one
you tune on screen and the rest are exported with the same settings as a ZIP
(queued images keep their own aspect ratio).

### Cross-tool features

- **Hand-off between tools** — "Continue in Crop / Sticker / Instagram" passes the result
  through IndexedDB with no re-upload. One-shot, 60-second TTL (`static/js/handoff.js`).
- **PWA** — installable (with app shortcuts and a dedicated maskable icon), and a service
  worker whose shell is *generated* from the tool list and the contents of `static/js`, so
  it can't fall behind the toolkit. The ~40 MB model lives in a separate long-lived cache
  that a redeploy never evicts.
- **Per-tool accent colours** — every tool has a signature colour that themes the whole
  page, including the browser chrome (`theme-color`).
- **Shared UI kit** — glassmorphism, dark mode, toasts, a custom colour picker, live value
  bubbles on every slider, before/after demo sliders, an "All tools" mega-menu with a
  responsive overflow nav.
- **`window.CBG`** (`static/js/kit.js`) — the helpers every tool needs (`$`, `Toast`,
  `loadImage`, drag/drop/paste wiring, ZIP export, a localStorage settings store). Loaded
  as a *classic* script from `base.html`, which is what lets tool modules share code at
  all: Django's static storage can't rewrite ES-module import paths, so a local `import`
  between modules breaks in production.

---

## ✂️ The background remover in depth (`/`)

**Input** — drag & drop, file picker, or clipboard paste (`Ctrl+V`); JPG / PNG / WEBP at
full resolution; batch; a one-click sample photo for visitors with nothing to hand.

**Backgrounds** — four one-tap **quick presets** (Transparent / White / Studio / Blur
photo) sit above the detailed controls, which offer colour presets or any custom colour, a
**two-colour gradient** (with angle), a **blurred copy of the original photo**, your **own
uploaded image**, or one of **17 preset photo backgrounds** grouped into Studio / Colorful
/ Scenes. Every quick preset drives the same setter as its detailed control, so the two
stay in sync in both directions.

**Refine brush editor** — erase leftover background or restore over-trimmed areas by hand,
with zoom/pan (wheel, Move tool, hold-Space), soft brushes, edge smoothing, undo, and
`R`/`E`/`M` + `[`/`]` shortcuts.

**Crop dialog** — circle, square, rounded square, 4:5 / 16:9 / 9:16 or any custom W:H, with
zoom, drag-to-reposition and rotate/flip. Choose the **source**: the transparent cut-out,
or the **original image with its background kept** — so you can crop without removing the
background at all. Works before removal finishes, and is non-destructive (re-open or
remove the crop any time).

**Effects & export** — coloured outline/stroke, drop shadow, padding and **trim
transparent edges** (crops the export to the subject's alpha bounding box, before any
background or outline is composited, so those hug the subject); PNG / JPG / WEBP;
keep the original size or scale to 512×512, 1080×1920 or a custom W×H (aspect preserved).

**Batch niceties** — per-card undo/redo, "apply this card's settings to all", download all
as ZIP, copy to clipboard, per-card retry, session history and stats, and remembered
background/format across the session.

**Performance** — full-resolution exports run in a **Web Worker** (OffscreenCanvas), so
downloading a large, heavily styled image never freezes the tab. On cross-origin-isolated
pages the full `isnet` model is used; elsewhere it falls back to `isnet_quint8`.

**Shortcuts** — `Ctrl+V` paste, `O` open, `Ctrl+S` download all, `D` theme, `?` shortcuts,
`Esc` close.

---

## 🧱 Tech stack

| Layer | Choice |
|-------|--------|
| Backend | Python + Django 5 (stateless, **no database**) |
| Frontend | HTML, compiled Tailwind CSS, self-hosted Inter + Font Awesome subset, vanilla JS (ESM) |
| AI model | `@imgly/background-removal` 1.6 (WASM/WebGPU, ISNet), loaded from jsDelivr |
| Other libs (all CDN ESM) | JSZip, gifenc, exifr, qrcode-generator, pdf-lib |
| Static | WhiteNoise (finders mode; compressed + hashed manifest in prod) |
| Counter | Upstash Redis REST (optional, env-gated) |
| Security | CSP + Permissions-Policy, COOP/COEP on tool pages, HSTS, secure cookies |
| Serving | Gunicorn + Nginx / Docker / Vercel |

### Three prebuilt artifacts you must not forget

Both are **committed build outputs with no build step at deploy time** — edit the source
and rebuild, or your change silently does nothing.

1. **`static/css/tailwind.css`** is a compiled, purged Tailwind build (source
   `static/src/input.css`, config `tailwind.config.js`). A class that wasn't in the
   templates at build time is simply absent. After adding classes, run
   `npm run build:css` and commit the result.
2. **`static/css/fontawesome.css` + `static/webfonts/fa-*.woff2`** are a ~93-glyph Font
   Awesome subset. An icon outside the subset renders as a blank box. Check with
   `grep '\.fa-name:before' static/css/fontawesome.css` before using a new one — the
   `IconSubsetTests` suite fails the build if you don't. FA's `fa-rotate-*`/`fa-flip-*`
   utilities are not included; use Tailwind transforms (`-scale-x-100`) instead.
3. **`static/css/inter.css` + `static/webfonts/inter/*.woff2`** are Google Fonts' variable
   Inter files, self-hosted. One file per subset covers the whole 400–800 range (the css2
   API returns the same file for each discrete weight). Regenerate by re-fetching
   `Inter:wght@400..800` with a browser User-Agent and keeping the latin/latin-ext faces.
   Google Fonts is still requested — but only on the four pages whose canvases paint with
   Anton / Bebas Neue / Pacifico / Playfair.

### The accent-colour system

Each tool has a signature colour, set as four CSS variables on `<body>` from
`TOOL_ACCENTS` in `remover/context_processors.py`. Two families exist because an accent
used as a **surface** (white text on it) and the same accent used as **text** on the page
background have opposite contrast needs:

- `--color-primary` / `--color-primary-hover` — the surface pair (does *not* vary by theme)
- `--accent-text-dark` / `--accent-text-dark-alt` — the dark-theme text pair

`primaryText` / `primaryTextAlt` are derived in `input.css` so the `.dark` flip can win.
Reach for `text-primaryText`, never `text-primary`. `AccentContrastTests` recomputes every
ratio and fails if an edit drops below WCAG AA.

---

## 📁 Project structure

```
bgremover/
├── config/
│   ├── settings/{base,development,production}.py
│   ├── middleware.py          # CSP, Permissions-Policy, COOP/COEP on tool pages
│   ├── urls.py                # i18n_patterns wrapper (English at /, Portuguese at /pt/)
│   ├── wsgi.py                # exposes `app` for Vercel
│   └── asgi.py
├── remover/
│   ├── views.py               # every page + the data that drives the SEO pages
│   ├── seo_content.py         # FAQ copy (renders the accordion AND the JSON-LD)
│   ├── passport_data.py       # 22 countries: sizes, rules, FAQs
│   ├── translations.py        # in-code pt-PT catalogue (no gettext build step)
│   ├── context_processors.py  # TOOL_NAV, TOOL_GROUPS, TOOL_ACCENTS, canonical/hreflang
│   ├── templatetags/i18n_extras.py   # the {% t %} tag
│   ├── urls.py
│   ├── models.py              # intentionally empty (no DB)
│   └── tests.py               # 62 tests
├── templates/
│   ├── base.html              # layout, SEO, theme, tool nav + mega-menu, footer
│   ├── remover/*.html         # one template per tool
│   ├── remover/landing.html   # shared data-driven landing page (privacy + compress)
│   ├── remover/comparison.html, use_case.html, passport_country.html
│   ├── remover/partials/      # demo, faq, tool_grid, related_tools, ad_slot, …
│   ├── sw.js, manifest.webmanifest
│   ├── seo/{robots.txt,sitemap.xml}
│   └── {404.html,500.html}
├── static/
│   ├── src/input.css          # Tailwind source + the design system
│   ├── css/tailwind.css       # compiled + minified (committed)
│   ├── css/fontawesome.css    # icon subset (committed)
│   ├── js/app.js              # background remover + refine editor + crop dialog
│   ├── js/compose-worker.js   # off-thread full-res export pipeline
│   ├── js/<tool>.js           # one module per tool, deliberately self-contained
│   ├── js/kit.js              # window.CBG — shared helpers (classic script)
│   ├── js/handoff.js          # cross-tool image hand-off via IndexedDB
│   ├── js/{theme,nav,stats,demo,range-value,colorpicker,landing,ads}.js  # shared chrome
│   └── img/backgrounds/       # 17 preset backgrounds (full + thumb WEBP)
├── tests/                     # Node geometry test + Playwright smoke tests
├── deploy/nginx.conf
├── Dockerfile / docker-compose.yml / .dockerignore
├── vercel.json / build_files.sh
├── package.json / tailwind.config.js
├── requirements.txt
├── .env.example
└── manage.py
```

There is **no database**. History, stats, saved looks and theme live in the browser;
`models.py` is empty on purpose.

> **Why each tool's JS is self-contained** (its own `$`, `Toast`, `loadImage`): Django's
> hashed-manifest static storage does not rewrite ES-module import paths, so cross-file
> *local* imports break in production. Absolute CDN imports are fine.

---

## 🚀 Local development

```bash
# 1. Virtualenv + deps
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Environment
cp .env.example .env              # set a SECRET_KEY; DEBUG=True is fine for dev

# 3. CSS (Node 18+). The committed build works — only needed if you touch classes.
npm install
npm run build:css                 # or: npm run watch:css

# 4. Run
python manage.py runserver        # http://127.0.0.1:8000
```

Generate a secret key:

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

> **First use** downloads the ~40 MB AI model from a CDN; the browser and the service
> worker cache it afterwards, so subsequent runs are instant. An internet connection is
> required the first time (and for the CDN-hosted libraries).

---

## 🔑 Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | ✅ (prod) | Long random string. |
| `DEBUG` | – | `True` dev / `False` prod (default `False`). |
| `ALLOWED_HOSTS` | ✅ (prod) | Comma-separated hostnames. |
| `CSRF_TRUSTED_ORIGINS` | recommended | Comma-separated `https://…` origins. |
| `SITE_URL` | recommended | Absolute URL for canonical tags, `og:url` and the sitemap. |
| `LOG_LEVEL` / `DJANGO_LOG_LEVEL` | – | `DEBUG`/`INFO`/`WARNING`/`ERROR`. |
| `SECURE_SSL_REDIRECT` | – | `False` if TLS is terminated upstream. |
| `GOOGLE_SITE_VERIFICATION` | – | Google Search Console token (HTML-tag method). |
| `BING_SITE_VERIFICATION` | – | Bing Webmaster Tools token. |
| `ADSENSE_CLIENT` | – | AdSense publisher ID (`ca-pub-…`). Ads load on use-case landing pages only; clear to disable. |
| `ADSENSE_SLOT_LANDING` | – | Optional explicit ad-unit slot; blank falls back to Auto ads. |
| `UPSTASH_REDIS_REST_URL` | – | Upstash Redis REST URL for the "images processed" counter. `KV_REST_API_URL` is accepted as an alias (Vercel KV). |
| `UPSTASH_REDIS_REST_TOKEN` | – | Matching token (alias: `KV_REST_API_TOKEN`). |
| `STATS_KEY` | – | Counter key namespace (default `clearbg:processed`). |

> `SITE_URL` must include the scheme (`https://…`); a bare domain is auto-corrected to
> `https://` so the sitemap never emits invalid URLs.
>
> Yandex ownership is verified by a **file**, not a meta tag: the verification HTML is
> served at the site root by the `yandex_verify` view (a plain static file wouldn't work,
> since Vercel routes every request through Django).

Settings are selected via `DJANGO_SETTINGS_MODULE`: `config.settings.development`
(default in `manage.py`) or `config.settings.production` (default in `wsgi.py`/Docker/Vercel).

---

## 🧪 Testing

```bash
python manage.py test           # 79 Django tests: pages, SEO, i18n, PWA, accents, icon subset
npm test                        # crop-geometry unit tests (Node, no browser)
python manage.py check --deploy # production security audit (use prod settings)
```

Beyond the obvious page tests, the Django suite guards a few things that are easy to break
silently: **WCAG AA contrast** for every tool accent, that gradient headlines use the text
pair rather than the surface pair, that no template references a **Font Awesome glyph
outside the committed subset**, that ads never render on cross-origin-isolated pages, and
that the Portuguese routes/hreflang work.

`EveryToolTests` walks `TOOL_NAV` itself, so every tool — present and future — is checked
to render, load its JS module, own an accent, and appear in both the sitemap and the
homepage grid. `PWATests` asserts the service-worker shell still covers every tool page
and script, which is the drift that made the offline claim untrue.

Browser smoke tests (Playwright) live in `tests/` — see [`tests/README.md`](tests/README.md).

Run the deploy check against production settings:

```bash
DJANGO_SETTINGS_MODULE=config.settings.production \
  SECRET_KEY=$(python -c "import secrets;print(secrets.token_urlsafe(50))") \
  ALLOWED_HOSTS=example.com python manage.py check --deploy
```

---

## 🔎 SEO & content architecture

Everything is generated from data in `remover/views.py`, so adding a page is a data edit
that automatically extends the nav, the internal links and the sitemap (**71 paths, listed
in both languages**).

| Set | Route | Source |
|-----|-------|--------|
| Use-case landings (11) | `/remove-background/<slug>/` | `USE_CASES` |
| Passport sizes by country (22) | `/passport-photo/<country>/` | `passport_data.COUNTRIES` |
| Privacy-angle landings (3) | `/private-image-tools/`, `/remove-background-without-uploading/`, `/offline-image-editor/` | `PRIVACY_PAGES` |
| Compress intent variants (9) | `/compress-png/`, `/compress-image-under-500kb/`, `/compress-image-for-discord/`, … | `COMPRESS_PAGES` |
| Competitor comparisons (4 + 1) | `/tinypng-alternative/`, `/canva-alternative/`, `/adobe-express-alternative/`, `/photoroom-alternative/`, `/remove-bg-alternative/` | `COMPARISONS`, `alternative()` |
| Info | `/about/`, `/privacy/`, `/terms/` | templates |

Also:

- **Structured data**: `WebApplication` + `WebSite` + `Organization` site-wide,
  `FAQPage` from a single source (`remover/seo_content.py` — the visible accordion and the
  JSON-LD render from the same list), `BreadcrumbList` on landing pages.
- **Canonicals**, `og:image` and the JSON-LD identity are all built from `SITE_URL` + path
  (query stripped), so every host/UTM variant consolidates onto one URL and advertises the
  same image.
- **hreflang** `en` / `pt` / `x-default` on every page and on every sitemap entry, plus a
  footer language switcher. The sitemap lists each page twice — once per language.
- **Contextual internal links**: a related-tools row is injected into every page by
  `base.html` (same-group tools first — see `_related_tools()`).
- `robots.txt` and `sitemap.xml` are generated from the page list with per-page
  `priority` and `lastmod` (~142 URLs: 71 paths × 2 languages).

---

## 🌍 Internationalisation

English is served at the root, Portuguese under `/pt/`, via `i18n_patterns` with
`prefix_default_language=False`.

Translations do **not** use gettext `.mo` files (msgfmt isn't assumed to exist on Vercel).
Instead `remover/translations.py` holds an in-code catalogue resolved by the `{% t %}` tag,
with graceful English fallback for anything untranslated. Current coverage: the shared
chrome, the home page and all 11 use-case landing pages. The tool editor UIs, passport /
country pages and legal pages still fall back to English — extend by adding strings to
`translations.py`.

---

## 🔐 Security & privacy

- Images are **never transmitted**. Every tool runs on `<canvas>` / WASM in the visitor's
  browser; the server has no upload endpoint at all.
- **CSP + Permissions-Policy** on HTML responses (`config/middleware.py`). The CSP allows
  `wasm-unsafe-eval` and `unsafe-eval` (required by the onnxruntime-web WASM backend),
  jsDelivr + staticimgly (libraries and model weights), AdSense hosts, and inline styles
  (Tailwind dynamic values).
- **Cross-origin isolation** (COOP + COEP `credentialless`) is applied to just the tool
  pages that run the removal model (`ISOLATED_VIEWS`), which unlocks multi-threaded + SIMD
  WASM — a 2–4× speed-up. Marketing pages are excluded so they stay embeddable and can run
  ad scripts. Safari, which lacks `credentialless`, silently falls back to single-threaded.
- Production enables HSTS, secure cookies, `nosniff`, `X-Frame-Options: DENY`, a referrer
  policy and (optionally) an SSL redirect.
- The stats endpoint validates `tool` and `event` against whitelists **before** they are
  used to build the Upstash REST key, so no client can inject arbitrary Redis keys, and it
  caps the increment (it is a public, unauthenticated vanity counter).
- No user data is stored server-side; history/stats/looks are per-browser
  (`sessionStorage` / `localStorage` / IndexedDB).

---

## ▲ Deploy to Vercel

The app is stateless, so it fits Vercel's serverless Python runtime.

1. Push to GitHub and **Import** the repo in Vercel.
2. Set the environment variables in the dashboard:
   `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS=…`, `CSRF_TRUSTED_ORIGINS=https://…`,
   `SITE_URL=https://…`, and `SECURE_SSL_REDIRECT=False` (Vercel terminates TLS; this
   avoids redirect loops).
3. Deploy. `vercel.json` runs `build_files.sh` (deps + `collectstatic`) and routes
   `/static/*` to the collected files and everything else to `config/wsgi.py`.

No database or persistent storage is needed. **Environment-variable changes require a
redeploy** to take effect.

---

## 🐳 Docker

```bash
cp .env.example .env   # set SECRET_KEY, ALLOWED_HOSTS, DEBUG=False
docker compose up --build
# open http://localhost
```

- `Dockerfile` builds the app, runs `collectstatic`, and serves via Gunicorn as non-root.
- `docker-compose.yml` adds an Nginx reverse proxy (`deploy/nginx.conf`); WhiteNoise
  serves static assets from inside the app.

```bash
docker build -t bgremover .
docker run -p 8000:8000 --env-file .env bgremover
```

---

## 🖥️ Production: Nginx + Gunicorn (VPS)

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export DJANGO_SETTINGS_MODULE=config.settings.production
python manage.py collectstatic --noinput
gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3 --timeout 60
```

Point Nginx at `127.0.0.1:8000` using `deploy/nginx.conf` (change the `upstream`), then add
TLS with `sudo certbot --nginx -d your-domain.com`.

A minimal `systemd` unit:

```ini
# /etc/systemd/system/bgremover.service
[Unit]
Description=ClearBG (Gunicorn)
After=network.target

[Service]
User=www-data
WorkingDirectory=/srv/bgremover
EnvironmentFile=/srv/bgremover/.env
Environment=DJANGO_SETTINGS_MODULE=config.settings.production
ExecStart=/srv/bgremover/venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 🔄 Swapping the background-removal model

The removal call is isolated per tool. In `static/js/app.js`:

```js
import { removeBackground } from 'https://cdn.jsdelivr.net/npm/@imgly/background-removal@1.6.0/+esm';
// ...
const blob = await removeBackground(this.originalUrl, { ...CONFIG.removalOptions, progress });
```

`CONFIG.removalOptions` picks `isnet` when `self.crossOriginIsolated` is true and
`isnet_quint8` otherwise. To use a different in-browser model (e.g. Transformers.js +
RMBG-1.4), replace the import and the call inside `Card.process()` — the rest of the UI is
model-agnostic. The same import appears in `blur.js`, `ecommerce.js`, `textbehind.js`,
`sticker.js`, `passport.js` and `instagram.js`, so update those too (and the
`MODEL_HOSTS` / CSP entries if the host changes).

---

## 📈 Operations

- **Health check**: `GET /healthz` → `200 ok`.
- **Scaling**: the server only ships static HTML/CSS/JS; all compute runs on visitors'
  devices.
- **Caching**: WhiteNoise serves hashed, compressed assets with far-future headers;
  `robots.txt` / `sitemap.xml` are cached for 1h; the service worker is network-first for
  same-origin requests (a redeploy is picked up on the next online load) and cache-first
  for the model.
- **Analytics**: Vercel Web Analytics (`/_vercel/insights/script.js`), privacy-friendly and
  active once enabled in Vercel.
- **Search Console**: set `GOOGLE_SITE_VERIFICATION` (and/or `BING_SITE_VERIFICATION`),
  then submit `/sitemap.xml`. New `USE_CASES` / `COMPRESS_PAGES` / `COMPARISONS` entries
  extend it automatically.
- **Social-proof counter**: `/api/stats/` returns `{"enabled": false}` until Upstash is
  configured, and the hero badge stays hidden — **no fabricated numbers**.

---

## 📝 Changelog

See [`CHANGELOG.md`](CHANGELOG.md) for the release history.

## 📄 License

Free and open source — use it however you like. `@imgly/background-removal` and the other
CDN libraries are distributed under their own licenses; review them before commercial use.
