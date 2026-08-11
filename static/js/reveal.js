/*
 * Scroll-triggered reveals — every [data-rise] element fades and rises 10px the
 * first time it enters the viewport.
 *
 * Deliberately tiny and deliberately one-shot. The initial hidden state is in
 * CSS (see [data-rise] in input.css), so there is no flash of un-transformed
 * content before this file runs; all this does is add a class and stop
 * observing. Nothing here reads layout, so it cannot cause a synchronous reflow
 * however many elements are on the page.
 *
 * The `js-rise` class on <html> is set FIRST, synchronously: the CSS hides
 * [data-rise] only when that class is present, so a visitor whose JS never
 * arrives (or errors) sees the content rather than a blank column. That is why
 * this script is not deferred behind anything that can throw.
 *
 * prefers-reduced-motion is honoured in the stylesheet rather than here — the
 * elements are simply never hidden — so this file still runs and still marks
 * things revealed, keeping the two paths from drifting.
 */
(function () {
  var root = document.documentElement;
  root.classList.add('js-rise');

  var items = document.querySelectorAll('[data-rise]');
  if (!items.length) return;

  // No IntersectionObserver (or reduced motion): show everything at once. The
  // class is still applied so any rule keyed on it behaves the same way.
  if (!('IntersectionObserver' in window)
      || window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    items.forEach(function (el) { el.classList.add('is-revealed'); });
    return;
  }

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('is-revealed');
      io.unobserve(entry.target);
    });
  }, {
    // Start the reveal slightly before the element's top edge arrives, so it is
    // already settled by the time it is properly in view rather than animating
    // under the reader's eye.
    rootMargin: '0px 0px -8% 0px',
    threshold: 0.05,
  });

  items.forEach(function (el) { io.observe(el); });
})();
