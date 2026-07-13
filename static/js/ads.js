/**
 * Initialise any AdSense units present on the page.
 *
 * Kept as an external file (not inline) so it satisfies the site's strict CSP,
 * which does not allow 'unsafe-inline' scripts. Each <ins.adsbygoogle> needs one
 * push() to be filled. Wrapped in try/catch so an ad blocker or a not-yet-approved
 * AdSense account fails silently instead of throwing.
 */
(function () {
  try {
    document.querySelectorAll('ins.adsbygoogle').forEach(function () {
      (window.adsbygoogle = window.adsbygoogle || []).push({});
    });
  } catch (e) {
    /* AdSense unavailable — ignore. */
  }
})();
