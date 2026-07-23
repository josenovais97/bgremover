/**
 * Image compressor — 100% client-side.
 *
 * Re-encodes each image with <canvas>.toBlob() at a chosen quality, or binary-
 * searches quality to hit a target file size (e.g. "under 200 KB"). Optionally
 * downscales the longest side. Never produces a file larger than the original —
 * if it can't beat it, the original is kept. Nothing is uploaded.
 *
 * Helpers ($, Toast, loadImage, t, …) come from window.CBG (static/js/kit.js),
 * a classic script — a local ES import would break, since Django's hashed-manifest
 * static storage does not rewrite ES-module import paths.
 */

const { $, Toast, loadImage, humanSize, download, t } = CBG;
import JSZip from 'https://cdn.jsdelivr.net/npm/jszip@3.10.1/+esm';

/* --------------------------------------------------------------- helpers */

const sanitizeName = (name) =>
  name.replace(/\.[^.]+$/, '').replace(/[^\w\-]+/g, '_').slice(0, 60) || 'image';

const extOf = (file) => {
  const t = { 'image/jpeg': 'jpg', 'image/png': 'png', 'image/webp': 'webp', 'image/gif': 'gif', 'image/bmp': 'bmp', 'image/avif': 'avif' }[file.type];
  return t || (file.name.split('.').pop() || 'img').toLowerCase();
};

const toBlob = (canvas, mime, q) => new Promise((res) => canvas.toBlob(res, mime, q));

/* ------------------------------------------------------------ global state */
const target = { mime: 'image/webp', ext: 'webp', mode: 'quality', quality: 0.75, targetKB: 200, maxDim: 0 };
const MIME_LABEL = { 'image/webp': 'WEBP', 'image/jpeg': 'JPG', 'image/png': 'PNG', 'image/avif': 'AVIF' };

/* Find the highest quality whose encoded size fits the byte budget. */
async function encodeToTarget(canvas, mime, targetBytes) {
  let lo = 0.05, hi = 0.96, best = null;
  for (let i = 0; i < 8; i++) {
    const q = (lo + hi) / 2;
    const b = await toBlob(canvas, mime, q);
    if (b && b.type === mime && b.size <= targetBytes) { best = b; lo = q; } else { hi = q; }
  }
  return best || toBlob(canvas, mime, 0.05);
}

/* --------------------------------------------------------------- compress card */
class CompressCard {
  constructor(file) {
    this.file = file;
    this.url = URL.createObjectURL(file);
    this.img = null;
    this.out = null;     // { blob, ext, label }
    this.build();
    this.load();
  }

  build() {
    this.el = $('#cmp-card-template').content.cloneNode(true).querySelector('.card');
    this.el.querySelector('.thumb').src = this.url;
    const name = this.el.querySelector('.filename');
    name.textContent = this.file.name;
    name.title = this.file.name;
    this.el.querySelector('.remove-btn').addEventListener('click', () => this.destroy());
    this.el.querySelector('.download-btn').addEventListener('click', () => this.download());
    $('#cmp-grid').appendChild(this.el);
  }

  async load() {
    try {
      this.img = await loadImage(this.url);
      await this.compress();
    } catch {
      this.el.querySelector('.meta').textContent = "Can't decode this image in the browser.";
      this.disableDownload();
    }
    App.refresh();
  }

  disableDownload() {
    const dl = this.el.querySelector('.download-btn');
    dl.disabled = true;
    dl.classList.add('opacity-50', 'cursor-not-allowed');
  }

  async compress(token) {
    if (!this.img) return;
    const iw = this.img.naturalWidth, ih = this.img.naturalHeight;
    const scale = target.maxDim ? Math.min(1, target.maxDim / Math.max(iw, ih)) : 1;
    const w = Math.max(1, Math.round(iw * scale));
    const h = Math.max(1, Math.round(ih * scale));

    const canvas = document.createElement('canvas');
    canvas.width = w; canvas.height = h;
    const ctx = canvas.getContext('2d');
    if (target.mime === 'image/jpeg') { ctx.fillStyle = '#ffffff'; ctx.fillRect(0, 0, w, h); }
    ctx.drawImage(this.img, 0, 0, w, h);

    let blob;
    if (target.mode === 'size' && target.mime !== 'image/png') {
      blob = await encodeToTarget(canvas, target.mime, target.targetKB * 1024);
    } else {
      const q = target.mime === 'image/png' ? undefined : target.quality;
      blob = await toBlob(canvas, target.mime, q);
    }

    // A newer recompress pass superseded this one while we were encoding — bail
    // before touching the DOM so a stale (slower) result can't win the race.
    if (token != null && token !== App.gen) return;

    // Unsupported encoders (e.g. WEBP on old Safari) silently fall back to PNG.
    if (!blob || blob.type !== target.mime) {
      this.el.querySelector('.meta').textContent = `${MIME_LABEL[target.mime]} isn't supported in this browser — try another format.`;
      this.disableDownload();
      this.out = null;
      return;
    }

    // Never hand back something bigger than what they already have.
    const grew = blob.size >= this.file.size && scale === 1;
    if (grew) {
      this.out = { blob: this.file, ext: extOf(this.file), label: extOf(this.file).toUpperCase() };
    } else {
      this.out = { blob, ext: target.ext, label: MIME_LABEL[target.mime] };
    }

    const saved = 1 - this.out.blob.size / this.file.size;
    const pct = Math.round(saved * 100);
    const dims = scale < 1 ? ` · ${w}×${h}` : '';
    // In target-size mode, flag when we hit the encoder's floor before the goal.
    const missed = target.mode === 'size' && !grew && this.out.blob.size > target.targetKB * 1024 * 1.03;
    this.el.querySelector('.meta').textContent = grew
      ? `Already optimized — ${humanSize(this.file.size)}, can't shrink further`
      : `${humanSize(this.file.size)} → ${humanSize(this.out.blob.size)} · ${pct}% smaller${dims}`
        + (missed ? ' · smallest possible, lower the max dimension for less' : '');

    const bar = this.el.querySelector('.bar');
    bar.style.width = `${Math.max(0, Math.min(100, pct))}%`;
    const badge = this.el.querySelector('.saved-badge');
    badge.textContent = grew ? '0%' : `−${pct}%`;
    badge.classList.toggle('hidden', false);
    badge.classList.toggle('bg-green-500', !grew);
    badge.classList.toggle('bg-gray-400', grew);

    const dl = this.el.querySelector('.download-btn');
    dl.disabled = false;
    dl.classList.remove('opacity-50', 'cursor-not-allowed');
  }

  download() {
    if (!this.out) return;
    CBG.download(this.out.blob, `${sanitizeName(this.file.name)}-min.${this.out.ext}`);
  }

  destroy() {
    URL.revokeObjectURL(this.url);
    this.el.remove();
    App.cards = App.cards.filter((c) => c !== this);
    App.refresh();
  }
}

/* --------------------------------------------------------------------- app */
const App = {
  cards: [],
  gen: 0,

  init() {
    this.dropzone = $('#cmp-dropzone');
    this.input = $('#cmp-input');
    this.controls = $('#cmp-controls');

    const open = () => this.input.click();
    $('#cmp-browse').addEventListener('click', (e) => { e.stopPropagation(); open(); });
    this.dropzone.addEventListener('click', open);
    this.dropzone.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); } });
    this.input.addEventListener('change', (e) => this.add(e.target.files));

    const icon = $('#cmp-icon');
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach((evt) =>
      this.dropzone.addEventListener(evt, (e) => { e.preventDefault(); e.stopPropagation(); }));
    ['dragenter', 'dragover'].forEach((evt) =>
      this.dropzone.addEventListener(evt, () => { this.dropzone.classList.add('border-primary', 'bg-primary/5'); icon.classList.add('scale-110'); }));
    ['dragleave', 'drop'].forEach((evt) =>
      this.dropzone.addEventListener(evt, () => { this.dropzone.classList.remove('border-primary', 'bg-primary/5'); icon.classList.remove('scale-110'); }));
    this.dropzone.addEventListener('drop', (e) => this.add(e.dataTransfer.files));
    document.addEventListener('paste', (e) => {
      const files = [...(e.clipboardData?.items || [])].filter((i) => i.kind === 'file').map((i) => i.getAsFile()).filter(Boolean);
      if (files.length) this.add(files);
    });

    document.querySelectorAll('.cmp-format-btn').forEach((btn) => btn.addEventListener('click', () => this.setFormat(btn)));
    document.querySelectorAll('.cmp-mode-btn').forEach((btn) => btn.addEventListener('click', () => this.setMode(btn)));

    const quality = $('#cmp-quality');
    quality.addEventListener('input', () => { $('#cmp-quality-value').textContent = `${quality.value}%`; });
    quality.addEventListener('change', () => { target.quality = +quality.value / 100; this.recompressAll(); });

    const tgt = $('#cmp-target');
    tgt.addEventListener('change', () => { const v = parseInt(tgt.value, 10); target.targetKB = v > 0 ? v : 200; this.recompressAll(); });

    const maxdim = $('#cmp-maxdim');
    maxdim.addEventListener('change', () => { const v = parseInt(maxdim.value, 10); target.maxDim = v > 0 ? v : 0; this.recompressAll(); });

    $('#cmp-add').addEventListener('click', () => this.input.click());
    $('#cmp-clear').addEventListener('click', () => this.clear());
    $('#cmp-download-all').addEventListener('click', () => this.downloadAll());
  },

  add(fileList) {
    const files = [...fileList].filter((f) => f.type.startsWith('image/') || /\.(png|jpe?g|webp|gif|bmp|avif)$/i.test(f.name));
    this.input.value = '';
    if (!files.length) { Toast.show(t('Please choose image files'), 'error'); return; }
    this.controls.classList.remove('hidden');
    for (const file of files) this.cards.push(new CompressCard(file));
    this.refresh();
  },

  setFormat(btn) {
    target.mime = btn.dataset.format;
    target.ext = btn.dataset.ext;
    document.querySelectorAll('.cmp-format-btn').forEach((b) => {
      const active = b === btn;
      b.classList.toggle('bg-primary', active);
      b.classList.toggle('text-white', active);
    });
    // PNG is lossless: quality/target-size don't apply.
    const isPng = target.mime === 'image/png';
    $('#cmp-quality-wrap').classList.toggle('opacity-40', isPng);
    $('#cmp-quality-wrap').classList.toggle('pointer-events-none', isPng);
    if (isPng && target.mode === 'size') this.setMode(document.querySelector('.cmp-mode-btn[data-mode="quality"]'));
    this.recompressAll();
  },

  setMode(btn) {
    target.mode = btn.dataset.mode;
    document.querySelectorAll('.cmp-mode-btn').forEach((b) => {
      const active = b === btn;
      b.classList.toggle('bg-primary', active);
      b.classList.toggle('text-white', active);
    });
    $('#cmp-quality-wrap').classList.toggle('hidden', target.mode !== 'quality');
    $('#cmp-size-wrap').classList.toggle('hidden', target.mode !== 'size');
    this.recompressAll();
  },

  async recompressAll() {
    const token = ++this.gen;
    for (const c of this.cards) {
      if (token !== this.gen) return;   // a newer pass took over
      await c.compress(token);
    }
    if (token === this.gen) this.refresh();
  },

  refresh() {
    const ready = this.cards.filter((c) => c.out);
    $('#cmp-download-all').classList.toggle('hidden', ready.length < 2);
    if (!this.cards.length) { this.controls.classList.add('hidden'); $('#cmp-summary').textContent = ''; return; }
    const orig = ready.reduce((s, c) => s + c.file.size, 0);
    const now = ready.reduce((s, c) => s + c.out.blob.size, 0);
    if (ready.length && orig > 0) {
      const pct = Math.round((1 - now / orig) * 100);
      $('#cmp-summary').textContent = `${ready.length} image${ready.length > 1 ? 's' : ''} · ${humanSize(orig)} → ${humanSize(now)} · saved ${pct}%`;
    } else {
      $('#cmp-summary').textContent = '';
    }
  },

  clear() {
    [...this.cards].forEach((c) => c.destroy());
    Toast.show(t('Cleared all images'), 'info');
  },

  async downloadAll() {
    const ready = this.cards.filter((c) => c.out);
    if (!ready.length) return;
    Toast.show(t('Building ZIP…'), 'info');
    const zip = new JSZip();
    const used = {};
    for (const card of ready) {
      const base = `${sanitizeName(card.file.name)}-min`;
      let name = `${base}.${card.out.ext}`;
      if (used[name]) name = `${base}-${used[name]++}.${card.out.ext}`;
      else used[name] = 1;
      zip.file(name, card.out.blob);
    }
    const blob = await zip.generateAsync({ type: 'blob' });
    download(blob, 'compressed-images.zip');
  },
};

document.addEventListener('DOMContentLoaded', () => App.init());
