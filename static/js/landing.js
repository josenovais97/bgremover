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

  // Two conditions, tracked separately because they change at opposite ends of
  // the page: the dropzone must be scrolled away (there is something to jump
  // back to) and the footer must not be on screen (see below).
  let past = false;      // dropzone has scrolled up past the trigger line
  let atFooter = false;  // footer is in view

  function sync() {
    const landingVisible = !landing || !landing.classList.contains('hidden');
    show(landingVisible && past && !atFooter);
  }

  // Show once the dropzone has scrolled up past a trigger line at ~45% of the
  // viewport (so it works even on short pages where it never fully leaves view),
  // and only while the landing — not the results workspace — is on screen.
  const io = new IntersectionObserver(function (entries) {
    past = !entries[0].isIntersecting;
    sync();
  }, { rootMargin: '-45% 0px 0px 0px', threshold: 0 });
  io.observe(dz);

  // Stand down over the footer. Fixed to the bottom-right, the CTA sat on top of
  // the footer's own content — it covered the language switcher outright, hiding
  // whichever language sorted last. The footer is also the one place the CTA has
  // nothing left to offer: the visitor has reached the end of the page, and the
  // footer carries its own links to every tool.
  const footer = document.querySelector('footer');
  if (footer) {
    new IntersectionObserver(function (entries) {
      atFooter = entries[0].isIntersecting;
      sync();
    }, { threshold: 0 }).observe(footer);
  }

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

  // The rotation set is named by the template (see data-subjects there): each
  // entry is an [after, before] pair of already-resolved URLs. Deriving them in
  // here by rewriting the filename broke as soon as static assets were
  // content-hashed, because the hash belongs to the file, not to the pattern.
  let subjects;
  try { subjects = JSON.parse(demo.dataset.subjects || '[]'); } catch (e) { subjects = []; }
  if (subjects.length < 2) return;

  let idx = 0; // subjects[0] is what the markup already shows
  let paused = false;
  demo.addEventListener('pointerenter', function () { paused = true; });
  demo.addEventListener('pointerleave', function () { paused = false; });

  // Warm the other subjects so the first transition is instant — but not during
  // load. Fetching them eagerly put ~245 KB on the critical path for rotations
  // the visitor does not see for another 4.5 and 9 seconds, competing with the
  // hero itself and with the AI model warm-up for the same bandwidth. Idle time
  // arrives long before the first rotation, so the transition is still instant.
  const warmRest = () => {
    subjects.slice(1).forEach(function (pair) {
      new Image().src = pair[0];
      new Image().src = pair[1];
    });
  };
  if ('requestIdleCallback' in window) requestIdleCallback(warmRest, { timeout: 3000 });
  else window.setTimeout(warmRest, 1500);

  function rotate() {
    if (paused) return;
    idx = (idx + 1) % subjects.length;
    const aURL = subjects[idx][0];
    const bURL = subjects[idx][1];
    let ready = 0;
    let failed = false;
    // Both halves must load before the crossfade: swapping one at a time shows a
    // subject against the previous one's background. If either fails, keep the
    // subject that IS on screen — a broken image in the hero is worse than no
    // rotation, and this is the one thing the hero cannot afford to get wrong.
    const commit = (ok) => {
      if (!ok) failed = true;
      if (++ready < 2 || failed) return;
      after.style.opacity = '0';
      before.style.opacity = '0';
      window.setTimeout(() => {
        after.src = aURL; before.src = bURL;
        after.style.opacity = ''; before.style.opacity = '';
      }, 280);
    };
    const a = new Image(); const b = new Image();
    a.onload = () => commit(true); b.onload = () => commit(true);
    a.onerror = () => commit(false); b.onerror = () => commit(false);
    a.src = aURL; b.src = bURL;
  }
  window.setInterval(rotate, 4500);
})();

