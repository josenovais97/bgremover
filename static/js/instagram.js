import { takeHandoff } from './handoff.js';

/**
 * Instagram photo editor — 100% client-side.
 *
 * Upload a photo and edit it right away (no background removal required):
 *  - pick an Instagram format (crops to the right aspect and exports at the
 *    exact recommended pixels),
 *  - Fill (cover-crop) or Fit (whole photo, filling the gaps with a blurred
 *    copy or a solid colour so nothing is cropped),
 *  - add a coloured border,
 *  - apply on-trend one-tap looks and dial their strength up or down,
 *  - fine-tune brightness / contrast / saturation / warmth / sharpen / grain /
 *    vignette,
 *  - press-and-hold to compare against the original,
 *  - toggle Story/Reel safe-zone guides so captions and UI don't cover faces,
 *  - split a wide photo into a seamless swipeable carousel (ZIP export),
 *  - reposition with drag + zoom.
 * Background removal is an optional extra, lazy-loaded only if used.
 *
 * Self-contained (own helpers/toast) because Django's hashed-manifest static
 * storage doesn't rewrite ES-module import paths — cross-file local imports
 * would break in production, but CDN (absolute-URL) imports are fine.
 *
 * Note: sharpen is a manual convolution pass, NOT a canvas `url(#…)` filter.
 * Combining an SVG `url()` reference with filter functions in `ctx.filter`
 * silently voids the whole filter in Chromium and Safari, which would drop the
 * colour grading — so the two are kept strictly separate.
 */

/* --------------------------------------------------------------- helpers */
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));

// Coalesce a burst of calls (e.g. the `input` events a native colour picker
// streams while open) into one run per animation frame, so a rapid stream of
// re-renders can't lock up the main thread and leave the picker un-dismissable.
function rafThrottle(fn) {
  let scheduled = false;
  return (...args) => {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(() => { scheduled = false; fn(...args); });
  };
}

const loadImage = (src) =>
  new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = src;
  });

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
    el.innerHTML = `<i class="fa-solid ${icon} text-lg"></i><span class="font-medium text-sm">${message}</span>`;
    c.appendChild(el);
    requestAnimationFrame(() => el.classList.remove('translate-y-4', 'opacity-0'));
    setTimeout(() => { el.classList.add('opacity-0', 'translate-y-4'); setTimeout(() => el.remove(), 300); }, 3600);
  },
};

// The adjustment keys that make up a "look". Everything blends linearly on these.
const ADJ_KEYS = ['brightness', 'contrast', 'saturate', 'warmth', 'sharpen', 'grain', 'vignette'];

// On-trend one-tap looks influencers reach for. Each is a full set of values.
const FILTERS = {
  original: { brightness: 100, contrast: 100, saturate: 100, warmth: 0, sharpen: 0, grain: 0, vignette: 0 },
  vivid: { brightness: 103, contrast: 116, saturate: 142, warmth: 6, sharpen: 22, grain: 0, vignette: 8 },
  punch: { brightness: 101, contrast: 132, saturate: 152, warmth: 0, sharpen: 34, grain: 0, vignette: 10 },
  clean: { brightness: 108, contrast: 96, saturate: 96, warmth: -6, sharpen: 12, grain: 0, vignette: 0 },
  golden: { brightness: 106, contrast: 106, saturate: 118, warmth: 42, sharpen: 14, grain: 6, vignette: 8 },
  moody: { brightness: 92, contrast: 124, saturate: 88, warmth: -14, sharpen: 18, grain: 10, vignette: 26 },
  film: { brightness: 104, contrast: 92, saturate: 86, warmth: 18, sharpen: 6, grain: 26, vignette: 8 },
  noir: { brightness: 106, contrast: 120, saturate: 0, warmth: 0, sharpen: 20, grain: 22, vignette: 24 },
  warm: { brightness: 103, contrast: 106, saturate: 116, warmth: 44, sharpen: 12, grain: 0, vignette: 8 },
  cool: { brightness: 102, contrast: 106, saturate: 110, warmth: -40, sharpen: 12, grain: 0, vignette: 6 },
  fade: { brightness: 111, contrast: 86, saturate: 80, warmth: 12, sharpen: 0, grain: 8, vignette: 0 },
  vintage: { brightness: 105, contrast: 110, saturate: 74, warmth: 34, sharpen: 6, grain: 16, vignette: 38 },
  crisp: { brightness: 102, contrast: 114, saturate: 108, warmth: 0, sharpen: 44, grain: 0, vignette: 0 },
  sunset: { brightness: 104, contrast: 108, saturate: 128, warmth: 60, sharpen: 12, grain: 4, vignette: 14 },
  mint: { brightness: 105, contrast: 100, saturate: 106, warmth: -28, sharpen: 10, grain: 0, vignette: 0 },
};

// Display order + labels for the filter thumbnails (built in buildFilterButtons).
const FILTER_ORDER = ['original', 'vivid', 'punch', 'crisp', 'clean', 'golden', 'sunset', 'warm', 'cool', 'mint', 'film', 'fade', 'vintage', 'moody', 'noir'];
const FILTER_LABELS = { original: 'Original', vivid: 'Vivid', punch: 'Punch', crisp: 'Crisp', clean: 'Clean', golden: 'Golden', sunset: 'Sunset', warm: 'Warm', cool: 'Cool', mint: 'Mint', film: 'Film', fade: 'Fade', vintage: 'Vintage', moody: 'Moody', noir: 'Noir' };

/* ------------------------------------------------------------ geometry */
// Cover-crop: sample a rect of the source at the target aspect, positioned by
// the normalised centre (u,v) and zoom, clamped to stay inside the image.
function frameGeometry(iw, ih, aspect, zoom, u, v) {
  const baseW = Math.min(iw, ih * aspect);
  const baseH = baseW / aspect;
  const z = Math.max(1, zoom);
  const sw = baseW / z;
  const sh = baseH / z;
  const halfU = sw / 2 / iw;
  const halfV = sh / 2 / ih;
  const cu = clamp(u, halfU, 1 - halfU);
  const cv = clamp(v, halfV, 1 - halfV);
  const sx = clamp(cu * iw - sw / 2, 0, iw - sw);
  const sy = clamp(cv * ih - sh / 2, 0, ih - sh);
  return { sx, sy, sw, sh };
}

/* --------------------------------------------------------------------- app */
const App = {
  format: { key: 'post', aspect: 1, w: 1080, h: 1080 },
  adj: { ...FILTERS.original }, // effective values used to render
  baseFilter: { ...FILTERS.original }, // the picked look at full strength
  strength: 100, // how far the look is applied (blend toward Original)
  zoom: 1,
  u: 0.5,
  v: 0.5,
  fitMode: 'fill', // 'fill' (cover-crop) | 'fit' (whole photo)
  fitBg: 'blur', // 'blur' or a colour hex, used to fill the gaps in Fit mode
  border: 0, // percent of the short side
  borderColor: '#ffffff',
  carousel: 1, // 1 = single post, 2/3 = split into tiles
  safeZones: false, // Story/Reel UI-coverage guides (preview only)
  grid: false, // rule-of-thirds composition guide (preview only)
  showOriginal: false, // press-and-hold compare
  orient: { rot: 0, flipH: false, flipV: false }, // 90° rotation steps + mirroring
  exportFmt: 'image/jpeg', // download encoding
  quality: 0.92, // JPEG/WEBP quality
  // Draggable text overlays (each rendered onto the canvas, so they export too).
  textEnabled: false,
  texts: [], // array of layers; each { content, font, size, color, align, bold, shadow, highlight, x, y, _box }
  activeText: -1, // index of the layer the controls edit / that's being dragged
  // Logo / @handle watermark, drawn into a chosen corner and exported.
  watermark: { on: false, handle: '', pos: 'br', size: 6, opacity: 90, logoUrl: null, logoImg: null },
  raw: null, // original uploaded image
  rawOriented: null, // `raw` with the current rotate/flip baked in (for compare)
  cutout: null, // background-removed image, if produced
  bgRemoved: false,
  bgColor: '#ffffff',
  origUrl: null,
  cutoutUrl: null,
  noise: null, // cached grain tile

  init() {
    this.dropzone = $('#ig-dropzone');
    this.input = $('#ig-input');
    this.editor = $('#ig-editor');
    this.canvas = $('#ig-canvas');
    this.ctx = this.canvas.getContext('2d');

    const open = () => this.input.click();
    $('#ig-browse').addEventListener('click', (e) => { e.stopPropagation(); open(); });
    this.dropzone.addEventListener('click', open);
    this.dropzone.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); } });
    this.input.addEventListener('change', (e) => this.load(e.target.files[0]));

    const icon = $('#ig-icon');
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach((evt) =>
      this.dropzone.addEventListener(evt, (e) => { e.preventDefault(); e.stopPropagation(); }));
    ['dragenter', 'dragover'].forEach((evt) =>
      this.dropzone.addEventListener(evt, () => icon.classList.add('scale-110')));
    ['dragleave', 'drop'].forEach((evt) =>
      this.dropzone.addEventListener(evt, () => icon.classList.remove('scale-110')));
    this.dropzone.addEventListener('drop', (e) => this.load(e.dataTransfer.files[0]));
    document.addEventListener('paste', (e) => {
      const f = [...(e.clipboardData?.items || [])].find((i) => i.kind === 'file');
      if (f) this.load(f.getAsFile());
    });

    // Format
    $$('.ig-format').forEach((b) => b.addEventListener('click', () => this.setFormat(b)));
    // Frame: fit/fill, fit background, border
    $$('.ig-fit').forEach((b) => b.addEventListener('click', () => this.setFitMode(b.dataset.fit, b)));
    $$('.ig-fitbg').forEach((b) => b.addEventListener('click', () => this.setFitBg(b.dataset.bg, b)));
    // Colour pickers stream `input` events while open; coalesce the re-renders
    // to one per frame so the picker stays dismissable on large photos.
    const throttledRender = rafThrottle(() => this.render());
    $('#ig-border').addEventListener('input', (e) => { this.border = +e.target.value; throttledRender(); });
    $('#ig-border-color').addEventListener('input', (e) => { this.borderColor = e.target.value; if (this.border > 0) throttledRender(); });
    // Looks + strength
    this.buildFilterButtons();
    $$('.ig-filter').forEach((b) => b.addEventListener('click', () => this.applyFilter(b)));
    $('#ig-strength').addEventListener('input', (e) => this.setStrength(+e.target.value));
    // Adjustment sliders (manual tweaks become the new base at full strength)
    $$('.ig-adj').forEach((s) => s.addEventListener('input', () => {
      this.adj[s.dataset.adj] = +s.value;
      this.baseFilter = { ...this.adj };
      this.strength = 100;
      $('#ig-strength').value = 100;
      $$('.ig-filter').forEach((b) => b.classList.remove('ring-2', 'ring-[#d62976]'));
      this.render();
    }));
    // Double-click a slider to reset just that adjustment to its neutral default.
    $$('.ig-adj').forEach((s) => {
      s.title = 'Double-click to reset';
      s.addEventListener('dblclick', () => {
        s.value = FILTERS.original[s.dataset.adj];
        s.dispatchEvent(new Event('input', { bubbles: true }));
      });
    });
    $('#ig-reset').addEventListener('click', () => this.resetAdjustments());
    // Carousel splitter
    $$('.ig-carousel').forEach((b) => b.addEventListener('click', () => this.setCarousel(+b.dataset.n, b)));
    // Compare (press and hold) + safe zones
    const cmp = $('#ig-compare');
    const showOrig = (on) => { this.showOriginal = on; this.render(); };
    cmp.addEventListener('pointerdown', (e) => { e.preventDefault(); showOrig(true); });
    ['pointerup', 'pointerleave', 'pointercancel'].forEach((ev) => cmp.addEventListener(ev, () => showOrig(false)));
    $('#ig-safezones').addEventListener('click', (e) => {
      this.safeZones = !this.safeZones;
      e.currentTarget.setAttribute('aria-pressed', String(this.safeZones));
      e.currentTarget.classList.toggle('ring-2', this.safeZones);
      e.currentTarget.classList.toggle('ring-[#d62976]', this.safeZones);
      this.render();
    });
    $('#ig-grid').addEventListener('click', (e) => {
      this.grid = !this.grid;
      e.currentTarget.setAttribute('aria-pressed', String(this.grid));
      e.currentTarget.classList.toggle('ring-2', this.grid);
      e.currentTarget.classList.toggle('ring-[#d62976]', this.grid);
      this.render();
    });

    // Transform: rotate 90° steps + flips (baked into the working image).
    $('#ig-rot-l').addEventListener('click', () => this.rotate(-90));
    $('#ig-rot-r').addEventListener('click', () => this.rotate(90));
    $('#ig-flip-h').addEventListener('click', () => this.flip('flipH'));
    $('#ig-flip-v').addEventListener('click', () => this.flip('flipV'));

    // Export format + quality.
    $$('.ig-expfmt').forEach((b) => b.addEventListener('click', () => this.setExportFmt(b.dataset.fmt, b)));
    $('#ig-quality').addEventListener('input', (e) => {
      this.quality = +e.target.value / 100;
      $('#ig-quality-val').textContent = e.target.value;
    });

    // Text overlays (multiple layers). The controls always edit the active layer.
    $('#ig-text-on').addEventListener('change', (e) => {
      this.textEnabled = e.target.checked;
      $('#ig-text-panel').classList.toggle('hidden', !this.textEnabled);
      if (this.textEnabled) {
        if (!this.texts.length) this.addTextLayer(false);
        else this.syncTextControls();
        this.ensureFont();
        if (this.activeLayer() && !this.activeLayer().content) $('#ig-text').focus();
      }
      this.render();
    });
    $('#ig-text-add').addEventListener('click', () => this.addTextLayer(true));
    $('#ig-text-delete').addEventListener('click', () => this.deleteTextLayer());
    const edit = (fn) => { const l = this.activeLayer(); if (l) { fn(l); this.render(); } };
    $('#ig-text').addEventListener('input', (e) => edit((l) => { l.content = e.target.value; this.renderTextChips(); }));
    $$('.ig-font').forEach((b) => b.addEventListener('click', () => edit((l) => {
      l.font = b.dataset.font;
      this.highlight('.ig-font', b);
      this.ensureFont();
    })));
    $('#ig-text-size').addEventListener('input', (e) => edit((l) => { l.size = +e.target.value; }));
    $('#ig-text-color').addEventListener('input', (e) => { const l = this.activeLayer(); if (l) { l.color = e.target.value; throttledRender(); } });
    $$('.ig-text-align').forEach((b) => b.addEventListener('click', () => edit((l) => {
      l.align = b.dataset.align;
      $$('.ig-text-align').forEach((x) => { const a = x === b; x.classList.toggle('bg-[#d62976]', a); x.classList.toggle('text-white', a); });
    })));
    [['#ig-text-bold', 'bold'], ['#ig-text-shadow', 'shadow'], ['#ig-text-hl', 'highlight']].forEach(([sel, key]) => {
      $(sel).addEventListener('click', (e) => edit((l) => {
        l[key] = !l[key];
        this.reflectTextToggle(e.currentTarget, l[key]);
      }));
    });

    // Watermark (logo + @handle).
    $('#ig-wm-on').addEventListener('change', (e) => {
      this.watermark.on = e.target.checked;
      $('#ig-wm-panel').classList.toggle('hidden', !this.watermark.on);
      this.render();
    });
    $('#ig-wm-handle').addEventListener('input', (e) => { this.watermark.handle = e.target.value; if (this.watermark.on) this.render(); });
    $('#ig-wm-logo').addEventListener('change', (e) => this.setLogo(e.target.files[0]));
    $('#ig-wm-logo-clear').addEventListener('click', () => this.setLogo(null));
    $$('.ig-wm-pos').forEach((b) => b.addEventListener('click', () => {
      this.watermark.pos = b.dataset.pos;
      this.highlight('.ig-wm-pos', b);
      this.render();
    }));
    $('#ig-wm-size').addEventListener('input', (e) => { this.watermark.size = +e.target.value; if (this.watermark.on) throttledRender(); });
    $('#ig-wm-opacity').addEventListener('input', (e) => { this.watermark.opacity = +e.target.value; if (this.watermark.on) throttledRender(); });

    // Saveable look presets.
    $('#ig-preset-save').addEventListener('click', () => this.savePreset());
    this.renderPresets();

    // Background removal (optional, lazy)
    $('#ig-remove-bg').addEventListener('click', () => this.removeBackground());
    $('#ig-restore-bg').addEventListener('click', () => { this.bgRemoved = false; this.rebuildSource(); $('#ig-restore-bg').classList.add('hidden'); this.render(); });
    $('#ig-bg-color').addEventListener('input', (e) => { this.bgColor = e.target.value; if (this.bgRemoved) throttledRender(); });

    // Framing
    const zoom = $('#ig-zoom');
    zoom.addEventListener('input', () => { this.zoom = +zoom.value; this.render(); });
    this.canvas.addEventListener('wheel', (e) => {
      e.preventDefault();
      this.zoom = clamp(this.zoom * (e.deltaY < 0 ? 1.1 : 1 / 1.1), 1, 4);
      zoom.value = this.zoom;
      this.render();
    }, { passive: false });
    this.canvas.addEventListener('pointerdown', (e) => {
      this.canvas.setPointerCapture?.(e.pointerId);
      const hit = this.hitTextLayer(e);
      if (hit >= 0) { // grab (and select) that text layer
        if (hit !== this.activeText) this.selectTextLayer(hit);
        this.textDrag = { x: e.clientX, y: e.clientY };
      } else { this.drag = { x: e.clientX, y: e.clientY }; } // otherwise reposition the photo
    });
    this.canvas.addEventListener('pointermove', (e) => { if (this.textDrag) this.onTextDrag(e); else this.onDrag(e); });
    ['pointerup', 'pointercancel', 'pointerleave'].forEach((ev) => this.canvas.addEventListener(ev, () => { this.drag = null; this.textDrag = null; }));

    $('#ig-download').addEventListener('click', () => (this.carousel > 1 ? this.downloadCarousel() : this.download()));
    $('#ig-new').addEventListener('click', () => this.reset());

    // Tool tabs — show one control group at a time (compact on laptop/phone).
    $$('.ig-tab').forEach((t) => t.addEventListener('click', () => this.setTab(t.dataset.tab)));
  },

  setTab(name) {
    $$('.ig-tab').forEach((t) => {
      const active = t.dataset.tab === name;
      t.setAttribute('aria-selected', String(active));
      t.classList.toggle('bg-[#d62976]', active);
      t.classList.toggle('text-white', active);
      t.classList.toggle('text-gray-600', !active);
      t.classList.toggle('dark:text-gray-300', !active);
    });
    $$('.ig-panel').forEach((p) => p.classList.toggle('hidden', p.dataset.panel !== name));
    const body = document.querySelector('.ig-panel:not(.hidden)')?.parentElement;
    if (body) body.scrollTop = 0;
  },

  async load(file) {
    this.input.value = '';
    if (!file || !file.type.startsWith('image/')) { Toast.show('Please choose an image', 'error'); return; }
    this.file = file;
    if (this.origUrl) URL.revokeObjectURL(this.origUrl);
    this.origUrl = URL.createObjectURL(file);
    try {
      this.raw = await loadImage(this.origUrl);
    } catch {
      Toast.show("Couldn't open that image", 'error');
      return;
    }
    // Reset state for the new photo.
    this.cutout = null;
    this.bgRemoved = false;
    this.zoom = 1;
    this.u = 0.5;
    this.v = 0.5;
    this.orient = { rot: 0, flipH: false, flipV: false };
    this.reflectFlips();
    // Clear text layers for the fresh photo.
    this.texts = [];
    this.activeText = -1;
    this.textEnabled = false;
    $('#ig-text-on').checked = false;
    $('#ig-text-panel').classList.add('hidden');
    this.syncTextControls();
    this.rebuildSource();
    this.resetAdjustments(false);
    $('#ig-zoom').value = 1;
    $('#ig-restore-bg').classList.add('hidden');
    this.dropzone.parentElement.classList.add('hidden');
    this.editor.classList.remove('hidden');
    this.render();
  },

  setFormat(btn) {
    this.format = { key: btn.dataset.key, aspect: +btn.dataset.aspect, w: +btn.dataset.w, h: +btn.dataset.h };
    this.highlight('.ig-format', btn);
    this.render();
  },

  setFitMode(mode, btn) {
    this.fitMode = mode;
    this.highlight('.ig-fit', btn);
    $('#ig-fitbg-row').classList.toggle('hidden', mode !== 'fit');
    this.updateFramingUI();
    this.render();
  },

  setFitBg(bg, btn) {
    this.fitBg = bg;
    this.highlight('.ig-fitbg', btn);
    this.render();
  },

  setCarousel(n, btn) {
    this.carousel = n;
    this.highlight('.ig-carousel', btn);
    $('#ig-download-label').textContent = n > 1 ? `Download ${n}-tile carousel (ZIP)` : 'Download for Instagram';
    this.updateFramingUI();
    this.render();
  },

  // Fit-single hides reposition (whole photo is shown); Fill and carousel keep it.
  updateFramingUI() {
    const canReposition = !(this.fitMode === 'fit' && this.carousel <= 1);
    $('#ig-zoom-row').classList.toggle('hidden', !canReposition);
    $('#ig-hint').classList.toggle('hidden', !canReposition);
  },

  /* ------------------------------------------------------ transform */
  // Return `base` with the current rotation/flip baked into a canvas (or the
  // untouched image when the transform is the identity, to avoid a needless copy).
  orientedOf(base) {
    if (!base) return null;
    const { rot, flipH, flipV } = this.orient;
    if (!rot && !flipH && !flipV) return base;
    const bw = base.naturalWidth || base.width;
    const bh = base.naturalHeight || base.height;
    const swap = rot === 90 || rot === 270;
    const c = document.createElement('canvas');
    c.width = swap ? bh : bw;
    c.height = swap ? bw : bh;
    const x = c.getContext('2d');
    x.translate(c.width / 2, c.height / 2);
    x.rotate((rot * Math.PI) / 180);
    x.scale(flipH ? -1 : 1, flipV ? -1 : 1);
    x.drawImage(base, -bw / 2, -bh / 2);
    return c;
  },

  // Rebuild the working image (and an oriented copy of the original for compare)
  // from whichever base is active. Called whenever orientation or bg state changes.
  rebuildSource() {
    const base = this.bgRemoved ? this.cutout : this.raw;
    this.img = this.orientedOf(base);
    this.rawOriented = this.orientedOf(this.raw);
    this.refreshFilterThumbs(); // keep the look previews matching the current photo
  },

  rotate(deg) {
    if (!this.raw) return;
    this.orient.rot = (((this.orient.rot + deg) % 360) + 360) % 360;
    this.u = this.v = 0.5; // axes changed — recentre the crop
    this.rebuildSource();
    this.render();
  },

  flip(axis) {
    if (!this.raw) return;
    this.orient[axis] = !this.orient[axis];
    this.u = this.v = 0.5;
    this.reflectFlips();
    this.rebuildSource();
    this.render();
  },

  // Reflect flip toggles in the button styling.
  reflectFlips() {
    [['#ig-flip-h', 'flipH'], ['#ig-flip-v', 'flipV']].forEach(([sel, key]) => {
      const b = $(sel);
      if (!b) return;
      b.setAttribute('aria-pressed', String(this.orient[key]));
      b.classList.toggle('ring-2', this.orient[key]);
      b.classList.toggle('ring-[#d62976]', this.orient[key]);
    });
  },

  setExportFmt(fmt, btn) {
    this.exportFmt = fmt;
    this.highlight('.ig-expfmt', btn);
    // Quality only applies to lossy encodings.
    $('#ig-quality-row').classList.toggle('hidden', fmt === 'image/png');
  },

  /* ------------------------------------------------------------- text */
  activeLayer() { return this.texts[this.activeText] || null; },

  newTextLayer() {
    return { content: '', font: 'Inter', size: 7, color: '#ffffff', align: 'center',
      bold: false, shadow: false, highlight: true, x: 0.5, y: 0.5, _box: null };
  },

  addTextLayer(focus) {
    // Stagger new layers slightly so they don't stack exactly on top of each other.
    const layer = this.newTextLayer();
    layer.y = clamp(0.5 + this.texts.length * 0.08, 0.2, 0.85);
    this.texts.push(layer);
    this.activeText = this.texts.length - 1;
    this.syncTextControls();
    this.ensureFont();
    this.render();
    if (focus) $('#ig-text').focus();
  },

  deleteTextLayer() {
    if (this.activeText < 0) return;
    this.texts.splice(this.activeText, 1);
    this.activeText = Math.min(this.activeText, this.texts.length - 1);
    this.syncTextControls();
    this.render();
  },

  selectTextLayer(i) {
    this.activeText = i;
    this.syncTextControls();
    this.render();
  },

  // Populate the text controls from the active layer and refresh the layer chips.
  syncTextControls() {
    const l = this.activeLayer();
    $('#ig-text-delete').disabled = !l;
    if (l) {
      $('#ig-text').value = l.content;
      $('#ig-text-size').value = l.size;
      $('#ig-text-color').value = l.color;
      $$('.ig-font').forEach((b) => { const a = b.dataset.font === l.font; b.classList.toggle('ring-2', a); b.classList.toggle('ring-[#d62976]', a); });
      $$('.ig-text-align').forEach((b) => { const a = b.dataset.align === l.align; b.classList.toggle('bg-[#d62976]', a); b.classList.toggle('text-white', a); });
      this.reflectTextToggle($('#ig-text-bold'), l.bold);
      this.reflectTextToggle($('#ig-text-shadow'), l.shadow);
      this.reflectTextToggle($('#ig-text-hl'), l.highlight);
    }
    this.renderTextChips();
  },

  reflectTextToggle(btn, on) {
    if (!btn) return;
    btn.setAttribute('aria-pressed', String(on));
    btn.classList.toggle('bg-[#d62976]', on);
    btn.classList.toggle('text-white', on);
    btn.classList.toggle('border-[#d62976]', on);
  },

  renderTextChips() {
    const wrap = $('#ig-text-layers');
    if (!wrap) return;
    wrap.innerHTML = '';
    this.texts.forEach((l, i) => {
      const chip = document.createElement('button');
      chip.type = 'button';
      const active = i === this.activeText;
      chip.className = 'px-2 py-1 rounded-lg border text-[11px] max-w-[8rem] truncate '
        + (active ? 'bg-[#d62976] text-white border-[#d62976]' : 'border-gray-300 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800');
      chip.textContent = (l.content.split('\n')[0] || `Text ${i + 1}`).slice(0, 18);
      chip.addEventListener('click', () => this.selectTextLayer(i));
      wrap.appendChild(chip);
    });
  },

  // Ask the browser to load the active layer's web font, then re-render so the
  // canvas (which can't wait on font loading itself) paints with the real face.
  ensureFont() {
    const l = this.activeLayer();
    if (!l || !document.fonts || !document.fonts.load) return;
    document.fonts.load(`700 40px ${l.font}`).then(() => this.render()).catch(() => {});
  },

  // Convert a pointer event to canvas-pixel coordinates.
  pointerPixel(e) {
    const rect = this.canvas.getBoundingClientRect();
    return {
      px: (e.clientX - rect.left) * (this.canvas.width / rect.width),
      py: (e.clientY - rect.top) * (this.canvas.height / rect.height),
    };
  },

  // Return the topmost text layer index under a pointer press, or -1. Selecting
  // it (and starting a drag) is done by the caller.
  hitTextLayer(e) {
    if (!this.textEnabled) return -1;
    const { px, py } = this.pointerPixel(e);
    for (let i = this.texts.length - 1; i >= 0; i--) {
      const box = this.texts[i]._box;
      if (box && px >= box.x && px <= box.x + box.w && py >= box.y && py <= box.y + box.h) return i;
    }
    return -1;
  },

  onTextDrag(e) {
    const l = this.activeLayer();
    if (!l) return;
    const rect = this.canvas.getBoundingClientRect();
    const dx = (e.clientX - this.textDrag.x) * (this.canvas.width / rect.width);
    const dy = (e.clientY - this.textDrag.y) * (this.canvas.height / rect.height);
    l.x = clamp(l.x + dx / this.canvas.width, 0, 1);
    l.y = clamp(l.y + dy / this.canvas.height, 0, 1);
    this.textDrag = { x: e.clientX, y: e.clientY };
    this.render();
  },

  // Paint every text layer over the frame, recording each layer's bounds.
  drawTexts(ctx, W, H) {
    if (!this.textEnabled) { this.texts.forEach((l) => { l._box = null; }); return; }
    this.texts.forEach((t) => this.drawTextLayer(ctx, W, H, t));
  },

  // Paint a single text layer and record its bounds on the layer object.
  drawTextLayer(ctx, W, H, t) {
    if (!t.content.trim()) { t._box = null; return; }
    const lines = t.content.replace(/\r/g, '').split('\n');
    const size = (t.size / 100) * W;
    const weight = t.bold ? 900 : 700;
    const lh = size * 1.2;
    const pad = size * 0.32;
    const cx = t.x * W;

    ctx.save();
    ctx.font = `${weight} ${size}px ${t.font}, sans-serif`;
    ctx.textBaseline = 'top';
    ctx.textAlign = t.align;

    // Measure to build the highlight boxes and the draggable hit region.
    let maxW = 0;
    const widths = lines.map((l) => { const w = ctx.measureText(l || ' ').width; maxW = Math.max(maxW, w); return w; });
    const blockH = lh * lines.length;
    const topY = t.y * H - blockH / 2;
    const anchorX = (w) => (t.align === 'left' ? cx : t.align === 'right' ? cx - w : cx - w / 2);
    t._box = { x: anchorX(maxW) - pad, y: topY - pad, w: maxW + 2 * pad, h: blockH + 2 * pad };

    const round = (x, y, w, h, r) => {
      if (ctx.roundRect) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
      else { ctx.beginPath(); ctx.rect(x, y, w, h); }
    };

    if (t.highlight) {
      ctx.fillStyle = 'rgba(0,0,0,0.42)';
      lines.forEach((l, i) => {
        if (!l.trim()) return;
        const w = widths[i];
        round(anchorX(w) - pad, topY + i * lh - pad * 0.35, w + 2 * pad, lh + pad * 0.5, size * 0.16);
        ctx.fill();
      });
    } else if (t.shadow) {
      ctx.shadowColor = 'rgba(0,0,0,0.55)';
      ctx.shadowBlur = size * 0.16;
      ctx.shadowOffsetY = size * 0.06;
    }

    ctx.fillStyle = t.color;
    lines.forEach((l, i) => ctx.fillText(l, cx, topY + i * lh));
    ctx.restore();
  },

  /* ------------------------------------------------------- watermark */
  async setLogo(file) {
    if (this.watermark.logoUrl) { URL.revokeObjectURL(this.watermark.logoUrl); this.watermark.logoUrl = null; }
    this.watermark.logoImg = null;
    if (file) {
      try {
        this.watermark.logoUrl = URL.createObjectURL(file);
        this.watermark.logoImg = await loadImage(this.watermark.logoUrl);
      } catch { Toast.show("Couldn't load that logo", 'error'); }
    }
    $('#ig-wm-logo-clear').classList.toggle('hidden', !this.watermark.logoImg);
    if (this.watermark.on) this.render();
  },

  // Draw the logo/@handle watermark into the chosen corner, scaled to the frame.
  drawWatermark(ctx, W, H) {
    const wm = this.watermark;
    const handle = (wm.handle || '').trim();
    if (!wm.on || (!handle && !wm.logoImg)) return;

    const unit = Math.min(W, H);
    const pad = unit * 0.035;
    const logoH = wm.logoImg ? (wm.size / 100) * unit * 1.4 : 0;
    const fontSize = (wm.size / 100) * unit;
    const gap = wm.logoImg && handle ? unit * 0.02 : 0;

    ctx.save();
    ctx.globalAlpha = clamp(wm.opacity / 100, 0, 1);
    ctx.font = `700 ${fontSize}px Inter, system-ui, sans-serif`;
    ctx.textBaseline = 'top';

    const logoW = wm.logoImg ? logoH * (wm.logoImg.width / wm.logoImg.height) : 0;
    const textW = handle ? ctx.measureText(handle).width : 0;
    const blockW = Math.max(logoW, textW);
    const blockH = logoH + gap + (handle ? fontSize : 0);

    const right = wm.pos === 'tr' || wm.pos === 'br';
    const bottom = wm.pos === 'bl' || wm.pos === 'br';
    const x0 = right ? W - pad - blockW : pad;
    const y0 = bottom ? H - pad - blockH : pad;

    if (wm.logoImg) {
      ctx.drawImage(wm.logoImg, x0 + (blockW - logoW) / 2, y0, logoW, logoH);
    }
    if (handle) {
      ctx.textAlign = right ? 'right' : 'left';
      const tx = right ? x0 + blockW : x0;
      // Legibility shadow so it reads over any background.
      ctx.shadowColor = 'rgba(0,0,0,0.5)';
      ctx.shadowBlur = fontSize * 0.12;
      ctx.shadowOffsetY = fontSize * 0.04;
      ctx.fillStyle = '#ffffff';
      ctx.fillText(handle, tx, y0 + logoH + gap);
    }
    ctx.restore();
  },

  /* ---------------------------------------------------- look presets */
  PRESET_KEY: 'ig-look-presets',

  loadPresets() {
    try { return JSON.parse(localStorage.getItem(this.PRESET_KEY)) || {}; }
    catch { return {}; }
  },

  storePresets(presets) {
    try { localStorage.setItem(this.PRESET_KEY, JSON.stringify(presets)); } catch { /* private mode */ }
  },

  savePreset() {
    const name = (prompt('Name this look:') || '').trim();
    if (!name) return;
    const presets = this.loadPresets();
    // Save the effective adjustment values (look + any manual tweaks) at full strength.
    presets[name] = {};
    for (const k of ADJ_KEYS) presets[name][k] = this.adj[k];
    this.storePresets(presets);
    this.renderPresets();
    Toast.show(`Saved look "${name}"`, 'success');
  },

  applyPreset(name) {
    const preset = this.loadPresets()[name];
    if (!preset) return;
    this.baseFilter = { ...FILTERS.original, ...preset };
    this.adj = { ...this.baseFilter };
    this.strength = 100;
    $('#ig-strength').value = 100;
    $$('.ig-filter').forEach((b) => b.classList.remove('ring-2', 'ring-[#d62976]'));
    this.syncSliders();
    this.render();
  },

  deletePreset(name) {
    const presets = this.loadPresets();
    delete presets[name];
    this.storePresets(presets);
    this.renderPresets();
  },

  renderPresets() {
    const wrap = $('#ig-presets');
    if (!wrap) return;
    const presets = this.loadPresets();
    const names = Object.keys(presets);
    $('#ig-presets-empty').classList.toggle('hidden', names.length > 0);
    wrap.innerHTML = '';
    names.forEach((name) => {
      const chip = document.createElement('span');
      chip.className = 'inline-flex items-center gap-1 pl-2.5 pr-1 py-1 rounded-lg border border-gray-300 dark:border-gray-700 text-xs';
      const apply = document.createElement('button');
      apply.type = 'button';
      apply.className = 'font-medium hover:text-[#d62976] max-w-[7rem] truncate';
      apply.textContent = name;
      apply.addEventListener('click', () => this.applyPreset(name));
      const del = document.createElement('button');
      del.type = 'button';
      del.className = 'w-4 h-4 grid place-items-center rounded text-gray-400 hover:text-red-500';
      del.setAttribute('aria-label', `Delete look ${name}`);
      del.innerHTML = '<i class="fa-solid fa-xmark text-[10px]" aria-hidden="true"></i>';
      del.addEventListener('click', () => this.deletePreset(name));
      chip.appendChild(apply); chip.appendChild(del);
      wrap.appendChild(chip);
    });
  },

  /* ---------------------------------------------------------- looks */
  blend(a, b, t) {
    const o = {};
    for (const k of ADJ_KEYS) o[k] = a[k] + (b[k] - a[k]) * t;
    return o;
  },

  // Build the filter thumbnail grid once (buttons are tinted per-look; the
  // photo itself is filled in by refreshFilterThumbs() when one loads).
  buildFilterButtons() {
    const wrap = $('#ig-filters');
    if (!wrap) return;
    wrap.innerHTML = FILTER_ORDER.map((key) => `
      <button type="button" data-filter="${key}" title="${FILTER_LABELS[key]}"
              class="ig-filter group relative rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#d62976] transition">
        <span class="ig-filter-thumb block aspect-square bg-gray-100 dark:bg-gray-800 relative">
          <img alt="" class="w-full h-full object-cover" draggable="false">
          <span class="ig-filter-tint absolute inset-0 pointer-events-none"></span>
        </span>
        <span class="block px-0.5 py-1 text-[10px] font-medium text-center truncate text-gray-600 dark:text-gray-300">${FILTER_LABELS[key]}</span>
      </button>`).join('');
  },

  // A small centre-cropped JPEG of the current photo, reused as the src of
  // every thumbnail (the browser decodes it once; CSS does the per-look grade).
  filterThumbURL() {
    const img = this.rawOriented || this.raw;
    if (!img) return '';
    const S = 128;
    const c = document.createElement('canvas');
    c.width = c.height = S;
    const x = c.getContext('2d');
    const iw = img.naturalWidth || img.width;
    const ih = img.naturalHeight || img.height;
    const s = Math.min(iw, ih);
    x.drawImage(img, (iw - s) / 2, (ih - s) / 2, s, s, 0, 0, S, S);
    return c.toDataURL('image/jpeg', 0.8);
  },

  // Approximate each look on the thumbnails with CSS: brightness/contrast/
  // saturate as a filter, warmth as a soft-light tint, vignette as an inset
  // shadow. (Grain/sharpen are omitted — invisible at thumbnail size.)
  refreshFilterThumbs() {
    const url = this.filterThumbURL();
    if (!url) return;
    $$('#ig-filters .ig-filter').forEach((btn) => {
      const f = FILTERS[btn.dataset.filter];
      const img = btn.querySelector('img');
      img.src = url;
      img.style.filter = `brightness(${f.brightness}%) contrast(${f.contrast}%) saturate(${f.saturate}%)`;
      const tint = btn.querySelector('.ig-filter-tint');
      const w = f.warmth / 100;
      if (Math.abs(w) < 0.02) {
        tint.style.background = 'transparent';
      } else {
        tint.style.mixBlendMode = 'soft-light';
        tint.style.background = w > 0
          ? `rgba(255,150,50,${Math.min(0.9, w * 0.9).toFixed(3)})`
          : `rgba(40,140,255,${Math.min(0.9, -w * 0.85).toFixed(3)})`;
      }
      tint.style.boxShadow = f.vignette
        ? `inset 0 0 ${Math.round(6 + f.vignette * 0.32)}px rgba(0,0,0,${(f.vignette / 100 * 0.75).toFixed(2)})`
        : 'none';
    });
  },

  applyFilter(btn) {
    this.baseFilter = { ...FILTERS[btn.dataset.filter] };
    this.strength = 100;
    $('#ig-strength').value = 100;
    this.adj = { ...this.baseFilter };
    this.highlight('.ig-filter', btn);
    this.syncSliders();
    this.render();
  },

  setStrength(v) {
    this.strength = v;
    this.adj = this.blend(FILTERS.original, this.baseFilter, v / 100);
    this.syncSliders();
    this.render();
  },

  resetAdjustments(rerender = true) {
    this.baseFilter = { ...FILTERS.original };
    this.adj = { ...FILTERS.original };
    this.strength = 100;
    $('#ig-strength').value = 100;
    $$('.ig-filter').forEach((b) => { const a = b.dataset.filter === 'original'; b.classList.toggle('ring-2', a); b.classList.toggle('ring-[#d62976]', a); });
    this.syncSliders();
    if (rerender) this.render();
  },

  syncSliders() {
    $$('.ig-adj').forEach((s) => { s.value = this.adj[s.dataset.adj]; });
  },

  // Toggle the active-ring styling across a group of buttons.
  highlight(selector, btn) {
    $$(selector).forEach((b) => { const a = b === btn; b.classList.toggle('ring-2', a); b.classList.toggle('ring-[#d62976]', a); });
  },

  onDrag(e) {
    if (!this.drag || !this.img) return;
    if (this.fitMode === 'fit' && this.carousel <= 1) return; // whole photo shown — nothing to reposition
    const iw = this.img.naturalWidth || this.img.width;
    const ih = this.img.naturalHeight || this.img.height;
    const aspect = this.effectiveAspect();
    const geo = frameGeometry(iw, ih, aspect, this.zoom, this.u, this.v);
    const rect = this.canvas.getBoundingClientRect();
    const dx = (e.clientX - this.drag.x) * (this.canvas.width / rect.width);
    const dy = (e.clientY - this.drag.y) * (this.canvas.height / rect.height);
    this.u -= (dx * geo.sw / this.canvas.width) / iw;
    this.v -= (dy * geo.sh / this.canvas.height) / ih;
    this.drag = { x: e.clientX, y: e.clientY };
    this.render();
  },

  // The crop aspect currently being sampled from the source.
  effectiveAspect() {
    return this.carousel > 1 ? this.format.aspect * this.carousel : this.format.aspect;
  },

  /* ------------------------------------------------------- pixel effects */
  // Colour-grade filter string — pure functions only (never mix in url()).
  gradeFilter() {
    const a = this.adj;
    return `brightness(${a.brightness}%) contrast(${a.contrast}%) saturate(${a.saturate}%)`;
  },

  // A plus-shaped 3x3 sharpen convolution over a destination rect. Manual (not a
  // canvas url() filter) so it can never void the colour grading.
  sharpen(ctx, x, y, w, h) {
    const amt = (this.adj.sharpen || 0) / 100 * 0.8;
    if (amt <= 0) return;
    x = clamp(Math.round(x), 0, ctx.canvas.width);
    y = clamp(Math.round(y), 0, ctx.canvas.height);
    w = Math.min(ctx.canvas.width - x, Math.round(w));
    h = Math.min(ctx.canvas.height - y, Math.round(h));
    if (w <= 2 || h <= 2) return;
    const src = ctx.getImageData(x, y, w, h);
    const s = src.data;
    const out = ctx.createImageData(w, h);
    const o = out.data;
    const c = 1 + 4 * amt;
    for (let yy = 0; yy < h; yy++) {
      for (let xx = 0; xx < w; xx++) {
        const i = (yy * w + xx) * 4;
        const up = yy > 0 ? i - w * 4 : i;
        const dn = yy < h - 1 ? i + w * 4 : i;
        const lf = xx > 0 ? i - 4 : i;
        const rt = xx < w - 1 ? i + 4 : i;
        for (let ch = 0; ch < 3; ch++) {
          const v = c * s[i + ch] - amt * (s[up + ch] + s[dn + ch] + s[lf + ch] + s[rt + ch]);
          o[i + ch] = v < 0 ? 0 : v > 255 ? 255 : v;
        }
        o[i + 3] = s[i + 3];
      }
    }
    ctx.putImageData(out, x, y);
  },

  // A cached monochrome noise tile for film grain.
  grainTile() {
    if (this.noise) return this.noise;
    const n = document.createElement('canvas');
    n.width = n.height = 160;
    const nx = n.getContext('2d');
    const id = nx.createImageData(160, 160);
    const d = id.data;
    for (let i = 0; i < d.length; i += 4) { const v = Math.random() * 255; d[i] = d[i + 1] = d[i + 2] = v; d[i + 3] = 255; }
    nx.putImageData(id, 0, 0);
    this.noise = n;
    return n;
  },

  // Warmth wash, grain and vignette, clipped to a destination rect.
  applyEffects(ctx, x, y, w, h) {
    const a = this.adj;
    if (a.warmth) {
      ctx.save();
      ctx.beginPath(); ctx.rect(x, y, w, h); ctx.clip();
      ctx.globalCompositeOperation = 'soft-light';
      const t = Math.abs(a.warmth) / 100 * 0.6;
      ctx.fillStyle = a.warmth > 0 ? `rgba(255,150,40,${t})` : `rgba(40,140,255,${t})`;
      ctx.fillRect(x, y, w, h);
      ctx.restore();
    }
    if (a.grain) {
      ctx.save();
      ctx.beginPath(); ctx.rect(x, y, w, h); ctx.clip();
      ctx.globalCompositeOperation = 'overlay';
      ctx.globalAlpha = (a.grain / 100) * 0.4;
      ctx.fillStyle = ctx.createPattern(this.grainTile(), 'repeat');
      ctx.fillRect(x, y, w, h);
      ctx.restore();
    }
    if (a.vignette) {
      ctx.save();
      ctx.beginPath(); ctx.rect(x, y, w, h); ctx.clip();
      const g = ctx.createRadialGradient(x + w / 2, y + h / 2, Math.min(w, h) * 0.35, x + w / 2, y + h / 2, Math.max(w, h) * 0.72);
      g.addColorStop(0, 'rgba(0,0,0,0)');
      g.addColorStop(1, `rgba(0,0,0,${(a.vignette / 100) * 0.6})`);
      ctx.fillStyle = g;
      ctx.fillRect(x, y, w, h);
      ctx.restore();
    }
  },

  /* ---------------------------------------------------------- painting */
  /** Draw the current single-post photo + edits into a canvas of the given size. */
  paint(canvas, W, H) {
    canvas.width = W;
    canvas.height = H;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, W, H);
    const m = Math.round((this.border / 100) * Math.min(W, H));
    if (m > 0) { ctx.fillStyle = this.borderColor; ctx.fillRect(0, 0, W, H); }
    this.paintContent(ctx, m, m, W - 2 * m, H - 2 * m);
    this.drawTexts(ctx, W, H);
    this.drawWatermark(ctx, W, H);
  },

  // Paint the photo (and its background) into the inner destination rect.
  paintContent(ctx, dx, dy, dw, dh) {
    const img = this.img;
    const siw = img.naturalWidth || img.width;
    const sih = img.naturalHeight || img.height;
    const fit = this.fitMode === 'fit' && !this.bgRemoved;

    ctx.save();
    ctx.beginPath(); ctx.rect(dx, dy, dw, dh); ctx.clip();

    // Background fill behind the photo.
    if (this.bgRemoved) {
      ctx.fillStyle = this.bgColor;
      ctx.fillRect(dx, dy, dw, dh);
    } else if (fit) {
      if (this.fitBg === 'blur') {
        const g = frameGeometry(siw, sih, dw / dh, 1, 0.5, 0.5);
        ctx.filter = `blur(${Math.max(2, Math.round(Math.min(dw, dh) * 0.06))}px) brightness(0.92)`;
        ctx.drawImage(img, g.sx, g.sy, g.sw, g.sh, dx - 6, dy - 6, dw + 12, dh + 12); // overscan hides blurred edge
        ctx.filter = 'none';
      } else {
        ctx.fillStyle = this.fitBg;
        ctx.fillRect(dx, dy, dw, dh);
      }
    }

    // Foreground photo (colour grade via pure-function filter).
    ctx.filter = this.gradeFilter();
    if (fit) {
      const scale = Math.min(dw / siw, dh / sih);
      const gw = siw * scale;
      const gh = sih * scale;
      ctx.drawImage(img, 0, 0, siw, sih, dx + (dw - gw) / 2, dy + (dh - gh) / 2, gw, gh);
    } else {
      const geo = frameGeometry(siw, sih, dw / dh, this.zoom, this.u, this.v);
      this.u = (geo.sx + geo.sw / 2) / siw;
      this.v = (geo.sy + geo.sh / 2) / sih;
      ctx.drawImage(img, geo.sx, geo.sy, geo.sw, geo.sh, dx, dy, dw, dh);
    }
    ctx.filter = 'none';

    this.sharpen(ctx, dx, dy, dw, dh);
    this.applyEffects(ctx, dx, dy, dw, dh);
    ctx.restore();
  },

  /** Draw carousel tile `i` of `n` (a cover-cropped strip) into a destination rect. */
  drawTile(ctx, i, n, dx, dy, dw, dh) {
    const img = this.img;
    const siw = img.naturalWidth || img.width;
    const sih = img.naturalHeight || img.height;
    const geo = frameGeometry(siw, sih, this.format.aspect * n, this.zoom, this.u, this.v);
    this.u = (geo.sx + geo.sw / 2) / siw;
    this.v = (geo.sy + geo.sh / 2) / sih;
    const stripW = geo.sw / n;

    ctx.save();
    ctx.beginPath(); ctx.rect(dx, dy, dw, dh); ctx.clip();
    ctx.filter = this.gradeFilter();
    ctx.drawImage(img, geo.sx + i * stripW, geo.sy, stripW, geo.sh, dx, dy, dw, dh);
    ctx.filter = 'none';
    this.sharpen(ctx, dx, dy, dw, dh);
    this.applyEffects(ctx, dx, dy, dw, dh);
    ctx.restore();
  },

  // The original (unedited) photo in the current framing, for press-hold compare.
  paintOriginal(canvas, W, H) {
    canvas.width = W;
    canvas.height = H;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, W, H);
    const img = this.rawOriented || this.raw;
    const siw = img.naturalWidth || img.width;
    const sih = img.naturalHeight || img.height;
    if (this.fitMode === 'fit') {
      const scale = Math.min(W / siw, H / sih);
      ctx.drawImage(img, 0, 0, siw, sih, (W - siw * scale) / 2, (H - sih * scale) / 2, siw * scale, sih * scale);
    } else {
      const geo = frameGeometry(siw, sih, W / H, this.zoom, this.u, this.v);
      ctx.drawImage(img, geo.sx, geo.sy, geo.sw, geo.sh, 0, 0, W, H);
    }
  },

  // Preview-only guides showing where Instagram's Story/Reel UI covers the frame.
  drawSafeZones(ctx, W, H) {
    const top = H * 0.12;
    const bottom = H * 0.20;
    ctx.save();
    ctx.fillStyle = 'rgba(214,41,118,0.16)';
    ctx.fillRect(0, 0, W, top);
    ctx.fillRect(0, H - bottom, W, bottom);
    ctx.strokeStyle = 'rgba(255,255,255,0.85)';
    ctx.lineWidth = Math.max(1, W * 0.003);
    ctx.setLineDash([W * 0.02, W * 0.015]);
    ctx.beginPath();
    ctx.moveTo(0, top); ctx.lineTo(W, top);
    ctx.moveTo(0, H - bottom); ctx.lineTo(W, H - bottom);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = 'rgba(255,255,255,0.95)';
    ctx.font = `600 ${Math.round(H * 0.022)}px system-ui, sans-serif`;
    ctx.textAlign = 'center';
    ctx.fillText('Keep faces & text out of the shaded areas', W / 2, top + H * 0.035);
    ctx.restore();
  },

  // Rule-of-thirds composition guide (preview only) — helps place the subject.
  drawGrid(ctx, W, H) {
    ctx.save();
    ctx.strokeStyle = 'rgba(255,255,255,0.7)';
    ctx.lineWidth = Math.max(1, W * 0.0022);
    ctx.shadowColor = 'rgba(0,0,0,0.35)';
    ctx.shadowBlur = Math.max(1, W * 0.004);
    for (let i = 1; i < 3; i++) {
      ctx.beginPath(); ctx.moveTo((W * i) / 3, 0); ctx.lineTo((W * i) / 3, H); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(0, (H * i) / 3); ctx.lineTo(W, (H * i) / 3); ctx.stroke();
    }
    ctx.restore();
  },

  render() {
    if (!this.img) return;
    const cap = 900;
    if (this.showOriginal && this.carousel <= 1) {
      const aspect = this.format.aspect;
      const W = aspect >= 1 ? cap : Math.round(cap * aspect);
      const H = aspect >= 1 ? Math.round(cap / aspect) : cap;
      this.paintOriginal(this.canvas, W, H);
      return;
    }
    if (this.carousel > 1) {
      this.texts.forEach((l) => { l._box = null; }); // text isn't drawn on the panorama preview
      // Preview the whole panorama with dashed tile dividers.
      const n = this.carousel;
      const aspect = this.format.aspect * n;
      const W = aspect >= 1 ? cap : Math.round(cap * aspect);
      const H = aspect >= 1 ? Math.round(cap / aspect) : cap;
      this.canvas.width = W;
      this.canvas.height = H;
      const ctx = this.canvas.getContext('2d');
      ctx.clearRect(0, 0, W, H);
      const tileW = W / n;
      for (let i = 0; i < n; i++) this.drawTile(ctx, i, n, i * tileW, 0, tileW, H);
      ctx.save();
      ctx.strokeStyle = 'rgba(255,255,255,0.9)';
      ctx.lineWidth = 2;
      ctx.setLineDash([9, 7]);
      for (let i = 1; i < n; i++) { ctx.beginPath(); ctx.moveTo(i * tileW, 0); ctx.lineTo(i * tileW, H); ctx.stroke(); }
      ctx.restore();
      return;
    }
    const aspect = this.format.aspect;
    const W = aspect >= 1 ? cap : Math.round(cap * aspect);
    const H = aspect >= 1 ? Math.round(cap / aspect) : cap;
    this.paint(this.canvas, W, H);
    if (this.grid) this.drawGrid(this.canvas.getContext('2d'), W, H);
    if (this.safeZones) this.drawSafeZones(this.canvas.getContext('2d'), W, H);
  },

  async removeBackground() {
    if (!this.raw) return;
    if (this.cutout) { this.bgRemoved = true; this.rebuildSource(); $('#ig-restore-bg').classList.remove('hidden'); this.render(); return; }
    const btn = $('#ig-remove-bg');
    const original = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin mr-1"></i>Removing…';
    try {
      const { removeBackground } = await import('https://cdn.jsdelivr.net/npm/@imgly/background-removal@1.6.0/+esm');
      // Full 'isnet' when cross-origin isolated (threaded WASM); quantized
      // fallback otherwise. See config/middleware.py ISOLATED_VIEWS.
      const blob = await removeBackground(this.file, { model: self.crossOriginIsolated ? 'isnet' : 'isnet_quint8' });
      if (this.cutoutUrl) URL.revokeObjectURL(this.cutoutUrl);
      this.cutoutUrl = URL.createObjectURL(blob);
      this.cutout = await loadImage(this.cutoutUrl);
      this.bgRemoved = true;
      this.rebuildSource();
      $('#ig-restore-bg').classList.remove('hidden');
      this.render();
      Toast.show('Background removed', 'success');
    } catch (err) {
      console.error('[instagram] bg removal failed:', err);
      Toast.show('Background removal failed', 'error');
    } finally {
      btn.disabled = false;
      btn.innerHTML = original;
    }
  },

  saveBlob(blob, name) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = name;
    document.body.appendChild(a);
    a.click();
    URL.revokeObjectURL(url);
    a.remove();
  },

  async download() {
    if (!this.img) return;
    const out = document.createElement('canvas');
    this.paint(out, this.format.w, this.format.h);
    const isPng = this.exportFmt === 'image/png';
    const blob = await new Promise((res) => out.toBlob(res, this.exportFmt, isPng ? undefined : this.quality));
    const ext = isPng ? 'png' : 'jpg';
    this.saveBlob(blob, `instagram-${this.format.key}-${this.format.w}x${this.format.h}.${ext}`);
    Toast.show(`Saved ${this.format.w}×${this.format.h} for Instagram`, 'success');
  },

  async downloadCarousel() {
    if (!this.img) return;
    const n = this.carousel;
    const fmt = this.format;
    Toast.show('Building carousel ZIP…', 'info');
    try {
      const JSZip = (await import('https://cdn.jsdelivr.net/npm/jszip@3.10.1/+esm')).default;
      const zip = new JSZip();
      const isPng = this.exportFmt === 'image/png';
      const ext = isPng ? 'png' : 'jpg';
      for (let i = 0; i < n; i++) {
        const c = document.createElement('canvas');
        c.width = fmt.w;
        c.height = fmt.h;
        this.drawTile(c.getContext('2d'), i, n, 0, 0, fmt.w, fmt.h);
        const blob = await new Promise((res) => c.toBlob(res, this.exportFmt, isPng ? undefined : this.quality));
        zip.file(`carousel-${i + 1}-of-${n}.${ext}`, blob);
      }
      const blob = await zip.generateAsync({ type: 'blob' });
      this.saveBlob(blob, `instagram-carousel-${n}x-${fmt.key}.zip`);
      Toast.show(`Saved a ${n}-tile carousel — post the tiles in order`, 'success');
    } catch (err) {
      console.error('[instagram] carousel export failed:', err);
      Toast.show('Carousel export failed', 'error');
    }
  },

  reset() {
    this.editor.classList.add('hidden');
    this.dropzone.parentElement.classList.remove('hidden');
    if (this.origUrl) { URL.revokeObjectURL(this.origUrl); this.origUrl = null; }
    if (this.cutoutUrl) { URL.revokeObjectURL(this.cutoutUrl); this.cutoutUrl = null; }
    this.raw = this.img = this.cutout = this.rawOriented = null;
    this.texts = []; this.activeText = -1;
  },
};

document.addEventListener('DOMContentLoaded', () => {
  App.init();
  // If we arrived via "Continue in Instagram" from another tool, load that image.
  takeHandoff().then((file) => { if (file) App.load(file); });
});
