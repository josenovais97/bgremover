/**
 * Responsive tool-nav overflow menu.
 *
 * The header tool switcher lists every tool. When they don't all fit on the
 * current screen (which varies by width AND OS font metrics), the trailing items
 * are moved into a "More ▾" dropdown instead of being clipped or forcing a
 * horizontal scroll. Recomputed on resize and once web fonts have loaded.
 *
 * Progressive enhancement: with JS off, the nav keeps its `overflow-x-auto`
 * scroll fallback and the "More" button stays hidden.
 */
(function () {
  const wrap = document.getElementById('tool-switcher');
  const nav = document.getElementById('tool-nav');
  const moreBtn = document.getElementById('tool-more-btn');
  const panel = document.getElementById('tool-more-panel');
  if (!wrap || !nav || !moreBtn || !panel) return;

  // In JS mode the dropdown handles overflow, so drop the scroll fallback
  // (which would otherwise clip the absolutely-positioned "More" button).
  nav.classList.remove('overflow-x-auto', 'no-scrollbar');

  const closePanel = () => {
    panel.classList.add('hidden');
    moreBtn.setAttribute('aria-expanded', 'false');
  };
  const openPanel = () => {
    panel.classList.remove('hidden');
    moreBtn.setAttribute('aria-expanded', 'true');
  };

  function layout() {
    // 1. Reset: move everything back into the row, hide the button.
    [...panel.querySelectorAll('[data-nav-item]')].forEach((el) => {
      el.classList.remove('w-full');
      nav.insertBefore(el, moreBtn);
    });
    moreBtn.style.display = 'none';
    closePanel();

    // 2. Does the full row fit? If so, we're done.
    if (nav.scrollWidth <= nav.clientWidth + 1) return;

    // 3. Reveal the button (so we can budget for its width) and move any item
    //    whose right edge would sit past the available space into the panel.
    moreBtn.style.display = 'inline-flex';
    const limit = nav.getBoundingClientRect().left + nav.clientWidth - moreBtn.offsetWidth - 10;
    let moved = false;
    [...nav.querySelectorAll('[data-nav-item]')].forEach((el) => {
      if (el.getBoundingClientRect().right > limit) {
        el.classList.add('w-full');
        panel.appendChild(el);
        moved = true;
      }
    });
    if (!moved) moreBtn.style.display = 'none';
  }

  moreBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    if (panel.classList.contains('hidden')) openPanel();
    else closePanel();
  });
  panel.addEventListener('click', (e) => e.stopPropagation());
  document.addEventListener('click', closePanel);
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closePanel(); });

  let raf;
  const schedule = () => { cancelAnimationFrame(raf); raf = requestAnimationFrame(layout); };
  window.addEventListener('resize', schedule);
  // Font swaps change label widths — re-run once fonts are ready.
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(layout);

  layout();
})();
