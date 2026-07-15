/**
 * Global "images processed" social-proof counter (client side).
 *
 * Reads the live total from /api/stats/ and shows it in the hero badge (if the
 * page has one). Exposes window.__clearbgReport(n) so the tools can increment
 * the counter after a real cut-out. If the server reports the counter disabled
 * (Upstash not configured), nothing is shown — no fabricated numbers.
 */
(function () {
  const el = document.getElementById('social-proof');
  const numEl = document.getElementById('social-proof-count');
  const lang = document.documentElement.lang || 'en';

  // Only show the badge once the count is worth showing. 1 = always show.
  // Raise this (e.g. 500 or 1000) to keep the badge hidden until the number is
  // genuinely impressive — a tiny count is weaker social proof than none.
  const MIN_DISPLAY = 1;

  // Full, concrete numbers up to 999,999 ("12,412") — more tangible than
  // "12k"; compact "M" only once it gets truly large.
  function fmt(n) {
    if (n >= 1e6) return (n / 1e6).toFixed(1).replace(/\.0$/, '') + 'M';
    try { return n.toLocaleString(lang); } catch (e) { return String(n); }
  }

  // Count up from 0 to the real total the first time the badge appears — a
  // small flourish that draws the eye without inventing any numbers.
  function animateCount(target) {
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      numEl.textContent = fmt(target);
      return;
    }
    const duration = 900;
    const start = performance.now();
    function step(now) {
      const p = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - p, 3); // ease-out cubic
      numEl.textContent = fmt(Math.round(target * eased));
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  let revealed = false;
  function show(count) {
    if (!el || !numEl || typeof count !== 'number' || count < MIN_DISPLAY) return;
    if (revealed) { numEl.textContent = fmt(count); return; }
    revealed = true;
    el.classList.remove('hidden');
    animateCount(count);
  }

  // Which tool the visitor is on, derived from the URL path (locale prefix
  // stripped) so per-tool conversion tracking needs no change in each tool's JS.
  const TOOL_BY_PATH = {
    '/': 'home', '/blur-background/': 'blur',
    '/ecommerce/': 'ecommerce', '/sticker-maker/': 'sticker',
    '/passport-photo/': 'passport', '/instagram/': 'instagram', '/crop/': 'crop',
    '/convert/': 'convert', '/compress/': 'compress', '/meme-maker/': 'meme',
    '/favicon-generator/': 'favicon',
  };
  function toolId() {
    const p = location.pathname.replace(/^\/pt(\/|$)/, '/');
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
      }).then((r) => r.json()).then((d) => { if (d && d.enabled) show(d.count); }).catch(() => {});
    } catch (e) { /* ignore */ }
  };

  // Only fetch the display total on pages that show the badge (the home page).
  if (el) {
    fetch('/api/stats/')
      .then((r) => r.json())
      .then((d) => { if (d && d.enabled) show(d.count); })
      .catch(() => {});
  }
})();
