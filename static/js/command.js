/**
 * Ctrl+K command palette — jump to any tool from anywhere.
 *
 * The list itself is server-rendered in base.html from TOOL_NAV (same source as
 * the pill row and the mega-menu), so a new tool shows up here by existing and
 * every label arrives already translated. This file only does behaviour:
 * open/close, filtering, keyboard navigation, and a "recent tools" ranking kept
 * in localStorage. All strings live in the template — none are raised here.
 */
(function () {
  const palette = document.getElementById('cmd-palette');
  const input = document.getElementById('cmd-input');
  const list = document.getElementById('cmd-list');
  const btn = document.getElementById('cmd-btn');
  if (!palette || !input || !list) return;

  const empty = document.getElementById('cmd-empty');
  const items = [...list.querySelectorAll('[data-cmd-item]')];
  const prefs = CBG.remember('cmdpalette');

  // Remember where the visitor actually goes, palette or not — the ranking is
  // about their habits, not about which affordance they used to travel.
  const here = items.find((el) => el.dataset.url === location.pathname);
  let recent = (prefs.get().recent || []).filter((n) => items.some((el) => el.dataset.name === n));
  if (here) {
    recent = [here.dataset.name, ...recent.filter((n) => n !== here.dataset.name)].slice(0, 6);
    prefs.set({ recent });
  }

  let isOpen = false;
  let visible = [];
  let active = -1;
  let restoreFocus = null;

  function render() {
    const q = input.value.trim().toLowerCase();
    const tokens = q.split(/\s+/).filter(Boolean);

    let ordered;
    if (tokens.length) {
      ordered = items
        .map((el) => {
          const text = el.dataset.text;
          let score = 0;
          for (const tk of tokens) {
            const at = text.indexOf(tk);
            if (at === -1) return null;
            score += at;
          }
          return { el, score };
        })
        .filter(Boolean)
        .sort((a, b) => a.score - b.score)
        .map((x) => x.el);
    } else {
      // No query: the visitor's recent tools first, then the natural nav order.
      const byName = new Map(items.map((el) => [el.dataset.name, el]));
      const top = recent.map((n) => byName.get(n)).filter(Boolean);
      ordered = [...top, ...items.filter((el) => !top.includes(el))];
    }

    for (const el of items) {
      const show = ordered.includes(el);
      el.classList.toggle('hidden', !show);
      const flag = el.querySelector('[data-cmd-flag]');
      if (flag) flag.classList.toggle('hidden', !!tokens.length || !recent.includes(el.dataset.name));
    }
    // Physically reorder so keyboard order matches what the eye sees.
    for (const el of ordered) list.insertBefore(el, empty);
    empty.classList.toggle('hidden', ordered.length > 0);

    visible = ordered;
    setActive(visible.length ? 0 : -1);
  }

  function setActive(i) {
    active = i;
    visible.forEach((el, idx) => {
      const a = idx === i;
      el.classList.toggle('bg-primary/10', a);
      el.setAttribute('aria-selected', a);
    });
    const el = visible[i];
    input.setAttribute('aria-activedescendant', el ? el.id : '');
    if (el) el.scrollIntoView({ block: 'nearest' });
  }

  function open() {
    if (isOpen) return;
    isOpen = true;
    restoreFocus = document.activeElement;
    palette.classList.remove('hidden');
    input.value = '';
    render();
    input.focus();
  }

  function close() {
    if (!isOpen) return;
    isOpen = false;
    palette.classList.add('hidden');
    if (restoreFocus && document.contains(restoreFocus)) restoreFocus.focus();
    restoreFocus = null;
  }

  function go(el) {
    if (el) location.href = el.dataset.url;
  }

  if (btn) btn.addEventListener('click', open);
  palette.querySelector('[data-cmd-close]').addEventListener('click', close);
  input.addEventListener('input', render);

  items.forEach((el) => {
    el.addEventListener('click', () => go(el));
    el.addEventListener('mousemove', () => {
      const idx = visible.indexOf(el);
      if (idx !== -1 && idx !== active) setActive(idx);
    });
  });

  document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && !e.shiftKey && !e.altKey && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      isOpen ? close() : open();
      return;
    }
    if (!isOpen) {
      // "/" also opens it (a la GitHub) — but never while the visitor is typing.
      const tag = e.target.tagName;
      if (e.key === '/' && !e.ctrlKey && !e.metaKey && !e.altKey
          && !['INPUT', 'TEXTAREA', 'SELECT'].includes(tag) && !e.target.isContentEditable) {
        e.preventDefault();
        open();
      }
      return;
    }
    if (e.key === 'Escape') { close(); return; }
    if (e.key === 'ArrowDown') { e.preventDefault(); if (visible.length) setActive((active + 1) % visible.length); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); if (visible.length) setActive((active - 1 + visible.length) % visible.length); }
    else if (e.key === 'Enter') { e.preventDefault(); go(visible[active]); }
  });
})();
