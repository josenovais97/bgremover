/**
 * AI image upscaler — 100% client-side.
 *
 * Enlarges an image 2×/4× with a neural super-resolution model (ESRGAN via
 * UpscalerJS + TensorFlow.js), running on the GPU (WebGL) in the browser.
 * Large images are processed in tiles (patchSize) so they don't blow the GPU
 * memory. Nothing is uploaded.
 *
 * Self-contained (own helpers/toast). Only absolute-URL (CDN) ESM imports are
 * used, since Django's static storage doesn't rewrite ES-module import paths.
 * Heavy deps are loaded lazily on first upscale so the page stays light.
 */

/* --------------------------------------------------------------- helpers */
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];

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

// Beyond this many source pixels the run is slow and memory-hungry; we warn and
// still let the user proceed (tiling keeps it from crashing).
const BIG_PIXELS = 1600 * 1600;

/* --------------------------------------------------------------------- app */
const App = {
  file: null,
  source: null,     // HTMLImageElement of the original
  resultUrl: null,
  scale: 2,
  busy: false,
  _upscaler: null,  // lazily-created UpscalerJS instance (2× ESRGAN model)

  init() {
    this.dropzone = $('#up-dropzone');
    this.input = $('#up-input');
    this.editor = $('#up-editor');

    const open = () => this.input.click();
    $('#up-browse').addEventListener('click', (e) => { e.stopPropagation(); open(); });
    this.dropzone.addEventListener('click', open);
    this.dropzone.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); } });
    this.input.addEventListener('change', (e) => this.load(e.target.files[0]));

    const icon = $('#up-icon');
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach((evt) =>
      this.dropzone.addEventListener(evt, (e) => { e.preventDefault(); e.stopPropagation(); }));
    ['dragenter', 'dragover'].forEach((evt) => this.dropzone.addEventListener(evt, () => { this.dropzone.classList.add('border-primary', 'bg-primary/5'); icon.classList.add('scale-110'); }));
    ['dragleave', 'drop'].forEach((evt) => this.dropzone.addEventListener(evt, () => { this.dropzone.classList.remove('border-primary', 'bg-primary/5'); icon.classList.remove('scale-110'); }));
    this.dropzone.addEventListener('drop', (e) => this.load(e.dataTransfer.files[0]));
    document.addEventListener('paste', (e) => {
      const f = [...(e.clipboardData?.items || [])].find((i) => i.kind === 'file');
      if (f) this.load(f.getAsFile());
    });

    $$('.up-scale').forEach((b) => b.addEventListener('click', () => {
      this.scale = +b.dataset.scale;
      $$('.up-scale').forEach((x) => { const a = x === b; x.classList.toggle('border-primary', a); x.classList.toggle('bg-primary/5', a); x.classList.toggle('text-primary', a); });
      this.updateEstimate();
    }));

    $('#up-run').addEventListener('click', () => this.run());
    $('#up-download').addEventListener('click', () => this.download());
    $('#up-new').addEventListener('click', () => this.reset());
  },

  async load(file) {
    this.input.value = '';
    if (!file || !/^image\//.test(file.type)) { Toast.show('Please choose an image', 'error'); return; }
    this.file = file;
    if (this.srcUrl) URL.revokeObjectURL(this.srcUrl);
    this.srcUrl = URL.createObjectURL(file);
    try {
      this.source = await loadImage(this.srcUrl);
    } catch {
      Toast.show('Could not read that image', 'error'); return;
    }
    this.clearResult();
    this.dropzone.parentElement.classList.add('hidden');
    this.editor.classList.remove('hidden');
    $('#up-preview').src = this.srcUrl;
    $('#up-dims-in').textContent = `${this.source.naturalWidth} × ${this.source.naturalHeight}px`;
    this.updateEstimate();
    $('#up-run').disabled = false;
    $('#up-download').classList.add('hidden');
  },

  updateEstimate() {
    if (!this.source) return;
    const w = this.source.naturalWidth * this.scale;
    const h = this.source.naturalHeight * this.scale;
    $('#up-dims-out').textContent = `${w} × ${h}px`;
    const big = this.source.naturalWidth * this.source.naturalHeight > BIG_PIXELS;
    $('#up-warn').classList.toggle('hidden', !big);
  },

  setProgress(pct, label) {
    $('#up-progress-wrap').classList.toggle('hidden', pct == null);
    if (pct != null) $('#up-progress-bar').style.width = `${Math.round(pct)}%`;
    if (label) $('#up-progress-label').textContent = label;
  },

  async ensureUpscaler() {
    if (this._upscaler) return this._upscaler;
    this.setProgress(0, 'Loading the AI model…');
    // Lazy CDN imports — heavy, so only fetched the first time someone upscales.
    const [{ default: Upscaler }, { default: model }] = await Promise.all([
      import('https://cdn.jsdelivr.net/npm/upscaler/+esm'),
      import('https://cdn.jsdelivr.net/npm/@upscalerjs/esrgan-slim/+esm'),
    ]);
    // tfjs is a peer dependency pulled in by upscaler; import it too so the
    // WebGL backend is registered before we run.
    await import('https://cdn.jsdelivr.net/npm/@tensorflow/tfjs/+esm');
    this._upscaler = new Upscaler({ model });
    return this._upscaler;
  },

  /** Upscale `img` by 2× with the model, tiling large inputs. Returns a data URL. */
  async upscale2x(img, onRate) {
    const upscaler = await this.ensureUpscaler();
    return upscaler.upscale(img, {
      output: 'base64',
      patchSize: 64,
      padding: 4,
      progress: (rate) => onRate?.(rate),
    });
  },

  async run() {
    if (!this.source || this.busy) return;
    this.busy = true;
    $('#up-run').disabled = true;
    $('#up-download').classList.add('hidden');
    this.setProgress(0, 'Loading the AI model…');
    try {
      let out;
      if (this.scale === 2) {
        out = await this.upscale2x(this.source, (r) => this.setProgress(r * 100, `Enhancing… ${Math.round(r * 100)}%`));
      } else {
        // 4× = two 2× passes (the model is 2×).
        const mid = await this.upscale2x(this.source, (r) => this.setProgress(r * 50, `Enhancing… pass 1 · ${Math.round(r * 100)}%`));
        const midImg = await loadImage(mid);
        out = await this.upscale2x(midImg, (r) => this.setProgress(50 + r * 50, `Enhancing… pass 2 · ${Math.round(r * 100)}%`));
      }
      this.clearResult();
      this.resultUrl = out; // base64 data URL
      const result = await loadImage(out);
      $('#up-preview').src = out;
      $('#up-dims-out').textContent = `${result.naturalWidth} × ${result.naturalHeight}px`;
      $('#up-badge').classList.remove('hidden');
      $('#up-download').classList.remove('hidden');
      this.setProgress(null);
      Toast.show('Upscaled — compare and download', 'success');
    } catch (err) {
      console.error('[upscaler] failed:', err);
      this.setProgress(null);
      Toast.show('Upscaling failed — try a smaller image', 'error');
    } finally {
      this.busy = false;
      $('#up-run').disabled = false;
    }
  },

  download() {
    if (!this.resultUrl) return;
    const a = document.createElement('a');
    a.href = this.resultUrl;
    const base = (this.file?.name || 'image').replace(/\.[^.]+$/, '');
    a.download = `${base}-upscaled-${this.scale}x.png`;
    document.body.appendChild(a);
    a.click();
    a.remove();
  },

  clearResult() {
    this.resultUrl = null;
    $('#up-badge')?.classList.add('hidden');
  },

  reset() {
    this.editor.classList.add('hidden');
    this.dropzone.parentElement.classList.remove('hidden');
    if (this.srcUrl) { URL.revokeObjectURL(this.srcUrl); this.srcUrl = null; }
    this.source = null; this.file = null;
    this.clearResult();
    this.setProgress(null);
  },
};

document.addEventListener('DOMContentLoaded', () => App.init());
