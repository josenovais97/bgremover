/**
 * Border & Polaroid frame — 100% client-side.
 *
 * Wraps a photo in either a plain border (solid or two-colour gradient, any
 * width/colour, optional rounded corners) or a Polaroid-style white frame with a
 * thick captioned bottom edge. Everything composites onto a canvas and exports
 * PNG or JPG. Nothing is uploaded. Shared helpers come from window.CBG.
 */
const { $, $$, Toast, loadImage, dropzone, download, baseName, remember, t } = CBG;

const prefs = remember('border');

const App = {
  style: 'solid',
  width: 6,          // border thickness, % of the shorter image edge
  radius: 0,         // outer corner radius, % of the shorter edge
  color: '#ffffff',
  color2: '',        // gradient second stop ('' = flat colour)
  angle: 90,
  caption: '',
  fmt: 'image/png',

  init() {
    this.dropzone = $('#bd-dropzone');
    this.hero = this.dropzone.closest('section');
    this.input = $('#bd-input');
    this.editor = $('#bd-editor');
    this.canvas = $('#bd-canvas');
    this.ctx = this.canvas.getContext('2d');

    dropzone(this.dropzone, {
      input: this.input,
      icon: $('#bd-icon'),
      browse: $('#bd-browse'),
      multiple: false,
      onFiles: (files) => this.load(files[0]),
    });

    $$('.bd-style').forEach((b) => b.addEventListener('click', () => this.setStyle(b.dataset.style)));
    $('#bd-width').addEventListener('input', (e) => { this.width = +e.target.value; this.draw(); });
    $('#bd-radius').addEventListener('input', (e) => { this.radius = +e.target.value; this.draw(); });
    $('#bd-color').addEventListener('input', (e) => { this.color = e.target.value; this.draw(); });
    $('#bd-color2').addEventListener('input', (e) => { this.color2 = e.target.value; this.draw(); });
    $('#bd-gradient').addEventListener('change', (e) => {
      this.color2 = e.target.checked ? ($('#bd-color2').value || '#000000') : '';
      $('#bd-color2-wrap').classList.toggle('hidden', !e.target.checked);
      this.draw();
    });
    $('#bd-angle').addEventListener('input', (e) => { this.angle = +e.target.value; this.draw(); });
    $('#bd-caption').addEventListener('input', (e) => { this.caption = e.target.value; this.draw(); });
    $$('.bd-fmt').forEach((b) => b.addEventListener('click', () => this.setFormat(b.dataset.fmt)));
    $('#bd-download').addEventListener('click', () => this.download());
    $('#bd-new').addEventListener('click', () => this.reset());

    const saved = prefs.get();
    if (saved.color) { this.color = saved.color; $('#bd-color').value = saved.color; }
    this.setStyle(this.style);
  },

  setStyle(style) {
    this.style = style;
    $$('.bd-style').forEach((b) => {
      const a = b.dataset.style === style;
      b.classList.toggle('bg-primary', a); b.classList.toggle('text-white', a);
      b.setAttribute('aria-selected', a);
    });
    // Caption only makes sense on the Polaroid; corner controls only on solid.
    $('#bd-caption-wrap').classList.toggle('hidden', style !== 'polaroid');
    $('#bd-solid-controls').classList.toggle('hidden', style !== 'solid');
    this.draw();
  },

  setFormat(fmt) {
    this.fmt = fmt;
    $$('.bd-fmt').forEach((b) => {
      const a = b.dataset.fmt === fmt;
      b.classList.toggle('ring-2', a); b.classList.toggle('ring-primary', a);
    });
  },

  async load(file) {
    if (this.url) URL.revokeObjectURL(this.url);
    this.url = URL.createObjectURL(file);
    this.name = baseName(file.name);
    try { this.img = await loadImage(this.url); } catch { Toast.show(t('Could not read that image'), 'error'); return; }
    this.hero.classList.add('hidden');
    this.editor.classList.remove('hidden');
    this.draw();
  },

  draw() {
    if (!this.img) return;
    const iw = this.img.naturalWidth, ih = this.img.naturalHeight;
    const short = Math.min(iw, ih);

    if (this.style === 'polaroid') {
      // Classic proportions: even margin on three sides, a deep captioned base.
      const pad = Math.round(short * 0.06);
      const base = Math.round(short * 0.22);
      const W = iw + pad * 2, H = ih + pad + base;
      this.canvas.width = W; this.canvas.height = H;
      const ctx = this.ctx;
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, W, H);
      // A faint inner edge so the photo doesn't float on pure white.
      ctx.drawImage(this.img, pad, pad, iw, ih);
      ctx.strokeStyle = 'rgba(0,0,0,0.08)';
      ctx.lineWidth = Math.max(1, Math.round(short * 0.003));
      ctx.strokeRect(pad, pad, iw, ih);
      if (this.caption) {
        ctx.fillStyle = '#374151';
        const fs = Math.round(base * 0.32);
        ctx.font = `${fs}px "Inter", system-ui, sans-serif`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(this.caption, W / 2, ih + pad + base / 2, W - pad * 2);
      }
      return;
    }

    // Solid / gradient border.
    const bw = Math.round(short * (this.width / 100));
    const W = iw + bw * 2, H = ih + bw * 2;
    this.canvas.width = W; this.canvas.height = H;
    const ctx = this.ctx;
    ctx.clearRect(0, 0, W, H);
    const rad = Math.round(short * (this.radius / 100));

    ctx.save();
    if (rad > 0) { roundRect(ctx, 0, 0, W, H, rad); ctx.clip(); }
    if (this.color2) {
      const a = (this.angle % 360) * Math.PI / 180;
      const cx = W / 2, cy = H / 2, len = Math.max(W, H) / 2;
      const g = ctx.createLinearGradient(cx - Math.cos(a) * len, cy - Math.sin(a) * len,
        cx + Math.cos(a) * len, cy + Math.sin(a) * len);
      g.addColorStop(0, this.color); g.addColorStop(1, this.color2);
      ctx.fillStyle = g;
    } else {
      ctx.fillStyle = this.color;
    }
    ctx.fillRect(0, 0, W, H);
    // Clip the photo to the same rounded profile, inset by the border width.
    const innerRad = Math.max(0, rad - bw);
    roundRect(ctx, bw, bw, iw, ih, innerRad);
    ctx.clip();
    ctx.drawImage(this.img, bw, bw, iw, ih);
    ctx.restore();
  },

  async download() {
    if (!this.img) return;
    prefs.set({ color: this.color });
    const type = this.fmt;
    if (type === 'image/jpeg') {
      // Flatten onto white — a JPG has no alpha, and rounded corners would
      // otherwise turn black.
      const flat = document.createElement('canvas');
      flat.width = this.canvas.width; flat.height = this.canvas.height;
      const fx = flat.getContext('2d');
      fx.fillStyle = '#ffffff'; fx.fillRect(0, 0, flat.width, flat.height);
      fx.drawImage(this.canvas, 0, 0);
      flat.toBlob((b) => this.save(b, 'jpg'), 'image/jpeg', 0.95);
    } else {
      this.canvas.toBlob((b) => this.save(b, 'png'), 'image/png');
    }
  },

  save(blob, ext) {
    if (!blob) { Toast.show(t('Export failed'), 'error'); return; }
    download(blob, `${this.name || 'image'}-framed.${ext}`);
  },

  reset() {
    this.editor.classList.add('hidden');
    this.hero.classList.remove('hidden');
    if (this.url) { URL.revokeObjectURL(this.url); this.url = null; }
    this.img = null;
  },
};

function roundRect(ctx, x, y, w, h, r) {
  r = Math.min(r, w / 2, h / 2);
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}

document.addEventListener('DOMContentLoaded', () => App.init());
