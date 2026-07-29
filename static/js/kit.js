/**
 * Shared browser kit — the helpers every tool page needs.
 *
 * Loaded as a CLASSIC script from base.html (not an ES module) on purpose:
 * Django's static storage does not rewrite ES-module import paths, so a local
 * `import` between tool modules breaks in production. A classic script that
 * publishes `window.CBG` sidesteps that entirely — it always runs before the
 * type="module" tool scripts, which are deferred by definition.
 *
 * Every tool used to carry its own private copy of $, $$, Toast, loadImage,
 * humanSize and the drag/drop/paste wiring — sixteen near-identical Toasts among
 * them, all of which built their markup with innerHTML and so interpolated the
 * user's own file name into HTML. Everything now routes through here.
 */
(function () {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];

  /* ------------------------------------------------------------------- i18n
   * Runtime strings need translating too. The template side has {% t %}, but
   * every message a tool raises while you use it ("Crop applied", "Export
   * failed") lived in JS as an English literal, so a Portuguese visitor hit
   * English at the exact moment something succeeded or failed.
   *
   * base.html emits the catalogue as JSON — and only on /pt/ pages, since on
   * English pages t() returns its key unchanged and the payload would be dead
   * weight. Keys are the English source text, matching the {% t %} convention,
   * so the English string stays readable at the call site.
   *
   *   t('Export failed')
   *   t('Could not read {name}', { name: file.name })
   */
  let CATALOGUE = {};
  try {
    const raw = document.getElementById('cbg-i18n');
    if (raw) CATALOGUE = JSON.parse(raw.textContent) || {};
  } catch { /* a broken catalogue must not take the tool down */ }

  function t(key, vars) {
    let out = CATALOGUE[key] || key;
    if (vars) {
      for (const [k, v] of Object.entries(vars)) out = out.split(`{${k}}`).join(v);
    }
    return out;
  }

  /** t() with singular/plural keys chosen by `n`, which is also passed as {n}. */
  const plural = (n, one, many, vars) => t(n === 1 ? one : many, { n, ...vars });

  const Toast = {
    show(message, type = 'success') {
      const c = $('#toast-container');
      if (!c) return;
      const map = {
        success: ['bg-green-50 dark:bg-green-900/40 text-green-800 dark:text-green-200 border-green-200 dark:border-green-800', 'fa-circle-check text-green-500'],
        error: ['bg-red-50 dark:bg-red-900/40 text-red-800 dark:text-red-200 border-red-200 dark:border-red-800', 'fa-circle-exclamation text-red-500'],
        info: ['bg-blue-50 dark:bg-blue-900/40 text-blue-800 dark:text-blue-200 border-blue-200 dark:border-blue-800', 'fa-circle-info text-blue-500'],
      };
      const [cls, icon] = map[type] || map.success;
      const el = document.createElement('div');
      el.className = `pointer-events-auto flex items-center gap-3 px-5 py-3.5 rounded-xl border shadow-lg transition-all duration-300 translate-y-4 opacity-0 ${cls}`;
      el.setAttribute('role', 'alert');
      el.innerHTML = `<i class="fa-solid ${icon} text-lg"></i><span class="font-medium text-sm"></span>`;
      // textContent, not innerHTML: messages can include a user's file name.
      el.querySelector('span').textContent = message;
      c.appendChild(el);
      requestAnimationFrame(() => el.classList.remove('translate-y-4', 'opacity-0'));
      setTimeout(() => { el.classList.add('opacity-0', 'translate-y-4'); setTimeout(() => el.remove(), 300); }, 3600);
    },
  };

  const loadImage = (src) => new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = src;
  });

  const humanSize = (b) =>
    (b < 1024 ? `${b} B` : b < 1048576 ? `${(b / 1024).toFixed(0)} KB` : `${(b / 1048576).toFixed(1)} MB`);

  const baseName = (name) => String(name || 'image').replace(/\.[^.]+$/, '');

  /**
   * Save a Blob to the user's downloads under `name`.
   *
   * Also offers the blob to Chain (below). Every tool's export funnels through
   * here, which is what makes "continue in another tool" work everywhere
   * without each tool having to know the feature exists: the thing you just
   * exported IS the thing you'd want to carry to the next tool.
   *
   * Pass `{ chain: false }` when the result must NOT be offered onwards. The
   * GIF maker does: every destination tool composites through a canvas, so a
   * chained GIF would arrive as its first frame with the animation silently
   * discarded — worse than not offering the hop at all.
   */
  function download(blob, name, { chain = true } = {}) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = name;
    document.body.appendChild(a);
    a.click();
    URL.revokeObjectURL(url);
    a.remove();
    if (chain && /^image\//.test(blob.type || '')) Chain.offer(blob, name);
  }

  /**
   * Wire a dropzone: click, keyboard, drag & drop, and clipboard paste.
   *
   * `onFiles` receives an array of image Files (already filtered). Pass
   * `multiple: false` to hand over only the first one. Pass `accept` (a
   * file => bool predicate) for tools whose input is not a plain raster image:
   * HEIC files sometimes arrive with an empty MIME type and PDFs are
   * `application/pdf`, so the default `image/*` filter would reject them.
   */
  function dropzone(el, { input, icon, browse, multiple = true, accept, onFiles }) {
    if (!el || !input) return;
    const ok = accept || ((f) => /^image\//.test(f.type));
    const deliver = (list) => {
      const files = [...(list || [])].filter((f) => f && ok(f));
      if (!files.length) { Toast.show(t('Please choose an image'), 'error'); return; }
      onFiles(multiple ? files : [files[0]]);
    };
    const open = () => input.click();

    if (browse) browse.addEventListener('click', (e) => { e.stopPropagation(); open(); });
    el.addEventListener('click', open);
    el.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); }
    });
    input.addEventListener('change', (e) => { deliver(e.target.files); input.value = ''; });

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach((evt) =>
      el.addEventListener(evt, (e) => { e.preventDefault(); e.stopPropagation(); }));
    ['dragenter', 'dragover'].forEach((evt) => el.addEventListener(evt, () => {
      el.classList.add('border-primary', 'bg-primary/5');
      if (icon) icon.classList.add('scale-110');
    }));
    ['dragleave', 'drop'].forEach((evt) => el.addEventListener(evt, () => {
      el.classList.remove('border-primary', 'bg-primary/5');
      if (icon) icon.classList.remove('scale-110');
    }));
    el.addEventListener('drop', (e) => deliver(e.dataTransfer.files));
    document.addEventListener('paste', (e) => {
      const items = [...(e.clipboardData?.items || [])].filter((i) => i.kind === 'file');
      if (items.length) deliver(items.map((i) => i.getAsFile()));
    });
  }

  /**
   * ZIP a list of {name, blob} entries and save it.
   *
   * JSZip is imported on demand (absolute CDN URL — allowed by the CSP and
   * cached by the service worker), so tools that never batch don't pay for it.
   */
  async function zipDownload(entries, zipName = 'clearbg.zip') {
    const { default: JSZip } = await import('https://cdn.jsdelivr.net/npm/jszip@3.10.1/+esm');
    const zip = new JSZip();
    const used = new Set();
    for (const { name, blob } of entries) {
      // Two source files can share a name; suffix collisions rather than
      // silently overwriting one of the user's results.
      let unique = name;
      for (let i = 2; used.has(unique); i++) unique = name.replace(/(\.[^.]+)$/, `-${i}$1`);
      used.add(unique);
      zip.file(unique, blob);
    }
    download(await zip.generateAsync({ type: 'blob' }), zipName);
  }

  /** Tiny localStorage-backed settings store, namespaced per tool. */
  function remember(ns) {
    const key = `clearbg:${ns}`;
    return {
      get() {
        try { return JSON.parse(localStorage.getItem(key)) || {}; } catch { return {}; }
      },
      set(patch) {
        try { localStorage.setItem(key, JSON.stringify({ ...this.get(), ...patch })); } catch { /* private mode */ }
      },
    };
  }

  /* ------------------------------------------------------------------ chain
   * Carrying one image from tool to tool without re-uploading it.
   *
   * This replaces the old one-shot handoff, which only ran remover → crop /
   * sticker / instagram. With nineteen tools the interesting journeys are
   * longer than one hop ("remove background → crop → watermark → compress"),
   * and re-picking the file at every step was the thing that made the toolkit
   * feel like nineteen separate pages instead of one editor.
   *
   * The blob lives in IndexedDB (too big for storage that holds strings) under
   * a single key, alongside the trail of tools it has already been through, so
   * the receiving page can say where the image came from.
   *
   * Reads are destructive and TTL-bounded. Both matter: a pending image that
   * survived would silently load itself into an unrelated visit to a tool page
   * days later, which looks like the site inventing a file you didn't choose.
   */
  const DB = 'clearbg-handoff';
  const STORE = 'img';
  const KEY = 'current';
  // Generous enough for a slow page load on a phone, short enough that the
  // image is always one you chose moments ago. The hop itself takes a second.
  const TTL_MS = 5 * 60 * 1000;

  function openDb() {
    return new Promise((resolve, reject) => {
      const req = indexedDB.open(DB, 1);
      req.onupgradeneeded = () => req.result.createObjectStore(STORE);
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
  }

  const Chain = {
    // The most recent exportable result on this page, set by download() and by
    // any tool that produces a result without an immediate download. Held in
    // memory only — nothing is written until the user picks a destination.
    _pending: null,

    /** Note `blob` as this page's current result (does not persist it). */
    offer(blob, name) {
      this._pending = { blob, name: name || 'image.png' };
      renderBar();
    },

    /** True if this page has a result worth carrying onwards. */
    has() {
      return !!this._pending;
    },

    /**
     * Persist a result and navigate to `url`.
     *
     * `payload` ({blob, name}) overrides the page's pending result, for tools
     * that hold several at once — the remover's batch has one cut-out per card,
     * so the card passes its own rather than whichever was offered last.
     */
    async sendTo(url, payload) {
      const current = payload || this._pending;
      if (!current) { location.href = url; return; }
      const { blob, name } = current;
      const here = document.body.dataset.toolLabel || '';
      try {
        const db = await openDb();
        await new Promise((resolve, reject) => {
          const tx = db.transaction(STORE, 'readwrite');
          tx.objectStore(STORE).put({
            blob,
            name,
            type: blob.type || 'image/png',
            ts: Date.now(),
            from: here,
            // The journey records where the image HAS BEEN, so it appends this
            // tool — not the destination, which hasn't touched the image yet
            // and will add itself when it renders its own bar.
            steps: [...currentSteps(), here].filter(Boolean),
          }, KEY);
          tx.oncomplete = resolve;
          tx.onerror = () => reject(tx.error);
        });
        db.close();
      } catch { /* fall through — the destination just starts empty */ }
      location.href = url;
    },

    /** Read-and-clear the pending image. Returns {file, from, steps} or null. */
    async take() {
      try {
        const db = await openDb();
        const rec = await new Promise((resolve, reject) => {
          const tx = db.transaction(STORE, 'readwrite');
          const store = tx.objectStore(STORE);
          const get = store.get(KEY);
          get.onsuccess = () => { store.delete(KEY); resolve(get.result); };
          get.onerror = () => reject(get.error);
        });
        db.close();
        if (!rec || !rec.blob || Date.now() - rec.ts > TTL_MS) return null;
        return {
          file: new File([rec.blob], rec.name, { type: rec.type }),
          from: rec.from || '',
          steps: rec.steps || [],
        };
      } catch {
        return null;
      }
    },
  };

  /** Tools this image has already been through, this session. */
  function currentSteps() {
    try { return JSON.parse(sessionStorage.getItem('clearbg:steps') || '[]'); } catch { return []; }
  }

  function setSteps(steps) {
    try { sessionStorage.setItem('clearbg:steps', JSON.stringify(steps)); } catch { /* private mode */ }
  }

  /**
   * Hand an incoming image to this page's primary file input.
   *
   * Marked up as `data-chain-input`, which is deliberately explicit: several
   * pages have more than one file input (a logo picker, a background image),
   * and guessing wrong would load the user's photo into the wrong slot. Tools
   * that can't accept an arbitrary image (the QR generator) simply omit it.
   *
   * Delivering through the input rather than a per-tool callback means the
   * tool's existing change handler does all the work — no tool needs to know
   * about chaining to be a valid destination.
   */
  async function receiveChained() {
    const input = $('[data-chain-input]');
    if (!input) return;
    const handoff = await Chain.take();
    if (!handoff) {
      // Arriving at a tool with nothing in flight starts a new journey. Without
      // this the trail from an earlier chain would persist for the whole session
      // and be shown over an unrelated image the user has just picked.
      setSteps([]);
      return;
    }
    try {
      const dt = new DataTransfer();
      dt.items.add(handoff.file);
      input.files = dt.files;
      input.dispatchEvent(new Event('change', { bubbles: true }));
    } catch {
      return; // no DataTransfer (old Safari) — the user picks the file as usual
    }
    setSteps(handoff.steps);
    if (handoff.from) Toast.show(t('Carried over from {tool}', { tool: handoff.from }), 'info');
  }

  /**
   * The "continue in" bar: appears once the page has a result to pass on.
   *
   * Rendered from `#chain-targets`, a JSON list base.html builds from TOOL_NAV
   * minus the current tool, so a new tool joins the chain by existing rather
   * than by being added to a second list here.
   */
  let barEl = null;

  /** Toasts and the bar both live at the bottom, so move the stack clear. */
  function liftToasts(up) {
    const c = $('#toast-container');
    if (!c) return;
    c.classList.toggle('bottom-5', !up);
    c.classList.toggle('bottom-28', up);
  }

  /**
   * Write the journey so far into `el`: "Remove BG → Crop → Watermark".
   *
   * The trail is what makes the toolkit read as one editor rather than a set of
   * pages that happen to hand files to each other — without it the bar can only
   * say "here are some other tools", which is the thing a user already knows.
   * On the first hop there is no journey yet, so it just states the offer.
   */
  function renderTrail(el) {
    const steps = [...currentSteps(), document.body.dataset.toolLabel]
      .filter(Boolean)
      // Re-entering the same tool twice in a row (export, tweak, export again)
      // is one step, not two.
      .filter((s, i, all) => s !== all[i - 1]);
    el.textContent = steps.length > 1
      ? `${steps.join(' → ')} ${t('— keep going:')}`
      : t('Keep editing this image:');
  }

  function renderBar() {
    if (barEl || !Chain.has()) return;
    let targets = [];
    try { targets = JSON.parse($('#chain-targets')?.textContent || '[]'); } catch { return; }
    if (!targets.length) return;

    barEl = document.createElement('div');
    barEl.className =
      'fixed inset-x-0 bottom-0 z-40 px-4 pb-4 pointer-events-none print:hidden';
    barEl.innerHTML = `
      <div class="pointer-events-auto mx-auto max-w-3xl glass border border-gray-200/70 dark:border-gray-800/70 rounded-2xl shadow-xl p-3 sm:p-4 flex flex-wrap items-center gap-x-3 gap-y-2 translate-y-3 opacity-0 transition-all duration-300">
        <span class="flex items-center gap-2 text-sm font-medium min-w-0">
          <i class="fa-solid fa-circle-check text-green-500 shrink-0" aria-hidden="true"></i>
          <span data-label class="truncate"></span>
        </span>
        <div class="flex flex-wrap items-center gap-1.5 ml-auto" data-targets></div>
        <button type="button" data-dismiss class="p-2 -m-1 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary">
          <i class="fa-solid fa-xmark" aria-hidden="true"></i>
        </button>
      </div>`;
    renderTrail(barEl.querySelector('[data-label]'));

    const holder = barEl.querySelector('[data-targets]');
    for (const tool of targets.slice(0, 5)) {
      const b = document.createElement('button');
      b.type = 'button';
      b.className =
        'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold border border-primary/40 bg-primary/5 text-primaryText hover:bg-primary/10 transition focus:outline-none focus-visible:ring-2 focus-visible:ring-primary';
      b.innerHTML = `<i class="${tool.icon}" aria-hidden="true"></i>`;
      b.appendChild(document.createTextNode(tool.label));
      b.addEventListener('click', () => Chain.sendTo(tool.url));
      holder.appendChild(b);
    }
    barEl.querySelector('[data-dismiss]').addEventListener('click', () => {
      barEl.remove();
      barEl = null;
      Chain._pending = null;
      liftToasts(false);
    });

    document.body.appendChild(barEl);
    liftToasts(true);
    requestAnimationFrame(() =>
      barEl.firstElementChild.classList.remove('translate-y-3', 'opacity-0'));
  }

  /* ---------------------------------------------------------------- sparkle
   * The reward moment for a finished cut-out.
   *
   * The sparkles trace the SILHOUETTE rather than scattering over the card:
   * every tool here spends its effort finding one edge, so the celebration is
   * that edge, drawn back to you. A random confetti burst would cost the same
   * and say nothing about the result.
   *
   * The edge comes from the result's own alpha channel — opaque pixels that
   * touch a transparent neighbour — sampled at 96px, which is coarse enough to
   * be free and detailed enough to read as the subject's outline.
   *
   * Two layers, because sparkles alone were too easy to miss after a 30-second
   * wait: a halo pulse that traces the whole silhouette at once (the
   * announcement) and the sparkles on top of it (the detail).
   */

  /** Normalised (0..1) points along the alpha edge of `src`. Empty if unreadable. */
  function silhouette(src) {
    const nw = src.naturalWidth || src.width;
    const nh = src.naturalHeight || src.height;
    if (!nw || !nh) return [];
    const scale = Math.min(1, 96 / Math.max(nw, nh));
    const w = Math.max(1, Math.round(nw * scale));
    const h = Math.max(1, Math.round(nh * scale));
    const c = document.createElement('canvas');
    c.width = w;
    c.height = h;
    const cx = c.getContext('2d', { willReadFrequently: true });
    let data;
    try {
      cx.drawImage(src, 0, 0, w, h);
      data = cx.getImageData(0, 0, w, h).data;
    } catch {
      return []; // cross-origin source tainted the canvas; caller scatters instead
    }
    const opaque = (x, y) => data[(y * w + x) * 4 + 3] >= 128;
    const pts = [];
    for (let y = 0; y < h; y++) {
      for (let x = 0; x < w; x++) {
        if (!opaque(x, y)) continue;
        // A pixel on the frame edge counts: a full-bleed result has no interior
        // boundary, and tracing its rectangle still beats tracing nothing.
        if (
          x === 0 || y === 0 || x === w - 1 || y === h - 1 ||
          !opaque(x - 1, y) || !opaque(x + 1, y) ||
          !opaque(x, y - 1) || !opaque(x, y + 1)
        ) pts.push([x / w, y / h]);
      }
    }
    return pts;
  }

  /** The page's current tool accent, as a canvas-usable colour. */
  function accentColour() {
    const accent = getComputedStyle(document.body).getPropertyValue('--color-primary').trim();
    return accent ? `rgb(${accent})` : '#6366f1';
  }

  /** Paint one spark at `p` (0 = born, 1 = gone). Shared by both modes. */
  function drawSpark(cx, s, p, color) {
    // Pop to full size quickly, then ease back slightly; fade in, fade out.
    const scale = p < 0.35 ? p / 0.35 : 1 - ((p - 0.35) / 0.65) * 0.35;
    const alpha = p < 0.25 ? p / 0.25 : 1 - (p - 0.25) / 0.75;
    cx.save();
    cx.globalAlpha = Math.max(0, alpha) * (s.dim || 1);
    cx.translate(s.x, s.y + s.rise * p);
    cx.rotate(s.spin + p * 0.9);
    cx.scale(scale, scale);
    cx.fillStyle = s.white ? '#ffffff' : color;
    // The halo is always the accent, including under a white sparkle: the
    // result sits on a light checkerboard as often as on a dark photo, and
    // a white glow on white leaves nothing to see.
    cx.shadowColor = color;
    cx.shadowBlur = s.white ? 10 : 8;
    starPath(cx, s.r);
    cx.fill();
    cx.restore();
  }

  /** Size a canvas to its own CSS box at capped DPR. Returns the box, or null. */
  function fitCanvas(canvas) {
    const box = canvas.getBoundingClientRect();
    if (!box.width || !box.height) return null;
    const dpr = Math.min(2, window.devicePixelRatio || 1);
    canvas.width = Math.round(box.width * dpr);
    canvas.height = Math.round(box.height * dpr);
    const cx = canvas.getContext('2d');
    if (!cx) return null;
    cx.scale(dpr, dpr);
    return { box, cx, dpr };
  }

  /** Trace a four-point star of radius `r`, centred on the current origin. */
  function starPath(cx, r) {
    const waist = r * 0.26;
    cx.beginPath();
    cx.moveTo(0, -r);
    cx.quadraticCurveTo(waist, -waist, r, 0);
    cx.quadraticCurveTo(waist, waist, 0, r);
    cx.quadraticCurveTo(-waist, waist, -r, 0);
    cx.quadraticCurveTo(-waist, -waist, 0, -r);
    cx.closePath();
  }

  /**
   * Twinkle a burst of sparkles over `canvas`, along the silhouette of `src`.
   *
   * `canvas` must overlay the same box `src` is painted into. By default `src`
   * is assumed to be `object-contain` within that box; a tool that places its
   * cut-out itself (a zoom/pan view, a fitted product frame) passes the actual
   * destination as `opts.rect` — {x, y, w, h} in CSS pixels of the overlay —
   * so the sparkles land on the edge the user is actually looking at.
   *
   * Returns a cancel function.
   */
  function sparkle(canvas, src, opts = {}) {
    const stop = () => {};
    if (!canvas || !src) return stop;
    // The effect is pure decoration, so reduced-motion drops it entirely rather
    // than substituting a static version.
    if (window.matchMedia?.('(prefers-reduced-motion: reduce)').matches) return stop;

    const nw = src.naturalWidth || src.width;
    const nh = src.naturalHeight || src.height;
    if (!nw || !nh) return stop;
    const fitted = fitCanvas(canvas);
    if (!fitted) return stop;
    const { box, cx, dpr } = fitted;

    // Where the cut-out actually sits inside the box: the caller's rect if it
    // placed the image itself, otherwise object-contain.
    const fit = Math.min(box.width / nw, box.height / nh);
    const r = opts.rect;
    const dw = r ? r.w : nw * fit;
    const dh = r ? r.h : nh * fit;
    const dx = r ? r.x : (box.width - dw) / 2;
    const dy = r ? r.y : (box.height - dh) / 2;

    let pts = silhouette(src);
    if (!pts.length) pts = Array.from({ length: 48 }, () => [Math.random(), Math.random()]);

    const color = opts.color || accentColour();
    const count = opts.count || 52;
    const life = 820;   // one sparkle, birth to gone
    const spread = 760; // stagger across the burst, so they twinkle on in waves
    const glowLife = 950;

    // A halo hugging the silhouette: draw the cut-out with a coloured shadow a
    // few times to build up intensity, then punch the subject itself back out,
    // which leaves only the glow that was spilling past its edge.
    const halo = document.createElement('canvas');
    halo.width = canvas.width;
    halo.height = canvas.height;
    const hx = halo.getContext('2d');
    if (hx) {
      hx.scale(dpr, dpr);
      hx.shadowColor = color;
      hx.shadowBlur = 16;
      for (let i = 0; i < 3; i++) hx.drawImage(src, dx, dy, dw, dh);
      hx.globalCompositeOperation = 'destination-out';
      hx.drawImage(src, dx, dy, dw, dh);
    }

    const sparks = Array.from({ length: count }, () => {
      const [px, py] = pts[(Math.random() * pts.length) | 0];
      // Mostly small with a few hero sparkles: a uniform size reads mechanical,
      // an uneven one reads like light catching an edge.
      const hero = Math.random() < 0.18;
      return {
        x: dx + px * dw + (Math.random() - 0.5) * 10,
        y: dy + py * dh + (Math.random() - 0.5) * 10,
        r: hero ? 8 + Math.random() * 5 : 3 + Math.random() * 3.5,
        spin: Math.random() * Math.PI,
        rise: -6 - Math.random() * 14,
        delay: Math.random() * spread,
        white: Math.random() < 0.5, // mixing in white keeps it from reading as one flat colour
      };
    });

    let raf = 0;
    const t0 = performance.now();
    const clear = () => cx.clearRect(0, 0, box.width, box.height);
    const frame = (now) => {
      const t = now - t0;
      clear();
      let alive = false;

      // Halo first, so the sparkles read as sitting on top of the glow.
      const gp = t / glowLife;
      if (hx && gp < 1) {
        alive = true;
        const ga = gp < 0.28 ? gp / 0.28 : 1 - (gp - 0.28) / 0.72;
        cx.save();
        cx.globalAlpha = Math.max(0, ga) * 0.9;
        cx.drawImage(halo, 0, 0, box.width, box.height);
        cx.restore();
      }

      for (const s of sparks) {
        const age = t - s.delay;
        if (age < 0) { alive = true; continue; }
        const p = age / life;
        if (p >= 1) continue;
        alive = true;
        drawSpark(cx, s, p, color);
      }
      if (alive) raf = requestAnimationFrame(frame);
      else clear();
    };
    raf = requestAnimationFrame(frame);
    return () => { cancelAnimationFrame(raf); clear(); };
  }

  /**
   * Ambient twinkle inside `host` (which must be a positioned element),
   * running until the returned function is called. This is the WAIT, not the
   * payoff: removal takes ~30 seconds against a spinner, and a celebration with
   * nothing leading up to it is a long blank pause followed by a flash.
   *
   * Deliberately quieter than the finish — fewer, dimmer, no halo, scattered
   * rather than tracing anything (there is no cut-out yet to trace). The burst
   * has to stay the moment that reads as "done".
   *
   * DOM + CSS rather than canvas, unlike the burst. WASM inference blocks the
   * main thread for several seconds, which starves requestAnimationFrame — a
   * canvas loop simply freezes for the entire removal, which is exactly the
   * phase the animation exists to cover. CSS animations of transform/opacity
   * run on the compositor and keep going regardless.
   */
  function sparkleLoop(host, opts = {}) {
    const stop = () => {};
    if (!host) return stop;
    if (window.matchMedia?.('(prefers-reduced-motion: reduce)').matches) return stop;

    const color = opts.color || accentColour();
    const count = opts.count || 16;

    // The star is a background image rather than a clip-path: clip-path can
    // disqualify an element from compositor-driven animation, which would put
    // the twinkle back on the blocked main thread and defeat the whole point.
    // A background paints once and leaves transform/opacity free to composite.
    const star = (fill) =>
      `url("data:image/svg+xml,${encodeURIComponent(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">' +
        `<path fill="${fill}" d="M50 0Q57 43 100 50Q57 57 50 100Q43 57 0 50Q43 43 50 0Z"/></svg>`,
      )}")`;

    const layer = document.createElement('div');
    layer.className = 'sparkle-idle';
    layer.setAttribute('aria-hidden', 'true');
    for (let i = 0; i < count; i++) {
      const s = document.createElement('span');
      const hero = Math.random() < 0.18;
      const size = hero ? 16 + Math.random() * 10 : 7 + Math.random() * 7;
      s.style.cssText =
        `left:${(Math.random() * 100).toFixed(2)}%;top:${(Math.random() * 100).toFixed(2)}%;` +
        `width:${size.toFixed(1)}px;height:${size.toFixed(1)}px;` +
        `background-image:${star(Math.random() < 0.5 ? '#ffffff' : color)};` +
        `--sparkle-dur:${(950 + Math.random() * 850).toFixed(0)}ms;` +
        `--sparkle-delay:${(Math.random() * 1500).toFixed(0)}ms;` +
        `--sparkle-peak:${(0.65 + Math.random() * 0.35).toFixed(2)};`;
      layer.appendChild(s);
    }
    host.appendChild(layer);
    return () => layer.remove();
  }

  /**
   * Position a throwaway canvas over `target`'s page box. Absolute at page
   * coordinates (not fixed) so it tracks the content if the page scrolls.
   */
  function overlayFor(target, tag = 'canvas') {
    const box = target.getBoundingClientRect();
    if (!box.width || !box.height) return null;
    const layer = document.createElement(tag);
    layer.setAttribute('aria-hidden', 'true');
    const place = () => {
      const b = target.getBoundingClientRect();
      layer.style.cssText =
        `position:absolute;left:${b.left + window.scrollX}px;top:${b.top + window.scrollY}px;` +
        `width:${b.width}px;height:${b.height}px;pointer-events:none;z-index:40;`;
    };
    place();
    document.body.appendChild(layer);
    return { layer, box, place, remove: () => layer.remove() };
  }

  /**
   * Ambient twinkle over any element, for tools that preview into their own
   * canvas. Re-anchors periodically because this runs for the length of the
   * wait, during which the page can scroll or reflow under it.
   */
  function sparkleLoopOver(target, opts = {}) {
    const stop = () => {};
    if (!target) return stop;
    // A div, not a canvas: the loop builds CSS-animated children inside it.
    const o = overlayFor(target, 'div');
    if (!o) return stop;
    o.layer.style.overflow = 'hidden';
    const cancel = sparkleLoop(o.layer, opts);
    // Callers do setBusy(true) then render() in one synchronous run, so the box
    // measured above is the pre-render one. Re-place after that run completes,
    // before the first paint, or the opening frame lands at the canvas default.
    requestAnimationFrame(o.place);
    // The target is typically sized by the render that follows setBusy(), so
    // track it directly; the interval only covers reflow the observer misses.
    const ro = window.ResizeObserver ? new window.ResizeObserver(o.place) : null;
    ro?.observe(target);
    const anchor = window.setInterval(o.place, 500);
    return () => {
      ro?.disconnect();
      window.clearInterval(anchor);
      cancel();
      o.remove();
    };
  }

  /**
   * Run the burst over an existing canvas without needing an overlay in the
   * markup: position a throwaway canvas at the target's page box, sparkle, then
   * remove it. Every tool here previews into a canvas that is intrinsically
   * sized (`max-w-full max-h-[60vh]`), so an `inset-0` overlay in the template
   * would cover the wrapper rather than the image.
   *
   * `opts.rect` is in the target's own drawing-buffer pixels — the coordinates a
   * tool already has from its render pass — and is scaled to the displayed box
   * here, so callers never deal with devicePixelRatio or CSS sizing.
   */
  function sparkleOver(target, src, opts = {}) {
    const stop = () => {};
    if (!target || !src) return stop;
    const o = overlayFor(target);
    if (!o) return stop;

    let rect = opts.rect;
    if (rect && target.width && target.height) {
      const sx = o.box.width / target.width;
      const sy = o.box.height / target.height;
      rect = { x: rect.x * sx, y: rect.y * sy, w: rect.w * sx, h: rect.h * sy };
    }

    const cancel = sparkle(o.layer, src, { ...opts, rect });
    const timer = window.setTimeout(o.remove, 2200); // outlives the longest burst
    return () => { cancel(); window.clearTimeout(timer); o.remove(); };
  }

  window.CBG = {
    $, $$, t, plural, Toast, loadImage, humanSize, baseName,
    download, dropzone, zipDownload, remember, Chain,
    sparkle, sparkleOver, sparkleLoop, sparkleLoopOver,
  };

  // Deliver any chained image once the tool's own module has wired its input.
  // Tool scripts are type="module" (deferred), so they finish before load.
  window.addEventListener('load', receiveChained);
})();
