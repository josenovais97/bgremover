import { takeHandoff } from './handoff.js';

/**
 * Standalone image crop tool — 100% client-side, no background removal.
 *
 * Upload a photo and crop it: choose a shape (rectangle, rounded, circle), an
 * aspect ratio (Original, 1:1, 4:5, 3:4, 16:9, 9:16 or a custom W:H), rotate in
 * 90° steps, flip horizontally/vertically, then zoom and drag to frame it.
 * Export a full-resolution PNG (transparent corners on rounded/circle crops) or
 * a JPG. Nothing is uploaded — the crop happens entirely in the browser.
 *
 * Self-contained (own helpers/toast) because Django's hashed-manifest static
 * storage doesn't rewrite ES-module import paths.
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
  shape: 'rect', // 'rect' | 'rounded' | 'circle'
  ratioKey: 'free', // 'free' | number | 'custom'
  customW: 4,
  customH: 3,
  rot: 0, // 0/90/180/270
  flipH: false,
  flipV: false,
  zoom: 1,
  u: 0.5,
  v: 0.5,
  format: 'png',
  raw: null,
  oriented: null, // raw with rotation/flip baked in; the crop source
  origUrl: null,

  init() {
    this.dropzone = $('#cr-dropzone');
    this.input = $('#cr-input');
    this.editor = $('#cr-editor');
    this.canvas = $('#cr-canvas');

    const open = () => this.input.click();
    $('#cr-browse').addEventListener('click', (e) => { e.stopPropagation(); open(); });
    this.dropzone.addEventListener('click', open);
    this.dropzone.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); } });
    this.input.addEventListener('change', (e) => this.load(e.target.files[0]));

    const icon = $('#cr-icon');
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

    $$('.cr-shape').forEach((b) => b.addEventListener('click', () => this.setShape(b)));
    $$('.cr-ratio').forEach((b) => b.addEventListener('click', () => this.setRatio(b)));
    $('#cr-custom-w').addEventListener('input', (e) => { this.customW = Math.max(1, +e.target.value || 1); if (this.ratioKey === 'custom') this.render(); });
    $('#cr-custom-h').addEventListener('input', (e) => { this.customH = Math.max(1, +e.target.value || 1); if (this.ratioKey === 'custom') this.render(); });
    $$('.cr-format').forEach((b) => b.addEventListener('click', () => this.setFormat(b)));

    $('#cr-rotate-l').addEventListener('click', () => this.rotate(-90));
    $('#cr-rotate-r').addEventListener('click', () => this.rotate(90));
    $('#cr-flip-h').addEventListener('click', () => { this.flipH = !this.flipH; this.buildOriented(); this.render(); });
    $('#cr-flip-v').addEventListener('click', () => { this.flipV = !this.flipV; this.buildOriented(); this.render(); });

    const zoom = $('#cr-zoom');
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

    $('#cr-download').addEventListener('click', () => this.download());
    $('#cr-new').addEventListener('click', () => this.reset());
  },

  async load(file) {
    this.input.value = '';
    if (!file || !file.type.startsWith('image/')) { Toast.show('Please choose an image', 'error'); return; }
    if (this.origUrl) URL.revokeObjectURL(this.origUrl);
    this.origUrl = URL.createObjectURL(file);
    try {
      this.raw = await loadImage(this.origUrl);
    } catch {
      Toast.show("Couldn't open that image", 'error');
      return;
    }
    this.rot = 0;
    this.flipH = false;
    this.flipV = false;
    this.zoom = 1;
    this.u = 0.5;
    this.v = 0.5;
    $('#cr-zoom').value = 1;
    this.buildOriented();
    this.dropzone.parentElement.classList.add('hidden');
    this.editor.classList.remove('hidden');
    this.render();
  },

  // Bake rotation + flip into an offscreen canvas that becomes the crop source.
  buildOriented() {
    const img = this.raw;
    if (!img) return;
    const iw = img.naturalWidth || img.width;
    const ih = img.naturalHeight || img.height;
    const swap = this.rot === 90 || this.rot === 270;
    const ow = swap ? ih : iw;
    const oh = swap ? iw : ih;
    const c = document.createElement('canvas');
    c.width = ow;
    c.height = oh;
    const x = c.getContext('2d');
    x.translate(ow / 2, oh / 2);
    x.rotate((this.rot * Math.PI) / 180);
    x.scale(this.flipH ? -1 : 1, this.flipV ? -1 : 1);
    x.drawImage(img, -iw / 2, -ih / 2);
    this.oriented = c;
  },

  rotate(delta) {
    this.rot = (this.rot + delta + 360) % 360;
    this.buildOriented();
    this.render();
  },

  setShape(btn) {
    this.shape = btn.dataset.shape;
    this.highlight('.cr-shape', btn);
    // Circle only makes sense at 1:1 — force a square ratio.
    if (this.shape === 'circle') {
      const one = $(".cr-ratio[data-ratio='1']");
      this.setRatio(one);
    } else {
      this.render();
    }
  },

  setRatio(btn) {
    this.ratioKey = btn.dataset.ratio;
    this.highlight('.cr-ratio', btn);
    $('#cr-custom').classList.toggle('hidden', this.ratioKey !== 'custom');
    $('#cr-custom').classList.toggle('flex', this.ratioKey === 'custom');
    this.render();
  },

  setFormat(btn) {
    this.format = btn.dataset.format;
    this.highlight('.cr-format', btn);
    $('#cr-format-note').textContent = this.format === 'png'
      ? 'PNG keeps transparent corners on rounded/circle crops.'
      : 'JPG has no transparency — rounded/circle corners fill white.';
  },

  highlight(selector, btn) {
    $$(selector).forEach((b) => { const a = b === btn; b.classList.toggle('ring-2', a); b.classList.toggle('ring-primary', a); });
  },

  // The crop aspect (width / height) currently selected.
  aspect() {
    if (this.ratioKey === 'free') {
      const o = this.oriented;
      return o ? o.width / o.height : 1;
    }
    if (this.ratioKey === 'custom') return this.customW / this.customH;
    return +this.ratioKey;
  },

  onDrag(e) {
    if (!this.drag || !this.oriented) return;
    const iw = this.oriented.width;
    const ih = this.oriented.height;
    const geo = frameGeometry(iw, ih, this.aspect(), this.zoom, this.u, this.v);
    const rect = this.canvas.getBoundingClientRect();
    const dx = (e.clientX - this.drag.x) * (this.canvas.width / rect.width);
    const dy = (e.clientY - this.drag.y) * (this.canvas.height / rect.height);
    this.u -= (dx * geo.sw / this.canvas.width) / iw;
    this.v -= (dy * geo.sh / this.canvas.height) / ih;
    this.drag = { x: e.clientX, y: e.clientY };
    this.render();
  },

  // Clip the context to the current shape within a W×H box.
  clipShape(ctx, W, H) {
    if (this.shape === 'rect') return;
    ctx.beginPath();
    if (this.shape === 'circle') {
      ctx.ellipse(W / 2, H / 2, W / 2, H / 2, 0, 0, Math.PI * 2);
    } else { // rounded
      const r = Math.min(W, H) * 0.12;
      ctx.moveTo(r, 0);
      ctx.arcTo(W, 0, W, H, r);
      ctx.arcTo(W, H, 0, H, r);
      ctx.arcTo(0, H, 0, 0, r);
      ctx.arcTo(0, 0, W, 0, r);
      ctx.closePath();
    }
    ctx.clip();
  },

  // Paint the crop into a canvas of the given pixel size.
  paint(canvas, W, H, flattenJpg = false) {
    const src = this.oriented;
    const geo = frameGeometry(src.width, src.height, this.aspect(), this.zoom, this.u, this.v);
    this.u = (geo.sx + geo.sw / 2) / src.width;
    this.v = (geo.sy + geo.sh / 2) / src.height;

    canvas.width = W;
    canvas.height = H;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, W, H);
    ctx.save();
    if (flattenJpg) { ctx.fillStyle = '#ffffff'; ctx.fillRect(0, 0, W, H); }
    this.clipShape(ctx, W, H);
    ctx.drawImage(src, geo.sx, geo.sy, geo.sw, geo.sh, 0, 0, W, H);
    ctx.restore();
  },

  render() {
    if (!this.oriented) return;
    // Preview at a capped size that matches the crop aspect.
    const cap = 720;
    const a = this.aspect();
    const W = a >= 1 ? cap : Math.round(cap * a);
    const H = a >= 1 ? Math.round(cap / a) : cap;
    this.paint(this.canvas, W, H);
  },

  async download() {
    if (!this.oriented) return;
    // Export at the crop's native source resolution (no upscaling).
    const src = this.oriented;
    const geo = frameGeometry(src.width, src.height, this.aspect(), this.zoom, this.u, this.v);
    const W = Math.max(1, Math.round(geo.sw));
    const H = Math.max(1, Math.round(geo.sh));
    const out = document.createElement('canvas');
    const jpg = this.format === 'jpg';
    this.paint(out, W, H, jpg);
    const mime = jpg ? 'image/jpeg' : 'image/png';
    const blob = await new Promise((res) => out.toBlob(res, mime, 0.95));
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `crop-${W}x${H}.${jpg ? 'jpg' : 'png'}`;
    document.body.appendChild(a);
    a.click();
    URL.revokeObjectURL(url);
    a.remove();
    Toast.show(`Saved crop ${W}×${H}`, 'success');
  },

  reset() {
    this.editor.classList.add('hidden');
    this.dropzone.parentElement.classList.remove('hidden');
    if (this.origUrl) { URL.revokeObjectURL(this.origUrl); this.origUrl = null; }
    this.raw = this.oriented = null;
  },
};

document.addEventListener('DOMContentLoaded', () => {
  App.init();
  // If we arrived via "Continue in Crop" from another tool, load that image.
  takeHandoff().then((file) => { if (file) App.load(file); });
});
