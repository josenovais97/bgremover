/*
 * Reusable before/after comparison slider for the tool landing demos.
 * Wires every [data-demo] block on the page: dragging the range input clips the
 * "before" layer over the "after" and moves the divider line. Pure illustration
 * (no upload). No-ops on pages without any [data-demo] markup.
 * The landing page keeps its own rotating demo (see app.js initDemoCompare).
 */
(function () {
  document.querySelectorAll('[data-demo]').forEach(function (demo) {
    var range = demo.querySelector('[data-demo-range]');
    var before = demo.querySelector('[data-demo-before]');
    var line = demo.querySelector('[data-demo-line]');
    if (!range || !before || !line) return;
    function set(v) {
      before.style.clipPath = 'inset(0 ' + (100 - v) + '% 0 0)';
      line.style.left = v + '%';
    }
    range.addEventListener('input', function () { set(+range.value); });
    set(+range.value);
  });
})();
