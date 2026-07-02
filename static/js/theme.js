/**
 * Theme handling, shared across all pages.
 *
 * The IIFE applies the saved/system theme before first paint (no flash). The
 * toggle wiring + `window.toggleTheme` live here (not in a page module) so the
 * theme button works on every page. Kept as a classic, dependency-free script.
 */
(function () {
  try {
    var stored = localStorage.getItem('theme');
    var prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (stored === 'dark' || (!stored && prefersDark)) {
      document.documentElement.classList.add('dark');
    }
  } catch (e) {
    /* localStorage may be unavailable (private mode) — ignore. */
  }
})();

function toggleTheme() {
  var dark = document.documentElement.classList.toggle('dark');
  try {
    localStorage.setItem('theme', dark ? 'dark' : 'light');
  } catch (e) {
    /* ignore */
  }
}
window.toggleTheme = toggleTheme;

document.addEventListener('DOMContentLoaded', function () {
  var btn = document.getElementById('theme-toggle');
  if (btn) btn.addEventListener('click', toggleTheme);
});

// Register the PWA service worker (installable + offline app shell).
if ('serviceWorker' in navigator) {
  window.addEventListener('load', function () {
    navigator.serviceWorker.register('/sw.js').catch(function () {});
  });
}
