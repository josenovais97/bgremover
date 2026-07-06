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
};

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
  showOriginal: false, // press-and-hold compare
  raw: null, // original uploaded image
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
    $('#ig-border').addEventListener('input', (e) => { this.border = +e.target.value; this.render(); });
    $('#ig-border-color').addEventListener('input', (e) => { this.borderColor = e.target.value; if (this.border > 0) this.render(); });
    // Looks + strength
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

    // Background removal (optional, lazy)
    $('#ig-remove-bg').addEventListener('click', () => this.removeBackground());
    $('#ig-restore-bg').addEventListener('click', () => { this.bgRemoved = false; this.img = this.raw; $('#ig-restore-bg').classList.add('hidden'); this.render(); });
    $('#ig-bg-color').addEventListener('input', (e) => { this.bgColor = e.target.value; if (this.bgRemoved) this.render(); });

    // Framing
    const zoom = $('#ig-zoom');
    zoom.addEventListener('input', () => { this.zoom = +zoom.value; this.render(); });
    this.canvas.addEventListener('wheel', (e) => {
      e.preventDefault();
      this.zoom = clamp(this.zoom * (e.deltaY < 0 ? 1.1 : 1 / 1.1), 1, 4);
      zoom.value = this.zoom;
      this.render();
    }, { passive: false });
    this.canvas.addEventListener('pointerdown', (e) => { this.drag = { x: e.clientX, y: e.clientY }; this.canvas.setPointerCapture?.(e.pointerId); });
    this.canvas.addEventListener('pointermove', (e) => this.onDrag(e));
    ['pointerup', 'pointercancel', 'pointerleave'].forEach((ev) => this.canvas.addEventListener(ev, () => { this.drag = null; }));

    $('#ig-download').addEventListener('click', () => (this.carousel > 1 ? this.downloadCarousel() : this.download()));
    $('#ig-new').addEventListener('click', () => this.reset());
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
    this.img = this.raw;
    this.cutout = null;
    this.bgRemoved = false;
    this.zoom = 1;
    this.u = 0.5;
    this.v = 0.5;
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

  /* ---------------------------------------------------------- looks */
  blend(a, b, t) {
    const o = {};
    for (const k of ADJ_KEYS) o[k] = a[k] + (b[k] - a[k]) * t;
    return o;
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
    const img = this.raw;
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
    if (this.safeZones) this.drawSafeZones(this.canvas.getContext('2d'), W, H);
  },

  async removeBackground() {
    if (!this.raw) return;
    if (this.cutout) { this.img = this.cutout; this.bgRemoved = true; $('#ig-restore-bg').classList.remove('hidden'); this.render(); return; }
    const btn = $('#ig-remove-bg');
    const original = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-1"></i>Removing…';
    try {
      const { removeBackground } = await import('https://cdn.jsdelivr.net/npm/@imgly/background-removal@1.6.0/+esm');
      const blob = await removeBackground(this.file);
      if (this.cutoutUrl) URL.revokeObjectURL(this.cutoutUrl);
      this.cutoutUrl = URL.createObjectURL(blob);
      this.cutout = await loadImage(this.cutoutUrl);
      this.img = this.cutout;
      this.bgRemoved = true;
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
    const blob = await new Promise((res) => out.toBlob(res, 'image/jpeg', 0.92));
    this.saveBlob(blob, `instagram-${this.format.key}-${this.format.w}x${this.format.h}.jpg`);
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
      for (let i = 0; i < n; i++) {
        const c = document.createElement('canvas');
        c.width = fmt.w;
        c.height = fmt.h;
        this.drawTile(c.getContext('2d'), i, n, 0, 0, fmt.w, fmt.h);
        const blob = await new Promise((res) => c.toBlob(res, 'image/jpeg', 0.92));
        zip.file(`carousel-${i + 1}-of-${n}.jpg`, blob);
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
    this.raw = this.img = this.cutout = null;
  },
};

document.addEventListener('DOMContentLoaded', () => App.init());
