/**
 * AI background blur (portrait mode) — 100% client-side.
 *
 * Uses the background-removal mask to keep the subject perfectly sharp while
 * blurring the rest of the photo, for a phone-style "portrait mode" depth
 * effect. The cut-out is the original image with its background removed, so it
 * lines up 1:1 with the original — we draw the blurred original, then the sharp
 * subject on top. Nothing is uploaded.
 *
 * Helpers ($, Toast, loadImage, t, …) come from window.CBG (static/js/kit.js),
 * a classic script — a local ES import would break, since Django's hashed-manifest
 * static storage does not rewrite ES-module import paths.
 */

const { $, Toast, loadImage, download, t } = CBG;
import { removeBackground } from 'https://cdn.jsdelivr.net/npm/@imgly/background-removal@1.6.0/+esm';

/* --------------------------------------------------------------- helpers */
const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));

function rafThrottle(fn) {
  let scheduled = false;
  return () => { if (scheduled) return; scheduled = true; requestAnimationFrame(() => { scheduled = false; fn(); }); };
}

/* --------------------------------------------------------------------- app */
const App = {
  original: null,   // HTMLImageElement of the source photo
  cutout: null,     // subject with background removed (same dimensions)
  amount: 14,       // blur radius as % of a 1000px reference

  init() {
    this.dropzone = $('#bl-dropzone');
    this.input = $('#bl-input');
    this.editor = $('#bl-editor');
    this.canvas = $('#bl-canvas');

    const open = () => this.input.click();
    $('#bl-browse').addEventListener('click', (e) => { e.stopPropagation(); open(); });
    this.dropzone.addEventListener('click', open);
    this.dropzone.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); } });
    this.input.addEventListener('change', (e) => this.load(e.target.files[0]));

    const icon = $('#bl-icon');
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
    $('#bl-amount').addEventListener('input', (e) => { this.amount = +e.target.value; render(); });
    $('#bl-download').addEventListener('click', () => this.export('image/jpeg'));
    $('#bl-download-png').addEventListener('click', () => this.export('image/png'));
    $('#bl-new').addEventListener('click', () => this.reset());

    this.setBusy(false);
  },

  setBusy(busy, text) {
    $('#bl-status').classList.toggle('hidden', !busy);
    if (text) $('#bl-status-text').textContent = text;
    $('#bl-download').disabled = busy || !this.cutout;
    $('#bl-download-png').disabled = busy || !this.cutout;
  },

  async load(file) {
    this.input.value = '';
    if (!file || !/^image\//.test(file.type)) { Toast.show(t('Please choose an image'), 'error'); return; }
    this.cutout = null;
    if (this.srcUrl) URL.revokeObjectURL(this.srcUrl);
    this.srcUrl = URL.createObjectURL(file);
    try {
      this.original = await loadImage(this.srcUrl);
    } catch {
      Toast.show(t('Could not read that image'), 'error'); return;
    }
    this.dropzone.parentElement.classList.add('hidden');
    this.editor.classList.remove('hidden');
    this.setBusy(true, 'Finding the subject…');
    this.render();
    try {
      const blob = await removeBackground(file, { model: self.crossOriginIsolated ? 'isnet' : 'isnet_quint8' });
      if (this.cutoutUrl) URL.revokeObjectURL(this.cutoutUrl);
      this.cutoutUrl = URL.createObjectURL(blob);
      this.cutout = await loadImage(this.cutoutUrl);
      window.__clearbgReport?.(1);
      this.setBusy(false);
      this.render();
      Toast.show(t('Portrait blur applied — adjust the strength'), 'success');
    } catch (err) {
      console.error('[blur] bg removal failed:', err);
      Toast.show(t('Could not find the subject'), 'error');
      this.setBusy(false);
    }
  },

  /** Blur radius in px for a given image width (scaled from the % reference). */
  radiusFor(w) {
    return Math.max(1, (this.amount / 100) * w * 0.6);
  },

  /** Paint blurred background + sharp subject into `canvas` at native size. */
  paint(canvas) {
    const w = this.original.naturalWidth, h = this.original.naturalHeight;
    canvas.width = w; canvas.height = h;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, w, h);
    // Blurred original underneath.
    ctx.save();
    ctx.filter = `blur(${this.radiusFor(w)}px)`;
    // Draw slightly overscaled so the blur doesn't reveal transparent edges.
    const pad = this.radiusFor(w);
    ctx.drawImage(this.original, -pad, -pad, w + pad * 2, h + pad * 2);
    ctx.restore();
    // Sharp subject on top (only where the cut-out has alpha).
    if (this.cutout) ctx.drawImage(this.cutout, 0, 0, w, h);
  },

  render() {
    if (!this.original) return;
    this.paint(this.canvas);
  },

  async export(fmt) {
    if (!this.cutout) return;
    const c = document.createElement('canvas');
    this.paint(c);
    const ext = fmt === 'image/png' ? 'png' : 'jpg';
    const blob = await new Promise((res) => c.toBlob(res, fmt, 0.95));
    if (!blob) { Toast.show(t('Export failed'), 'error'); return; }
    download(blob, `portrait-blur.${ext}`);
    $('#bl-done').innerHTML = `<i class="fa-solid fa-circle-check text-green-500 mr-1"></i>Saved ${ext.toUpperCase()} · ${Math.round(blob.size / 1024)} KB`;
  },

  reset() {
    this.editor.classList.add('hidden');
    this.dropzone.parentElement.classList.remove('hidden');
    if (this.srcUrl) { URL.revokeObjectURL(this.srcUrl); this.srcUrl = null; }
    if (this.cutoutUrl) { URL.revokeObjectURL(this.cutoutUrl); this.cutoutUrl = null; }
    this.original = null; this.cutout = null;
    $('#bl-done').textContent = '';
  },
};

document.addEventListener('DOMContentLoaded', () => App.init());
