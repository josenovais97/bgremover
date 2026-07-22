# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project aims to
follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **QR codes for Wi-Fi, contacts, email, SMS and phone**, not just links. A QR can
  carry these already, but only in the exact syntax a scanner expects
  (`WIFI:T:WPA;S:…;P:…;;`, a vCard block, `mailto:`), so the content box had been
  advertising "Wi-Fi · email" while accepting raw text — you had to know the
  format and type it yourself. Each type now has real fields and qr.js encodes
  them, including the escaping the Wi-Fi format needs and the structured-vs-
  escaped distinction in a vCard `N:` line. A type with its key field still blank
  disables export rather than rendering a scannable code for a single space.
- **The GIF maker's export goes through the shared download path**, and
  deliberately opts OUT of cross-tool chaining (`CBG.download(…, {chain: false})`).
  Every destination tool composites through a canvas, so a chained GIF would
  arrive as its first frame with the animation silently discarded. Not offering
  the hop is better than offering a lossy one.
- **Cross-tool chaining is now advertised** on the homepage tool grid and in the
  related-tools block at the foot of every tool page. The feature shipped in
  1.9.0 with no way to discover it: the bar that offers the next tool only
  appears once you export, which is the moment you were already leaving.
- **The chain bar shows the journey** — "Crop → Convert → Compress — keep going:"
  rather than a fixed label. 1.9.0 carried the trail through IndexedDB and
  sessionStorage but never rendered it; without it the bar could only say "here
  are some other tools", which is the thing a user already knows. Arriving at a
  tool with nothing in flight clears the trail, so an earlier journey is never
  shown over an unrelated image.
- **Compare against the original in Blur & Redact** (`/redact-image/`). The point
  of redacting is that something is really covered, and that can only be judged
  against the original — but the tool only ever showed the redacted result. A
  toggle (not press-and-hold, so it works the same for a mouse, a thumb and a
  keyboard) swaps the canvas, with a badge on the photo so the two views can't be
  confused. Drawing while comparing snaps back rather than placing a region
  against a picture you aren't editing.
- **A demo on Image to PDF** (`/image-to-pdf/`), which was the only tool page
  without one. Deliberately not the shared before/after slider: there is no
  "after" of the same frame to wipe between — three photos become one paged
  document, and the document is the thing worth showing. The asset is generated
  from the same page geometry the exporter uses (A4 portrait, image fitted inside
  the margin).

### Fixed
- **`tests/smoke_crop.py` had been failing and nobody noticed.** The options
  panel gained tabs (Background / Size & format / Effects) and now opens by
  itself when a card finishes, so the test's unconditional `.options-btn` click
  was *closing* it and every control below became unreachable. It ensures the
  panel is open and activates the right tab per assertion. This is the only
  end-to-end coverage of the remover's crop dialog, effects and export sizing —
  the 98 Django tests assert markup, not behaviour.
- **The EXIF demo contradicted the sample photo the same page offers.** It listed
  an invented iPhone-in-Lisbon set while "Try a sample photo" loads a Pixel 7 Pro
  photo taken in Kenya. The demo now shows the real metadata inside that file.

### Changed
- **The QR generator was rebuilt to match the rest of the toolkit.** It read as
  the cheapest page on the site: the code floated small in a mostly empty panel,
  the download buttons sat below six stacked panels of equal visual weight, and
  the four style presets were four words in four boxes — you had to click each
  one to find out what it did.
  - The style presets now render a live miniature of the code they produce,
    painted by the same routine as the 512px export (the drawing code was pulled
    out of `App` into free functions taking an options object, so a thumbnail
    cannot drift from what clicking it does).
  - Downloads moved beside the preview, which is presented on a white card that
    stays white in dark mode — a QR is ink on paper, and previewing it on a dark
    surface misrepresents what you print.
  - Added one-tap curated colour pairs, a live export summary (size, recovery
    level), and a **low-contrast warning**: the two reliable ways to make a QR
    unscannable are low contrast and a light foreground, and nothing flagged
    either. Gradients are checked at their weakest stop.
  - Size, error correction and quiet-zone margin moved into a collapsed
    "Advanced" panel; they had been pushing the download button off the page.

## [1.9.0] — 2026-07-22

Nineteen tools become one editor, the runtime speaks Portuguese, and the site
stops telling Google about translations that don't exist.

### Added
- **Chain an image across tools.** Export from any tool and a "Keep editing this
  image" bar offers the others; the result travels through IndexedDB with no
  re-upload, for as many hops as you like — *remove background → crop →
  watermark → compress*. Previously this ran one hop, from the remover to three
  hard-coded destinations; with nineteen tools the interesting journeys are
  longer than that, and re-picking the file at every step was what made the site
  feel like nineteen separate pages instead of one editor.

  Any tool is a destination automatically: the incoming file is delivered to
  whichever input carries `data-chain-input` and the tool's own change handler
  does the rest, so no tool needs to know the feature exists. Destinations come
  from `TOOL_NAV`, so a new tool joins by existing. The QR generator is excluded
  — its only file input is an optional centre logo.
- **`CBG.t()` — runtime strings are translatable.** Every message a tool raises
  while you use it ("Crop applied", "Export failed", "Copied to clipboard") was
  an English literal in JS. A Portuguese visitor hit English at the exact moment
  something succeeded or failed, on the one page that *was* translated.
  `remover/translations.py` now carries a second catalogue (`JS_UI`), shipped as
  JSON on `/pt/` pages only — keys are the English source text, so an English
  page needs no payload at all. `CBG.plural(n, one, many)` picks between two keys
  where the languages disagree about which counts are plural.

### Fixed
- **The site advertised a Portuguese version of 60 pages that render English.**
  Every page emitted `hreflang="pt"` and the sitemap listed all 71 paths twice,
  but only the home page and the 11 use-case landings are actually translated —
  so ~60 Portuguese URLs were near-duplicates of their English twins, declared as
  translations. `views.TRANSLATED_PATHS` now gates the alternate set, the sitemap
  and the canonical: an untranslated `/pt/` page stays reachable and keeps its
  translated chrome, but it is not advertised as Portuguese and canonicalises to
  its English twin instead of competing with it. Sitemap: 142 → 84 URLs.

  The footer language switcher is deliberately *not* gated on this. It shared the
  flag before, so narrowing one would have silently removed the other from most
  of the site.
- **Sixteen tools each carried a private `Toast` that built its markup with
  `innerHTML`** — interpolating the user's own file name into HTML. They now use
  `CBG.Toast`, which uses `textContent`.

### Changed
- **The `window.CBG` migration is finished.** 1.8.0 introduced the shared kit and
  said it replaced the per-tool copies; four of nineteen modules had actually
  adopted it, so the codebase was paying for both approaches. All nineteen now
  use it — `$`, `$$`, `Toast`, `loadImage`, `humanSize`, `download` — which
  deleted ~1.4 KB of duplication per module, and is what makes chaining work
  everywhere: `CBG.download()` is the single export path, so the thing you just
  saved is the thing offered to the next tool.
- `static/js/handoff.js` is gone; `CBG.Chain` replaces it. Its TTL went from 60 s
  to 5 minutes — long enough for a slow page load on a phone, short enough that
  the image is always one you chose moments ago.
- 79 → 98 tests. The new ones guard the things this release could silently
  regress: `TranslationCoverageTests` measures how much Portuguese each page
  really renders and fails if `TRANSLATED_PATHS` disagrees in either direction;
  `JsTranslationTests` fails on a string wrapped in `t()` with no catalogue entry,
  a raw literal passed to `Toast.show`, or a `{placeholder}` dropped in
  translation; `ChainTests` and `SharedKitTests` guard the chain wiring and stop a
  tool re-growing a private `Toast` or a hand-rolled download anchor.

## [1.8.0] — 2026-07-21

Six new tools since 1.7.0, batch support where it was missing, an image → PDF
builder, and a round of correctness fixes to the SEO/PWA plumbing.

### Added
- **Image → PDF** (`/image-to-pdf/`) — combine photos or scans into one
  multi-page PDF (pdf-lib). Drag thumbnails to reorder, remove pages, pick
  A4 / US Letter / fit-the-image, auto or fixed orientation, and a margin.
  JPEG and PNG bytes are embedded **as-is** (no canvas round-trip), so a scan
  keeps exactly the quality it had. Built in the page — the format people use for
  IDs, contracts and payslips never leaves the device.
- **Batch for resize, watermark and EXIF removal.** The first file stays the one
  you tune on screen; the rest are exported with the same settings as a ZIP.
  Queued images keep their own aspect ratio (they're fitted inside the target box
  rather than forced to its exact dimensions), and every watermark setting is
  already relative to the image, so one mark lands correctly on any size.
- **Auto-detect faces** in the redact tool, via the browser's own on-device
  FaceDetector. The button only appears where the API exists, and detected boxes
  are padded outwards so hair and chin are actually covered.
- **Trim transparent edges** in the background remover — crops the export to the
  subject's alpha bounding box *before* any background, outline, shadow or
  padding is composited, so those hug the subject instead of the original frame.
- **Quick background presets** (Transparent / White / Studio / Blur photo) above
  the remover's detailed controls. Each drives the same setter as its detailed
  control, so selection stays in sync in both directions.
- **`window.CBG`** (`static/js/kit.js`) — shared `$`, `Toast`, `loadImage`,
  drag/drop/paste wiring, ZIP export and a localStorage settings store, replacing
  per-tool copies. A classic script, because Django's static storage cannot
  rewrite ES-module import paths.
- **PWA app shortcuts** and a dedicated maskable icon; resize/watermark/PDF now
  remember their layout choices between visits.
- **`EveryToolTests`** walks `TOOL_NAV` itself, so every tool present and future
  is checked to render, load its JS, own an accent, and appear in the sitemap and
  the homepage grid. 62 → 79 tests.

### Fixed
- **The service-worker shell had fallen nine tool pages behind** while
  `/offline-image-editor/` advertised those tools as working offline. The shell
  is now generated from the tool list and the contents of `static/js`, and a test
  fails if it drifts again.
- **The Portuguese site was absent from the sitemap entirely** — only reachable
  through footer links. Every page is now listed once per language, and each
  entry carries the full `xhtml:link` hreflang set (71 paths → 142 URLs).
- **`og:image` and the JSON-LD identity were built from the request host** while
  the canonical used `SITE_URL`, so a www/apex or http/https variant advertised a
  different image and identity than the canonical it pointed at.
- The remover's workspace, result card, refine editor and crop dialog were
  hard-coded English — a Portuguese visitor hit mixed language exactly at the
  moment of use. All of it now runs through `{% t %}`.
- `"purpose": "any maskable"` on every manifest icon (the documented
  anti-pattern) — there is now a dedicated maskable asset.
- The homepage carried **two Product Hunt badges**, one directly under the
  primary CTA, both hard-coded to the light theme. One badge remains, in the
  footer, and it follows the theme.

### Changed
- **Inter is self-hosted** (`static/css/inter.css` + `static/webfonts/inter/`).
  Google Fonts is now requested only by the four pages whose canvases paint with
  Anton / Bebas Neue / Pacifico / Playfair, and those carry a preconnect.
- **Bricolage Grotesque is gone.** It was downloaded on every page and used by
  nothing — no template ever referenced the `font-display` family it fed.
- **Preset backgrounds re-encoded**: 3.7 MB → 2.2 MB (−43%), capped at 1600px and
  ~250 KB each, so picking one is snappier.
- The homepage tool grid moved directly under the hero. The site is an 18-tool
  kit; the grid was below the explainer, where it was invisible without scrolling.
- Per-tool conversion counters now cover redact, EXIF, resize, watermark, GIF, QR,
  text-behind and PDF — they previously reported as `other` and were dropped.

## [1.7.0] — 2026-07-13

eCommerce tools, portrait-mode blur, and a real social-proof counter.

### Added
- **Marketplace product photos** (`/ecommerce/`) — one click removes the
  background, centres the product on pure white and exports the exact size
  **Amazon** (2000×2000, ~85% fill), **Etsy** (2000×2000) and **Shopify**
  (2048×2048) require. Optional transparent PNG and a soft-shadow toggle. Fully
  client-side; verified end-to-end (removal → compose → JPEG export).
- **AI background blur / portrait mode** (`/blur-background/`) — uses the
  removal mask to keep the subject sharp while blurring the background, for a
  phone-style depth effect, with an adjustable strength slider. Client-side.
- **Social-proof counter** — a genuine global "images processed" total backed by
  Upstash Redis (`/api/stats/`, env-gated via `UPSTASH_REDIS_REST_*`). Tools
  report a cut-out via `__clearbgReport()`; the home hero shows the live total.
  When Upstash isn't configured the counter is disabled and the badge stays
  hidden — **no fabricated numbers**.
- FAQ + `FAQPage` schema on both new tools; nav, footer and sitemap updated;
  Portuguese nav/footer labels for the new tools.

### Note
- The AI Image Generator and AI Product Photography were scoped out for now:
  they require a paid server-side generative model (and would upload user photos
  to a third party), which conflicts with the free/in-browser/private model.
  Deferred as a deliberate, separate decision.

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
