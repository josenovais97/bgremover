# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project aims to
follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

### Fixed
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

[1.2.0]: https://github.com/josenovais97/bgremover/releases/tag/v1.2.0
[1.1.0]: https://github.com/josenovais97/bgremover/releases/tag/v1.1.0
[1.0.0]: https://github.com/josenovais97/bgremover/releases/tag/v1.0.0
