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

  // Compact, readable numbers: 3 → "3", 1240 → "1.2k", 34500 → "34.5k", 2.1M.
  function fmt(n) {
    if (n >= 1e6) return (n / 1e6).toFixed(1).replace(/\.0$/, '') + 'M';
    if (n >= 1e4) return Math.round(n / 1e3) + 'k';
    if (n >= 1e3) return (n / 1e3).toFixed(1).replace(/\.0$/, '') + 'k';
    try { return n.toLocaleString(lang); } catch (e) { return String(n); }
  }

  function show(count) {
    if (!el || !numEl || typeof count !== 'number' || count < MIN_DISPLAY) return;
    numEl.textContent = fmt(count);
    el.classList.remove('hidden');
  }

  // Report a real cut-out (fire-and-forget). Available on every page.
  window.__clearbgReport = function (n) {
    try {
      fetch('/api/stats/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ n: n || 1 }),
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
