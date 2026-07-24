/**
 * Screenshot beautifier — 100% client-side.
 *
 * Centres a screenshot on a gradient or solid backdrop with padding, rounded
 * corners, a soft drop shadow and an optional macOS-style browser window frame
 * (the "launch post" look). Everything composites onto a canvas and exports PNG
 * or JPG. Nothing is uploaded. Shared helpers come from window.CBG.
 */
const { $, $$, Toast, loadImage, dropzone, download, baseName, remember, t } = CBG;

const prefs = remember('screenshot');

// macOS-style traffic lights, identical in both frame themes.
const LIGHTS = ['#ff5f57', '#febc2e', '#28c840'];

const App = {
  c1: '#6366f1',     // backdrop first stop ('' = transparent backdrop)
  c2: '#a855f7',     // second stop ('' = solid colour)
  angle: 135,
  pad: 10,           // padding, % of the shot's shorter edge
  radius: 4,         // corner radius, % of the shot's shorter edge
  shadow: 55,        // 0–100
  frame: 'light',    // none | light | dark
  ratio: 'auto',     // auto | 16:9 | 4:3 | 1:1
  fmt: 'image/png',

  init() {
    this.dropzone = $('#sb-dropzone');
    this.hero = this.dropzone.closest('section');
    this.input = $('#sb-input');
    this.editor = $('#sb-editor');
    this.canvas = $('#sb-canvas');
    this.ctx = this.canvas.getContext('2d');

    dropzone(this.dropzone, {
      input: this.input,
      icon: $('#sb-icon'),
      browse: $('#sb-browse'),
      multiple: false,
      onFiles: (files) => this.load(files[0]),
    });

    $$('.sb-bg').forEach((b) => b.addEventListener('click', () => this.setBg(b)));
    $('#sb-color').addEventListener('input', (e) => {
      // Typing in the picker implies the custom swatch is the one you want.
      const custom = $('#sb-bg-custom');
      custom.dataset.c1 = e.target.value;
      custom.style.background = e.target.value;
      this.setBg(custom);
    });
    $('#sb-pad').addEventListener('input', (e) => { this.pad = +e.target.value; this.draw(); });
    $('#sb-radius').addEventListener('input', (e) => { this.radius = +e.target.value; this.draw(); });
    $('#sb-shadow').addEventListener('input', (e) => { this.shadow = +e.target.value; this.draw(); });
    $$('.sb-frame').forEach((b) => b.addEventListener('click', () => this.setFrame(b.dataset.frame)));
    $$('.sb-ratio').forEach((b) => b.addEventListener('click', () => this.setRatio(b.dataset.ratio)));
    $$('.sb-fmt').forEach((b) => b.addEventListener('click', () => this.setFormat(b.dataset.fmt)));
    $('#sb-download').addEventListener('click', () => this.download());
    $('#sb-new').addEventListener('click', () => this.reset());

    // Restore the last backdrop; fall back to the first preset.
    const saved = prefs.get();
    if (saved.c1 !== undefined) { this.c1 = saved.c1; this.c2 = saved.c2 || ''; this.angle = saved.angle || 135; }
    const match = $$('.sb-bg').find((b) => b.dataset.c1 === this.c1 && (b.dataset.c2 || '') === this.c2);
    this.markBg(match || $$('.sb-bg')[0]);
  },

  markBg(btn) {
    $$('.sb-bg').forEach((b) => {
      const a = b === btn;
      b.classList.toggle('ring-2', a);
      b.classList.toggle('border-white', a);
      b.setAttribute('aria-pressed', a);
    });
  },

  setBg(btn) {
    this.c1 = btn.dataset.c1;
    this.c2 = btn.dataset.c2 || '';
    this.angle = +(btn.dataset.angle || 135);
    this.markBg(btn);
    $('#sb-custom-wrap').classList.toggle('hidden', btn.id !== 'sb-bg-custom');
    this.draw();
  },

  setFrame(frame) {
    this.frame = frame;
    $$('.sb-frame').forEach((b) => {
      const a = b.dataset.frame === frame;
      b.classList.toggle('bg-primary', a); b.classList.toggle('text-white', a);
      b.setAttribute('aria-pressed', a);
    });
    this.draw();
  },

  setRatio(ratio) {
    this.ratio = ratio;
    $$('.sb-ratio').forEach((b) => {
      const a = b.dataset.ratio === ratio;
      b.classList.toggle('bg-primary', a); b.classList.toggle('text-white', a);
      b.setAttribute('aria-pressed', a);
    });
    this.draw();
  },

  setFormat(fmt) {
    this.fmt = fmt;
    $$('.sb-fmt').forEach((b) => {
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

  /** The shot block = optional title bar + the screenshot, sharing one outline. */
  metrics() {
    const iw = this.img.naturalWidth, ih = this.img.naturalHeight;
    const barH = this.frame === 'none' ? 0 : Math.round(Math.max(28, iw * 0.045));
    const sw = iw, sh = ih + barH;
    const short = Math.min(sw, sh);
    return { iw, ih, barH, sw, sh, short };
  },

  draw() {
    if (!this.img) return;
    const { iw, ih, barH, sw, sh, short } = this.metrics();
    const pad = Math.round(short * (this.pad / 100));

    let W = sw + pad * 2, H = sh + pad * 2;
    if (this.ratio !== 'auto') {
      const [rw, rh] = this.ratio.split(':').map(Number);
      const r = rw / rh;
      W = Math.round(Math.max(W, H * r));
      H = Math.round(W / r);
    }
    this.canvas.width = W; this.canvas.height = H;
    const ctx = this.ctx;
    ctx.clearRect(0, 0, W, H);

    this.paintBackdrop(ctx, W, H);

    const ox = Math.round((W - sw) / 2), oy = Math.round((H - sh) / 2);
    const rad = Math.round(short * (this.radius / 100));

    // Shadow is cast by the whole block, then everything inside is clipped to
    // the same rounded profile so the bar and image can't poke past a corner.
    ctx.save();
    if (this.shadow > 0) {
      const s = this.shadow / 100;
      ctx.shadowColor = `rgba(15, 23, 42, ${0.18 + s * 0.3})`;
      ctx.shadowBlur = short * s * 0.12;
      ctx.shadowOffsetY = short * s * 0.03;
    }
    roundRect(ctx, ox, oy, sw, sh, rad);
    ctx.fillStyle = this.frame === 'dark' ? '#1e293b' : '#ffffff';
    ctx.fill();
    ctx.restore();

    ctx.save();
    roundRect(ctx, ox, oy, sw, sh, rad);
    ctx.clip();
    if (barH) this.paintBar(ctx, ox, oy, sw, barH);
    ctx.drawImage(this.img, ox, oy + barH, iw, ih);
    ctx.restore();
  },

  paintBackdrop(ctx, W, H) {
    if (!this.c1) return; // transparent
    if (this.c2) {
      const a = (this.angle % 360) * Math.PI / 180;
      const cx = W / 2, cy = H / 2, len = Math.max(W, H) / 2;
      const g = ctx.createLinearGradient(cx - Math.cos(a) * len, cy - Math.sin(a) * len,
        cx + Math.cos(a) * len, cy + Math.sin(a) * len);
      g.addColorStop(0, this.c1); g.addColorStop(1, this.c2);
      ctx.fillStyle = g;
    } else {
      ctx.fillStyle = this.c1;
    }
    ctx.fillRect(0, 0, W, H);
  },

  paintBar(ctx, x, y, w, h) {
    const dark = this.frame === 'dark';
    ctx.fillStyle = dark ? '#1e293b' : '#f8fafc';
    ctx.fillRect(x, y, w, h);
    // Hairline between the bar and the page, like a real window.
    ctx.fillStyle = dark ? 'rgba(255,255,255,0.08)' : 'rgba(15,23,42,0.08)';
    ctx.fillRect(x, y + h - Math.max(1, Math.round(h * 0.03)), w, Math.max(1, Math.round(h * 0.03)));
    // Traffic lights.
    const r = h * 0.16, gap = r * 2.6, cx0 = x + h * 0.55, cy = y + h / 2;
    LIGHTS.forEach((c, i) => {
      ctx.beginPath();
      ctx.arc(cx0 + gap * i, cy, r, 0, Math.PI * 2);
      ctx.fillStyle = c;
      ctx.fill();
    });
    // Address pill, centred.
    const pw = w * 0.42, ph = h * 0.5;
    ctx.fillStyle = dark ? '#334155' : '#e2e8f0';
    roundRect(ctx, x + (w - pw) / 2, cy - ph / 2, pw, ph, ph / 2);
    ctx.fill();
  },

  async download() {
    if (!this.img) return;
    prefs.set({ c1: this.c1, c2: this.c2, angle: this.angle });
    if (this.fmt === 'image/jpeg') {
      // A JPG has no alpha: a transparent backdrop would export black.
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
    download(blob, `${this.name || 'screenshot'}-beautified.${ext}`);
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
