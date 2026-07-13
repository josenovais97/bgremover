/**
 * eCommerce / marketplace product-photo maker — 100% client-side.
 *
 * Removes the background, drops the product on a pure-white backdrop, centres it
 * and scales it to fill the frame, then exports at the exact size each
 * marketplace expects. One click per marketplace (Amazon / Etsy / Shopify).
 * Nothing is uploaded.
 *
 * Self-contained (own helpers/toast) — only absolute-URL (CDN) imports are used.
 */
import { removeBackground } from 'https://cdn.jsdelivr.net/npm/@imgly/background-removal@1.6.0/+esm';

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

function rafThrottle(fn) {
  let scheduled = false;
  return () => { if (scheduled) return; scheduled = true; requestAnimationFrame(() => { scheduled = false; fn(); }); };
}

// Marketplace specs. `size` = export px (square). `fill` = fraction of the frame
// the product should occupy. `bg` white unless the user picks transparent.
const MARKETS = {
  amazon:  { label: 'Amazon',  size: 2000, fill: 0.85, note: 'Pure white · 2000×2000 · product fills 85%' },
  etsy:    { label: 'Etsy',    size: 2000, fill: 0.90, note: 'Square 2000×2000 · clean white' },
  shopify: { label: 'Shopify', size: 2048, fill: 0.90, note: 'Square 2048×2048 · clean white' },
};

/* --------------------------------------------------------------------- app */
const App = {
  cutout: null,
  bbox: null,
  market: 'amazon',
  bg: '#ffffff',       // '' = transparent
  shadow: false,

  init() {
    this.dropzone = $('#ec-dropzone');
    this.input = $('#ec-input');
    this.editor = $('#ec-editor');
    this.canvas = $('#ec-canvas');

    const open = () => this.input.click();
    $('#ec-browse').addEventListener('click', (e) => { e.stopPropagation(); open(); });
    this.dropzone.addEventListener('click', open);
    this.dropzone.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); } });
    this.input.addEventListener('change', (e) => this.load(e.target.files[0]));

    const icon = $('#ec-icon');
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach((evt) =>
      this.dropzone.addEventListener(evt, (e) => { e.preventDefault(); e.stopPropagation(); }));
    ['dragenter', 'dragover'].forEach((evt) => this.dropzone.addEventListener(evt, () => { this.dropzone.classList.add('border-primary', 'bg-primary/5'); icon.classList.add('scale-110'); }));
    ['dragleave', 'drop'].forEach((evt) => this.dropzone.addEventListener(evt, () => { this.dropzone.classList.remove('border-primary', 'bg-primary/5'); icon.classList.remove('scale-110'); }));
    this.dropzone.addEventListener('drop', (e) => this.load(e.dataTransfer.files[0]));
    document.addEventListener('paste', (e) => {
      const f = [...(e.clipboardData?.items || [])].find((i) => i.kind === 'file');
      if (f) this.load(f.getAsFile());
    });

    // Marketplace buttons.
    const wrap = $('#ec-markets');
    wrap.innerHTML = Object.entries(MARKETS).map(([k, m]) =>
      `<button type="button" data-market="${k}" class="ec-market text-left px-4 py-3 rounded-xl border transition ${k === this.market ? 'border-primary bg-primary/5 text-primary' : 'border-gray-300 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800'}">
        <span class="block font-semibold">${m.label} Ready</span>
        <span class="block text-xs text-gray-400">${m.note}</span>
      </button>`).join('');
    wrap.addEventListener('click', (e) => {
      const b = e.target.closest('.ec-market');
      if (!b) return;
      this.market = b.dataset.market;
      $$('.ec-market').forEach((x) => {
        const a = x.dataset.market === this.market;
        x.classList.toggle('border-primary', a); x.classList.toggle('bg-primary/5', a); x.classList.toggle('text-primary', a);
        x.classList.toggle('border-gray-300', !a); x.classList.toggle('dark:border-gray-700', !a);
      });
      this.updateButton();
      this.render();
    });

    const render = rafThrottle(() => this.render());
    // Background toggle (white / transparent).
    $$('.ec-bg').forEach((b) => b.addEventListener('click', () => {
      this.bg = b.dataset.bg;
      $$('.ec-bg').forEach((x) => { const a = x.dataset.bg === this.bg; x.classList.toggle('ring-2', a); x.classList.toggle('ring-primary', a); });
      this.render();
    }));
    $('#ec-fill').addEventListener('input', (e) => { this.fillOverride = +e.target.value / 100; render(); });
    $('#ec-shadow').addEventListener('change', (e) => { this.shadow = e.target.checked; this.render(); });

    $('#ec-download').addEventListener('click', () => this.export());
    $('#ec-new').addEventListener('click', () => this.reset());

    this.setBusy(false);
  },

  fill() {
    return this.fillOverride != null ? this.fillOverride : MARKETS[this.market].fill;
  },

  updateButton() {
    $('#ec-download-label').textContent = `Download ${MARKETS[this.market].label} photo`;
    $('#ec-fill').value = Math.round(this.fill() * 100);
  },

  setBusy(busy, text) {
    $('#ec-status').classList.toggle('hidden', !busy);
    if (text) $('#ec-status-text').textContent = text;
    $('#ec-download').disabled = busy || !this.cutout;
  },

  async load(file) {
    this.input.value = '';
    if (!file || !/^image\//.test(file.type)) { Toast.show('Please choose an image', 'error'); return; }
    this.cutout = null;
    this.fillOverride = null;
    this.dropzone.parentElement.classList.add('hidden');
    this.editor.classList.remove('hidden');
    this.updateButton();
    this.setBusy(true, 'Removing background…');
    this.render();
    try {
      const blob = await removeBackground(file, { model: self.crossOriginIsolated ? 'isnet' : 'isnet_quint8' });
      if (this.cutoutUrl) URL.revokeObjectURL(this.cutoutUrl);
      this.cutoutUrl = URL.createObjectURL(blob);
      this.cutout = await loadImage(this.cutoutUrl);
      this.bbox = this.alphaBBox(this.cutout);
      window.__clearbgReport?.(1);
      this.setBusy(false);
      this.render();
      Toast.show('Done — pick a marketplace and download', 'success');
    } catch (err) {
      console.error('[ecommerce] bg removal failed:', err);
      Toast.show('Background removal failed', 'error');
      this.setBusy(false);
    }
  },

  alphaBBox(img) {
    const w = img.naturalWidth, h = img.naturalHeight;
    const c = document.createElement('canvas');
    c.width = w; c.height = h;
    const ctx = c.getContext('2d');
    ctx.drawImage(img, 0, 0);
    const data = ctx.getImageData(0, 0, w, h).data;
    let minX = w, minY = h, maxX = 0, maxY = 0, found = false;
    for (let y = 0; y < h; y++) {
      for (let x = 0; x < w; x++) {
        if (data[(y * w + x) * 4 + 3] > 12) {
          found = true;
          if (x < minX) minX = x; if (x > maxX) maxX = x;
          if (y < minY) minY = y; if (y > maxY) maxY = y;
        }
      }
    }
    if (!found) return { x: 0, y: 0, w, h };
    return { x: minX, y: minY, w: maxX - minX + 1, h: maxY - minY + 1 };
  },

  /** Compose the product photo into `canvas` at `size` px. */
  paint(canvas, size) {
    canvas.width = size; canvas.height = size;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, size, size);
    if (this.bg) { ctx.fillStyle = this.bg; ctx.fillRect(0, 0, size, size); }
    if (!this.cutout || !this.bbox) return;

    const target = size * this.fill();
    const scale = target / Math.max(this.bbox.w, this.bbox.h);
    const dw = this.cutout.naturalWidth * scale;
    const dh = this.cutout.naturalHeight * scale;
    // Centre the product's bounding box within the frame.
    const bcx = (this.bbox.x + this.bbox.w / 2) * scale;
    const bcy = (this.bbox.y + this.bbox.h / 2) * scale;
    const dx = size / 2 - bcx;
    const dy = size / 2 - bcy;

    if (this.shadow) {
      ctx.save();
      ctx.shadowColor = 'rgba(0,0,0,0.28)';
      ctx.shadowBlur = size * 0.03;
      ctx.shadowOffsetY = size * 0.02;
    }
    ctx.imageSmoothingQuality = 'high';
    ctx.drawImage(this.cutout, dx, dy, dw, dh);
    if (this.shadow) ctx.restore();
  },

  render() {
    // Preview at a manageable size; export re-renders at full resolution.
    this.paint(this.canvas, 640);
    this.canvas.classList.toggle('checkerboard', !this.bg);
  },

  async export() {
    if (!this.cutout) return;
    const m = MARKETS[this.market];
    const c = document.createElement('canvas');
    this.paint(c, m.size);
    // JPEG for white backgrounds (what marketplaces want); PNG when transparent.
    const transparent = !this.bg;
    const fmt = transparent ? 'image/png' : 'image/jpeg';
    const ext = transparent ? 'png' : 'jpg';
    const blob = await new Promise((res) => c.toBlob(res, fmt, 0.95));
    if (!blob) { Toast.show('Export failed', 'error'); return; }
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = `${m.label.toLowerCase()}-product-${m.size}.${ext}`;
    document.body.appendChild(a); a.click(); URL.revokeObjectURL(url); a.remove();
    const kb = Math.round(blob.size / 1024);
    $('#ec-done').innerHTML = `<i class="fa-solid fa-circle-check text-green-500 mr-1"></i>${m.label} photo saved · ${m.size}×${m.size}px · ${kb} KB`;
  },

  reset() {
    this.editor.classList.add('hidden');
    this.dropzone.parentElement.classList.remove('hidden');
    if (this.cutoutUrl) { URL.revokeObjectURL(this.cutoutUrl); this.cutoutUrl = null; }
    this.cutout = null; this.bbox = null;
    $('#ec-done').textContent = '';
  },
};

document.addEventListener('DOMContentLoaded', () => App.init());
