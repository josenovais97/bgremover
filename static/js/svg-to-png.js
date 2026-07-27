/**
 * SVG → PNG/JPG — 100% client-side.
 *
 * The browser rasterises the vector itself: the SVG text becomes a blob URL,
 * loads into an <img>, and is drawn onto a canvas at the exact output size —
 * so a 4× export carries 4× the real detail instead of stretched pixels.
 *
 * Intrinsic size comes from the width/height attributes when present, else the
 * viewBox, else a 512px fallback — an SVG with none of those has no size at all.
 *
 * Nothing is uploaded. Shared helpers come from window.CBG.
 */
const { $, $$, Toast, loadImage, dropzone, download, baseName, t } = CBG;

const MAX_OUT = 8000;

const isSvg = (f) => f.type === 'image/svg+xml' || /\.svg$/i.test(f.name);

const App = {
  scale: 1,
  width: null,     // explicit width overrides scale
  bg: 'transparent',
  fmt: 'png',

  init() {
    this.hero = $('#sv-hero');
    this.editor = $('#sv-editor');

    dropzone($('#sv-dropzone'), {
      input: $('#sv-input'),
      icon: $('#sv-icon'),
      browse: $('#sv-browse'),
      multiple: false,
      accept: isSvg,
      onFiles: (files) => this.load(files[0]),
    });

    $$('.sv-scale').forEach((b) => b.addEventListener('click', () => {
      this.scale = +b.dataset.scale;
      this.width = null;
      $('#sv-width').value = '';
      $$('.sv-scale').forEach((x) => {
        const a = x === b;
        x.classList.toggle('bg-primary', a); x.classList.toggle('text-white', a);
      });
      this.updateSize();
    }));
    $('#sv-width').addEventListener('input', (e) => {
      this.width = +e.target.value || null;
      $$('.sv-scale').forEach((x) => { x.classList.remove('bg-primary', 'text-white'); });
      this.updateSize();
    });
    $$('.sv-bg').forEach((b) => b.addEventListener('click', () => {
      this.bg = b.dataset.bg;
      $$('.sv-bg').forEach((x) => {
        const a = x === b;
        x.classList.toggle('bg-primary', a); x.classList.toggle('text-white', a);
      });
    }));
    $$('.sv-fmt').forEach((b) => b.addEventListener('click', () => {
      this.fmt = b.dataset.fmt;
      $$('.sv-fmt').forEach((x) => {
        const a = x === b;
        x.classList.toggle('bg-primary', a); x.classList.toggle('text-white', a);
      });
    }));

    $('#sv-download').addEventListener('click', () => this.export());
    $('#sv-new').addEventListener('click', () => this.reset());
  },

  async load(file) {
    if (!isSvg(file)) { Toast.show(t('That is not an SVG file'), 'error'); return; }
    const text = await file.text();
    if (this.url) URL.revokeObjectURL(this.url);
    this.url = URL.createObjectURL(new Blob([text], { type: 'image/svg+xml' }));
    try { this.img = await loadImage(this.url); }
    catch { Toast.show(t('Could not render that SVG'), 'error'); return; }
    this.name = baseName(file.name);

    // Intrinsic size: rendered size, else the viewBox, else a square fallback.
    let w = this.img.naturalWidth, h = this.img.naturalHeight;
    if (!w || !h) {
      const vb = /viewBox\s*=\s*["'][^"']*?([\d.]+)[\s,]+([\d.]+)\s*["']$/;
      const m = text.match(/viewBox\s*=\s*["']\s*[\d.-]+[\s,]+[\d.-]+[\s,]+([\d.]+)[\s,]+([\d.]+)\s*["']/);
      if (m) { w = parseFloat(m[1]); h = parseFloat(m[2]); }
    }
    if (!w || !h) { w = 512; h = 512; }
    this.base = { w, h };

    $('#sv-preview').src = this.url;
    this.updateSize();
    this.hero.classList.add('hidden');
    this.editor.classList.remove('hidden');
  },

  outSize() {
    let w = this.width ? this.width : this.base.w * this.scale;
    let h = Math.round(w * (this.base.h / this.base.w));
    const k = Math.min(1, MAX_OUT / Math.max(w, h));
    return { w: Math.max(1, Math.round(w * k)), h: Math.max(1, Math.round(h * k)) };
  },

  updateSize() {
    if (!this.base) return;
    const { w, h } = this.outSize();
    $('#sv-size').textContent = `${Math.round(this.base.w)}×${Math.round(this.base.h)} → ${w}×${h}px`;
  },

  export() {
    if (!this.img) return;
    const { w, h } = this.outSize();
    const canvas = document.createElement('canvas');
    canvas.width = w; canvas.height = h;
    const ctx = canvas.getContext('2d');
    const fill = this.fmt === 'jpg' && this.bg === 'transparent' ? '#ffffff' : this.bg;
    if (fill !== 'transparent') { ctx.fillStyle = fill; ctx.fillRect(0, 0, w, h); }
    ctx.drawImage(this.img, 0, 0, w, h);
    const mime = this.fmt === 'jpg' ? 'image/jpeg' : 'image/png';
    canvas.toBlob((blob) => {
      if (!blob) { Toast.show(t('Export failed'), 'error'); return; }
      window.__clearbgReport?.(1, 'downloaded');
      download(blob, `${this.name || 'image'}-${w}x${h}.${this.fmt}`);
    }, mime, 0.92);
  },

  reset() {
    this.editor.classList.add('hidden');
    this.hero.classList.remove('hidden');
    if (this.url) { URL.revokeObjectURL(this.url); this.url = null; }
    this.img = null;
    this.base = null;
  },
};

document.addEventListener('DOMContentLoaded', () => App.init());
