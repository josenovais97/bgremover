/**
 * Header tool switcher: pill row + "All tools" mega-menu.
 *
 * The pill row shows as many tools as fit on the current screen (which varies by
 * width AND OS font metrics); pills that don't fit are hidden rather than clipped
 * or scrolled. Every tool — including any hidden pill — is always reachable from
 * the grouped "All tools" menu, which is server-rendered (see base.html) so its
 * contents are stable and don't shuffle as the window resizes.
 *
 * Progressive enhancement: with JS off, the nav keeps its `overflow-x-auto`
 * scroll fallback and every tool is still reachable from the footer.
 *
 * The nav KEEPS `overflow-x-auto`: it's what constrains `clientWidth` to the
 * space actually available (otherwise the row grows to fit its content and
 * would report that everything fits, colliding with the header's utilities).
 * The mega-menu panel lives outside `#tool-nav`, so it is never clipped by it.
 */
(function () {
  const nav = document.getElementById('tool-nav');
  const moreBtn = document.getElementById('tool-more-btn');
  const panel = document.getElementById('tool-more-panel');
  if (!nav || !moreBtn || !panel) return;

  const chevron = moreBtn.querySelector('[data-chevron]');
  const pills = [...nav.querySelectorAll('[data-nav-item]')];

  const closePanel = () => {
    panel.classList.add('hidden');
    moreBtn.setAttribute('aria-expanded', 'false');
    if (chevron) chevron.style.transform = '';
  };
  const openPanel = () => {
    panel.classList.remove('hidden');
    moreBtn.setAttribute('aria-expanded', 'true');
    if (chevron) chevron.style.transform = 'rotate(180deg)';
  };

  function layout() {
    // Reveal every pill, then hide from the first one that doesn't fit onward.
    // Use inline `display` (not the `hidden` attribute) — a Tailwind display
    // utility like `inline-flex` would otherwise out-rank `[hidden]` and the
    // pill would stay visible, leaving the row overflowing.
    pills.forEach((el) => { el.style.display = ''; });
    if (nav.scrollWidth <= nav.clientWidth + 1) return; // everything fits
    const limit = nav.getBoundingClientRect().left + nav.clientWidth - moreBtn.offsetWidth - 8;

    // Measure every pill BEFORE hiding any. Hiding reflows the row and pulls the
    // later pills leftwards, so a measure-and-hide loop would find that a pill
    // which didn't fit now does — leaving an arbitrary set on show (tools 1-8 and
    // then #14). TOOL_NAV is ordered most-used first, so the row must be a stable
    // prefix of it: cut at the first pill that overflows and hide the rest.
    const rights = pills.map((el) => el.getBoundingClientRect().right);
    const firstOverflowing = rights.findIndex((right) => right > limit);
    if (firstOverflowing === -1) return;
    pills.slice(firstOverflowing).forEach((el) => { el.style.display = 'none'; });
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
