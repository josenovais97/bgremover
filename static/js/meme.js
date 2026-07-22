/**
 * Meme generator — 100% client-side.
 *
 * Draws an uploaded image to a canvas, stamps classic top/bottom captions in a
 * bold outlined meme font (draggable, word-wrapped, uppercase by default), and
 * exports a PNG/JPG or copies to the clipboard. Nothing is uploaded.
 *
 * Helpers ($, Toast, loadImage, t, …) come from window.CBG (static/js/kit.js),
 * a classic script — a local ES import would break, since Django's hashed-manifest
 * static storage does not rewrite ES-module import paths.
 */

const { $, $$, Toast, loadImage, download, t } = CBG;

/* --------------------------------------------------------------- helpers */
const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));

const toBlob = (canvas, mime, q) => new Promise((res) => canvas.toBlob(res, mime, q));

function rafThrottle(fn) {
  let scheduled = false;
  return () => { if (scheduled) return; scheduled = true; requestAnimationFrame(() => { scheduled = false; fn(); }); };
}

const MAX_DIM = 1600; // cap the working resolution so huge photos stay snappy

/* --------------------------------------------------------------------- app */
const App = {
  img: null,
  imgUrl: null,
  style: { font: 'Impact', size: 8, outline: 6, color: '#ffffff', caps: true },
  texts: { top: { content: '', x: 0.5, y: 0.09 }, bottom: { content: '', x: 0.5, y: 0.91 } },
  boxes: { top: null, bottom: null },
  drag: null,

  init() {
    this.dropzone = $('#mm-dropzone');
    this.input = $('#mm-input');
    this.editor = $('#mm-editor');
    this.canvas = $('#mm-canvas');
    this.ctx = this.canvas.getContext('2d');

    const open = () => this.input.click();
    $('#mm-browse').addEventListener('click', (e) => { e.stopPropagation(); open(); });
    this.dropzone.addEventListener('click', open);
    this.dropzone.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); } });
    this.input.addEventListener('change', (e) => this.load(e.target.files[0]));

    const icon = $('#mm-icon');
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
    $('#mm-top').addEventListener('input', (e) => { this.texts.top.content = e.target.value; this.render(); });
    $('#mm-bottom').addEventListener('input', (e) => { this.texts.bottom.content = e.target.value; this.render(); });
    $$('.mm-font').forEach((b) => b.addEventListener('click', () => {
      this.style.font = b.dataset.font;
      $$('.mm-font').forEach((x) => { const a = x === b; x.classList.toggle('ring-2', a); x.classList.toggle('ring-primary', a); });
      this.ensureFont();
      this.render();
    }));
    $('#mm-size').addEventListener('input', (e) => { this.style.size = +e.target.value; render(); });
    $('#mm-outline').addEventListener('input', (e) => { this.style.outline = +e.target.value; render(); });
    $('#mm-color').addEventListener('input', (e) => { this.style.color = e.target.value; render(); });
    $('#mm-caps').addEventListener('change', (e) => { this.style.caps = e.target.checked; this.render(); });

    this.canvas.addEventListener('pointerdown', (e) => {
      const key = this.hitText(e);
      if (!key) return;
      this.canvas.setPointerCapture?.(e.pointerId);
      this.drag = { key, x: e.clientX, y: e.clientY };
    });
    this.canvas.addEventListener('pointermove', (e) => this.onDrag(e));
    ['pointerup', 'pointercancel', 'pointerleave'].forEach((ev) => this.canvas.addEventListener(ev, () => { this.drag = null; }));

    $('#mm-download').addEventListener('click', () => this.export('image/png'));
    $('#mm-download-jpg').addEventListener('click', () => this.export('image/jpeg'));
    $('#mm-copy').addEventListener('click', () => this.copy());
    $('#mm-new').addEventListener('click', () => this.reset());
  },

  async load(file) {
    this.input.value = '';
    if (!file || !/^image\//.test(file.type)) { Toast.show(t('Please choose an image'), 'error'); return; }
    try {
      if (this.imgUrl) URL.revokeObjectURL(this.imgUrl);
      this.imgUrl = URL.createObjectURL(file);
      this.img = await loadImage(this.imgUrl);
    } catch {
      Toast.show(t("Couldn't open that image"), 'error');
      return;
    }
    const iw = this.img.naturalWidth, ih = this.img.naturalHeight;
    const scale = Math.min(1, MAX_DIM / Math.max(iw, ih));
    this.canvas.width = Math.max(1, Math.round(iw * scale));
    this.canvas.height = Math.max(1, Math.round(ih * scale));
    this.dropzone.parentElement.classList.add('hidden');
    this.editor.classList.remove('hidden');
    this.ensureFont();
    this.render();
  },

  ensureFont() {
    if (!document.fonts || !document.fonts.load) return;
    document.fonts.load(`700 40px "${this.style.font}"`).then(() => this.render()).catch(() => {});
  },

  /* ------------------------------------------------------------ drawing */
  render() {
    const { canvas, ctx, img } = this;
    if (!img) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    this.drawBlock('top');
    this.drawBlock('bottom');
  },

  wrap(ctx, text, maxW) {
    const words = text.split(/\s+/).filter(Boolean);
    if (!words.length) return [''];
    const lines = [];
    let cur = '';
    for (const w of words) {
      const test = cur ? `${cur} ${w}` : w;
      if (ctx.measureText(test).width > maxW && cur) { lines.push(cur); cur = w; }
      else cur = test;
    }
    if (cur) lines.push(cur);
    return lines;
  },

  drawBlock(key) {
    const t = this.texts[key];
    const raw = t.content;
    if (!raw.trim()) { this.boxes[key] = null; return; }
    const { canvas, ctx, style } = this;
    const W = canvas.width, H = canvas.height;
    const content = style.caps ? raw.toUpperCase() : raw;
    const fs = (style.size / 100) * W;

    ctx.save();
    ctx.font = `700 ${fs}px "${style.font}", Impact, "Anton", sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    const maxW = W * 0.94;
    const lines = [];
    content.replace(/\r/g, '').split('\n').forEach((l) => this.wrap(ctx, l, maxW).forEach((x) => lines.push(x)));
    const lh = fs * 1.12;
    const blockH = lh * lines.length;
    const cx = clamp(t.x, 0, 1) * W;
    const cy = clamp(t.y, 0, 1) * H;
    const top = cy - blockH / 2;

    let maxLineW = 0;
    lines.forEach((l) => { maxLineW = Math.max(maxLineW, ctx.measureText(l || ' ').width); });
    this.boxes[key] = { x: cx - maxLineW / 2 - fs * 0.15, y: top - fs * 0.1, w: maxLineW + fs * 0.3, h: blockH + fs * 0.2 };

    ctx.lineJoin = 'round';
    ctx.miterLimit = 2;
    ctx.strokeStyle = '#000000';
    ctx.lineWidth = fs * (style.outline / 50);
    if (ctx.lineWidth > 0) lines.forEach((l, i) => ctx.strokeText(l, cx, top + lh * (i + 0.5)));
    ctx.fillStyle = style.color;
    lines.forEach((l, i) => ctx.fillText(l, cx, top + lh * (i + 0.5)));
    ctx.restore();
  },

  /* ------------------------------------------------------------ dragging */
  pointerPixel(e) {
    const r = this.canvas.getBoundingClientRect();
    return { px: (e.clientX - r.left) * (this.canvas.width / r.width), py: (e.clientY - r.top) * (this.canvas.height / r.height) };
  },

  hitText(e) {
    const { px, py } = this.pointerPixel(e);
    for (const key of ['top', 'bottom']) {
      const b = this.boxes[key];
      if (b && px >= b.x && px <= b.x + b.w && py >= b.y && py <= b.y + b.h) return key;
    }
    return null;
  },

  onDrag(e) {
    if (!this.drag) return;
    const r = this.canvas.getBoundingClientRect();
    const dx = (e.clientX - this.drag.x) * (this.canvas.width / r.width);
    const dy = (e.clientY - this.drag.y) * (this.canvas.height / r.height);
    const t = this.texts[this.drag.key];
    t.x = clamp(t.x + dx / this.canvas.width, 0, 1);
    t.y = clamp(t.y + dy / this.canvas.height, 0, 1);
    this.drag.x = e.clientX;
    this.drag.y = e.clientY;
    this.render();
  },

  /* ------------------------------------------------------------- export */
  compose(fmt) {
    const c = document.createElement('canvas');
    c.width = this.canvas.width;
    c.height = this.canvas.height;
    const x = c.getContext('2d');
    if (fmt === 'image/jpeg') { x.fillStyle = '#ffffff'; x.fillRect(0, 0, c.width, c.height); }
    x.drawImage(this.canvas, 0, 0);
    return c;
  },

  async export(fmt) {
    if (!this.img) return;
    const blob = await toBlob(this.compose(fmt), fmt, 0.92);
    if (!blob) { Toast.show(t('Export failed'), 'error'); return; }
    const ext = fmt === 'image/jpeg' ? 'jpg' : 'png';
    download(blob, `meme.${ext}`);
  },

  async copy() {
    if (!this.img) return;
    try {
      const blob = await toBlob(this.compose('image/png'), 'image/png');
      await navigator.clipboard.write([new ClipboardItem({ 'image/png': blob })]);
      Toast.show(t('Meme copied to clipboard'), 'success');
    } catch {
      Toast.show(t('Copy not supported here — use Download'), 'error');
    }
  },

  reset() {
    this.editor.classList.add('hidden');
    this.dropzone.parentElement.classList.remove('hidden');
    if (this.imgUrl) { URL.revokeObjectURL(this.imgUrl); this.imgUrl = null; }
    this.img = null;
    this.texts.top.content = '';
    this.texts.bottom.content = '';
    this.texts.top.y = 0.09;
    this.texts.bottom.y = 0.91;
    $('#mm-top').value = '';
    $('#mm-bottom').value = '';
  },
};

document.addEventListener('DOMContentLoaded', () => App.init());
