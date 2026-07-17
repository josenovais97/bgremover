/**
 * Image resizer — 100% client-side.
 *
 * Resize to exact pixels or a percentage with the aspect ratio optionally
 * locked, then export JPG / PNG / WEBP. The resize is a single high-quality
 * canvas draw at the target size. Nothing is uploaded.
 */
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const clampInt = (v) => Math.max(1, Math.round(v || 0));

const loadImage = (src) => new Promise((resolve, reject) => {
  const img = new Image(); img.onload = () => resolve(img); img.onerror = reject; img.src = src;
});

const Toast = {
  show(message, type = 'success') {
    const c = $('#toast-container');
    if (!c) return;
    const map = {
      success: ['bg-green-50 dark:bg-green-900/40 text-green-800 dark:text-green-200 border-green-200 dark:border-green-800', 'fa-circle-check text-green-500'],
      error: ['bg-red-50 dark:bg-red-900/40 text-red-800 dark:text-red-200 border-red-200 dark:border-red-800', 'fa-circle-exclamation text-red-500'],
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

const App = {
  img: null,
  ow: 0, oh: 0,          // original dimensions
  w: 0, h: 0,            // target dimensions
  lock: true,
  fmt: '',              // '' = keep original format

  init() {
    this.dropzone = $('#rs-dropzone');
    // See watermark.js: closest('section') survives the demo-wrapper grid.
    this.hero = this.dropzone.closest('section');
    this.input = $('#rs-input');
    this.editor = $('#rs-editor');

    const open = () => this.input.click();
    $('#rs-browse').addEventListener('click', (e) => { e.stopPropagation(); open(); });
    this.dropzone.addEventListener('click', open);
    this.dropzone.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); } });
    this.input.addEventListener('change', (e) => this.load(e.target.files[0]));

    const icon = $('#rs-icon');
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach((evt) =>
      this.dropzone.addEventListener(evt, (e) => { e.preventDefault(); e.stopPropagation(); }));
    ['dragenter', 'dragover'].forEach((evt) => this.dropzone.addEventListener(evt, () => { this.dropzone.classList.add('border-primary', 'bg-primary/5'); icon.classList.add('scale-110'); }));
    ['dragleave', 'drop'].forEach((evt) => this.dropzone.addEventListener(evt, () => { this.dropzone.classList.remove('border-primary', 'bg-primary/5'); icon.classList.remove('scale-110'); }));
    this.dropzone.addEventListener('drop', (e) => this.load(e.dataTransfer.files[0]));
    document.addEventListener('paste', (e) => {
      const f = [...(e.clipboardData?.items || [])].find((i) => i.kind === 'file');
      if (f) this.load(f.getAsFile());
    });

    $('#rs-w').addEventListener('input', (e) => this.setW(+e.target.value));
    $('#rs-h').addEventListener('input', (e) => this.setH(+e.target.value));
    $('#rs-lock').addEventListener('change', (e) => { this.lock = e.target.checked; });
    $$('.rs-pct').forEach((b) => b.addEventListener('click', () => this.setScale(+b.dataset.pct / 100)));
    $$('.rs-preset').forEach((b) => b.addEventListener('click', () => this.fitWithin(+b.dataset.max)));
    $$('.rs-fmt-btn').forEach((b) => b.addEventListener('click', () => {
      this.fmt = b.dataset.fmt;
      $$('.rs-fmt-btn').forEach((x) => { const a = x === b; x.classList.toggle('ring-2', a); x.classList.toggle('ring-primary', a); });
    }));
    $('#rs-download').addEventListener('click', () => this.download());
    $('#rs-new').addEventListener('click', () => this.reset());
  },

  aspect() { return this.ow / this.oh; },

  setW(v) {
    this.w = clampInt(v);
    if (this.lock) this.h = clampInt(this.w / this.aspect());
    this.syncInputs();
  },
  setH(v) {
    this.h = clampInt(v);
    if (this.lock) this.w = clampInt(this.h * this.aspect());
    this.syncInputs();
  },
  setScale(f) { this.w = clampInt(this.ow * f); this.h = clampInt(this.oh * f); this.syncInputs(); },
  fitWithin(max) {
    const s = Math.min(1, max / Math.max(this.ow, this.oh));
    this.w = clampInt(this.ow * s); this.h = clampInt(this.oh * s); this.syncInputs();
  },

  syncInputs() {
    $('#rs-w').value = this.w;
    $('#rs-h').value = this.h;
    const pct = Math.round((this.w / this.ow) * 100);
    $('#rs-dims').textContent = `${this.ow} × ${this.oh}  →  ${this.w} × ${this.h} px (${pct}%)`;
  },

  async load(file) {
    this.input.value = '';
    if (!file || !/^image\//.test(file.type)) { Toast.show('Please choose an image', 'error'); return; }
    this.file = file;
    if (this.url) URL.revokeObjectURL(this.url);
    this.url = URL.createObjectURL(file);
    try { this.img = await loadImage(this.url); } catch { Toast.show('Could not read that image', 'error'); return; }
    this.ow = this.img.naturalWidth; this.oh = this.img.naturalHeight;
    this.w = this.ow; this.h = this.oh;
    $('#rs-preview').src = this.url;
    this.syncInputs();
    this.hero.classList.add('hidden');
    this.editor.classList.remove('hidden');
  },

  async download() {
    if (!this.img) return;
    const c = document.createElement('canvas');
    c.width = this.w; c.height = this.h;
    const ctx = c.getContext('2d');
    ctx.imageSmoothingQuality = 'high';
    ctx.drawImage(this.img, 0, 0, this.w, this.h);
    const type = this.fmt || (this.file.type === 'image/jpeg' ? 'image/jpeg' : this.file.type === 'image/webp' ? 'image/webp' : 'image/png');
    const ext = type === 'image/jpeg' ? 'jpg' : type === 'image/webp' ? 'webp' : 'png';
    const blob = await new Promise((res) => c.toBlob(res, type, 0.95));
    if (!blob) { Toast.show('Export failed', 'error'); return; }
    const base = this.file.name.replace(/\.[^.]+$/, '');
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = `${base}-${this.w}x${this.h}.${ext}`;
    document.body.appendChild(a); a.click(); URL.revokeObjectURL(url); a.remove();
    $('#rs-dims').innerHTML = `<i class="fa-solid fa-circle-check text-green-500 mr-1"></i>Saved ${this.w} × ${this.h}px · ${Math.round(blob.size / 1024)} KB`;
  },

  reset() {
    this.editor.classList.add('hidden');
    this.hero.classList.remove('hidden');
    if (this.url) { URL.revokeObjectURL(this.url); this.url = null; }
    this.img = null;
  },
};

document.addEventListener('DOMContentLoaded', () => App.init());
