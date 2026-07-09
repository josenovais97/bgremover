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

/*
 * Rotate the hero before/after demo through a few real product subjects so the
 * landing feels alive. Crossfades the two images together (the slider keeps
 * working), pauses while the visitor is interacting, and stays put for anyone
 * who prefers reduced motion.
 */
(function () {
  const after = document.getElementById('demo-after-img');
  const before = document.getElementById('demo-before-img');
  const demo = document.getElementById('demo');
  if (!after || !before || !demo) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  const COUNT = 3;
  let idx = 1;
  let paused = false;
  demo.addEventListener('pointerenter', function () { paused = true; });
  demo.addEventListener('pointerleave', function () { paused = false; });

  const swap = (src, i) => src.replace(/demo\d+-/, 'demo' + i + '-');

  // Warm the other subjects so the first transition is instant.
  for (let i = 2; i <= COUNT; i++) { new Image().src = swap(after.src, i); new Image().src = swap(before.src, i); }

  function rotate() {
    if (paused) return;
    idx = (idx % COUNT) + 1;
    const aURL = swap(after.src, idx);
    const bURL = swap(before.src, idx);
    let ready = 0;
    const commit = () => {
      if (++ready < 2) return;
      after.style.opacity = '0';
      before.style.opacity = '0';
      window.setTimeout(() => {
        after.src = aURL; before.src = bURL;
        after.style.opacity = ''; before.style.opacity = '';
      }, 280);
    };
    const a = new Image(); const b = new Image();
    a.onload = commit; b.onload = commit;
    a.onerror = commit; b.onerror = commit;
    a.src = aURL; b.src = bURL;
  }
  window.setInterval(rotate, 4500);
})();

