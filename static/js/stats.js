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
  const fmt = (n) => { try { return n.toLocaleString(lang); } catch (e) { return String(n); } };

  function show(count) {
    if (!el || !numEl || typeof count !== 'number' || count <= 0) return;
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
