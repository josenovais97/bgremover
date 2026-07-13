# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project aims to
follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.6.0] — 2026-07-13

Portuguese localisation, hreflang, and a robust responsive tool nav.

### Added
- **Portuguese (pt-PT) site** served under `/pt/` via `i18n_patterns`
  (`prefix_default_language=False`, so English stays at the root). Translations
  live in a lightweight in-code catalogue (`remover/translations.py`) resolved by
  a `{% t %}` template tag — **no gettext build tooling required** — with
  graceful English fallback for any untranslated string. Translated so far: the
  shared chrome (nav, footer, buttons), the home page, and **all 11 use-case
  landing pages** (titles, descriptions, headings and body copy — the primary
  Portuguese SEO target).
- **hreflang** alternates (`en`, `pt`, `x-default`) on every page and a language
  switcher (English · Português) in the footer, so Google serves the right
  language and the two versions don't compete.
- **Responsive tool-nav overflow menu** (`static/js/nav.js`): tools that don't
  fit collapse into a "More ▾" dropdown instead of clipping or scrolling —
  adapts to any width and OS font metrics, with a horizontal-scroll fallback when
  JS is off.

### Changed
- The tool-nav items are slightly more compact so more fit before the overflow
  menu kicks in.

## [1.5.0] — 2026-07-13

SEO growth release: programmatic passport-size pages, FAQ rich results, and more
long-tail landing pages.

### Added
- **Passport photo pages by country** (`/passport-photo/<country>/`) — 22
  programmatic landing pages (US, UK, Canada, Schengen/EU, India, China, Japan,
  Brazil and more) targeting high-intent "\<country\> passport photo size"
  queries. Each shows the exact size in mm + pixels @300 DPI, background and
  head-size requirements, a country-specific FAQ, breadcrumb structured data, and
  a CTA that opens the maker **with that size pre-selected** (via `?w=&h=&country=`).
  All are listed in the sitemap and cross-linked.
- **FAQ sections with `FAQPage` structured data** on the home page and the
  passport and upscaler tools (plus the country pages) — real, keyword-rich
  content that can earn expanded FAQ rich results in search. The visible
  accordion and the JSON-LD render from one source (`remover/seo_content.py`).
- **More use-case landing pages** — eBay listings, Discord avatars, and Twitch /
  streaming, bringing the keyword-targeted `/remove-background/<slug>/` set to 11.
- The passport tool now lists **all supported countries** with internal links to
  their size pages.
- **About, Privacy Policy and Terms of Use pages** (`/about/`, `/privacy/`,
  `/terms/`) — accurate to the privacy-first architecture, linked in the footer
  and sitemap. The privacy policy discloses analytics and AdSense cookie use
  (commonly required for AdSense approval), and the About page cross-links every
  tool with a contact address.
- **`Organization` structured data** (name, URL, logo) site-wide for brand
  recognition in search.

### Changed
- **Sitemap** now includes `<lastmod>` and differentiated `<priority>` per page
  (home 1.0, tools 0.9, landing/country 0.7, info 0.4) instead of a flat 1.0.
- **404 page** now links to every tool so a wrong URL still lands somewhere useful.
- Removed a duplicate Google Fonts request in `<head>` (minor page-load win).

## [1.4.0] — 2026-07-13

Two new AI tools, a big background-removal speed-up, and monetization wiring.

### Added
- **Passport & ID photo maker** (`/passport-photo/`) — removes the background,
  drops the subject on a compliant background (white / off-white / grey / blue),
  and exports the **exact biometric pixel size at 300 DPI** for the US (2×2 in),
  EU / Schengen / UK / India / Australia (35×45 mm), Canada (50×70 mm), China
  visa (33×48 mm) or any **custom** size. Includes crown/chin/centre **guide
  lines** and a head oval, **auto-fit**, drag-and-zoom positioning, and a
  **6×4 inch print sheet** tiled with copies (with cut lines) for photo kiosks.
  100% in the browser.
- **AI image upscaler** (`/upscale/`) — enlarges images **2× or 4×** with a
  neural super-resolution model (ESRGAN via UpscalerJS + TensorFlow.js) running
  on the **GPU (WebGL)**. Large inputs are processed in tiles to stay within GPU
  memory; the model is lazy-loaded on first use and cached. No watermark, nothing
  uploaded.
- **Monetization** — Google AdSense loader (env-gated via `ADSENSE_CLIENT`) plus
  an optional in-content ad unit (`ADSENSE_SLOT_LANDING`), rendered on the
  **marketing / SEO landing pages only**. The interactive tool pages stay ad-free
  and fast.

### Changed
- **Faster background removal.** The background-remover, sticker, Instagram and
  passport pages are now served **cross-origin isolated** (COOP + COEP
  `credentialless`), which unlocks multi-threaded + SIMD WASM. On isolated pages
  the tool now runs the **full-quality `isnet` model** (instead of the quantized
  `isnet_quint8`) without freezing the page — a large speed and edge-quality win.
  Non-isolating browsers (e.g. Safari) transparently keep the quantized fallback.
- CSP: allow the AdSense script/frame hosts (used only on landing pages) and
  broaden `img-src` to `https:` for ad creatives.

## [1.3.0] — 2026-07-09

Toolbox release: two brand-new standalone tools, a richer Instagram editor, and
a smoother, safer background-remover workflow.

### Added
- **Image compressor** (`/compress/`) — shrink JPG / PNG / WEBP file size with a
  **quality** slider or a **target size** ("under 200 KB" and it binary-searches
  the quality to hit it), with an optional max-dimension downscale. Shows the
  before→after size and % saved per image and across the batch, never returns a
  file bigger than the original, and downloads singly or as a ZIP. 100% in the
  browser.
- **Meme generator** (`/meme-maker/`) — drop any image, add classic **top &
  bottom** captions in a bold outlined meme font (Impact / Anton / Oswald),
  drag them anywhere, tune size / outline / colour / uppercase, and export a PNG
  or JPG or copy straight to the clipboard. Nothing is uploaded.
- **Favicon & app-icon generator** (`/favicon-generator/`) — drop one image and
  get a complete icon set as a ZIP: a multi-size `favicon.ico` (16/32/48), PNGs
  for every common size, a 180×180 Apple touch icon, 192/512 PWA icons plus a
  **maskable** 512 with a safe zone, a ready `site.webmanifest`, and the exact
  `<link>` HTML to paste. Pick a background (transparent or any colour), a shape
  (square / rounded / circle) and padding, set the app name / short name / theme
  colour, and preview the real 16px icon in a browser-tab mock-up. 100% in the
  browser.
- **WhatsApp & Telegram sticker maker** (`/sticker-maker/`) — removes the
  background automatically, adds the classic sticker **outline** (colour +
  thickness) and a **draggable caption** in bold / clean / tall / script fonts,
  and exports a ready-to-use **512×512 transparent WebP** (or PNG). Nothing is
  uploaded.
- **AVIF export** in the image converter — next-gen, smallest-file output on
  Chromium, alongside PNG / JPG / WEBP.
- **Instagram editor upgrades** — add **text captions** (font, colour, size,
  drag to place), a **logo / watermark** overlay you can upload and position, a
  coloured **frame**, and **save your own looks** (My looks) for reuse. The
  optional background removal now drops in a solid colour inline.
- **Undo / redo and “apply to all”** in the background remover — step backward
  and forward through edits per card, and push one card's background, format,
  size and sticker settings onto every image at once.
- **Landing-page polish** — a privacy reassurance ("Your images never leave your
  device") right at the dropzone, a friendlier first-run model loader ("Loading
  the AI — one-time, then instant"), and a sticky **"Remove a background"** button
  that fades in once the upload area scrolls out of view.
- **Four new keyword-targeted landing pages** (`/remove-background/<slug>/`) for
  **car photos**, **clothing & fashion**, **pet photos** and **YouTube
  thumbnails** — added to the same `USE_CASES` source, so each is automatically
  indexed in the sitemap, linked from the footer, and carries breadcrumb
  structured data. These widen search entry points on lower-competition
  long-tail queries.

### Changed
- **UI polish across every tool** — the app now actually loads its intended
  typeface (**Inter**, which was declared but never served) and pairs it with a
  **Bricolage Grotesque** display face on the headlines, so pages read designed
  rather than templated. Glass surfaces gained a top-edge sheen and a warmer,
  slightly indigo-tinted dark neutral, and every page carries a subtle ambient
  brand glow for depth instead of flat grey. **Result cards** now lift with a
  layered, brand-tinted shadow on hover. All at the shared layer, so it
  propagates to the whole toolkit.
- **Real before/after hero demo** — the homepage comparison slider now shows
  actual photos resolving to genuine transparent cut-outs (a person, a pet and a
  classic car — covering the profile-picture, pet and car use cases), **rotating
  through the three** with a crossfade, pausing on interaction and respecting
  reduced-motion. The cut-outs were produced by ClearBG itself, so they reflect
  the tool's real output.
- **Refined controls** — every range slider across the tools now uses a thin
  track with a floating thumb instead of the default browser control, and text
  selection is brand-tinted.
- **Gradient primary buttons** — the main call-to-action buttons on every page
  (Select images, Download, …) now carry the brand gradient with a hover-brighten
  instead of flat indigo.
- **Success flourish** — a green check-mark pops over the result the moment a
  background is removed, so the "magic moment" feels rewarding.
- **Rebranded to ClearBG** (`clearbg.pt`) — new name across the header, footer,
  PWA manifest, error pages and structured data; a new **logo/favicon** (a clean
  photo/image glyph on the brand gradient), full-bleed **maskable** app icons
  with a proper safe zone, and a branded Open Graph share image. The GitHub link
  and tech-stack line were removed from the site chrome.
- **Full-resolution exports run in a Web Worker** (`compose-worker.js`) on an
  OffscreenCanvas, so downloading a large, heavily-styled image no longer freezes
  the tab. The main thread falls back to the in-page compositor if the worker is
  unavailable, and a parity guard keeps the two in sync.
- **Colour picker** rebuilt: an arbitrary-colour picker without the flaky
  eyedropper, a visible swatch border, and no GPU-freezing `backdrop-filter`.

### Fixed
- Compositing very large images could freeze the tab (unbounded preview
  resolution) — preview resolution is now capped.
- Various colour-picker glitches on label-wrapped inputs and the native colour
  dialog appearing unexpectedly.

## [1.2.0] — 2026-07-06

Editing release: an interactive crop tool for shaping the finished cut-out.

### Added
- **Crop tool** — crop to a **circle**, **square**, **rounded square**, or a
  **4:5 / 16:9 / 9:16** aspect ratio. Zoom (slider or scroll) and drag to
  reposition inside the frame; the live preview uses the same geometry as the
  export, so what you see is what you get. Circle and rounded shapes are masked
  with real transparency in the PNG, and fall back to a white fill for JPG. The
  crop is non-destructive — re-open to adjust or **Remove crop** to revert — and
  is applied to single downloads, the copy action, and the batch ZIP.
- **Crop source toggle** — crop either the transparent **cut-out** or the
  **original image with its background intact**, so you can crop without
  removing the background. The crop dialog opens immediately on the original,
  even before (or without) background removal finishing; the cut-out option
  unlocks once removal completes.
- **Sticker effects** — a coloured **outline/stroke**, **drop shadow**, and
  **padding** around the cut-out, composited resolution-independently into the
  exported PNG.
- **Custom crop ratio and orientation** — enter any **W:H** ratio in the crop
  dialog, and **rotate 90°** / **flip** horizontally or vertically. Combined with
  zoom and drag, this frames an arbitrary region without preset shapes.
- **Rich backgrounds** — beyond solid colours, place the cut-out on a **two-colour
  gradient** (with adjustable angle), a **blurred version of the original photo**,
  or an **uploaded image**.
- **Export sizes** — scale the exported result to a **profile picture (512×512)**,
  a **story (1080×1920)**, or a **custom width × height**, preserving aspect
  without distortion.
- **Instagram photo editor** (`/instagram`) — a standalone tool (like the
  converter) for editing photos for Instagram **without needing to remove the
  background**. Upload a photo and: pick a format (Post, Portrait, Story/Reel,
  Landscape, Profile) that crops to the right aspect and exports at Instagram's
  exact pixels; choose **Fill** (crop) or **Fit** (post the whole photo with no
  crop, filling the gaps with a blurred copy or a solid colour); add a coloured
  **border**; apply **12 on-trend one-tap looks** (Vivid, Punch, Clean, Golden,
  Moody, Film, Noir, Warm, Cool, Fade, Vintage) and dial their **strength** up or
  down; fine-tune brightness / contrast / saturation / warmth / **sharpen** /
  **film grain** / vignette; **press-and-hold to compare** against the original;
  toggle **Story/Reel safe-zone guides** so captions and UI don't cover faces;
  split a wide photo into a seamless **swipeable carousel** (2–3 tiles, exported
  as a ZIP); crop and reposition with drag + zoom; and optionally remove the
  background and drop in a solid colour. Everything runs in the browser.
- **Crop tool page** (`/crop`) — a standalone crop tool (no background removal):
  crop to a **rectangle, rounded square or circle** at a **1:1 / 4:5 / 3:4 /
  16:9 / 9:16** or **custom W:H** ratio (or the photo's original ratio), with
  **rotate** (90°) and **flip**, zoom and drag. Exports a full-resolution
  transparent **PNG** (rounded/circle keep transparent corners) or a **JPG**.
- **Support link** — an optional "Buy me a coffee" button in the footer.

### Changed
- Instagram sizing now lives in the dedicated `/instagram` editor rather than in
  the background remover's options, keeping each tool focused.

### Fixed
- **Slow removal / "page not responding" freeze** — background removal now uses
  the quantized **`isnet_quint8`** model instead of the full `isnet`. Inference is
  markedly faster and the download smaller, so the main-thread stall stays short
  enough to avoid the browser's "page unresponsive" prompt. Applied across the
  remover, sticker maker and Instagram editor. (Swap back to `isnet` in
  `CONFIG.removalOptions` for the last few % of edge quality at the cost of speed.)
- Instagram looks that included sharpening (Vivid, Warm, Cool, Punch and others)
  silently lost their colour grading: combining an SVG `url()` sharpen filter with
  filter functions in one canvas `ctx.filter` voids the whole filter in Chromium
  and Safari. Sharpen is now a separate convolution pass, so every look applies.
- Crop dialog silently did nothing when opened before background removal
  finished; it now opens immediately on the original image.
- Overlapping preview renders (e.g. dragging the padding slider) could commit an
  out-of-order result; the latest render now always wins.

### Changed
- Hardened the editor and crop dialogs: keyboard focus is trapped while open and
  returned to the trigger on close, shape/source toggles expose `aria-pressed`,
  and failed image composites surface a toast instead of failing silently.

## [1.1.0] — 2026-07-03

Search-visibility release: verified the site in Google Search Console and
expanded the SEO surface, plus a batch-workflow convenience.

### Added
- **Search-engine ownership verification** via optional `<meta>` tags, driven by
  the `GOOGLE_SITE_VERIFICATION` and `BING_SITE_VERIFICATION` environment
  variables.
- **Keyword-targeted use-case landing pages** at `/remove-background/<slug>/`
  (product photos, profile pictures, logos, signatures). Pages are generated
  from a single `USE_CASES` source that also feeds the sitemap, homepage cards,
  and site-wide footer navigation. Each page carries `BreadcrumbList`
  structured data.
- **Session memory for background & output format** — the last-used background
  color and export format are remembered (via `localStorage`) and pre-applied to
  each new image, so batch runs no longer need re-selecting per image.

### Changed
- **FAQ structured data is now generated from a single source** (`FAQS`) instead
  of being hardcoded in the template, so the `FAQPage` rich-result markup can no
  longer drift from the visible FAQ.
- Lowered the `robots.txt` / `sitemap.xml` cache lifetime from 24h to 1h so SEO
  changes reach crawlers faster.

### Fixed
- **Scheme-less `SITE_URL`** (e.g. `example.com`) produced invalid sitemap
  `<loc>` URLs that Google Search Console rejected; a bare domain is now
  auto-normalized to `https://`.

## [1.0.0]

Initial public release.

- In-browser AI background removal via `@imgly/background-removal` — no uploads,
  no watermarks, full-resolution output.
- Drag & drop / file picker / clipboard upload, batch processing, ZIP download,
  before/after comparison, zoom lightbox.
- Manual **refine brush editor** with zoom/pan, soft brushes, edge smoothing,
  undo and keyboard shortcuts.
- Custom background colors and PNG / JPG / WEBP export.
- Standalone in-browser **image format converter** (`/convert`).
- PWA support (installable, service worker), privacy-friendly analytics.
- SEO foundation: meta / Open Graph / Twitter cards, JSON-LD, `robots.txt`,
  `sitemap.xml`, canonical URLs.
- Light/dark theme, responsive glassmorphism UI, accessibility support.
- Stateless Django backend (no database) deployable to Vercel, Docker, or a
  classic Nginx + Gunicorn VPS.

[1.3.0]: https://github.com/josenovais97/bgremover/releases/tag/v1.3.0
[1.2.0]: https://github.com/josenovais97/bgremover/releases/tag/v1.2.0
[1.1.0]: https://github.com/josenovais97/bgremover/releases/tag/v1.1.0
[1.0.0]: https://github.com/josenovais97/bgremover/releases/tag/v1.0.0
