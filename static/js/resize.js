/**
 * Image resizer — 100% client-side.
 *
 * Resize to exact pixels or a percentage with the aspect ratio optionally
 * locked, then export JPG / PNG / WEBP. The resize is a single high-quality
 * canvas draw at the target size. Nothing is uploaded.
 *
 * Batch: the first file is the one you see and tune; any others are queued and
 * exported with the same settings as a ZIP. Because a batch mixes aspect ratios,
 * queued images are FITTED INSIDE the target box rather than forced to its exact
 * dimensions — same rule as "fit within", and nothing is ever distorted.
 *
 * Shared helpers come from window.CBG (static/js/kit.js).
 */
const { $, $$, Toast, loadImage, dropzone, zipDownload, remember, baseName } = window.CBG;

const clampInt = (v) => Math.max(1, Math.round(v || 0));
const prefs = remember('resize');

const App = {
  img: null,
  ow: 0, oh: 0,          // original dimensions
  w: 0, h: 0,            // target dimensions
  lock: true,
  fmt: '',               // '' = keep original format
  queue: [],             // extra files exported with the same settings

  init() {
    this.dropzone = $('#rs-dropzone');
    // See watermark.js: closest('section') survives the demo-wrapper grid.
    this.hero = this.dropzone.closest('section');
    this.input = $('#rs-input');
    this.editor = $('#rs-editor');
    this.batch = $('[data-batch]');

    dropzone(this.dropzone, {
      input: this.input,
      icon: $('#rs-icon'),
      browse: $('#rs-browse'),
      onFiles: (files) => this.load(files),
    });

    $('#rs-w').addEventListener('input', (e) => this.setW(+e.target.value));
    $('#rs-h').addEventListener('input', (e) => this.setH(+e.target.value));
    $('#rs-lock').addEventListener('change', (e) => { this.lock = e.target.checked; });
    $$('.rs-pct').forEach((b) => b.addEventListener('click', () => this.setScale(+b.dataset.pct / 100)));
    $$('.rs-preset').forEach((b) => b.addEventListener('click', () => this.fitWithin(+b.dataset.max)));
    $$('.rs-fmt-btn').forEach((b) => b.addEventListener('click', () => this.setFormat(b.dataset.fmt)));
    $('#rs-download').addEventListener('click', () => this.download());
    $('#rs-new').addEventListener('click', () => this.reset());
    $('[data-batch-zip]').addEventListener('click', () => this.downloadAll());

    // The output format is a preference, not a per-photo decision.
    const saved = prefs.get();
    if (saved.fmt !== undefined) this.setFormat(saved.fmt);
  },

  aspect() { return this.ow / this.oh; },

  setFormat(fmt) {
    this.fmt = fmt;
    $$('.rs-fmt-btn').forEach((x) => {
      const a = x.dataset.fmt === fmt;
      x.classList.toggle('ring-2', a);
      x.classList.toggle('ring-primary', a);
    });
    prefs.set({ fmt });
  },

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

  async load(files) {
    const [first, ...rest] = files;
    this.file = first;
    this.queue = rest;
    if (this.url) URL.revokeObjectURL(this.url);
    this.url = URL.createObjectURL(first);
    try { this.img = await loadImage(this.url); } catch { Toast.show('Could not read that image', 'error'); return; }
    this.ow = this.img.naturalWidth; this.oh = this.img.naturalHeight;
    this.w = this.ow; this.h = this.oh;
    $('#rs-preview').src = this.url;
    this.syncInputs();
    this.hero.classList.add('hidden');
    this.editor.classList.remove('hidden');
    this.syncBatch();
  },

  syncBatch() {
    const n = this.queue.length + 1;
    this.batch.classList.toggle('hidden', n < 2);
    this.batch.querySelector('[data-batch-count]').textContent = n;
  },

  /** Target type + extension for a source file, honouring the format choice. */
  typeFor(file) {
    const type = this.fmt
      || (file.type === 'image/jpeg' ? 'image/jpeg' : file.type === 'image/webp' ? 'image/webp' : 'image/png');
    return { type, ext: type === 'image/jpeg' ? 'jpg' : type === 'image/webp' ? 'webp' : 'png' };
  },

  /** Resize one image and return {name, blob}. `exact` forces this.w × this.h. */
  async resizeFile(file, exact) {
    const url = URL.createObjectURL(file);
    try {
      const img = await loadImage(url);
      const iw = img.naturalWidth;
      const ih = img.naturalHeight;
      // Queued images keep their own aspect: fit inside the target box.
      const s = exact ? 1 : Math.min(this.w / iw, this.h / ih);
      const w = exact ? this.w : Math.max(1, Math.round(iw * s));
      const h = exact ? this.h : Math.max(1, Math.round(ih * s));
      const c = document.createElement('canvas');
      c.width = w; c.height = h;
      const ctx = c.getContext('2d');
      ctx.imageSmoothingQuality = 'high';
      const { type, ext } = this.typeFor(file);
      if (type === 'image/jpeg') { ctx.fillStyle = '#ffffff'; ctx.fillRect(0, 0, w, h); }
      ctx.drawImage(img, 0, 0, w, h);
      const blob = await new Promise((res) => c.toBlob(res, type, 0.95));
      return blob ? { name: `${baseName(file.name)}-${w}x${h}.${ext}`, blob } : null;
    } finally {
      URL.revokeObjectURL(url);
    }
  },

  async download() {
    if (!this.img) return;
    const out = await this.resizeFile(this.file, true);
    if (!out) { Toast.show('Export failed', 'error'); return; }
    window.CBG.download(out.blob, out.name);
    $('#rs-dims').innerHTML = `<i class="fa-solid fa-circle-check text-green-500 mr-1"></i>Saved ${this.w} × ${this.h}px · ${Math.round(out.blob.size / 1024)} KB`;
  },

  async downloadAll() {
    const btn = $('[data-batch-zip]');
    const label = btn.querySelector('[data-batch-label]');
    const original = label.textContent;
    btn.disabled = true;
    label.textContent = 'Resizing…';
    try {
      const entries = [await this.resizeFile(this.file, true)];
      for (const f of this.queue) entries.push(await this.resizeFile(f, false));
      await zipDownload(entries.filter(Boolean), 'clearbg-resized.zip');
    } catch {
      Toast.show('Could not build the ZIP', 'error');
    } finally {
      btn.disabled = false;
      label.textContent = original;
    }
  },

  reset() {
    this.editor.classList.add('hidden');
    this.hero.classList.remove('hidden');
    if (this.url) { URL.revokeObjectURL(this.url); this.url = null; }
    this.img = null;
    this.queue = [];
    this.syncBatch();
  },
};

document.addEventListener('DOMContentLoaded', () => App.init());
