/**
 * Header menus: the desktop "Tools" / "Use cases" dropdowns and the mobile sheet.
 *
 * This replaces the old width-measuring pill row, which showed as many tools as
 * happened to fit and hid the rest — a nav whose contents changed with the window
 * and which, on a phone, collapsed to one or two arbitrary tools. The header now
 * renders the same four entries at every width and this file only opens and
 * closes panels.
 *
 * Progressive enhancement: every panel is a plain server-rendered list of links.
 * With JS off they stay hidden, and every tool is still reachable from the footer
 * (which lists all of them) and from the homepage tool grid.
 *
 * A button opts in with `data-menu-btn` + `aria-controls="<panel id>"`; the panel
 * carries `data-menu-panel`. Only one is open at a time.
 */
(function () {
  const buttons = [...document.querySelectorAll('[data-menu-btn]')];
  if (!buttons.length) return;

  const pairs = buttons
    .map((btn) => ({ btn, panel: document.getElementById(btn.getAttribute('aria-controls')) }))
    .filter((p) => p.panel);

  function setOpen(pair, open) {
    pair.panel.classList.toggle('hidden', !open);
    pair.btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    const chevron = pair.btn.querySelector('[data-chevron]');
    if (chevron) chevron.style.transform = open ? 'rotate(180deg)' : '';
    // The mobile button swaps a hamburger for a close cross, so the same control
    // visibly undoes itself rather than looking inert while the sheet is open.
    const closed = pair.btn.querySelector('[data-menu-icon="closed"]');
    const opened = pair.btn.querySelector('[data-menu-icon="open"]');
    if (closed && opened) {
      closed.classList.toggle('hidden', open);
      opened.classList.toggle('hidden', !open);
    }
  }

  function closeAll(except) {
    pairs.forEach((p) => { if (p !== except) setOpen(p, false); });
    syncSticky();
  }

  // The landing page's sticky CTA is fixed to the bottom of the viewport, where
  // it lands on top of the mobile sheet's own tool list. A class on <html> lets
  // CSS stand it down (see .nav-open in input.css) without this file having to
  // know anything about landing.js's own show/hide logic.
  function syncSticky() {
    const anyOpen = pairs.some((p) => !p.panel.classList.contains('hidden'));
    document.documentElement.classList.toggle('nav-open', anyOpen);
  }

  pairs.forEach((pair) => {
    pair.btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const willOpen = pair.panel.classList.contains('hidden');
      closeAll(pair);
      setOpen(pair, willOpen);
      syncSticky();
    });
    // A click inside a panel that isn't on a link (a group heading, the padding)
    // shouldn't dismiss the menu the visitor is still reading.
    pair.panel.addEventListener('click', (e) => {
      if (!e.target.closest('a')) e.stopPropagation();
    });
  });

  document.addEventListener('click', () => closeAll());
  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape') return;
    const open = pairs.find((p) => !p.panel.classList.contains('hidden'));
    if (!open) return;
    setOpen(open, false);
    syncSticky();
    open.btn.focus();
  });

  // Crossing the lg breakpoint swaps which panels exist visually; leaving one
  // open through the change strands it (the mobile sheet is `lg:hidden`, so it
  // would simply vanish with its button still reading "expanded").
  const wide = window.matchMedia('(min-width: 1024px)');
  const onChange = () => closeAll();
  if (wide.addEventListener) wide.addEventListener('change', onChange);
  else if (wide.addListener) wide.addListener(onChange);

  // The mobile sheet's Search row hands off to the Ctrl+K palette rather than
  // duplicating it.
  const mobileSearch = document.getElementById('mobile-search');
  const cmdBtn = document.getElementById('cmd-btn');
  if (mobileSearch && cmdBtn) {
    mobileSearch.addEventListener('click', (e) => {
      e.stopPropagation();
      closeAll();
      cmdBtn.click();
    });
  }
})();
