/*
 * Sticky "Remove a background" CTA for the landing page.
 * Fades in once the upload dropzone has scrolled out of view, so a visitor
 * reading the how-it-works / FAQ sections is always one tap from uploading.
 * Kept separate from app.js so the core tool logic stays untouched.
 */
(function () {
  const dz = document.getElementById('dropzone');
  const cta = document.getElementById('sticky-cta');
  const landing = document.getElementById('landing');
  const fileInput = document.getElementById('file-input');
  if (!dz || !cta) return;

  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function show(on) {
    cta.classList.toggle('opacity-0', !on);
    cta.classList.toggle('translate-y-4', !on);
    cta.classList.toggle('pointer-events-none', !on);
  }

  // Show once the dropzone has scrolled up past a trigger line at ~45% of the
  // viewport (so it works even on short pages where it never fully leaves view),
  // and only while the landing — not the results workspace — is on screen.
  const io = new IntersectionObserver(function (entries) {
    const e = entries[0];
    const landingVisible = !landing || !landing.classList.contains('hidden');
    show(landingVisible && !e.isIntersecting);
  }, { rootMargin: '-45% 0px 0px 0px', threshold: 0 });
  io.observe(dz);

  cta.addEventListener('click', function () {
    dz.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'center' });
    if (fileInput) window.setTimeout(function () { fileInput.click(); }, reduce ? 0 : 450);
  });
})();
