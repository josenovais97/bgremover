/*
 * Live value bubble for range sliders — a shared, layout-safe enhancer.
 *
 * One floating bubble (appended to <body>) follows whichever slider is being
 * dragged/focused and shows its formatted value, so no tool leaves users
 * dragging blind. It touches no slider's own layout, and uses event delegation
 * so sliders added later (the remover's per-card template clones, Instagram's
 * built controls) are covered automatically.
 *
 * Opt-out: any range with `opacity-0` in its class list is skipped — those are
 * the invisible before/after compare drag-layers, not real controls.
 *
 * Unit: the optional `data-range` attribute picks how the value reads —
 *   omitted ⇒ percent of the track (works for strength/opacity/blur/size/…)
 *   "deg"   ⇒ degrees      "x" ⇒ multiplier
 *   "px"    ⇒ pixels        "raw" ⇒ the raw value
 * The bubble paints in the page's accent (`--color-primary`), so it matches
 * each tool automatically.
 */
(function () {
  const bubble = document.createElement('div');
  bubble.className = 'range-bubble';
  bubble.setAttribute('aria-hidden', 'true');
  let active = null;
  let hideTimer = null;

  const isSlider = (el) =>
    el && el.matches && el.matches('input[type="range"]') &&
    String(el.className).indexOf('opacity-0') === -1;

  function format(el) {
    const v = parseFloat(el.value);
    switch (el.dataset.range) {
      case 'deg': return Math.round(v) + '°';
      case 'x': return (Math.round(v * 10) / 10) + '×';
      case 'px': return Math.round(v) + ' px';
      case 'raw': return String(el.value);
      default: {
        const min = parseFloat(el.min) || 0;
        const max = parseFloat(el.max);
        const range = (isNaN(max) ? 100 : max) - min;
        return Math.round(range ? ((v - min) / range) * 100 : v) + '%';
      }
    }
  }

  function place() {
    if (!active) return;
    const r = active.getBoundingClientRect();
    const min = parseFloat(active.min) || 0;
    const max = parseFloat(active.max);
    const v = parseFloat(active.value) || 0;
    const span = (isNaN(max) ? 100 : max) - min;
    const frac = span ? (v - min) / span : 0;
    const thumb = 16; // approx native thumb width; keeps the bubble near it
    bubble.style.left = (r.left + thumb / 2 + frac * (r.width - thumb)) + 'px';
    bubble.style.top = r.top + 'px';
    bubble.textContent = format(active);
  }

  function show(el) {
    clearTimeout(hideTimer);
    active = el;
    if (!bubble.isConnected) document.body.appendChild(bubble);
    place();
    bubble.classList.add('show');
  }

  function hide() {
    hideTimer = setTimeout(() => {
      bubble.classList.remove('show');
      active = null;
    }, 700);
  }

  // Delegated so dynamically-added sliders are covered too. `input` and the
  // focus*/pointer* events used here all bubble to document.
  document.addEventListener('input', (e) => {
    if (isSlider(e.target)) (active === e.target ? place() : show(e.target));
  });
  document.addEventListener('pointerdown', (e) => { if (isSlider(e.target)) show(e.target); });
  document.addEventListener('focusin', (e) => { if (isSlider(e.target)) show(e.target); });
  document.addEventListener('pointerup', (e) => { if (isSlider(e.target)) hide(); });
  document.addEventListener('focusout', (e) => { if (isSlider(e.target)) hide(); });
  window.addEventListener('scroll', place, true);
  window.addEventListener('resize', place);
})();
