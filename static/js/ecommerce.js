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
import JSZip from 'https://cdn.jsdelivr.net/npm/jszip@3.10.1/+esm';

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
  items: [],           // { file, name, cutout, bbox, cutoutUrl, status, canvas, statusEl }
  market: 'amazon',
  bg: '#ffffff',       // '' = transparent
  shadow: false,
  fillOverride: null,
  busy: false,

  init() {
    this.dropzone = $('#ec-dropzone');
    this.input = $('#ec-input');
    this.editor = $('#ec-editor');
    this.grid = $('#ec-grid');

    const open = () => this.input.click();
    $('#ec-browse').addEventListener('click', (e) => { e.stopPropagation(); open(); });
    this.dropzone.addEventListener('click', open);
    this.dropzone.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); } });
    this.input.addEventListener('change', (e) => this.load(e.target.files));

    const icon = $('#ec-icon');
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach((evt) =>
      this.dropzone.addEventListener(evt, (e) => { e.preventDefault(); e.stopPropagation(); }));
    ['dragenter', 'dragover'].forEach((evt) => this.dropzone.addEventListener(evt, () => { this.dropzone.classList.add('border-primary', 'bg-primary/5'); icon.classList.add('scale-110'); }));
    ['dragleave', 'drop'].forEach((evt) => this.dropzone.addEventListener(evt, () => { this.dropzone.classList.remove('border-primary', 'bg-primary/5'); icon.classList.remove('scale-110'); }));
    this.dropzone.addEventListener('drop', (e) => this.load(e.dataTransfer.files));
    document.addEventListener('paste', (e) => {
      const files = [...(e.clipboardData?.items || [])].filter((i) => i.kind === 'file').map((i) => i.getAsFile()).filter(Boolean);
      if (files.length) this.load(files);
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

    this.updateButton();
    this.updateDownload();
  },

  fill() {
    return this.fillOverride != null ? this.fillOverride : MARKETS[this.market].fill;
  },

  doneItems() {
    return this.items.filter((it) => it.status === 'done');
  },

  updateButton() {
    $('#ec-fill').value = Math.round(this.fill() * 100);
  },

  // Enable/label the download control from the current queue state.
  updateDownload() {
    const done = this.doneItems().length;
    const btn = $('#ec-download');
    btn.disabled = this.busy || done === 0;
    $('#ec-download-label').textContent = done > 1
      ? `Download all ${done} · ${MARKETS[this.market].label} (ZIP)`
      : `Download ${MARKETS[this.market].label} photo`;
  },

  // Add a card to the results grid for one file; processing happens in the queue.
  addItem(file) {
    const tile = document.createElement('div');
    tile.className = 'ec-item glass rounded-xl border border-gray-200/70 dark:border-gray-800/70 p-2 flex flex-col gap-2';
    tile.innerHTML = `
      <div class="relative">
        <canvas class="ec-item-canvas w-full rounded-lg block" width="480" height="480"></canvas>
        <div class="ec-item-status absolute inset-0 grid place-items-center rounded-lg bg-white/70 dark:bg-gray-950/70 backdrop-blur-sm text-[11px] font-medium">
          <span class="flex items-center gap-1.5 text-primary"><i class="fa-solid fa-circle-notch fa-spin" aria-hidden="true"></i> Removing…</span>
        </div>
      </div>
      <div class="flex items-center justify-between gap-2">
        <span class="ec-item-name text-[11px] truncate text-gray-500 dark:text-gray-400" title="${file.name}">${file.name}</span>
        <button type="button" class="ec-item-dl shrink-0 w-7 h-7 grid place-items-center rounded-lg text-gray-500 hover:text-primary hover:bg-gray-100 dark:hover:bg-gray-800 transition disabled:opacity-40" title="Download this photo" disabled>
          <i class="fa-solid fa-download text-xs" aria-hidden="true"></i>
        </button>
      </div>`;
    this.grid.appendChild(tile);
    const item = {
      file, name: file.name, cutout: null, bbox: null, cutoutUrl: null, status: 'queued',
      canvas: tile.querySelector('.ec-item-canvas'),
      statusEl: tile.querySelector('.ec-item-status'),
    };
    tile.querySelector('.ec-item-dl').addEventListener('click', () => this.exportOne(item));
    item.dlBtn = tile.querySelector('.ec-item-dl');
    this.items.push(item);
    return item;
  },

  setItemStatus(item, show, text = '', error = false) {
    item.statusEl.classList.toggle('hidden', !show);
    if (show) {
      item.statusEl.innerHTML = error
        ? `<span class="flex items-center gap-1.5 text-red-500"><i class="fa-solid fa-triangle-exclamation" aria-hidden="true"></i> ${text}</span>`
        : `<span class="flex items-center gap-1.5 text-primary"><i class="fa-solid fa-circle-notch fa-spin" aria-hidden="true"></i> ${text}</span>`;
    }
  },

  async load(fileList) {
    // Snapshot the files BEFORE clearing the input — `fileList` is the live
    // input.files, so resetting the value first would empty it out.
    const files = [...(fileList || [])].filter((f) => f && /^image\//.test(f.type));
    this.input.value = '';
    if (!files.length) { Toast.show('Please choose image files', 'error'); return; }
    this.dropzone.parentElement.classList.add('hidden');
    this.editor.classList.remove('hidden');
    files.forEach((f) => this.addItem(f));
    this.updateDownload();
    await this.processQueue();
  },

  // Remove backgrounds one at a time (the model is heavy; sequential keeps
  // memory flat and the UI responsive as each card fills in).
  async processQueue() {
    if (this.busy) return;
    this.busy = true;
    this.updateDownload();
    for (const it of this.items) {
      if (it.status !== 'queued') continue;
      it.status = 'processing';
      this.setItemStatus(it, true, 'Removing…');
      try {
        const blob = await removeBackground(it.file, { model: self.crossOriginIsolated ? 'isnet' : 'isnet_quint8' });
        it.cutoutUrl = URL.createObjectURL(blob);
        it.cutout = await loadImage(it.cutoutUrl);
        it.bbox = this.alphaBBox(it.cutout);
        it.status = 'done';
        window.__clearbgReport?.(1);
        this.setItemStatus(it, false);
        it.dlBtn.disabled = false;
        this.paintItem(it);
      } catch (err) {
        console.error('[ecommerce] bg removal failed:', err);
        it.status = 'error';
        this.setItemStatus(it, true, 'Failed', true);
      }
      this.updateDownload();
    }
    this.busy = false;
    this.updateDownload();
    const done = this.doneItems().length;
    if (done) Toast.show(`Ready — ${done} photo${done > 1 ? 's' : ''}. Pick a marketplace and download.`, 'success');
  },

  paintItem(it) {
    if (!it.cutout) return;
    this.paint(it.canvas, 480, it);
    it.canvas.classList.toggle('checkerboard', !this.bg);
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

  /** Compose one product's cut-out into `canvas` at `size` px. */
  paint(canvas, size, item) {
    canvas.width = size; canvas.height = size;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, size, size);
    if (this.bg) { ctx.fillStyle = this.bg; ctx.fillRect(0, 0, size, size); }
    if (!item || !item.cutout || !item.bbox) return;

    const target = size * this.fill();
    const scale = target / Math.max(item.bbox.w, item.bbox.h);
    const dw = item.cutout.naturalWidth * scale;
    const dh = item.cutout.naturalHeight * scale;
    // Centre the product's bounding box within the frame.
    const bcx = (item.bbox.x + item.bbox.w / 2) * scale;
    const bcy = (item.bbox.y + item.bbox.h / 2) * scale;
    const dx = size / 2 - bcx;
    const dy = size / 2 - bcy;

    if (this.shadow) {
      ctx.save();
      ctx.shadowColor = 'rgba(0,0,0,0.28)';
      ctx.shadowBlur = size * 0.03;
      ctx.shadowOffsetY = size * 0.02;
    }
    ctx.imageSmoothingQuality = 'high';
    ctx.drawImage(item.cutout, dx, dy, dw, dh);
    if (this.shadow) ctx.restore();
  },

  // Repaint every finished card at preview size (settings apply to all).
  render() {
    for (const it of this.items) if (it.status === 'done') this.paintItem(it);
    this.updateDownload();
  },

  fmt() {
    const transparent = !this.bg; // white → JPEG (what marketplaces want), else PNG
    return { transparent, mime: transparent ? 'image/png' : 'image/jpeg', ext: transparent ? 'png' : 'jpg' };
  },

  async renderExportBlob(item) {
    const c = document.createElement('canvas');
    this.paint(c, MARKETS[this.market].size, item);
    const { mime } = this.fmt();
    return new Promise((res) => c.toBlob(res, mime, 0.95));
  },

  saveBlob(blob, name) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = name;
    document.body.appendChild(a); a.click(); URL.revokeObjectURL(url); a.remove();
  },

  async exportOne(item) {
    if (item.status !== 'done') return;
    const m = MARKETS[this.market];
    const { ext } = this.fmt();
    const blob = await this.renderExportBlob(item);
    if (!blob) { Toast.show('Export failed', 'error'); return; }
    const base = item.name.replace(/\.[^.]+$/, '');
    this.saveBlob(blob, `${base}-${m.label.toLowerCase()}-${m.size}.${ext}`);
  },

  async export() {
    const done = this.doneItems();
    if (!done.length) return;
    const m = MARKETS[this.market];
    const { ext } = this.fmt();
    if (done.length === 1) {
      await this.exportOne(done[0]);
      $('#ec-done').innerHTML = `<i class="fa-solid fa-circle-check text-green-500 mr-1"></i>${m.label} photo saved · ${m.size}×${m.size}px`;
      return;
    }
    // Batch → one ZIP.
    $('#ec-done').textContent = 'Zipping…';
    const zip = new JSZip();
    let i = 0;
    for (const it of done) {
      const blob = await this.renderExportBlob(it);
      if (blob) zip.file(`${String(++i).padStart(2, '0')}-${m.label.toLowerCase()}-${m.size}.${ext}`, blob);
    }
    const out = await zip.generateAsync({ type: 'blob' });
    this.saveBlob(out, `${m.label.toLowerCase()}-products-${done.length}.zip`);
    $('#ec-done').innerHTML = `<i class="fa-solid fa-circle-check text-green-500 mr-1"></i>${done.length} ${m.label} photos saved as a ZIP · ${m.size}×${m.size}px`;
  },

  reset() {
    this.editor.classList.add('hidden');
    this.dropzone.parentElement.classList.remove('hidden');
    for (const it of this.items) if (it.cutoutUrl) URL.revokeObjectURL(it.cutoutUrl);
    this.items = [];
    this.fillOverride = null;
    this.grid.innerHTML = '';
    $('#ec-done').textContent = '';
    this.updateButton();
    this.updateDownload();
  },
};

document.addEventListener('DOMContentLoaded', () => App.init());
