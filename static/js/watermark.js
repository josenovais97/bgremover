/**
 * Watermark tool — 100% client-side.
 *
 * Draws the photo to a canvas at full resolution, then bakes a text watermark
 * on top: either a single mark anchored to one of nine positions, or a tiled
 * pattern repeated across the whole image (harder to crop out). Nothing is
 * uploaded.
 *
 * Batch: every setting here is relative (size is a % of the shorter side, the
 * position is an anchor), so the same watermark applies cleanly to any number of
 * photos at any size. Extra files are queued and exported together as a ZIP.
 *
 * Shared helpers come from window.CBG (static/js/kit.js).
 */
const { $, $$, Toast, loadImage, dropzone, zipDownload, remember, baseName, download, t } = CBG;

const prefs = remember('watermark');

const App = {
  img: null,
  text: '© Your Name',
  mode: 'single',
  pos: 'br',
  size: 5,        // % of the image's smaller side
  opacity: 45,
  rotate: 0,
  color: '#ffffff',
  shadow: true,
  queue: [],      // extra files exported with the same watermark

  init() {
    this.dropzone = $('#wm-dropzone');
    // The hero section (dropzone + demo) is hidden once a photo loads. Resolved
    // via closest('section') rather than dropzone.parentElement so it survives the
    // dropzone being wrapped in a grid column alongside the demo.
    this.hero = this.dropzone.closest('section');
    this.input = $('#wm-input');
    this.editor = $('#wm-editor');
    this.canvas = $('#wm-canvas');
    this.batch = $('[data-batch]');

    dropzone(this.dropzone, {
      input: this.input,
      icon: $('#wm-icon'),
      browse: $('#wm-browse'),
      onFiles: (files) => this.load(files),
    });

    $('#wm-text').addEventListener('input', (e) => { this.text = e.target.value; this.render(); prefs.set({ text: this.text }); });

    $$('.wm-mode').forEach((b) => b.addEventListener('click', () => {
      this.mode = b.dataset.mode;
      $$('.wm-mode').forEach((x) => {
        const a = x === b;
        x.classList.toggle('ring-2', a); x.classList.toggle('ring-primary', a);
        x.classList.toggle('hover:bg-gray-100', !a); x.classList.toggle('dark:hover:bg-gray-800', !a);
      });
      // Anchoring is meaningless for a tiled mark — it covers the whole image.
      $('#wm-pos-wrap').classList.toggle('hidden', this.mode === 'tile');
      this.render();
    }));

    $$('.wm-pos-btn').forEach((b) => b.addEventListener('click', () => {
      this.pos = b.dataset.pos;
      $$('.wm-pos-btn').forEach((x) => {
        const a = x === b;
        x.classList.toggle('ring-2', a); x.classList.toggle('ring-primary', a);
        x.classList.toggle('border-primary', a); x.classList.toggle('bg-primary/10', a);
        x.classList.toggle('border-gray-300', !a); x.classList.toggle('dark:border-gray-700', !a);
      });
      this.render();
    }));

    $('#wm-size').addEventListener('input', (e) => { this.size = +e.target.value; this.render(); });
    $('#wm-opacity').addEventListener('input', (e) => { this.opacity = +e.target.value; this.render(); });
    $('#wm-rotate').addEventListener('input', (e) => { this.rotate = +e.target.value; this.render(); });
    $('#wm-color').addEventListener('input', (e) => { this.color = e.target.value; this.render(); });
    $('#wm-shadow').addEventListener('change', (e) => { this.shadow = e.target.checked; this.render(); });

    $('#wm-download').addEventListener('click', () => this.download());
    $('#wm-new').addEventListener('click', () => this.reset());
    $('[data-batch-zip]').addEventListener('click', () => this.downloadAll());

    // The mark itself is a preference — retyping it for every photo is busywork.
    const saved = prefs.get();
    if (saved.text) { this.text = saved.text; $('#wm-text').value = saved.text; }
  },

  async load(files) {
    const [first, ...rest] = files;
    this.file = first;
    this.queue = rest;
    if (this.url) URL.revokeObjectURL(this.url);
    this.url = URL.createObjectURL(first);
    try { this.img = await loadImage(this.url); } catch { Toast.show(t('Could not read that image'), 'error'); return; }
    this.canvas.width = this.img.naturalWidth;
    this.canvas.height = this.img.naturalHeight;
    this.render();
    this.hero.classList.add('hidden');
    this.editor.classList.remove('hidden');
    $('#wm-done').textContent = `${this.img.naturalWidth} × ${this.img.naturalHeight} px — full resolution, exported as-is`;
    this.syncBatch();
  },

  syncBatch() {
    const n = this.queue.length + 1;
    this.batch.classList.toggle('hidden', n < 2);
    this.batch.querySelector('[data-batch-count]').textContent = n;
  },

  /** Apply the shared text style to a context sized for `this.canvas`. */
  styleText(ctx, fontPx) {
    ctx.font = `600 ${fontPx}px system-ui, -apple-system, "Segoe UI", sans-serif`;
    ctx.fillStyle = this.color;
    ctx.globalAlpha = this.opacity / 100;
    if (this.shadow) {
      // A soft dark shadow keeps a light watermark legible over light photos
      // (and vice versa) without needing an outline.
      ctx.shadowColor = 'rgba(0,0,0,0.45)';
      ctx.shadowBlur = fontPx * 0.18;
    } else {
      ctx.shadowColor = 'transparent';
      ctx.shadowBlur = 0;
    }
  },

  render(canvas = this.canvas, img = this.img) {
    if (!img) return;
    const { width: w, height: h } = canvas;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, w, h);
    ctx.drawImage(img, 0, 0, w, h);

    const text = this.text.trim();
    if (!text) return;

    const fontPx = Math.max(8, (Math.min(w, h) * this.size) / 100);
    const rad = (this.rotate * Math.PI) / 180;

    ctx.save();
    this.styleText(ctx, fontPx);

    if (this.mode === 'tile') {
      const m = ctx.measureText(text);
      const stepX = m.width + fontPx * 2.2;
      const stepY = fontPx * 3;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      // Rotate about the centre, then paint a grid large enough that the tilted
      // canvas corners are still covered (the diagonal bounds any rotation).
      ctx.translate(w / 2, h / 2);
      ctx.rotate(rad);
      const reach = Math.hypot(w, h) / 2;
      for (let y = -reach; y <= reach; y += stepY) {
        // Offset every other row so the tiles read as a pattern, not columns.
        const odd = Math.round((y + reach) / stepY) % 2;
        for (let x = -reach - stepX; x <= reach + stepX; x += stepX) {
          ctx.fillText(text, x + (odd ? stepX / 2 : 0), y);
        }
      }
    } else {
      const margin = Math.min(w, h) * 0.04;
      const [vy, hx] = [this.pos[0], this.pos[1]];
      ctx.textAlign = hx === 'l' ? 'left' : hx === 'r' ? 'right' : 'center';
      ctx.textBaseline = vy === 't' ? 'top' : vy === 'b' ? 'bottom' : 'middle';
      const x = hx === 'l' ? margin : hx === 'r' ? w - margin : w / 2;
      const y = vy === 't' ? margin : vy === 'b' ? h - margin : h / 2;
      ctx.translate(x, y);
      ctx.rotate(rad);
      ctx.fillText(text, 0, 0);
    }
    ctx.restore();
  },

  /** Watermark one file at full resolution and return {name, blob}. */
  async stamp(file, canvas = null, img = null) {
    const own = !canvas;
    let url = null;
    try {
      if (own) {
        url = URL.createObjectURL(file);
        img = await loadImage(url);
        canvas = document.createElement('canvas');
        canvas.width = img.naturalWidth;
        canvas.height = img.naturalHeight;
        this.render(canvas, img);
      }
      const jpg = file.type === 'image/jpeg';
      const type = jpg ? 'image/jpeg' : 'image/png';
      const blob = await new Promise((res) => canvas.toBlob(res, type, 0.95));
      return blob ? { name: `${baseName(file.name)}-watermarked.${jpg ? 'jpg' : 'png'}`, blob } : null;
    } finally {
      if (url) URL.revokeObjectURL(url);
    }
  },

  async download() {
    if (!this.img) return;
    // The visible canvas is already the full-resolution result — reuse it.
    const out = await this.stamp(this.file, this.canvas, this.img);
    if (!out) { Toast.show(t('Export failed'), 'error'); return; }
    download(out.blob, out.name);
    $('#wm-done').innerHTML = `<i class="fa-solid fa-circle-check text-green-500 mr-1"></i>Saved ${this.canvas.width} × ${this.canvas.height}px · ${Math.round(out.blob.size / 1024)} KB`;
  },

  async downloadAll() {
    const btn = $('[data-batch-zip]');
    const label = btn.querySelector('[data-batch-label]');
    const original = label.textContent;
    btn.disabled = true;
    label.textContent = 'Watermarking…';
    try {
      const entries = [await this.stamp(this.file, this.canvas, this.img)];
      for (const f of this.queue) entries.push(await this.stamp(f));
      await zipDownload(entries.filter(Boolean), 'clearbg-watermarked.zip');
    } catch {
      Toast.show(t('Could not build the ZIP'), 'error');
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
