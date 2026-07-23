/**
 * Colour palette extractor — 100% client-side.
 *
 * Reads an image into a canvas, quantises its pixels and surfaces the dominant
 * colours as copy-to-clipboard swatches (HEX or RGB), plus a one-click "copy all
 * as CSS variables". Also a live eyedropper: hover the image to read the colour
 * under the pointer.
 *
 * The quantiser is a cheap popularity count in a reduced colour space (5 bits per
 * channel) — fast, dependency-free, and good enough to pull a photo's real
 * palette. Nothing is uploaded. Shared helpers come from window.CBG.
 */
const { $, $$, Toast, loadImage, dropzone, t } = CBG;

const hex = (r, g, b) => '#' + [r, g, b].map((c) => c.toString(16).padStart(2, '0')).join('');

const App = {
  count: 6,
  format: 'hex',
  colors: [],

  init() {
    this.dropzone = $('#pl-dropzone');
    this.hero = this.dropzone.closest('section');
    this.input = $('#pl-input');
    this.editor = $('#pl-editor');
    this.canvas = document.createElement('canvas');
    this.ctx = this.canvas.getContext('2d', { willReadFrequently: true });

    dropzone(this.dropzone, {
      input: this.input,
      icon: $('#pl-icon'),
      browse: $('#pl-browse'),
      multiple: false,
      onFiles: (files) => this.load(files[0]),
    });

    $$('.pl-count').forEach((b) => b.addEventListener('click', () => {
      this.count = +b.dataset.count;
      $$('.pl-count').forEach((x) => {
        const a = x === b;
        x.classList.toggle('bg-primary', a); x.classList.toggle('text-white', a);
      });
      this.render();
    }));
    $$('.pl-fmt').forEach((b) => b.addEventListener('click', () => {
      this.format = b.dataset.fmt;
      $$('.pl-fmt').forEach((x) => {
        const a = x === b;
        x.classList.toggle('bg-primary', a); x.classList.toggle('text-white', a);
      });
      this.render();
    }));
    $('#pl-copy-all').addEventListener('click', () => this.copyAll());
    $('#pl-new').addEventListener('click', () => this.reset());

    const preview = $('#pl-preview');
    preview.addEventListener('mousemove', (e) => this.pick(e));
    preview.addEventListener('mouseleave', () => { $('#pl-eyedrop').classList.add('opacity-0'); });
  },

  async load(file) {
    if (this.url) URL.revokeObjectURL(this.url);
    this.url = URL.createObjectURL(file);
    let img;
    try { img = await loadImage(this.url); } catch { Toast.show(t('Could not read that image'), 'error'); return; }
    this.img = img;
    // Downscale for the sampling pass — 160px longest edge is plenty for a
    // palette and keeps the getImageData scan instant even on huge photos.
    const s = Math.min(1, 160 / Math.max(img.naturalWidth, img.naturalHeight));
    this.canvas.width = Math.max(1, Math.round(img.naturalWidth * s));
    this.canvas.height = Math.max(1, Math.round(img.naturalHeight * s));
    this.ctx.drawImage(img, 0, 0, this.canvas.width, this.canvas.height);
    this.data = this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height).data;

    $('#pl-preview').src = this.url;
    this.hero.classList.add('hidden');
    this.editor.classList.remove('hidden');
    this.render();
  },

  /** Popularity-count quantiser: bucket colours to 5 bits/channel, keep the top N. */
  extract(n) {
    const buckets = new Map();
    const d = this.data;
    for (let i = 0; i < d.length; i += 4) {
      if (d[i + 3] < 128) continue;                 // skip transparent pixels
      const r = d[i] >> 3, g = d[i + 1] >> 3, b = d[i + 2] >> 3;
      const key = (r << 10) | (g << 5) | b;
      const acc = buckets.get(key);
      if (acc) { acc[0] += d[i]; acc[1] += d[i + 1]; acc[2] += d[i + 2]; acc[3]++; }
      else buckets.set(key, [d[i], d[i + 1], d[i + 2], 1]);
    }
    const sorted = [...buckets.values()].sort((a, b) => b[3] - a[3]);
    const out = [];
    for (const [r, g, b, c] of sorted) {
      const avg = [Math.round(r / c), Math.round(g / c), Math.round(b / c)];
      // Drop near-duplicates so the swatches read as a real palette, not six
      // shades of the same wall.
      if (out.every((o) => Math.abs(o[0] - avg[0]) + Math.abs(o[1] - avg[1]) + Math.abs(o[2] - avg[2]) > 40)) {
        out.push(avg);
        if (out.length >= n) break;
      }
    }
    return out;
  },

  render() {
    this.colors = this.extract(this.count);
    const holder = $('#pl-swatches');
    holder.innerHTML = '';
    for (const [r, g, b] of this.colors) {
      const value = this.format === 'rgb' ? `rgb(${r}, ${g}, ${b})` : hex(r, g, b);
      const lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255;   // label contrast
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'group relative h-24 rounded-xl border border-black/5 dark:border-white/10 flex items-end p-2 transition hover:scale-[1.03] focus:outline-none focus-visible:ring-2 focus-visible:ring-primary';
      btn.style.backgroundColor = `rgb(${r}, ${g}, ${b})`;
      const tag = document.createElement('span');
      tag.className = `text-[11px] font-semibold tracking-tight ${lum > 0.6 ? 'text-black/70' : 'text-white/90'}`;
      tag.textContent = value;
      btn.appendChild(tag);
      btn.title = t('Click to copy');
      btn.addEventListener('click', () => this.copy(value));
      holder.appendChild(btn);
    }
  },

  pick(e) {
    if (!this.data) return;
    const img = $('#pl-preview');
    const rect = img.getBoundingClientRect();
    const x = Math.floor(((e.clientX - rect.left) / rect.width) * this.canvas.width);
    const y = Math.floor(((e.clientY - rect.top) / rect.height) * this.canvas.height);
    const i = (y * this.canvas.width + x) * 4;
    const d = this.data;
    if (i < 0 || i >= d.length) return;
    const value = this.format === 'rgb' ? `rgb(${d[i]}, ${d[i + 1]}, ${d[i + 2]})` : hex(d[i], d[i + 1], d[i + 2]);
    const drop = $('#pl-eyedrop');
    drop.classList.remove('opacity-0');
    drop.querySelector('[data-swatch]').style.backgroundColor = `rgb(${d[i]}, ${d[i + 1]}, ${d[i + 2]})`;
    drop.querySelector('[data-value]').textContent = value;
    this.eyedropValue = value;
    drop.onclick = () => this.copy(value);
  },

  async copy(value) {
    try { await navigator.clipboard.writeText(value); Toast.show(t('Copied {value}', { value })); }
    catch { Toast.show(t('Copy failed'), 'error'); }
  },

  async copyAll() {
    if (!this.colors.length) return;
    const lines = this.colors.map(([r, g, b], i) =>
      `  --color-${i + 1}: ${this.format === 'rgb' ? `rgb(${r}, ${g}, ${b})` : hex(r, g, b)};`);
    try {
      await navigator.clipboard.writeText(`:root {\n${lines.join('\n')}\n}`);
      Toast.show(t('Palette copied as CSS'));
    } catch { Toast.show(t('Copy failed'), 'error'); }
  },

  reset() {
    this.editor.classList.add('hidden');
    this.hero.classList.remove('hidden');
    if (this.url) { URL.revokeObjectURL(this.url); this.url = null; }
    this.data = null;
  },
};

document.addEventListener('DOMContentLoaded', () => App.init());
