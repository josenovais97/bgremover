import { takeHandoff } from './handoff.js';

/**
 * WhatsApp / Telegram sticker maker — 100% client-side.
 *
 * Removes the background from a photo (lazy-loaded @imgly model), stamps the
 * classic sticker outline around the cut-out, lets you drag a caption on top,
 * and exports a ready-to-use 512×512 transparent WebP (kept under WhatsApp's
 * 100KB limit) or a PNG. Nothing is uploaded.
 *
 * Self-contained (own helpers/toast) — only absolute-URL (CDN) imports are used,
 * since Django's static storage doesn't rewrite ES-module import paths.
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

function rafThrottle(fn) {
  let scheduled = false;
  return () => { if (scheduled) return; scheduled = true; requestAnimationFrame(() => { scheduled = false; fn(); }); };
}

/** Recolour a sprite to a solid tint, keeping its alpha (for the outline). */
function tintCanvas(src, color) {
  const c = document.createElement('canvas');
  c.width = src.width; c.height = src.height;
  const x = c.getContext('2d');
  x.drawImage(src, 0, 0);
  x.globalCompositeOperation = 'source-in';
  x.fillStyle = color;
  x.fillRect(0, 0, c.width, c.height);
  return c;
}

const SIZE = 512;
const MODEL_CDN = 'https://cdn.jsdelivr.net/npm/@imgly/background-removal@1.6.0/+esm';

/* --------------------------------------------------------------------- app */
const App = {
  cutout: null,
  outline: { on: true, color: '#ffffff', width: 3.5 }, // width = % of the 512 frame
  text: { content: '', font: 'Anton', color: '#ffffff', size: 12, x: 0.5, y: 0.84 },
  _textBox: null,

  init() {
    this.dropzone = $('#stk-dropzone');
    this.input = $('#stk-input');
    this.editor = $('#stk-editor');
    this.canvas = $('#stk-canvas');

    const open = () => this.input.click();
    $('#stk-browse').addEventListener('click', (e) => { e.stopPropagation(); open(); });
    this.dropzone.addEventListener('click', open);
    this.dropzone.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); } });
    this.input.addEventListener('change', (e) => this.load(e.target.files[0]));

    const icon = $('#stk-icon');
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach((evt) =>
      this.dropzone.addEventListener(evt, (e) => { e.preventDefault(); e.stopPropagation(); }));
    ['dragenter', 'dragover'].forEach((evt) => this.dropzone.addEventListener(evt, () => { this.dropzone.classList.add('border-primary', 'bg-primary/5'); icon.classList.add('scale-110'); }));
    ['dragleave', 'drop'].forEach((evt) => this.dropzone.addEventListener(evt, () => { this.dropzone.classList.remove('border-primary', 'bg-primary/5'); icon.classList.remove('scale-110'); }));
    this.dropzone.addEventListener('drop', (e) => this.load(e.dataTransfer.files[0]));
    document.addEventListener('paste', (e) => {
      const f = [...(e.clipboardData?.items || [])].find((i) => i.kind === 'file');
      if (f) this.load(f.getAsFile());
    });

    const render = rafThrottle(() => this.render());

    // Outline controls.
    $('#stk-outline-on').addEventListener('change', (e) => {
      this.outline.on = e.target.checked;
      $('#stk-outline-opts').classList.toggle('opacity-40', !this.outline.on);
      $('#stk-outline-opts').classList.toggle('pointer-events-none', !this.outline.on);
      this.render();
    });
    $('#stk-outline-color').addEventListener('input', (e) => { this.outline.color = e.target.value; render(); });
    $('#stk-outline-width').addEventListener('input', (e) => { this.outline.width = +e.target.value; render(); });

    // Text controls.
    $('#stk-text').addEventListener('input', (e) => { this.text.content = e.target.value; this.render(); });
    $$('.stk-font').forEach((b) => b.addEventListener('click', () => {
      this.text.font = b.dataset.font;
      $$('.stk-font').forEach((x) => { const a = x === b; x.classList.toggle('ring-2', a); x.classList.toggle('ring-primary', a); });
      this.ensureFont();
      this.render();
    }));
    $('#stk-text-color').addEventListener('input', (e) => { this.text.color = e.target.value; render(); });
    $('#stk-text-size').addEventListener('input', (e) => { this.text.size = +e.target.value; this.render(); });

    // Drag the caption on the sticker.
    this.canvas.addEventListener('pointerdown', (e) => {
      if (!this.hitText(e)) return;
      this.canvas.setPointerCapture?.(e.pointerId);
      this.drag = { x: e.clientX, y: e.clientY };
    });
    this.canvas.addEventListener('pointermove', (e) => this.onDrag(e));
    ['pointerup', 'pointercancel', 'pointerleave'].forEach((ev) => this.canvas.addEventListener(ev, () => { this.drag = null; }));

    $('#stk-download').addEventListener('click', () => this.export('image/webp'));
    $('#stk-download-png').addEventListener('click', () => this.export('image/png'));
    $('#stk-new').addEventListener('click', () => this.reset());

    this.setBusy(false);
  },

  setBusy(busy, text) {
    $('#stk-status').classList.toggle('hidden', !busy);
    if (text) $('#stk-status-text').textContent = text;
    $('#stk-download').disabled = busy || !this.cutout;
    $('#stk-download-png').disabled = busy || !this.cutout;
  },

  async load(file) {
    this.input.value = '';
    if (!file || !/^image\//.test(file.type)) { Toast.show('Please choose an image', 'error'); return; }
    this.cutout = null;
    this.dropzone.parentElement.classList.add('hidden');
    this.editor.classList.remove('hidden');
    this.setBusy(true, 'Removing background…');
    this.render();
    try {
      const { removeBackground } = await import(MODEL_CDN);
      // Full 'isnet' when the page is cross-origin isolated (threaded WASM);
      // quantized fallback otherwise. See config/middleware.py ISOLATED_VIEWS.
      const blob = await removeBackground(file, { model: self.crossOriginIsolated ? 'isnet' : 'isnet_quint8' });
      if (this.cutoutUrl) URL.revokeObjectURL(this.cutoutUrl);
      this.cutoutUrl = URL.createObjectURL(blob);
      this.cutout = await loadImage(this.cutoutUrl);
      this.setBusy(false);
      this.ensureFont();
      this.render();
      window.__clearbgReport?.(1);
      Toast.show('Background removed — add your outline & text', 'success');
    } catch (err) {
      console.error('[sticker] bg removal failed:', err);
      Toast.show('Background removal failed', 'error');
      this.setBusy(false);
    }
  },

  ensureFont() {
    if (!document.fonts || !document.fonts.load) return;
    document.fonts.load(`700 40px ${this.text.font}`).then(() => this.render()).catch(() => {});
  },

  /* ------------------------------------------------------------ drawing */
  outlinePx(size) { return this.outline.on ? (this.outline.width / 100) * size : 0; },

  /** Composite the sticker (cut-out + outline + text) into `canvas` at `size`. */
  paint(canvas, size) {
    canvas.width = size; canvas.height = size;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, size, size);
    if (!this.cutout) return;

    const margin = size * 0.06; // transparent margin WhatsApp expects
    const ow = this.outlinePx(size);
    const box = size - 2 * margin - 2 * ow;
    const cw = this.cutout.naturalWidth || this.cutout.width;
    const ch = this.cutout.naturalHeight || this.cutout.height;
    const scale = Math.min(box / cw, box / ch);
    const dw = cw * scale;
    const dh = ch * scale;
    const dx = (size - dw) / 2;
    const dy = (size - dh) / 2;

    // Scaled sprite of the cut-out (outline is stamped from its silhouette).
    const sprite = document.createElement('canvas');
    sprite.width = Math.max(1, Math.round(dw));
    sprite.height = Math.max(1, Math.round(dh));
    sprite.getContext('2d').drawImage(this.cutout, 0, 0, sprite.width, sprite.height);

    if (ow > 0) {
      const sil = tintCanvas(sprite, this.outline.color);
      const steps = 48;
      for (let i = 0; i < steps; i++) {
        const a = (i / steps) * Math.PI * 2;
        ctx.drawImage(sil, dx + Math.cos(a) * ow, dy + Math.sin(a) * ow);
      }
    }
    ctx.drawImage(sprite, dx, dy);
    this.drawText(ctx, size);
  },

  drawText(ctx, size) {
    const t = this.text;
    if (!t.content.trim()) { this._textBox = null; return; }
    const lines = t.content.replace(/\r/g, '').split('\n');
    const fs = (t.size / 100) * size;
    const lh = fs * 1.15;
    const cx = t.x * size;
    const cy = t.y * size;
    const blockH = lh * lines.length;

    ctx.save();
    ctx.font = `700 ${fs}px ${t.font}, sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    let maxW = 0;
    lines.forEach((l) => { maxW = Math.max(maxW, ctx.measureText(l || ' ').width); });
    this._textBox = { x: cx - maxW / 2 - fs * 0.2, y: cy - blockH / 2 - fs * 0.1, w: maxW + fs * 0.4, h: blockH + fs * 0.2 };

    // Black outline around the letters so any colour reads on any sticker.
    ctx.lineJoin = 'round';
    ctx.strokeStyle = 'rgba(0,0,0,0.85)';
    ctx.lineWidth = fs * 0.18;
    lines.forEach((l, i) => ctx.strokeText(l, cx, cy - blockH / 2 + lh * (i + 0.5)));
    ctx.fillStyle = t.color;
    lines.forEach((l, i) => ctx.fillText(l, cx, cy - blockH / 2 + lh * (i + 0.5)));
    ctx.restore();
  },

  pointerPixel(e) {
    const r = this.canvas.getBoundingClientRect();
    return { px: (e.clientX - r.left) * (this.canvas.width / r.width), py: (e.clientY - r.top) * (this.canvas.height / r.height) };
  },

  hitText(e) {
    const b = this._textBox;
    if (!b) return false;
    const { px, py } = this.pointerPixel(e);
    return px >= b.x && px <= b.x + b.w && py >= b.y && py <= b.y + b.h;
  },

  onDrag(e) {
    if (!this.drag) return;
    const r = this.canvas.getBoundingClientRect();
    const dx = (e.clientX - this.drag.x) * (this.canvas.width / r.width);
    const dy = (e.clientY - this.drag.y) * (this.canvas.height / r.height);
    this.text.x = clamp(this.text.x + dx / this.canvas.width, 0, 1);
    this.text.y = clamp(this.text.y + dy / this.canvas.height, 0, 1);
    this.drag = { x: e.clientX, y: e.clientY };
    this.render();
  },

  render() {
    this.paint(this.canvas, SIZE);
  },

  /* ------------------------------------------------------------- export */
  async export(fmt) {
    if (!this.cutout) return;
    const c = document.createElement('canvas');
    this.paint(c, SIZE);
    const isWebp = fmt === 'image/webp';
    let quality = 0.92;
    let blob = await new Promise((res) => c.toBlob(res, fmt, quality));
    // WhatsApp caps stickers at 100KB — step quality down for WebP until it fits.
    if (isWebp) {
      while (blob && blob.size > 100 * 1024 && quality > 0.4) {
        quality -= 0.12;
        blob = await new Promise((res) => c.toBlob(res, fmt, quality));
      }
    }
    if (!blob) { Toast.show('Export failed', 'error'); return; }
    // Some browsers can't encode WebP — fall back to PNG rather than mislabel it.
    if (isWebp && blob.type !== 'image/webp') {
      Toast.show('WebP not supported here — downloading PNG instead', 'info');
      return this.export('image/png');
    }
    const ext = isWebp ? 'webp' : 'png';
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `sticker.${ext}`;
    document.body.appendChild(a);
    a.click();
    URL.revokeObjectURL(url);
    a.remove();
    const kb = Math.round(blob.size / 1024);
    $('#stk-size-note').innerHTML = `<i class="fa-solid fa-circle-check text-green-500 mr-1"></i>Saved ${ext.toUpperCase()} · ${kb} KB${isWebp && kb <= 100 ? ' · WhatsApp ready' : ''}`;
  },

  reset() {
    this.editor.classList.add('hidden');
    this.dropzone.parentElement.classList.remove('hidden');
    if (this.cutoutUrl) { URL.revokeObjectURL(this.cutoutUrl); this.cutoutUrl = null; }
    this.cutout = null;
    this.text.content = '';
    $('#stk-text').value = '';
  },
};

document.addEventListener('DOMContentLoaded', () => {
  App.init();
  // If we arrived via "Continue in Sticker" from another tool, load that image.
  takeHandoff().then((file) => { if (file) App.load(file); });
});
