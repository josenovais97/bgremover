/**
 * Photo filters & adjustments — 100% client-side.
 *
 * One-tap looks are just presets over the same six sliders, so tapping a look
 * and then nudging a slider always composes instead of fighting. The pipeline:
 * ctx.filter handles brightness/contrast/saturation (GPU-accelerated), warmth
 * is a soft-light colour wash, vignette a multiplied radial gradient, grain a
 * tiled noise pattern — all canvas-native, no per-pixel loops, so the preview
 * tracks the sliders live.
 *
 * The preview runs on a downscaled canvas for speed; export re-applies the
 * exact settings at full resolution. Nothing is uploaded. Helpers: window.CBG.
 */
const { $, $$, Toast, loadImage, dropzone, download, baseName, t } = CBG;

const PREVIEW_DIM = 1400;

const DEFAULTS = { bright: 100, contrast: 100, sat: 100, warmth: 0, vignette: 0, grain: 0 };

const LOOKS = [
  ['None',   {}],
  ['Vivid',  { sat: 135, contrast: 112, bright: 103 }],
  ['Punch',  { contrast: 120, sat: 125 }],
  ['Warm',   { warmth: 35, sat: 110 }],
  ['Golden', { warmth: 50, bright: 105, contrast: 105 }],
  ['Cool',   { warmth: -30, sat: 105 }],
  ['Moody',  { bright: 92, contrast: 118, sat: 85, vignette: 40 }],
  ['Film',   { contrast: 92, sat: 85, warmth: 15, grain: 35, bright: 104 }],
  ['Fade',   { contrast: 85, bright: 108, sat: 90 }],
  ['Noir',   { sat: 0, contrast: 115, vignette: 35, grain: 20 }],
];

const App = {
  state: { ...DEFAULTS },
  fmt: 'jpg',

  init() {
    this.hero = $('#pf-hero');
    this.editor = $('#pf-editor');
    this.canvas = $('#pf-canvas');
    this.ctx = this.canvas.getContext('2d');
    this.noise = this.makeNoise();

    dropzone($('#pf-dropzone'), {
      input: $('#pf-input'),
      icon: $('#pf-icon'),
      browse: $('#pf-browse'),
      multiple: false,
      onFiles: (files) => this.load(files[0]),
    });

    // Looks strip.
    const holder = $('#pf-looks');
    LOOKS.forEach(([name, patch], i) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.textContent = name;
      b.className = 'pf-look px-1.5 py-2 rounded-lg border border-gray-300 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800 transition' +
        (i === 0 ? ' bg-primary text-white' : '');
      b.addEventListener('click', () => {
        this.state = { ...DEFAULTS, ...patch };
        $$('.pf-look').forEach((x) => {
          const a = x === b;
          x.classList.toggle('bg-primary', a); x.classList.toggle('text-white', a);
        });
        this.syncSliders();
        this.render();
      });
      holder.appendChild(b);
    });

    $$('.pf-slider').forEach((s) => s.addEventListener('input', () => {
      this.state[s.dataset.k] = +s.value;
      $(`[data-val="${s.dataset.k}"]`).textContent = s.value;
      this.render();
    }));

    const compare = $('#pf-compare');
    const showOriginal = (on) => {
      $('#pf-compare-badge').classList.toggle('hidden', !on);
      if (on) this.drawBase(this.ctx, this.preview);
      else this.render();
    };
    compare.addEventListener('pointerdown', () => showOriginal(true));
    window.addEventListener('pointerup', () => showOriginal(false));
    compare.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); showOriginal(true); }
    });
    compare.addEventListener('keyup', () => showOriginal(false));

    $('#pf-reset').addEventListener('click', () => {
      this.state = { ...DEFAULTS };
      this.syncSliders();
      this.render();
    });
    $$('.pf-fmt').forEach((b) => b.addEventListener('click', () => {
      this.fmt = b.dataset.fmt;
      $$('.pf-fmt').forEach((x) => {
        const a = x === b;
        x.classList.toggle('bg-primary', a); x.classList.toggle('text-white', a);
      });
    }));
    $('#pf-download').addEventListener('click', () => this.export());
    $('#pf-new').addEventListener('click', () => this.reset());
  },

  async load(file) {
    if (this.url) URL.revokeObjectURL(this.url);
    this.url = URL.createObjectURL(file);
    try { this.img = await loadImage(this.url); }
    catch { Toast.show(t('Could not read that image'), 'error'); return; }
    this.name = baseName(file.name);

    const s = Math.min(1, PREVIEW_DIM / Math.max(this.img.naturalWidth, this.img.naturalHeight));
    this.preview = document.createElement('canvas');
    this.preview.width = Math.max(1, Math.round(this.img.naturalWidth * s));
    this.preview.height = Math.max(1, Math.round(this.img.naturalHeight * s));
    this.preview.getContext('2d').drawImage(this.img, 0, 0, this.preview.width, this.preview.height);

    this.canvas.width = this.preview.width;
    this.canvas.height = this.preview.height;
    this.hero.classList.add('hidden');
    this.editor.classList.remove('hidden');
    this.render();
  },

  syncSliders() {
    $$('.pf-slider').forEach((s) => {
      s.value = this.state[s.dataset.k];
      $(`[data-val="${s.dataset.k}"]`).textContent = s.value;
    });
  },

  makeNoise() {
    const c = document.createElement('canvas');
    c.width = 256; c.height = 256;
    const nctx = c.getContext('2d');
    const d = nctx.createImageData(256, 256);
    for (let i = 0; i < d.data.length; i += 4) {
      const v = 128 + (Math.random() - 0.5) * 255;
      d.data[i] = d.data[i + 1] = d.data[i + 2] = v;
      d.data[i + 3] = 255;
    }
    nctx.putImageData(d, 0, 0);
    return c;
  },

  drawBase(ctx, source) {
    ctx.filter = 'none';
    ctx.globalCompositeOperation = 'source-over';
    ctx.globalAlpha = 1;
    ctx.drawImage(source, 0, 0, ctx.canvas.width, ctx.canvas.height);
  },

  /** Apply the current state onto `ctx` from `source` (any resolution). */
  paint(ctx, source) {
    const { bright, contrast, sat, warmth, vignette, grain } = this.state;
    const W = ctx.canvas.width, H = ctx.canvas.height;
    ctx.globalCompositeOperation = 'source-over';
    ctx.globalAlpha = 1;
    ctx.filter = `brightness(${bright / 100}) contrast(${contrast / 100}) saturate(${sat / 100})`;
    ctx.drawImage(source, 0, 0, W, H);
    ctx.filter = 'none';

    if (warmth) {
      ctx.globalCompositeOperation = 'soft-light';
      ctx.globalAlpha = Math.min(0.55, Math.abs(warmth) / 100 * 1.1);
      ctx.fillStyle = warmth > 0 ? '#ff9a3c' : '#3c8dff';
      ctx.fillRect(0, 0, W, H);
    }
    if (vignette) {
      ctx.globalCompositeOperation = 'multiply';
      ctx.globalAlpha = 1;
      const r = Math.hypot(W, H) / 2;
      const g = ctx.createRadialGradient(W / 2, H / 2, r * 0.45, W / 2, H / 2, r);
      g.addColorStop(0, 'rgba(255,255,255,1)');
      const dark = Math.round(255 - (vignette / 100) * 160);
      g.addColorStop(1, `rgb(${dark},${dark},${dark})`);
      ctx.fillStyle = g;
      ctx.fillRect(0, 0, W, H);
    }
    if (grain) {
      ctx.globalCompositeOperation = 'overlay';
      ctx.globalAlpha = (grain / 100) * 0.35;
      const pattern = ctx.createPattern(this.noise, 'repeat');
      ctx.fillStyle = pattern;
      ctx.fillRect(0, 0, W, H);
    }
    ctx.globalCompositeOperation = 'source-over';
    ctx.globalAlpha = 1;
  },

  render() {
    if (!this.preview) return;
    this.paint(this.ctx, this.preview);
  },

  export() {
    if (!this.img) return;
    const full = document.createElement('canvas');
    full.width = this.img.naturalWidth;
    full.height = this.img.naturalHeight;
    this.paint(full.getContext('2d'), this.img);
    const mime = { jpg: 'image/jpeg', png: 'image/png', webp: 'image/webp' }[this.fmt];
    full.toBlob((blob) => {
      if (!blob) { Toast.show(t('Export failed'), 'error'); return; }
      download(blob, `${this.name || 'photo'}-edited.${this.fmt}`);
    }, mime, 0.92);
  },

  reset() {
    this.editor.classList.add('hidden');
    this.hero.classList.remove('hidden');
    if (this.url) { URL.revokeObjectURL(this.url); this.url = null; }
    this.img = null;
    this.preview = null;
    this.state = { ...DEFAULTS };
    this.syncSliders();
  },
};

document.addEventListener('DOMContentLoaded', () => App.init());
