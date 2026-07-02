/**
 * Image format converter — 100% client-side.
 *
 * Detects each uploaded image's format automatically and re-encodes it to the
 * chosen target (PNG / JPG / WEBP) with <canvas>.toBlob(). Nothing is uploaded.
 *
 * This module is intentionally self-contained (its own small helpers/toast)
 * rather than importing shared local modules: Django's hashed-manifest static
 * storage doesn't rewrite ES-module import paths, so cross-file local imports
 * would break in production. CDN imports (absolute URLs) are fine.
 */
import JSZip from 'https://cdn.jsdelivr.net/npm/jszip@3.10.1/+esm';

/* --------------------------------------------------------------- helpers */
const $ = (s, r = document) => r.querySelector(s);

const humanSize = (b) =>
  b < 1024 ? `${b} B` : b < 1048576 ? `${(b / 1024).toFixed(0)} KB` : `${(b / 1048576).toFixed(1)} MB`;

const sanitizeName = (name) =>
  name.replace(/\.[^.]+$/, '').replace(/[^\w\-]+/g, '_').slice(0, 60) || 'image';

const loadImage = (src) =>
  new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = src;
  });

const MIME_LABEL = {
  'image/png': 'PNG', 'image/jpeg': 'JPG', 'image/webp': 'WEBP', 'image/gif': 'GIF',
  'image/bmp': 'BMP', 'image/avif': 'AVIF', 'image/svg+xml': 'SVG', 'image/tiff': 'TIFF',
};

function detectLabel(file) {
  if (file.type && MIME_LABEL[file.type]) return MIME_LABEL[file.type];
  if (file.type) return file.type.split('/')[1].toUpperCase();
  const ext = file.name.split('.').pop();
  return ext ? ext.toUpperCase() : 'IMG';
}

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

/* ------------------------------------------------------------ global state */
const target = { mime: 'image/png', ext: 'png', lossy: false, quality: 0.9 };

/* --------------------------------------------------------------- convert card */
class ConvertCard {
  constructor(file) {
    this.file = file;
    this.url = URL.createObjectURL(file);
    this.blob = null;
    this.img = null;
    this.build();
    this.load();
  }

  build() {
    this.el = $('#convert-card-template').content.cloneNode(true).querySelector('.card');
    this.el.querySelector('.thumb').src = this.url;
    const name = this.el.querySelector('.filename');
    name.textContent = this.file.name;
    name.title = this.file.name;
    this.el.querySelector('.from-badge').textContent = detectLabel(this.file);
    this.el.querySelector('.remove-btn').addEventListener('click', () => this.destroy());
    this.el.querySelector('.download-btn').addEventListener('click', () => this.download());
    $('#convert-grid').appendChild(this.el);
  }

  async load() {
    try {
      this.img = await loadImage(this.url);
      await this.reconvert();
    } catch {
      this.el.querySelector('.meta').textContent = "Can't decode this format in the browser.";
      this.el.querySelector('.download-btn').disabled = true;
      this.el.querySelector('.download-btn').classList.add('opacity-50', 'cursor-not-allowed');
    }
  }

  async reconvert() {
    if (!this.img) return;
    const canvas = document.createElement('canvas');
    canvas.width = this.img.naturalWidth;
    canvas.height = this.img.naturalHeight;
    const ctx = canvas.getContext('2d');
    if (target.mime === 'image/jpeg') { // JPG has no alpha
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
    }
    ctx.drawImage(this.img, 0, 0);

    this.blob = await new Promise((res) =>
      canvas.toBlob(res, target.mime, target.lossy ? target.quality : undefined),
    );
    this.ext = target.ext;
    this.el.querySelector('.to-badge').textContent = MIME_LABEL[target.mime];
    this.el.querySelector('.dl-label').textContent = MIME_LABEL[target.mime];
    this.el.querySelector('.meta').textContent =
      `${detectLabel(this.file)} ${humanSize(this.file.size)} → ${MIME_LABEL[target.mime]} ${humanSize(this.blob.size)}`;
  }

  download() {
    if (!this.blob) return;
    const url = URL.createObjectURL(this.blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${sanitizeName(this.file.name)}.${this.ext}`;
    document.body.appendChild(a);
    a.click();
    URL.revokeObjectURL(url);
    a.remove();
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

  init() {
    this.dropzone = $('#convert-dropzone');
    this.input = $('#convert-input');
    this.controls = $('#convert-controls');

    const open = () => this.input.click();
    $('#convert-browse').addEventListener('click', (e) => { e.stopPropagation(); open(); });
    this.dropzone.addEventListener('click', open);
    this.dropzone.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); } });
    this.input.addEventListener('change', (e) => this.add(e.target.files));

    const icon = $('#convert-icon');
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

    // Target format buttons
    document.querySelectorAll('.convert-format-btn').forEach((btn) =>
      btn.addEventListener('click', () => this.setFormat(btn)));

    // Quality
    const quality = $('#convert-quality');
    quality.addEventListener('input', () => { $('#quality-value').textContent = `${quality.value}%`; });
    quality.addEventListener('change', () => { target.quality = +quality.value / 100; this.reconvertAll(); });

    $('#convert-add').addEventListener('click', () => this.input.click());
    $('#convert-clear').addEventListener('click', () => this.clear());
    $('#convert-download-all').addEventListener('click', () => this.downloadAll());

    this.updateQualityVisibility();
  },

  add(fileList) {
    const files = [...fileList].filter((f) => f.type.startsWith('image/') || /\.(png|jpe?g|webp|gif|bmp|avif|tiff?)$/i.test(f.name));
    this.input.value = '';
    if (!files.length) { Toast.show('Please choose image files', 'error'); return; }
    this.controls.classList.remove('hidden');
    for (const file of files) this.cards.push(new ConvertCard(file));
    this.refresh();
  },

  setFormat(btn) {
    target.mime = btn.dataset.format;
    target.ext = btn.dataset.ext;
    target.lossy = btn.dataset.lossy === '1';
    document.querySelectorAll('.convert-format-btn').forEach((b) => {
      const active = b === btn;
      b.classList.toggle('bg-primary', active);
      b.classList.toggle('text-white', active);
    });
    this.updateQualityVisibility();
    this.reconvertAll();
  },

  updateQualityVisibility() {
    $('#quality-wrap').classList.toggle('invisible', !target.lossy);
  },

  reconvertAll() {
    this.cards.forEach((c) => c.reconvert());
  },

  refresh() {
    $('#convert-download-all').classList.toggle('hidden', this.cards.length < 2);
    if (!this.cards.length) this.controls.classList.add('hidden');
  },

  clear() {
    [...this.cards].forEach((c) => c.destroy());
    Toast.show('Cleared all images', 'info');
  },

  async downloadAll() {
    const ready = this.cards.filter((c) => c.blob);
    if (!ready.length) return;
    Toast.show('Building ZIP…', 'info');
    const zip = new JSZip();
    const used = {};
    for (const card of ready) {
      const base = sanitizeName(card.file.name);
      let name = `${base}.${card.ext}`;
      if (used[name]) name = `${base}-${used[name]++}.${card.ext}`;
      else used[name] = 1;
      zip.file(name, card.blob);
    }
    const blob = await zip.generateAsync({ type: 'blob' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'converted-images.zip';
    document.body.appendChild(a);
    a.click();
    URL.revokeObjectURL(url);
    a.remove();
  },
};

document.addEventListener('DOMContentLoaded', () => App.init());
