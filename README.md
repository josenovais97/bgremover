# BG Remover — Free AI Background Remover

A production-ready, privacy-first web app that removes image backgrounds **entirely in the browser**. No API keys, no watermarks, no uploads — images never leave the user's device. Django serves a fast, SEO-optimized single-page app; the AI runs client-side via [`@imgly/background-removal`](https://github.com/imgly/background-removal-js) (ISNet / U²-Net).

> **Why client-side?** It makes the app truly free (no per-image API cost), private by design, and deployable to serverless hosts like **Vercel** — a Python background-removal model would be far too large for serverless functions.

---

## ✨ Features

**Core**
- Upload via drag & drop, file picker, or clipboard paste (`Ctrl+V`)
- JPG / PNG / WEBP support, full resolution preserved
- Before/after comparison slider + side-by-side view + zoom lightbox
- Choose a background: transparent, colour presets or any custom colour, a **two-colour gradient**, a **blurred version of the original photo**, or your **own uploaded image**
- **Refine brush editor** — erase leftover background or restore over-trimmed areas by hand, with **zoom/pan** (wheel, Move tool, hold-Space), soft brushes, undo & keyboard shortcuts
- **Crop tool** — crop to a **circle, square, rounded square**, preset **4:5 / 16:9 / 9:16**, or any **custom W:H ratio**, with zoom, drag-to-reposition, and **rotate / flip**; circle/rounded masks keep transparent corners in the PNG. Choose the **source**: the transparent cut-out, or the **original image with its background kept** — so you can crop without removing the background at all. Works right away (even before removal finishes) and is non-destructive — re-open or remove the crop any time
- **Sticker effects** — add a coloured **outline/stroke**, a **drop shadow**, and **padding** around the cut-out, composited live into the exported PNG
- **Export sizes** — keep the original size, or scale to a **profile picture (512×512)**, a **story (1080×1920)**, or any **custom width × height** (aspect preserved, no distortion)
- Export as PNG (transparent), JPG, or WEBP — no watermark

**Favicon & app-icon generator** (`/favicon-generator`) — a separate tool, no background removal required
- Drop one image and download a complete icon set as a ZIP: a multi-size `favicon.ico` (16/32/48), PNGs for every common size, a 180×180 **Apple touch icon**, 192/512 **PWA icons** plus a **maskable** 512 with a safe zone
- Includes a ready `site.webmanifest` (app name, short name, theme colour) and the exact `<link>` **HTML to paste** into your `<head>`
- Choose a background (transparent or any colour), a **shape** (square / rounded / circle) and padding; preview the real 16px icon in a browser-tab mock-up
- 100% in the browser — nothing is uploaded

**WhatsApp & Telegram sticker maker** (`/sticker-maker`) — a separate tool
- Removes the background automatically, then adds the classic sticker **outline** (colour + thickness) and a **draggable caption** in bold / clean / tall / script fonts
- Exports a ready-to-use **512×512 transparent WebP** (or PNG) — exactly what WhatsApp and Telegram expect
- 100% in the browser — nothing is uploaded

**Instagram photo editor** (`/instagram`) — a separate tool, no background removal required
- Upload a photo and edit it immediately: pick a **format** (Post, Portrait, Story/Reel, Landscape, Profile) that crops to the right aspect and exports at Instagram's **exact pixel sizes**
- **Fill or Fit** — crop to the frame, or post the whole photo with **no crop**, filling the gaps with a blurred copy or a solid colour; add a coloured **border**
- **12 on-trend one-tap looks** (Vivid, Punch, Clean, Golden, Moody, Film, Noir, Warm, Cool, Fade, Vintage) with a **strength** slider, plus **adjustments** — brightness, contrast, saturation, warmth, **sharpen**, **film grain**, vignette
- **Text captions** (font, colour, size, drag to place), a **logo / watermark** overlay you can upload and position, and a coloured **frame**
- **Save your own looks** ("My looks") to reuse a favourite grade across photos
- **Press-and-hold compare** against the original, and **Story/Reel safe-zone guides** so captions/UI don't cover faces
- **Carousel splitter** — slice a wide photo into a seamless **swipeable carousel** (2–3 tiles), exported as a ZIP
- **Crop & reposition** with drag + zoom; **optionally remove the background** and drop in a solid colour
- 100% in the browser — nothing is uploaded

**Crop tool** (`/crop`) — a separate tool, no background removal required
- Crop to a **rectangle, rounded square or circle** at **1:1 / 4:5 / 3:4 / 16:9 / 9:16**, a **custom W:H**, or the photo's original ratio
- **Rotate** (90°) and **flip** H/V, with zoom and drag to frame
- Export a full-resolution transparent **PNG** (rounded/circle keep transparent corners) or a **JPG** — nothing is uploaded

**Image converter** (`/convert`)
- Convert any image to PNG / JPG / WEBP / **AVIF** — input format is **auto-detected**
- Quality control for lossy formats, batch conversion + ZIP download
- Also runs 100% in the browser
- Model warm-up preload so the first result is fast
- Transparent checkerboard preview

**Batch & extras**
- Batch processing (select multiple images)
- **Undo / redo** per card, and **apply one card's** background, format, size & sticker settings **to all** images at once
- Full-resolution exports run in a **Web Worker** (OffscreenCanvas), so downloading a large, heavily-styled image never freezes the tab
- Download all as a ZIP
- Copy result to clipboard
- **Remembers your background & format** across the session so batch runs stay fast
- Recent history (session only) & processing statistics
- Optional per-card retry, keyboard shortcuts (`O`, `Ctrl+S`, `D`, `Esc`, `?`)

**UX / UI**
- Fully responsive, glassmorphism, smooth animations
- Light/dark mode remembered in `localStorage`
- Accessible: keyboard nav, ARIA labels, focus states, reduced-motion support
- Toast notifications, attractive empty states, helpful errors

**SEO**
- Meta / Open Graph / Twitter cards, canonical URLs, semantic HTML
- JSON-LD structured data: `WebApplication` + `WebSite`, a `FAQPage` generated
  from a single source (see `remover.views.faq_jsonld`), and `BreadcrumbList`
  on landing pages
- Keyword-targeted **use-case landing pages** (`/remove-background/<slug>/`) for
  product photos, profile pictures, logos, signatures, car photos, clothing &
  fashion, pet photos and YouTube thumbnails — generated from a single
  `USE_CASES` list that also feeds the sitemap and internal links
- `robots.txt` + `sitemap.xml` (auto-generated from the page list)
- Search-engine ownership verification via optional meta tags (Google / Bing)

---

## 🧱 Tech stack

| Layer      | Choice                                             |
|------------|----------------------------------------------------|
| Backend    | Python + Django 5 (stateless, no DB)               |
| Frontend   | HTML, compiled Tailwind CSS, Font Awesome, vanilla JS (ESM) |
| AI model   | `@imgly/background-removal` (WASM/WebGPU, ISNet)   |
| Static     | WhiteNoise (compressed + hashed manifest)          |
| Security   | CSP + Permissions-Policy, HSTS, secure cookies     |
| Serving    | Gunicorn + Nginx / Docker / Vercel                 |

> **Tailwind is compiled, not CDN.** `static/css/tailwind.css` is a minified build
> committed to the repo — no runtime CDN, no `eval`, no flash of unstyled content.
> Rebuild it with `npm run build:css` after editing templates or `static/js`.

---

## 📁 Project structure

```
bgremover/
├── config/
│   ├── settings/
│   │   ├── base.py            # shared settings
│   │   ├── development.py     # DEBUG, local hosts
│   │   └── production.py      # HTTPS + security hardening
│   ├── middleware.py         # CSP + Permissions-Policy headers
│   ├── urls.py
│   ├── wsgi.py               # exposes `app` for Vercel
│   └── asgi.py
├── remover/
│   ├── views.py              # index + convert + instagram + crop + favicon + sticker + use-case pages + healthz + robots + sitemap
│   ├── context_processors.py # SEO tokens + shared footer nav data
│   ├── urls.py
│   ├── models.py             # intentionally empty (no DB)
│   └── tests.py
├── templates/
│   ├── base.html             # layout, SEO, theme, floating nav + tool switcher
│   ├── remover/index.html    # background remover + refine editor
│   ├── remover/convert.html  # image format converter
│   ├── remover/instagram.html # Instagram photo editor
│   ├── remover/crop.html     # standalone crop tool
│   ├── remover/favicon.html  # favicon / app-icon generator
│   ├── remover/sticker.html  # WhatsApp / Telegram sticker maker
│   ├── remover/use_case.html # keyword-targeted landing page (data-driven)
│   ├── seo/{robots.txt,sitemap.xml}
│   └── {404.html,500.html}
├── static/
│   ├── src/input.css                 # Tailwind source
│   ├── css/tailwind.css              # compiled + minified (committed)
│   ├── js/app.js                     # background remover + editor
│   ├── js/compose-worker.js          # off-thread full-res export pipeline
│   ├── js/converter.js               # image converter
│   ├── js/instagram.js               # Instagram photo editor
│   ├── js/crop.js                    # standalone crop tool
│   ├── js/favicon.js                 # favicon / app-icon generator
│   ├── js/sticker.js                 # sticker maker
│   ├── js/colorpicker.js             # shared custom colour picker
│   ├── js/theme.js                   # pre-paint theme + toggle (all pages)
│   └── img/{favicon.svg,og-image.svg}
├── deploy/nginx.conf
├── Dockerfile / docker-compose.yml / .dockerignore
├── vercel.json / build_files.sh
├── package.json / tailwind.config.js   # CSS build tooling
├── requirements.txt
├── .env.example
└── manage.py
```

There is **no database** — history, stats, and theme live in the browser. `models.py` is empty on purpose.

---

## 🚀 Local development

```bash
# 1. Clone and enter the project
cd bgremover

# 2. Create a virtualenv and install deps
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# then set a SECRET_KEY (see below); DEBUG=True is fine for dev

# 4. Build the CSS (needs Node 18+). The committed build already works,
#    so this is only required if you change templates or JS classes.
npm install
npm run build:css        # or: npm run watch:css  (rebuild on change)

# 5. Run the dev server
python manage.py runserver
# open http://127.0.0.1:8000
```

> **Editing styles:** Tailwind scans `templates/**/*.html` and `static/js/**/*.js`.
> After adding/removing classes, run `npm run build:css` (or keep `watch:css`
> running) to regenerate `static/css/tailwind.css`.

Generate a secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

> **First use** downloads the ~40 MB AI model from a CDN; the browser caches it afterward, so subsequent runs are instant. An internet connection is required the first time.

---

## 🔑 Environment variables

| Variable                | Required     | Description                                        |
|-------------------------|--------------|----------------------------------------------------|
| `SECRET_KEY`            | ✅ (prod)     | Long random string.                                |
| `DEBUG`                 | –            | `True` dev / `False` prod (default `False`).       |
| `ALLOWED_HOSTS`         | ✅ (prod)     | Comma-separated hostnames.                         |
| `CSRF_TRUSTED_ORIGINS`  | recommended  | Comma-separated `https://…` origins.               |
| `SITE_URL`              | recommended  | Absolute URL for canonical tags & sitemap.         |
| `LOG_LEVEL`             | –            | `DEBUG`/`INFO`/`WARNING`/`ERROR`.                  |
| `SECURE_SSL_REDIRECT`   | –            | `False` if TLS is terminated upstream.             |
| `GOOGLE_SITE_VERIFICATION` | –         | Token from Google Search Console (HTML-tag method). |
| `BING_SITE_VERIFICATION`   | –         | Token from Bing Webmaster Tools.                   |

> `SITE_URL` must include the scheme (`https://…`); a bare domain is auto-corrected
> to `https://` so the sitemap never emits invalid URLs.

Settings are selected via `DJANGO_SETTINGS_MODULE`:
`config.settings.development` (default in `manage.py`) or `config.settings.production` (default in `wsgi.py`/Docker/Vercel).

---

## 🧪 Testing

```bash
python manage.py test          # runs the view + SEO endpoint tests
python manage.py check --deploy # production security audit (use prod settings)
```

Run the deploy check against production settings:
```bash
DJANGO_SETTINGS_MODULE=config.settings.production \
  SECRET_KEY=$(python -c "import secrets;print(secrets.token_urlsafe(50))") \
  ALLOWED_HOSTS=example.com python manage.py check --deploy
```

---

## ▲ Deploy to Vercel

The app is stateless, so it fits Vercel's serverless Python runtime.

1. Push the repo to GitHub and **Import** it in Vercel.
2. Set environment variables in the Vercel dashboard:
   - `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS=your-app.vercel.app`,
     `CSRF_TRUSTED_ORIGINS=https://your-app.vercel.app`, `SITE_URL=https://your-app.vercel.app`
   - `SECURE_SSL_REDIRECT=False` (Vercel handles TLS; avoids redirect loops)
3. Deploy. `vercel.json` runs `build_files.sh` (installs deps + `collectstatic`) and routes:
   - `/static/*` → collected static files
   - everything else → `config/wsgi.py` (which exposes `app`)

No database or persistent storage is needed.

> Other hosts (Netlify, Render static, GitHub Pages behind a proxy) work too, since the heavy lifting is client-side.

---

## 🐳 Docker

```bash
cp .env.example .env   # set SECRET_KEY, ALLOWED_HOSTS, DEBUG=False
docker compose up --build
# open http://localhost
```

- `Dockerfile` builds the app, runs `collectstatic`, and serves via Gunicorn as a non-root user.
- `docker-compose.yml` adds an Nginx reverse proxy (`deploy/nginx.conf`); WhiteNoise serves static assets from inside the app.

Run the image standalone:
```bash
docker build -t bgremover .
docker run -p 8000:8000 --env-file .env bgremover
```

---

## 🖥️ Production: Nginx + Gunicorn (VPS)

```bash
# On the server
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export DJANGO_SETTINGS_MODULE=config.settings.production
python manage.py collectstatic --noinput

# Run Gunicorn (behind Nginx / a systemd service)
gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3 --timeout 60
```

Point Nginx at `127.0.0.1:8000` using `deploy/nginx.conf` (change the `upstream` to `127.0.0.1:8000`), then add TLS with Certbot:

```bash
sudo certbot --nginx -d your-domain.com
```

A minimal `systemd` unit:

```ini
# /etc/systemd/system/bgremover.service
[Unit]
Description=BG Remover (Gunicorn)
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

All AI logic is isolated in `static/js/app.js`:

```js
import { removeBackground } from 'https://cdn.jsdelivr.net/npm/@imgly/background-removal@1.6.0/+esm';
// ...
const blob = await removeBackground(this.originalUrl, { ...CONFIG.removalOptions, progress });
```

To use a different in-browser model (e.g. Transformers.js + RMBG-1.4), replace the import and the call inside `Card.process()`; the rest of the UI is model-agnostic. For faster/lower-quality output, set `model: 'isnet_quint8'` in `CONFIG.removalOptions`.

---

## 📈 Operations

- **Health check:** `GET /healthz` returns `200 ok` — point your load balancer or
  uptime monitor here.
- **Scaling:** the server only serves static HTML/CSS/JS, so it scales trivially.
  The compute-heavy AI work runs on each visitor's device, not your servers.
- **Caching:** WhiteNoise serves hashed, compressed static assets with far-future
  cache headers; `robots.txt`/`sitemap.xml` are cached for 1h.
- **Search Console:** verify ownership by setting `GOOGLE_SITE_VERIFICATION`
  (and/or `BING_SITE_VERIFICATION`), then submit `/sitemap.xml`. Adding a new
  `USE_CASES` entry automatically extends the sitemap.

## 🔐 Security & privacy notes

- Images are **never** transmitted to the server — processing is 100% client-side.
- A **Content-Security-Policy** and **Permissions-Policy** are set on HTML responses
  (`config/middleware.py`). The CSP allows `wasm-unsafe-eval` (the model is WASM),
  the jsdelivr CDN (library + model), and inline styles (Tailwind dynamic values).
- Production enables HSTS, secure cookies, `nosniff`, `X-Frame-Options: DENY`,
  referrer policy, and (optionally) SSL redirect.
- CSRF middleware is enabled as defense-in-depth even though there are no server-side forms.
- No user data is stored server-side; history/stats are per-browser (`sessionStorage` / `localStorage`).

---

## 📝 Changelog

See [`CHANGELOG.md`](CHANGELOG.md) for the release history.

---

## 📄 License

Free and open source — use it however you like. The `@imgly/background-removal` model is distributed under its own license; review it before commercial use.
