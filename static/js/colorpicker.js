/**
 * Custom in-page colour picker (classic, dependency-free script).
 *
 * Replaces `<input type="color">` with a self-contained popover so we never rely
 * on the native colour dialog. Deliberately has NO eyedropper (screen-sampler):
 * the `EyeDropper` API — the native dialog's built-in one and any custom one —
 * hangs the browser on some systems, and that was the actual freeze. The SV
 * square + hue slider + hex field give full arbitrary-colour selection without it.
 *
 * Progressive enhancement: each input stays in the DOM (hidden) so all existing
 * code that reads `.value` or listens for `input`/`change` keeps working — we set
 * the value and dispatch those events. New inputs (e.g. cloned card templates)
 * are picked up via a MutationObserver.
 */
(function () {
  'use strict';

  /* ------------------------------------------------------------ colour math */
  var clamp = function (v, a, b) { return Math.min(b, Math.max(a, v)); };

  function normHex(str) {
    if (!str) return null;
    var s = String(str).trim().replace(/^#/, '');
    if (/^[0-9a-fA-F]{3}$/.test(s)) s = s.split('').map(function (c) { return c + c; }).join('');
    if (!/^[0-9a-fA-F]{6}$/.test(s)) return null;
    return '#' + s.toLowerCase();
  }
  function hexToRgb(hex) {
    var h = normHex(hex) || '#000000';
    return { r: parseInt(h.slice(1, 3), 16), g: parseInt(h.slice(3, 5), 16), b: parseInt(h.slice(5, 7), 16) };
  }
  function rgbToHex(r, g, b) {
    var to = function (n) { return clamp(Math.round(n), 0, 255).toString(16).padStart(2, '0'); };
    return '#' + to(r) + to(g) + to(b);
  }
  function rgbToHsv(r, g, b) {
    r /= 255; g /= 255; b /= 255;
    var max = Math.max(r, g, b), min = Math.min(r, g, b), d = max - min, h = 0;
    if (d) {
      if (max === r) h = ((g - b) / d) % 6;
      else if (max === g) h = (b - r) / d + 2;
      else h = (r - g) / d + 4;
      h *= 60; if (h < 0) h += 360;
    }
    return { h: h, s: max ? d / max : 0, v: max };
  }
  function hsvToRgb(h, s, v) {
    var c = v * s, x = c * (1 - Math.abs(((h / 60) % 2) - 1)), m = v - c, r = 0, g = 0, b = 0;
    if (h < 60) { r = c; g = x; } else if (h < 120) { r = x; g = c; }
    else if (h < 180) { g = c; b = x; } else if (h < 240) { g = x; b = c; }
    else if (h < 300) { r = x; b = c; } else { r = c; b = x; }
    return { r: (r + m) * 255, g: (g + m) * 255, b: (b + m) * 255 };
  }
  function rgbToHsv2(hexStr) { var c = hexToRgb(hexStr); return rgbToHsv(c.r, c.g, c.b); }

  /* --------------------------------------------------------------- styles */
  // No backdrop-filter: blurring the re-rendering preview behind the popover
  // every frame freezes real GPUs. Solid background instead.
  var css = ''
    + '.cp-pop{position:absolute;z-index:80;width:224px;padding:12px;border-radius:16px;'
    + 'background:#ffffff;border:1px solid rgba(0,0,0,0.10);box-shadow:0 12px 40px rgba(17,24,39,0.28);'
    + 'font-family:Inter,ui-sans-serif,system-ui,sans-serif;-webkit-user-select:none;user-select:none;}'
    + 'html.dark .cp-pop{background:#18181b;border-color:rgba(255,255,255,0.12);box-shadow:0 12px 40px rgba(0,0,0,0.55);}'
    + '.cp-sv{position:relative;width:200px;height:130px;border-radius:10px;cursor:crosshair;'
    + 'box-shadow:inset 0 0 0 1px rgba(0,0,0,0.12);touch-action:none;}'
    + '.cp-sv-thumb{position:absolute;width:14px;height:14px;border-radius:9999px;border:2px solid #fff;'
    + 'box-shadow:0 0 0 1px rgba(0,0,0,0.4),0 1px 3px rgba(0,0,0,0.4);transform:translate(-50%,-50%);pointer-events:none;}'
    + '.cp-hue{-webkit-appearance:none;appearance:none;width:200px;height:12px;margin:12px 0 0;border-radius:9999px;'
    + 'background:linear-gradient(to right,#f00,#ff0,#0f0,#0ff,#00f,#f0f,#f00);cursor:pointer;}'
    + '.cp-hue::-webkit-slider-thumb{-webkit-appearance:none;appearance:none;width:16px;height:16px;border-radius:9999px;'
    + 'background:#fff;border:2px solid rgba(0,0,0,0.35);box-shadow:0 1px 3px rgba(0,0,0,0.35);cursor:pointer;}'
    + '.cp-hue::-moz-range-thumb{width:16px;height:16px;border-radius:9999px;background:#fff;border:2px solid rgba(0,0,0,0.35);box-shadow:0 1px 3px rgba(0,0,0,0.35);cursor:pointer;}'
    + '.cp-row{display:flex;align-items:center;gap:8px;margin-top:10px;}'
    + '.cp-prev{width:26px;height:26px;border-radius:8px;box-shadow:inset 0 0 0 1px rgba(0,0,0,0.15);flex:none;}'
    + '.cp-hex{flex:1;min-width:0;padding:6px 8px;border-radius:8px;font-size:13px;font-family:ui-monospace,monospace;'
    + 'text-transform:uppercase;background:rgba(0,0,0,0.04);border:1px solid rgba(0,0,0,0.12);color:#111827;outline:none;}'
    + 'html.dark .cp-hex{background:rgba(255,255,255,0.06);border-color:rgba(255,255,255,0.14);color:#f4f4f5;}'
    + '.cp-hex:focus{border-color:#4f46e5;box-shadow:0 0 0 2px rgba(79,70,229,0.3);}'
    + '.cp-swatches{display:grid;grid-template-columns:repeat(8,1fr);gap:5px;margin-top:10px;}'
    + '.cp-sw{width:100%;aspect-ratio:1;border-radius:6px;cursor:pointer;box-shadow:inset 0 0 0 1px rgba(0,0,0,0.18);padding:0;border:0;transition:transform .1s ease;}'
    + '.cp-sw:hover{transform:scale(1.12);}'
    + '.cp-sw.cp-active{box-shadow:inset 0 0 0 1px rgba(0,0,0,0.18),0 0 0 2px #4f46e5;}'
    // Visible border so a white/light swatch trigger isn't invisible on a light panel.
    + '.cp-trigger{cursor:pointer;padding:0;box-sizing:border-box;box-shadow:inset 0 0 0 1px rgba(0,0,0,0.25);min-width:24px;min-height:24px;}'
    + 'html.dark .cp-trigger{box-shadow:inset 0 0 0 1px rgba(255,255,255,0.3);}'
    // "Pick from image": samples a pixel from the result image / canvas (getImageData),
    // NOT the freezing EyeDropper API.
    + '.cp-pick{margin-top:10px;width:100%;padding:7px;border-radius:8px;border:1px solid rgba(0,0,0,0.12);'
    + 'background:rgba(0,0,0,0.04);color:#374151;font-size:12px;font-weight:600;cursor:pointer;'
    + 'display:flex;align-items:center;justify-content:center;gap:6px;}'
    + 'html.dark .cp-pick{border-color:rgba(255,255,255,0.14);background:rgba(255,255,255,0.06);color:#d1d5db;}'
    + '.cp-pick:hover{background:rgba(79,70,229,0.12);color:#4f46e5;}'
    + '.cp-sampling,.cp-sampling *{cursor:crosshair !important;}'
    + '.cp-hint{position:fixed;top:14px;left:50%;transform:translateX(-50%);z-index:90;background:#111827;color:#fff;'
    + 'padding:8px 14px;border-radius:9999px;font-size:13px;font-weight:500;box-shadow:0 6px 20px rgba(0,0,0,0.3);pointer-events:none;}';

  var style = document.createElement('style');
  style.textContent = css;

  var PRESETS = ['#ffffff', '#000000', '#4f46e5', '#ec4899', '#22c55e', '#f59e0b', '#ef4444', '#0ea5e9',
    '#1f2937', '#6b7280', '#8b5cf6', '#14b8a6', '#f43f5e', '#84cc16', '#3b82f6', '#eab308'];

  /* --------------------------------------------------------------- popover */
  var pop, sv, svThumb, hue, hex, prev, swatchEls = [], active = null;
  var cur = { h: 0, s: 0, v: 0 };
  var rafScheduled = false, lastHueBg = -1;

  function buildPopover() {
    pop = document.createElement('div');
    pop.className = 'cp-pop';
    pop.setAttribute('role', 'dialog');
    pop.style.display = 'none';

    sv = document.createElement('div'); sv.className = 'cp-sv';
    svThumb = document.createElement('div'); svThumb.className = 'cp-sv-thumb';
    sv.appendChild(svThumb);

    hue = document.createElement('input');
    hue.type = 'range'; hue.min = 0; hue.max = 360; hue.step = 1; hue.className = 'cp-hue';
    hue.setAttribute('aria-label', 'Hue');

    var row = document.createElement('div'); row.className = 'cp-row';
    prev = document.createElement('div'); prev.className = 'cp-prev';
    hex = document.createElement('input');
    hex.type = 'text'; hex.className = 'cp-hex'; hex.setAttribute('aria-label', 'Hex colour'); hex.maxLength = 7;
    row.appendChild(prev); row.appendChild(hex);

    swatchEls = [];
    var sw = document.createElement('div'); sw.className = 'cp-swatches';
    PRESETS.forEach(function (c) {
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'cp-sw'; b.style.background = c; b.title = c; b.dataset.c = c;
      b.addEventListener('click', function () { setFromHex(c, true); });
      sw.appendChild(b); swatchEls.push(b);
    });

    var pick = document.createElement('button');
    pick.type = 'button'; pick.className = 'cp-pick';
    pick.innerHTML = '<i class="fa-solid fa-eye-dropper" aria-hidden="true"></i> Pick from image';
    pick.addEventListener('click', startSampling);

    pop.appendChild(sv); pop.appendChild(hue); pop.appendChild(row); pop.appendChild(sw); pop.appendChild(pick);
    document.body.appendChild(pop);

    var svDrag = false;
    var pickSV = function (e) {
      var r = sv.getBoundingClientRect();
      cur.s = clamp((e.clientX - r.left) / r.width, 0, 1);
      cur.v = 1 - clamp((e.clientY - r.top) / r.height, 0, 1);
      commit(true);
    };
    sv.addEventListener('pointerdown', function (e) { svDrag = true; sv.setPointerCapture(e.pointerId); pickSV(e); });
    sv.addEventListener('pointermove', function (e) { if (svDrag) pickSV(e); });
    sv.addEventListener('pointerup', function () { svDrag = false; });
    sv.addEventListener('pointercancel', function () { svDrag = false; });

    hue.addEventListener('input', function () { cur.h = +hue.value; commit(true); });
    hex.addEventListener('input', function () {
      var h = normHex(hex.value);
      if (h) { var hsv = rgbToHsv2(h); cur.h = hsv.h; cur.s = hsv.s; cur.v = hsv.v; commit(true, true); }
    });

    document.addEventListener('pointerdown', function (e) {
      if (!active || pop.style.display === 'none') return;
      if (pop.contains(e.target) || e.target === active.trigger) return;
      close();
    }, true);
    document.addEventListener('keydown', function (e) {
      if (active && pop.style.display !== 'none' && e.key === 'Escape') { e.stopPropagation(); close(); }
    }, true);
    window.addEventListener('resize', function () { if (active) close(); });
    window.addEventListener('scroll', function () { if (active) position(); }, true);
  }

  /* ------------------------------------------- sample colour from an image */
  // Read the pixel colour under a click on an <img> (object-contain) or <canvas>.
  // Uses getImageData on same-origin (blob:) pixels — no EyeDropper API involved.
  function sampleAt(el, clientX, clientY) {
    if (!el) return null;
    try {
      if (el.tagName === 'CANVAS') {
        var cr = el.getBoundingClientRect();
        var cx = Math.round((clientX - cr.left) * (el.width / cr.width));
        var cy = Math.round((clientY - cr.top) * (el.height / cr.height));
        var cd = el.getContext('2d').getImageData(cx, cy, 1, 1).data;
        return cd[3] === 0 ? null : rgbToHex(cd[0], cd[1], cd[2]);
      }
      if (el.tagName === 'IMG' && el.naturalWidth) {
        var r = el.getBoundingClientRect();
        var iw = el.naturalWidth, ih = el.naturalHeight;
        var scale = Math.min(r.width / iw, r.height / ih); // object-contain
        var ox = r.left + (r.width - iw * scale) / 2, oy = r.top + (r.height - ih * scale) / 2;
        var ix = Math.round((clientX - ox) / scale), iy = Math.round((clientY - oy) / scale);
        if (ix < 0 || iy < 0 || ix >= iw || iy >= ih) return null;
        var c = document.createElement('canvas'); c.width = iw; c.height = ih;
        var g = c.getContext('2d'); g.drawImage(el, 0, 0);
        var d = g.getImageData(ix, iy, 1, 1).data;
        return d[3] === 0 ? null : rgbToHex(d[0], d[1], d[2]);
      }
    } catch (err) { /* tainted canvas / cross-origin — give up quietly */ }
    return null;
  }

  function startSampling() {
    if (!active) return;
    var ctx = active; // remember which input/trigger we're editing
    pop.style.display = 'none';
    document.documentElement.classList.add('cp-sampling');
    var hint = document.createElement('div');
    hint.className = 'cp-hint';
    hint.textContent = 'Click your image to sample a colour — Esc to cancel';
    document.body.appendChild(hint);

    function done(sampledHex) {
      document.documentElement.classList.remove('cp-sampling');
      hint.remove();
      document.removeEventListener('click', onClick, true);
      document.removeEventListener('keydown', onKey, true);
      active = ctx; // restore
      if (sampledHex) setFromHex(sampledHex, true);
      pop.style.display = 'block';
      position();
    }
    function onClick(e) {
      e.preventDefault(); e.stopPropagation();
      // Find the first <img>/<canvas> under the pointer — overlays (e.g. the
      // compare-slider input) can sit on top of the result image.
      var stack = document.elementsFromPoint(e.clientX, e.clientY);
      var target = null;
      for (var i = 0; i < stack.length; i++) {
        if (stack[i].tagName === 'CANVAS' || stack[i].tagName === 'IMG') { target = stack[i]; break; }
      }
      done(sampleAt(target, e.clientX, e.clientY));
    }
    function onKey(e) { if (e.key === 'Escape') { e.stopPropagation(); done(null); } }

    // Null active while sampling so the outside-click close handler stays quiet;
    // defer binding so the click that pressed "Pick from image" isn't caught.
    active = null;
    setTimeout(function () {
      document.addEventListener('click', onClick, true);
      document.addEventListener('keydown', onKey, true);
    }, 0);
  }

  function currentHex() { var c = hsvToRgb(cur.h, cur.s, cur.v); return rgbToHex(c.r, c.g, c.b); }

  function commit(dispatch, skipHexField) {
    var hexv = currentHex();
    // The SV gradient only depends on hue — repaint it only when hue changes.
    if (cur.h !== lastHueBg) {
      var base = rgbToHex(hsvToRgb(cur.h, 1, 1).r, hsvToRgb(cur.h, 1, 1).g, hsvToRgb(cur.h, 1, 1).b);
      sv.style.background = 'linear-gradient(to top,#000,rgba(0,0,0,0)),linear-gradient(to right,#fff,' + base + ')';
      lastHueBg = cur.h;
    }
    svThumb.style.left = (cur.s * 100) + '%';
    svThumb.style.top = ((1 - cur.v) * 100) + '%';
    svThumb.style.background = hexv;
    prev.style.background = hexv;
    if (!skipHexField && document.activeElement !== hex) hex.value = hexv.toUpperCase();
    if (active && active.trigger) active.trigger.style.background = hexv;
    for (var i = 0; i < swatchEls.length; i++) swatchEls[i].classList.toggle('cp-active', swatchEls[i].dataset.c === hexv);
    if (dispatch && active) {
      active.input.value = hexv;
      if (!rafScheduled) {
        rafScheduled = true;
        requestAnimationFrame(function () {
          rafScheduled = false;
          if (active) active.input.dispatchEvent(new Event('input', { bubbles: true }));
        });
      }
    }
  }

  function setFromHex(hexStr, dispatch) {
    var hsv = rgbToHsv2(hexStr); cur.h = hsv.h; cur.s = hsv.s; cur.v = hsv.v;
    hue.value = Math.round(cur.h);
    commit(!!dispatch);
  }

  function position() {
    if (!active) return;
    var r = active.trigger.getBoundingClientRect();
    var pw = pop.offsetWidth, ph = pop.offsetHeight;
    var left = clamp(r.left, 8, window.innerWidth - pw - 8);
    var top = r.bottom + 8;
    if (top + ph > window.innerHeight - 8) top = Math.max(8, r.top - ph - 8);
    pop.style.left = (left + window.scrollX) + 'px';
    pop.style.top = (top + window.scrollY) + 'px';
  }

  function openFor(input, trigger) {
    active = { input: input, trigger: trigger };
    hue.value = Math.round((rgbToHsv2(input.value || '#000000')).h);
    setFromHex(input.value || '#000000', false);
    pop.style.display = 'block';
    position();
  }

  function close() {
    if (!active) return;
    active.input.dispatchEvent(new Event('input', { bubbles: true }));
    active.input.dispatchEvent(new Event('change', { bubbles: true }));
    pop.style.display = 'none';
    active = null;
  }

  /* --------------------------------------------------------------- enhance */
  function enhance(input) {
    if (input.dataset.cpEnhanced) return;
    input.dataset.cpEnhanced = '1';

    var trigger = document.createElement('button');
    trigger.type = 'button';
    trigger.className = (input.className ? input.className + ' ' : '') + 'cp-trigger';
    trigger.style.background = normHex(input.value) || '#000000';
    var label = input.getAttribute('aria-label');
    trigger.setAttribute('aria-label', (label || 'Colour') + ' — open colour picker');
    trigger.setAttribute('aria-haspopup', 'dialog');

    input.style.display = 'none';
    input.insertAdjacentElement('afterend', trigger);

    // Many inputs sit inside a <label>; clicking anything in a label would
    // forward-activate the native dialog (whose built-in eyedropper is the thing
    // that freezes). Swallow the native picker at the source.
    input.addEventListener('click', function (e) { e.preventDefault(); e.stopPropagation(); });
    input.addEventListener('change', function () { trigger.style.background = normHex(input.value) || trigger.style.background; });

    trigger.addEventListener('click', function (e) {
      e.preventDefault(); e.stopPropagation();
      if (active && active.input === input && pop.style.display !== 'none') { close(); return; }
      openFor(input, trigger);
    });
  }

  function scan(root) {
    if (!root || root.nodeType !== 1) return;
    if (root.matches && root.matches('input[type="color"]')) enhance(root);
    if (root.querySelectorAll) root.querySelectorAll('input[type="color"]').forEach(enhance);
  }

  function init() {
    document.head.appendChild(style);
    buildPopover();
    scan(document.body);
    new MutationObserver(function (muts) {
      muts.forEach(function (m) { m.addedNodes.forEach(scan); });
    }).observe(document.body, { childList: true, subtree: true });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
