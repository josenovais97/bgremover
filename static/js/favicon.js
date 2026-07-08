/**
 * Favicon / app-icon generator — 100% client-side.
 *
 * One image in → a complete icon pack out: favicon.ico (16/32/48), PNGs for
 * every size, an Apple touch icon, PWA + maskable icons, a site.webmanifest and
 * a copy-paste <head> snippet, bundled into a ZIP. Nothing is uploaded.
 *
 * Self-contained (own helpers/toast) — Django's static storage doesn't rewrite
 * ES-module import paths, so only absolute-URL (CDN) imports are used.
 */
import JSZip from 'https://cdn.jsdelivr.net/npm/jszip@3.10.1/+esm';

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

function rafThrottle(fn) {
  let scheduled = false;
  return () => { if (scheduled) return; scheduled = true; requestAnimationFrame(() => { scheduled = false; fn(); }); };
}

function roundRectPath(ctx, x, y, w, h, r) {
  r = Math.min(r, w / 2, h / 2);
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}

/* --------------------------------------------------------------------- app */
const App = {
  img: null,
  state: { bg: 'transparent', shape: 'square', pad: 0, name: 'My App', short: 'App', theme: '#4F46E5' },

  init() {
    this.dropzone = $('#fav-dropzone');
    this.input = $('#fav-input');
    this.editor = $('#fav-editor');

    const open = () => this.input.click();
    $('#fav-browse').addEventListener('click', (e) => { e.stopPropagation(); open(); });
    this.dropzone.addEventListener('click', open);
    this.dropzone.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); } });
    this.input.addEventListener('change', (e) => this.load(e.target.files[0]));

    const icon = $('#fav-icon');
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

    // Background swatches + custom colour.
    $$('.fav-bg').forEach((b) => b.addEventListener('click', () => { this.state.bg = b.dataset.bg; this.reflectBg(b); render(); }));
    $('.fav-bg-custom').addEventListener('input', (e) => { this.state.bg = e.target.value; this.reflectBg(null); render(); });

    // Shape.
    $$('.fav-shape').forEach((b) => b.addEventListener('click', () => {
      this.state.shape = b.dataset.shape;
      $$('.fav-shape').forEach((x) => { const a = x === b; x.classList.toggle('ring-2', a); x.classList.toggle('ring-primary', a); });
      render();
    }));

    // Padding.
    $('#fav-pad').addEventListener('input', (e) => { this.state.pad = +e.target.value / 100; $('#fav-pad-val').textContent = `${e.target.value}%`; render(); });

    // Manifest fields.
    $('#fav-name').addEventListener('input', (e) => { this.state.name = e.target.value; this.updateTabName(); });
    $('#fav-short').addEventListener('input', (e) => { this.state.short = e.target.value; });
    $('#fav-theme').addEventListener('input', (e) => { this.state.theme = e.target.value; $('#fav-theme-val').textContent = e.target.value.toUpperCase(); });

    $('#fav-download').addEventListener('click', () => this.download());
    $('#fav-new').addEventListener('click', () => this.reset());
    $('#fav-copy').addEventListener('click', () => this.copySnippet());
  },

  reflectBg(activeBtn) {
    $$('.fav-bg').forEach((b) => {
      const a = b === activeBtn;
      b.classList.toggle('ring-2', a);
      b.classList.toggle('ring-primary', a);
      b.classList.toggle('ring-offset-1', a);
    });
  },

  updateTabName() { $('#fav-tab-name').textContent = this.state.name || 'Your Site'; },

  async load(file) {
    this.input.value = '';
    if (!file || !/^image\//.test(file.type)) { Toast.show('Please choose an image', 'error'); return; }
    if (this.url) URL.revokeObjectURL(this.url);
    this.url = URL.createObjectURL(file);
    try {
      this.img = await loadImage(this.url);
    } catch {
      Toast.show("Couldn't open that image", 'error');
      return;
    }
    this.dropzone.parentElement.classList.add('hidden');
    this.editor.classList.remove('hidden');
    $('#fav-snippet-section').classList.remove('hidden');
    this.updateTabName();
    this.render();
  },

  /** Clip the drawing context to the chosen icon shape. */
  clipShape(ctx, size) {
    if (this.state.shape === 'circle') {
      ctx.beginPath();
      ctx.ellipse(size / 2, size / 2, size / 2, size / 2, 0, 0, Math.PI * 2);
      ctx.clip();
    } else if (this.state.shape === 'rounded') {
      roundRectPath(ctx, 0, 0, size, size, size * 0.2);
      ctx.clip();
    }
  },

  /** Draw the icon at `size`. `opts.forceOpaque` fills a bg even when transparent
   *  (Apple touch icons render black behind transparency). `opts.maskable` makes
   *  a full-bleed opaque icon with an Android safe-zone margin. */
  drawIcon(size, opts = {}) {
    const c = document.createElement('canvas');
    c.width = c.height = size;
    const ctx = c.getContext('2d');
    ctx.clearRect(0, 0, size, size);
    ctx.save();

    if (opts.maskable) {
      // Maskable: never clipped, always opaque, extra margin so nothing is cut.
      const bg = this.state.bg === 'transparent' ? (this.state.theme || '#ffffff') : this.state.bg;
      ctx.fillStyle = bg;
      ctx.fillRect(0, 0, size, size);
      this.drawContained(ctx, size, Math.max(this.state.pad, 0.14));
      ctx.restore();
      return c;
    }

    this.clipShape(ctx, size);
    let bg = this.state.bg;
    if (bg === 'transparent' && opts.forceOpaque) bg = '#ffffff';
    if (bg !== 'transparent') { ctx.fillStyle = bg; ctx.fillRect(0, 0, size, size); }
    this.drawContained(ctx, size, this.state.pad);
    ctx.restore();
    return c;
  },

  drawContained(ctx, size, pad) {
    const iw = this.img.naturalWidth || this.img.width;
    const ih = this.img.naturalHeight || this.img.height;
    const inner = size * (1 - 2 * pad);
    const scale = Math.min(inner / iw, inner / ih);
    const dw = iw * scale;
    const dh = ih * scale;
    ctx.drawImage(this.img, (size - dw) / 2, (size - dh) / 2, dw, dh);
  },

  render() {
    if (!this.img) return;
    // Big preview (drawn at 256 for crispness).
    const big = this.drawIcon(256);
    const pv = $('#fav-preview').getContext('2d');
    pv.clearRect(0, 0, 256, 256);
    pv.drawImage(big, 0, 0);
    // Browser-tab 16px favicon.
    const tab = this.drawIcon(16);
    const tc = $('#fav-tab').getContext('2d');
    tc.clearRect(0, 0, 16, 16);
    tc.drawImage(tab, 0, 0);
    // Actual-size thumbs.
    $$('.fav-thumb').forEach((cv) => {
      const s = +cv.dataset.size;
      const ic = this.drawIcon(s);
      const ctx = cv.getContext('2d');
      ctx.clearRect(0, 0, s, s);
      ctx.drawImage(ic, 0, 0);
    });
    // Keep the copy-paste snippet in sync (filenames are fixed; theme colour isn't).
    const snip = $('#fav-snippet');
    if (snip) snip.textContent = this.snippet();
  },

  toBlob(canvas) {
    return new Promise((res) => canvas.toBlob(res, 'image/png'));
  },

  /** Build a multi-image .ico from PNG blobs (PNG-in-ICO, supported everywhere). */
  async buildIco(sizes) {
    const buffers = await Promise.all(sizes.map((s) => this.toBlob(this.drawIcon(s)).then((b) => b.arrayBuffer())));
    const header = new ArrayBuffer(6 + sizes.length * 16);
    const dv = new DataView(header);
    dv.setUint16(0, 0, true); // reserved
    dv.setUint16(2, 1, true); // type: icon
    dv.setUint16(4, sizes.length, true);
    let offset = 6 + sizes.length * 16;
    sizes.forEach((s, i) => {
      const o = 6 + i * 16;
      dv.setUint8(o, s >= 256 ? 0 : s); // width  (0 == 256)
      dv.setUint8(o + 1, s >= 256 ? 0 : s); // height
      dv.setUint8(o + 2, 0); // palette
      dv.setUint8(o + 3, 0); // reserved
      dv.setUint16(o + 4, 1, true); // colour planes
      dv.setUint16(o + 6, 32, true); // bits per pixel
      dv.setUint32(o + 8, buffers[i].byteLength, true);
      dv.setUint32(o + 12, offset, true);
      offset += buffers[i].byteLength;
    });
    return new Blob([header, ...buffers], { type: 'image/x-icon' });
  },

  manifestJson() {
    const bg = this.state.bg === 'transparent' ? '#ffffff' : this.state.bg;
    return JSON.stringify({
      name: this.state.name || 'My App',
      short_name: this.state.short || this.state.name || 'App',
      icons: [
        { src: '/icon-192.png', sizes: '192x192', type: 'image/png' },
        { src: '/icon-512.png', sizes: '512x512', type: 'image/png' },
        { src: '/icon-maskable-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
      ],
      theme_color: this.state.theme,
      background_color: bg,
      display: 'standalone',
    }, null, 2);
  },

  snippet() {
    return [
      '<link rel="icon" href="/favicon.ico" sizes="any">',
      '<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">',
      '<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">',
      '<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">',
      '<link rel="manifest" href="/site.webmanifest">',
      `<meta name="theme-color" content="${this.state.theme}">`,
    ].join('\n');
  },

  copySnippet() {
    navigator.clipboard.writeText(this.snippet())
      .then(() => Toast.show('HTML copied to clipboard', 'success'))
      .catch(() => Toast.show('Copy failed', 'error'));
  },

  async download() {
    if (!this.img) return;
    Toast.show('Building your icon pack…', 'info');
    try {
      const zip = new JSZip();
      // PNG icons.
      const pngs = [
        ['favicon-16x16.png', this.drawIcon(16)],
        ['favicon-32x32.png', this.drawIcon(32)],
        ['favicon-48x48.png', this.drawIcon(48)],
        ['apple-touch-icon.png', this.drawIcon(180, { forceOpaque: true })],
        ['icon-192.png', this.drawIcon(192)],
        ['icon-512.png', this.drawIcon(512)],
        ['icon-maskable-512.png', this.drawIcon(512, { maskable: true })],
      ];
      for (const [name, canvas] of pngs) zip.file(name, await this.toBlob(canvas));
      zip.file('favicon.ico', await this.buildIco([16, 32, 48]));
      zip.file('site.webmanifest', this.manifestJson());
      zip.file('head-snippet.html', this.snippet() + '\n');

      const blob = await zip.generateAsync({ type: 'blob' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'favicon-pack.zip';
      document.body.appendChild(a);
      a.click();
      URL.revokeObjectURL(url);
      a.remove();
      Toast.show('Icon pack downloaded', 'success');
    } catch (err) {
      console.error('[favicon] export failed:', err);
      Toast.show('Could not build the icon pack', 'error');
    }
  },

  reset() {
    this.editor.classList.add('hidden');
    $('#fav-snippet-section').classList.add('hidden');
    this.dropzone.parentElement.classList.remove('hidden');
    if (this.url) { URL.revokeObjectURL(this.url); this.url = null; }
    this.img = null;
  },
};

document.addEventListener('DOMContentLoaded', () => App.init());
