/**
 * Text-behind-image effect — 100% client-side.
 *
 * Removes the background to isolate the subject, then composes three layers:
 * the original photo, the text on top of it, and finally the subject cut-out —
 * so the text appears to sit *behind* the subject. Nothing is uploaded.
 *
 * Helpers ($, Toast, loadImage, t, …) come from window.CBG (static/js/kit.js),
 * a classic script — a local ES import would break, since Django's hashed-manifest
 * static storage does not rewrite ES-module import paths.
 */

const { $, $$, Toast, loadImage, download, t } = CBG;
import { removeBackground } from 'https://cdn.jsdelivr.net/npm/@imgly/background-removal@1.6.0/+esm';

/* --------------------------------------------------------------- helpers */
const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));

function rafThrottle(fn) {
  let scheduled = false;
  return () => { if (scheduled) return; scheduled = true; requestAnimationFrame(() => { scheduled = false; fn(); }); };
}

/* --------------------------------------------------------------------- app */
const App = {
  original: null,  // HTMLImageElement of the source photo
  cutout: null,    // subject with background removed (same dimensions)
  text: { content: 'POV', font: 'Anton', size: 26, color: '#ffffff', opacity: 1, bold: true, x: 0.5, y: 0.5 },

  init() {
    this.dropzone = $('#tb-dropzone');
    this.input = $('#tb-input');
    this.editor = $('#tb-editor');
    this.canvas = $('#tb-canvas');

    const open = () => this.input.click();
    $('#tb-browse').addEventListener('click', (e) => { e.stopPropagation(); open(); });
    this.dropzone.addEventListener('click', open);
    this.dropzone.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); } });
    this.input.addEventListener('change', (e) => this.load(e.target.files[0]));

    const icon = $('#tb-icon');
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
    $('#tb-text').addEventListener('input', (e) => { this.text.content = e.target.value; render(); });
    $('#tb-size').addEventListener('input', (e) => { this.text.size = +e.target.value; render(); });
    $('#tb-opacity').addEventListener('input', (e) => { this.text.opacity = +e.target.value / 100; render(); });
    $('#tb-color').addEventListener('input', (e) => { this.text.color = e.target.value; render(); });
    $('#tb-bold').addEventListener('click', (e) => {
      this.text.bold = !this.text.bold;
      e.currentTarget.setAttribute('aria-pressed', String(this.text.bold));
      e.currentTarget.classList.toggle('ring-2', this.text.bold);
      e.currentTarget.classList.toggle('ring-primary', this.text.bold);
      this.render();
    });
    $('#tb-center').addEventListener('click', () => { this.text.x = 0.5; this.text.y = 0.5; this.render(); });
    $$('.tb-font').forEach((b) => b.addEventListener('click', () => {
      this.text.font = b.dataset.font;
      $$('.tb-font').forEach((x) => { const a = x === b; x.classList.toggle('ring-2', a); x.classList.toggle('ring-primary', a); });
      this.loadFontThenRender();
    }));

    // Drag the text across the image (grab-and-move, in normalised coords).
    this.canvas.addEventListener('pointerdown', (e) => {
      this.canvas.setPointerCapture?.(e.pointerId);
      const p = this.pointer(e);
      this.drag = { px: p.x, py: p.y, x: this.text.x, y: this.text.y };
    });
    this.canvas.addEventListener('pointermove', (e) => {
      if (!this.drag) return;
      const p = this.pointer(e);
      this.text.x = clamp(this.drag.x + (p.x - this.drag.px), 0, 1);
      this.text.y = clamp(this.drag.y + (p.y - this.drag.py), 0, 1);
      render();
    });
    ['pointerup', 'pointercancel', 'pointerleave'].forEach((ev) => this.canvas.addEventListener(ev, () => { this.drag = null; }));

    $('#tb-download').addEventListener('click', () => this.export('image/png'));
    $('#tb-download-jpg').addEventListener('click', () => this.export('image/jpeg'));
    $('#tb-new').addEventListener('click', () => this.reset());

    this.setBusy(false);
  },

  // Pointer position as a 0..1 fraction of the canvas box.
  pointer(e) {
    const r = this.canvas.getBoundingClientRect();
    return { x: (e.clientX - r.left) / r.width, y: (e.clientY - r.top) / r.height };
  },

  setBusy(busy, text) {
    $('#tb-status').classList.toggle('hidden', !busy);
    if (text) $('#tb-status-text').textContent = text;
    const dis = busy || !this.original;
    $('#tb-download').disabled = dis;
    $('#tb-download-jpg').disabled = dis;
  },

  loadFontThenRender() {
    if (document.fonts && document.fonts.load) {
      document.fonts.load(`700 40px ${this.text.font}`).then(() => this.render()).catch(() => this.render());
    } else {
      this.render();
    }
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
    this.setBusy(true, 'Cutting out your subject…');
    this.loadFontThenRender();
    try {
      const blob = await removeBackground(file, { model: self.crossOriginIsolated ? 'isnet' : 'isnet_quint8' });
      if (this.cutoutUrl) URL.revokeObjectURL(this.cutoutUrl);
      this.cutoutUrl = URL.createObjectURL(blob);
      this.cutout = await loadImage(this.cutoutUrl);
      window.__clearbgReport?.(1);
      this.setBusy(false);
      this.render();
      Toast.show(t('Type your text and drag it behind the subject'), 'success');
    } catch (err) {
      console.error('[textbehind] bg removal failed:', err);
      Toast.show(t('Could not cut out the subject'), 'error');
      this.setBusy(false);
      this.render();
    }
  },

  drawText(ctx, w, h) {
    const t = this.text;
    if (!t.content.trim()) return;
    const fontPx = (t.size / 100) * w;
    ctx.save();
    ctx.font = `${t.bold ? '700' : '400'} ${fontPx}px ${t.font}, sans-serif`;
    ctx.fillStyle = t.color;
    ctx.globalAlpha = t.opacity;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    const lines = t.content.split('\n');
    const lineH = fontPx * 1.02;
    const cx = t.x * w;
    let y = t.y * h - ((lines.length - 1) * lineH) / 2;
    for (const ln of lines) { ctx.fillText(ln, cx, y); y += lineH; }
    ctx.restore();
  },

  /** Compose original → text → subject cut-out at native resolution. */
  paint(canvas) {
    const w = this.original.naturalWidth, h = this.original.naturalHeight;
    canvas.width = w; canvas.height = h;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, w, h);
    ctx.drawImage(this.original, 0, 0, w, h);
    this.drawText(ctx, w, h);
    if (this.cutout) ctx.drawImage(this.cutout, 0, 0, w, h);
  },

  render() {
    if (!this.original) return;
    this.paint(this.canvas);
  },

  async export(fmt) {
    if (!this.original) return;
    const c = document.createElement('canvas');
    this.paint(c);
    const ext = fmt === 'image/png' ? 'png' : 'jpg';
    const blob = await new Promise((res) => c.toBlob(res, fmt, 0.95));
    if (!blob) { Toast.show(t('Export failed'), 'error'); return; }
    download(blob, `text-behind.${ext}`);
    $('#tb-done').innerHTML = `<i class="fa-solid fa-circle-check text-green-500 mr-1"></i>Saved ${ext.toUpperCase()} · ${Math.round(blob.size / 1024)} KB`;
  },

  reset() {
    this.editor.classList.add('hidden');
    this.dropzone.parentElement.classList.remove('hidden');
    if (this.srcUrl) { URL.revokeObjectURL(this.srcUrl); this.srcUrl = null; }
    if (this.cutoutUrl) { URL.revokeObjectURL(this.cutoutUrl); this.cutoutUrl = null; }
    this.original = null; this.cutout = null;
    $('#tb-done').textContent = '';
  },
};

document.addEventListener('DOMContentLoaded', () => App.init());
