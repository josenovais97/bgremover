/**
 * Console note addressed to the one visitor who checks: the developer who opens
 * DevTools to find out whether "nothing is uploaded" is true.
 *
 * That person is the site's best possible advocate and its harshest reviewer, so
 * this deliberately does NOT claim "zero network requests" — that claim is
 * trivially disproved in the Network tab (analytics, the counter, the model
 * download, ads on the guides) and one disproved claim discredits the real one.
 *
 * The real claim is narrower and actually verifiable: no request ever carries
 * your image. So the note names every request the page DOES make, then points at
 * the strongest proof available — go offline and everything still works, which
 * is only possible because the processing was never remote to begin with.
 *
 * Kept as an external file because the site's CSP has no 'unsafe-inline'.
 */
(function () {
  // A console banner is for humans reading a live page. Skip it when there is no
  // styling support (piped/CI consoles print the raw %c directives as noise).
  if (!window.console || !console.log) return;

  var h = 'font:600 14px/1.5 system-ui,sans-serif;color:#4F46E5';
  var b = 'font:13px/1.6 system-ui,sans-serif;color:inherit';
  var d = 'font:12px/1.6 system-ui,sans-serif;color:#6b7280';

  console.log(
    '%cClearBG — your images never leave this tab.\n' +
      '%cThe AI runs here, on your device. Two ways to check:\n' +
      '  1. Open the Network tab and process an image — no upload appears.\n' +
      '  2. Stronger: go offline (Network ▸ Offline, or turn off Wi-Fi) and\n' +
      '     reload. Every tool keeps working, including the background remover.\n\n' +
      '%cFull disclosure — the page does make these requests, and none of them\n' +
      'carry your image: the AI model and libraries (downloaded once, then\n' +
      'cached), Vercel Web Analytics, an anonymous "images processed" counter,\n' +
      'and Google AdSense on the written guides. Details: /privacy/',
    h, b, d,
  );
})();
