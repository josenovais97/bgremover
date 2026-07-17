/**
 * Watermark tool — 100% client-side.
 *
 * Draws the photo to a canvas at full resolution, then bakes a text watermark
 * on top: either a single mark anchored to one of nine positions, or a tiled
 * pattern repeated across the whole image (harder to crop out). Nothing is
 * uploaded.
 */
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];

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
  text: '© Your Name',
  mode: 'single',
  pos: 'br',
  size: 5,        // % of the image's smaller side
  opacity: 45,
  rotate: 0,
  color: '#ffffff',
  shadow: true,

  init() {
    this.dropzone = $('#wm-dropzone');
    // The hero section (dropzone + demo) is hidden once a photo loads. Resolved
    // via closest('section') rather than dropzone.parentElement so it survives the
    // dropzone being wrapped in a grid column alongside the demo.
    this.hero = this.dropzone.closest('section');
    this.input = $('#wm-input');
    this.editor = $('#wm-editor');
    this.canvas = $('#wm-canvas');

    const open = () => this.input.click();
    $('#wm-browse').addEventListener('click', (e) => { e.stopPropagation(); open(); });
    this.dropzone.addEventListener('click', open);
    this.dropzone.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); } });
    this.input.addEventListener('change', (e) => this.load(e.target.files[0]));

    const icon = $('#wm-icon');
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach((evt) =>
      this.dropzone.addEventListener(evt, (e) => { e.preventDefault(); e.stopPropagation(); }));
    ['dragenter', 'dragover'].forEach((evt) => this.dropzone.addEventListener(evt, () => { this.dropzone.classList.add('border-primary', 'bg-primary/5'); icon.classList.add('scale-110'); }));
    ['dragleave', 'drop'].forEach((evt) => this.dropzone.addEventListener(evt, () => { this.dropzone.classList.remove('border-primary', 'bg-primary/5'); icon.classList.remove('scale-110'); }));
    this.dropzone.addEventListener('drop', (e) => this.load(e.dataTransfer.files[0]));
    document.addEventListener('paste', (e) => {
      const f = [...(e.clipboardData?.items || [])].find((i) => i.kind === 'file');
      if (f) this.load(f.getAsFile());
    });

    $('#wm-text').addEventListener('input', (e) => { this.text = e.target.value; this.render(); });

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
  },

  async load(file) {
    this.input.value = '';
    if (!file || !/^image\//.test(file.type)) { Toast.show('Please choose an image', 'error'); return; }
    this.file = file;
    if (this.url) URL.revokeObjectURL(this.url);
    this.url = URL.createObjectURL(file);
    try { this.img = await loadImage(this.url); } catch { Toast.show('Could not read that image', 'error'); return; }
    this.canvas.width = this.img.naturalWidth;
    this.canvas.height = this.img.naturalHeight;
    this.render();
    this.hero.classList.add('hidden');
    this.editor.classList.remove('hidden');
    $('#wm-done').textContent = `${this.img.naturalWidth} × ${this.img.naturalHeight} px — full resolution, exported as-is`;
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

  render() {
    if (!this.img) return;
    const { width: w, height: h } = this.canvas;
    const ctx = this.canvas.getContext('2d');
    ctx.clearRect(0, 0, w, h);
    ctx.drawImage(this.img, 0, 0, w, h);

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

  async download() {
    if (!this.img) return;
    const jpg = this.file.type === 'image/jpeg';
    const type = jpg ? 'image/jpeg' : 'image/png';
    const blob = await new Promise((res) => this.canvas.toBlob(res, type, 0.95));
    if (!blob) { Toast.show('Export failed', 'error'); return; }
    const base = this.file.name.replace(/\.[^.]+$/, '');
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = `${base}-watermarked.${jpg ? 'jpg' : 'png'}`;
    document.body.appendChild(a); a.click(); URL.revokeObjectURL(url); a.remove();
    $('#wm-done').innerHTML = `<i class="fa-solid fa-circle-check text-green-500 mr-1"></i>Saved ${this.canvas.width} × ${this.canvas.height}px · ${Math.round(blob.size / 1024)} KB`;
  },

  reset() {
    this.editor.classList.add('hidden');
    this.hero.classList.remove('hidden');
    if (this.url) { URL.revokeObjectURL(this.url); this.url = null; }
    this.img = null;
  },
};

document.addEventListener('DOMContentLoaded', () => App.init());
