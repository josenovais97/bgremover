/**
 * Usage reporting (client side).
 *
 * Exposes window.__clearbgReport(n, event) so the tools can record a real
 * cut-out or export against /api/stats/. Fire-and-forget: no response is read
 * and nothing is rendered.
 *
 * This file used to also drive a hero badge showing the live "N this week /
 * N all time" totals. The numbers were real, but at this stage they were small,
 * and a small number is weaker proof than none — it invites a visitor to size up
 * the product instead of trying it. The homepage now states four properties that
 * are true on every visit (free / no signup / no watermark / nothing uploaded),
 * as static markup with nothing to fetch. The counter itself stays: the totals
 * are still worth having, they simply are not a sales argument yet.
 */
(function () {
  // Which tool the visitor is on, derived from the URL path (locale prefix
  // stripped) so per-tool conversion tracking needs no change in each tool's JS.
  // Keep in step with TOOLS in worker/lib.mjs — the server drops any tool it
  // doesn't recognise, so a missing entry here is a silently lost count.
  const TOOL_BY_PATH = {
    '/': 'home', '/blur-background/': 'blur',
    '/ecommerce/': 'ecommerce', '/sticker-maker/': 'sticker',
    '/passport-photo/': 'passport', '/instagram/': 'instagram', '/crop/': 'crop',
    '/convert/': 'convert', '/compress/': 'compress', '/meme-maker/': 'meme',
    '/favicon-generator/': 'favicon', '/redact-image/': 'redact',
    '/exif-remover/': 'exif', '/resize-image/': 'resize',
    '/watermark-image/': 'watermark', '/gif-maker/': 'gif',
    '/qr-code-generator/': 'qr', '/text-behind-image/': 'text_behind',
    '/image-to-pdf/': 'pdf', '/color-palette/': 'palette', '/collage/': 'collage',
    '/add-border/': 'border', '/base64-image/': 'base64',
    '/video-to-gif/': 'video_gif', '/video-converter/': 'video_converter',
    '/screenshot-beautifier/': 'screenshot',
    '/remove-object/': 'remove_object', '/photo-filters/': 'photo_filters',
    '/upscale/': 'upscale', '/heic-to-jpg/': 'heic',
    '/pdf-to-image/': 'pdf_to_image', '/image-to-text/': 'ocr',
    '/svg-to-png/': 'svg_to_png',
    '/word-to-pdf/': 'word_to_pdf', '/pdf-to-word/': 'pdf_to_word',
    '/merge-pdf/': 'pdf_tools', '/csv-to-excel/': 'csv_excel',
  };
  function toolId() {
    // Every configured locale, not just /pt — the Spanish pages were reporting
    // as 'other' (and so being dropped) for as long as /es/ has existed.
    const p = location.pathname.replace(/^\/(pt|es)(\/|$)/, '/');
    if (TOOL_BY_PATH[p]) return TOOL_BY_PATH[p];
    if (p.indexOf('/passport-photo/') === 0) return 'passport';  // country sub-pages
    return 'other';
  }

  // Report a real cut-out (fire-and-forget). Available on every page.
  // `event` defaults to 'processed'; pass 'downloaded' on a successful export.
  window.__clearbgReport = function (n, event) {
    try {
      fetch('/api/stats/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ n: n || 1, tool: toolId(), event: event || 'processed' }),
        keepalive: true,
      }).catch(() => {});
    } catch (e) { /* ignore */ }
  };
})();
