/**
 * WhatsApp / Telegram sticker maker — 100% client-side.
 *
 * Removes the background from a photo (lazy-loaded @imgly model), stamps the
 * classic sticker outline around the cut-out, lets you drag a caption on top,
 * and exports a ready-to-use 512×512 transparent WebP (kept under WhatsApp's
 * 100KB limit) or a PNG. Nothing is uploaded.
 *
 * Helpers ($, Toast, loadImage, t, …) come from window.CBG (static/js/kit.js),
 * a classic script — it has already run by the time this deferred module does,
 * so nothing here needs an import to reach them.
 */

const { $, $$, Toast, loadImage, download, share, canShare, t } = CBG;

/* --------------------------------------------------------------- helpers */
const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));

function rafThrottle(fn) {
  let scheduled = false;
  return () => { if (scheduled) return; scheduled = true; requestAnimationFrame(() => { scheduled = false; fn(); }); };
}

/** Rounded-rect path, for the caption highlight. */
function roundRectPath(ctx, x, y, w, h, r) {
  r = Math.min(r, w / 2, h / 2);
  ctx.beginPath();
  if (ctx.roundRect) { ctx.roundRect(x, y, w, h, r); return; }
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}

/** Recolour a sprite to a solid tint, keeping its alpha (for the outline). */
function tintCanvas(src, color) {
  const c = document.createElement('canvas');
  c.width = src.width; c.height = src.height;
  const x = c.getContext('2d');
  x.drawImage(src, 0, 0);
  x.globalCompositeOperation = 'source-in';
  x.fillStyle = color;
  x.fillRect(0, 0, c.width, c.height);
  return c;
}

const SIZE = 512;
const MODEL_CDN = 'https://cdn.jsdelivr.net/npm/@imgly/background-removal@1.6.0/+esm';

/* --------------------------------------------------------------------- app */
const SUB_MIN = 0.5;
const SUB_MAX = 3;

const App = {
  cutout: null,
  outline: { on: true, color: '#ffffff', width: 3.5 }, // width = % of the 512 frame
  // Subject transform, applied on top of the automatic fit. dx/dy are fractions
  // of the frame so the whole thing is resolution-independent — the same numbers
  // paint the 512 export, the on-screen preview and the chat chips.
  sub: { scale: 1, dx: 0, dy: 0, rot: 0, flip: false },
  text: { content: '', font: 'Anton', color: '#ffffff', size: 12, x: 0.5, y: 0.84,
          pill: false, pillColor: '#000000' },
  _textBox: null,

  init() {
    this.dropzone = $('#stk-dropzone');
    this.input = $('#stk-input');
    this.editor = $('#stk-editor');
    this.canvas = $('#stk-canvas');

    const open = () => this.input.click();
    $('#stk-browse').addEventListener('click', (e) => { e.stopPropagation(); open(); });
    this.dropzone.addEventListener('click', open);
    this.dropzone.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); } });
    this.input.addEventListener('change', (e) => this.load(e.target.files[0]));

    const icon = $('#stk-icon');
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

    // Outline controls.
    $('#stk-outline-on').addEventListener('change', (e) => {
      this.outline.on = e.target.checked;
      $('#stk-outline-opts').classList.toggle('opacity-40', !this.outline.on);
      $('#stk-outline-opts').classList.toggle('pointer-events-none', !this.outline.on);
      this.render();
    });
    $('#stk-outline-color').addEventListener('input', (e) => { this.outline.color = e.target.value; render(); });
    $('#stk-outline-width').addEventListener('input', (e) => { this.outline.width = +e.target.value; render(); });

    // Text controls.
    $('#stk-text').addEventListener('input', (e) => { this.text.content = e.target.value; this.render(); });
    $$('.stk-font').forEach((b) => b.addEventListener('click', () => {
      this.text.font = b.dataset.font;
      $$('.stk-font').forEach((x) => { const a = x === b; x.classList.toggle('ring-2', a); x.classList.toggle('ring-primary', a); });
      this.ensureFont();
      this.render();
    }));
    $('#stk-text-color').addEventListener('input', (e) => { this.text.color = e.target.value; render(); });
    $('#stk-text-size').addEventListener('input', (e) => { this.text.size = +e.target.value; this.render(); });

    // Subject controls. The sliders and the gestures below drive the same state,
    // so each has to write the other's UI back — syncSub() is that one direction.
    $('#stk-zoom').addEventListener('input', (e) => { this.sub.scale = +e.target.value / 100; this.syncSubLabels(); render(); });
    $('#stk-rotate').addEventListener('input', (e) => { this.sub.rot = +e.target.value; this.syncSubLabels(); render(); });
    $('#stk-flip').addEventListener('click', () => { this.sub.flip = !this.sub.flip; this.render(); });
    $('#stk-reset-sub').addEventListener('click', () => this.resetSubject());

    // Text pill.
    $('#stk-text-pill').addEventListener('change', (e) => { this.text.pill = e.target.checked; this.render(); });
    $('#stk-pill-color').addEventListener('input', (e) => { this.text.pillColor = e.target.value; render(); });

    /* Pointer gestures. Grabbing the caption drags the caption; grabbing anywhere
       else moves the subject — which is what a user reaches for first, and there
       is nothing else on the canvas to hit. Two fingers pinch-zoom. */
    this._pointers = new Map();
    this.canvas.addEventListener('pointerdown', (e) => {
      if (!this.cutout) return;
      this.canvas.setPointerCapture?.(e.pointerId);
      this._pointers.set(e.pointerId, e);
      if (this._pointers.size === 2) {
        this._pinch = { dist: this.pinchDist(), scale: this.sub.scale };
        this.drag = null;
        return;
      }
      this.drag = { x: e.clientX, y: e.clientY, target: this.hitText(e) ? 'text' : 'subject' };
      this.canvas.classList.add('cursor-grabbing');
    });
    this.canvas.addEventListener('pointermove', (e) => {
      if (this._pointers.has(e.pointerId)) this._pointers.set(e.pointerId, e);
      if (this._pinch && this._pointers.size === 2) {
        const d = this.pinchDist();
        if (this._pinch.dist > 0) this.setScale(this._pinch.scale * (d / this._pinch.dist));
        return;
      }
      this.onDrag(e);
    });
    ['pointerup', 'pointercancel', 'pointerleave'].forEach((ev) =>
      this.canvas.addEventListener(ev, (e) => {
        this._pointers.delete(e.pointerId);
        if (this._pointers.size < 2) this._pinch = null;
        this.drag = null;
        this.canvas.classList.remove('cursor-grabbing');
      }));
    // passive:false — zooming the sticker has to win over scrolling the page.
    this.canvas.addEventListener('wheel', (e) => {
      if (!this.cutout) return;
      e.preventDefault();
      this.setScale(this.sub.scale * (e.deltaY < 0 ? 1.08 : 1 / 1.08));
    }, { passive: false });

    $('#stk-download').addEventListener('click', () => this.export('image/webp'));
    $('#stk-download-png').addEventListener('click', () => this.export('image/png'));
    $('#stk-share').addEventListener('click', () => this.shareSticker());
    $('#stk-new').addEventListener('click', () => this.reset());
    this.offerShare();

    this.setBusy(false);
  },

  /**
   * Show the share button, and demote Download beside it, where sharing works.
   *
   * Probed with a real one-pixel WebP because canShare() inspects the file's
   * type: desktop Chrome has navigator.share but refuses file payloads, so a
   * bare feature-check would raise a button that does nothing on the platform
   * where it is least useful anyway.
   */
  offerShare() {
    const c = document.createElement('canvas');
    c.width = c.height = 1;
    c.toBlob((probe) => {
      if (!probe || !canShare(probe, 'sticker.webp')) return;
      $('#stk-share').hidden = false;
      // Two full-width gradient buttons would compete; Download steps back to
      // the outline treatment its PNG/New siblings already use.
      const dl = $('#stk-download');
      dl.className = dl.className
        .replace(/text-white |shadow-lg shadow-primary\/30 |bg-gradient-to-r from-primary to-primaryHover hover:brightness-110/g, '')
        + ' border border-gray-300 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800';
    }, 'image/webp');
  },

  setBusy(busy, text) {
    // Twinkle over the preview for the whole wait; hooked in here so every exit
    // path — success, failure, a future caller — stops it.
    if (busy && !this._stopIdle) this._stopIdle = CBG.sparkleLoopOver(this.canvas);
    if (!busy && this._stopIdle) { this._stopIdle(); this._stopIdle = null; }
    $('#stk-status').classList.toggle('hidden', !busy);
    if (text) $('#stk-status-text').textContent = text;
    $('#stk-download').disabled = busy || !this.cutout;
    $('#stk-download-png').disabled = busy || !this.cutout;
    $('#stk-share').disabled = busy || !this.cutout;
  },

  async load(file) {
    this.input.value = '';
    if (!file || !/^image\//.test(file.type)) { Toast.show(t('Please choose an image'), 'error'); return; }
    this.cutout = null;
    // A new photo gets the automatic framing, not the last photo's zoom.
    this.resetSubject();
    this.dropzone.parentElement.classList.add('hidden');
    this.editor.classList.remove('hidden');
    this.setBusy(true, 'Removing background…');
    this.render();
    try {
      const [{ removeBackground }, { removalConfig, markRemovalSucceeded }] = await Promise.all([
        import(MODEL_CDN),
        import('./accel.js'),
      ]);
      // Model + CPU/GPU backend are chosen once in accel.js, shared with
      // every tool page that cuts out a subject.
      const blob = await removeBackground(file, await removalConfig());
      markRemovalSucceeded();  // full-quality weights from the next load on (accel.js)
      if (this.cutoutUrl) URL.revokeObjectURL(this.cutoutUrl);
      this.cutoutUrl = URL.createObjectURL(blob);
      this.cutout = await loadImage(this.cutoutUrl);
      this.setBusy(false);
      this.ensureFont();
      this.render();
      // The sticker frame insets and centres the cut-out, so pass that rect.
      CBG.sparkleOver(this.canvas, this.cutout, {
        rect: this.spriteRect(this.canvas.width),
      });
      window.__clearbgReport?.(1);
      Toast.show(t('Background removed — add your outline & text'), 'success');
    } catch (err) {
      console.error('[sticker] bg removal failed:', err);
      Toast.show(t('Background removal failed'), 'error');
      this.setBusy(false);
    }
  },

  ensureFont() {
    if (!document.fonts || !document.fonts.load) return;
    document.fonts.load(`700 40px ${this.text.font}`).then(() => this.render()).catch(() => {});
  },

  /* ------------------------------------------------------------ drawing */
  outlinePx(size) { return this.outline.on ? (this.outline.width / 100) * size : 0; },

  /** Where the cut-out lands inside a `size`×`size` sticker frame. */
  spriteRect(size) {
    const margin = size * 0.06; // transparent margin WhatsApp expects
    const ow = this.outlinePx(size);
    const box = size - 2 * margin - 2 * ow;
    const cw = this.cutout.naturalWidth || this.cutout.width;
    const ch = this.cutout.naturalHeight || this.cutout.height;
    const scale = Math.min(box / cw, box / ch);
    const w = cw * scale;
    const h = ch * scale;
    return { x: (size - w) / 2, y: (size - h) / 2, w, h };
  },

  /**
   * The transformed cut-out, alone, on its own `size`×`size` layer.
   *
   * Rendering the subject to a full-frame layer first is what lets zoom, rotate
   * and flip exist at all: the outline is stamped by offsetting a silhouette,
   * and offsetting a *rotated* sprite around its own centre would swing the
   * outline with it. Against a square layer the stamp is always frame-aligned,
   * so the die-cut border stays an even width at any angle.
   */
  subjectLayer(size) {
    const layer = document.createElement('canvas');
    layer.width = layer.height = size;
    const lx = layer.getContext('2d');
    const { w, h } = this.spriteRect(size);
    const s = this.sub;
    lx.translate(size / 2 + s.dx * size, size / 2 + s.dy * size);
    lx.rotate((s.rot * Math.PI) / 180);
    lx.scale(s.flip ? -s.scale : s.scale, s.scale);
    lx.drawImage(this.cutout, -w / 2, -h / 2, w, h);
    return layer;
  },

  /** Composite the sticker (cut-out + outline + text) into `canvas` at `size`. */
  paint(canvas, size) {
    canvas.width = size; canvas.height = size;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, size, size);
    if (!this.cutout) return;

    const ow = this.outlinePx(size);
    const layer = this.subjectLayer(size);

    if (ow > 0) {
      const sil = tintCanvas(layer, this.outline.color);
      const steps = 48;
      for (let i = 0; i < steps; i++) {
        const a = (i / steps) * Math.PI * 2;
        ctx.drawImage(sil, Math.cos(a) * ow, Math.sin(a) * ow);
      }
    }
    ctx.drawImage(layer, 0, 0);
    this.drawText(ctx, size);
  },

  drawText(ctx, size) {
    const t = this.text;
    if (!t.content.trim()) { this._textBox = null; return; }
    const lines = t.content.replace(/\r/g, '').split('\n');
    const fs = (t.size / 100) * size;
    const lh = fs * 1.15;
    const cx = t.x * size;
    const cy = t.y * size;
    const blockH = lh * lines.length;

    ctx.save();
    ctx.font = `700 ${fs}px ${t.font}, sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    let maxW = 0;
    lines.forEach((l) => { maxW = Math.max(maxW, ctx.measureText(l || ' ').width); });
    this._textBox = { x: cx - maxW / 2 - fs * 0.2, y: cy - blockH / 2 - fs * 0.1, w: maxW + fs * 0.4, h: blockH + fs * 0.2 };

    if (t.pill) {
      const b = this._textBox;
      // A little wider than the hit box, so the letters are not touching the edge.
      const pad = fs * 0.25;
      ctx.fillStyle = t.pillColor;
      roundRectPath(ctx, b.x - pad, b.y - pad * 0.6, b.w + pad * 2, b.h + pad * 1.2, fs * 0.45);
      ctx.fill();
    } else {
      // Black outline around the letters so any colour reads on any sticker. The
      // pill already guarantees contrast, and stroking on top of it reads as a
      // heavy drop shadow rather than as a caption.
      ctx.lineJoin = 'round';
      ctx.strokeStyle = 'rgba(0,0,0,0.85)';
      ctx.lineWidth = fs * 0.18;
      lines.forEach((l, i) => ctx.strokeText(l, cx, cy - blockH / 2 + lh * (i + 0.5)));
    }
    ctx.fillStyle = t.color;
    lines.forEach((l, i) => ctx.fillText(l, cx, cy - blockH / 2 + lh * (i + 0.5)));
    ctx.restore();
  },

  pointerPixel(e) {
    const r = this.canvas.getBoundingClientRect();
    return { px: (e.clientX - r.left) * (this.canvas.width / r.width), py: (e.clientY - r.top) * (this.canvas.height / r.height) };
  },

  hitText(e) {
    const b = this._textBox;
    if (!b) return false;
    const { px, py } = this.pointerPixel(e);
    return px >= b.x && px <= b.x + b.w && py >= b.y && py <= b.y + b.h;
  },

  onDrag(e) {
    if (!this.drag) return;
    const r = this.canvas.getBoundingClientRect();
    const dx = (e.clientX - this.drag.x) * (this.canvas.width / r.width);
    const dy = (e.clientY - this.drag.y) * (this.canvas.height / r.height);
    if (this.drag.target === 'text') {
      this.text.x = clamp(this.text.x + dx / this.canvas.width, 0, 1);
      this.text.y = clamp(this.text.y + dy / this.canvas.height, 0, 1);
    } else {
      // Half a frame of travel in each direction: enough to push any part of the
      // subject to any corner, without letting it be dragged out of sight.
      this.sub.dx = clamp(this.sub.dx + dx / this.canvas.width, -0.5, 0.5);
      this.sub.dy = clamp(this.sub.dy + dy / this.canvas.height, -0.5, 0.5);
    }
    this.drag = { x: e.clientX, y: e.clientY };
    this.render();
  },

  /** Distance between the two active pointers, for pinch-zoom. */
  pinchDist() {
    const [a, b] = [...this._pointers.values()];
    return Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY);
  },

  /** Numbers beside the sliders — a gesture moves the slider, so it moves these too. */
  syncSubLabels() {
    $('#stk-zoom-val').textContent = `${Math.round(this.sub.scale * 100)}%`;
    $('#stk-rot-val').textContent = `${Math.round(this.sub.rot)}°`;
  },

  setScale(v) {
    this.sub.scale = clamp(v, SUB_MIN, SUB_MAX);
    $('#stk-zoom').value = Math.round(this.sub.scale * 100);
    this.syncSubLabels();
    this.render();
  },

  resetSubject() {
    this.sub = { scale: 1, dx: 0, dy: 0, rot: 0, flip: false };
    $('#stk-zoom').value = 100;
    $('#stk-rotate').value = 0;
    this.syncSubLabels();
    this.render();
  },

  render() {
    this.paint(this.canvas, SIZE);
    this.paintChips();
  },

  /**
   * Redraw the two chat-wallpaper thumbnails from the main canvas.
   *
   * A straight downscale of what was just painted, rather than a second
   * composite — the chips can never disagree with the preview, and the cost is
   * one drawImage each. The chip canvases stay transparent so the wallpaper
   * colour behind them (set on the wrapper in the template) shows through.
   */
  paintChips() {
    ['#stk-chip-light', '#stk-chip-dark'].forEach((sel) => {
      const chip = $(sel);
      if (!chip) return;
      const cx = chip.getContext('2d');
      cx.clearRect(0, 0, chip.width, chip.height);
      if (this.cutout) cx.drawImage(this.canvas, 0, 0, chip.width, chip.height);
    });
  },

  /* ------------------------------------------------------------- export */

  /**
   * Encode the sticker at `fmt`, or null if encoding failed.
   *
   * Split out of `export()` so the share button can reach the same bytes: the
   * WhatsApp size squeeze belongs to the sticker, not to the download button.
   */
  async encode(fmt) {
    if (!this.cutout) return null;
    const c = document.createElement('canvas');
    this.paint(c, SIZE);
    const isWebp = fmt === 'image/webp';
    let quality = 0.92;
    let blob = await new Promise((res) => c.toBlob(res, fmt, quality));
    // WhatsApp caps stickers at 100KB — step quality down for WebP until it fits.
    if (isWebp) {
      while (blob && blob.size > 100 * 1024 && quality > 0.4) {
        quality -= 0.12;
        blob = await new Promise((res) => c.toBlob(res, fmt, quality));
      }
    }
    return blob;
  },

  /** Report the size of what just left the tool, in the note under the buttons. */
  note(verb, ext, size) {
    const kb = Math.round(size / 1024);
    $('#stk-size-note').innerHTML =
      `<i class="fa-solid fa-circle-check text-green-500 mr-1"></i>${verb} ${ext.toUpperCase()} · ${kb} KB`
      + (ext === 'webp' && kb <= 100 ? ' · WhatsApp ready' : '');
  },

  async export(fmt) {
    if (!this.cutout) return;
    const isWebp = fmt === 'image/webp';
    const blob = await this.encode(fmt);
    if (!blob) { Toast.show(t('Export failed'), 'error'); return; }
    // Some browsers can't encode WebP — fall back to PNG rather than mislabel it.
    if (isWebp && blob.type !== 'image/webp') {
      Toast.show(t('WebP not supported here — downloading PNG instead'), 'info');
      return this.export('image/png');
    }
    const ext = isWebp ? 'webp' : 'png';
    download(blob, `sticker.${ext}`);
    this.note('Saved', ext, blob.size);
  },

  /**
   * Hand the sticker straight to the OS share sheet — the WhatsApp/Telegram path.
   *
   * This is the only export that finishes the job on a phone: a downloaded
   * sticker lands in Files and has to be found again, while a shared one goes
   * into the chat the user opened this page to post in. Nothing is uploaded —
   * navigator.share moves the bytes locally to the app the user picks.
   */
  async shareSticker() {
    const blob = await this.encode('image/webp');
    if (!blob) { Toast.show(t('Export failed'), 'error'); return; }
    // A WebP the sheet refuses is still shareable as PNG on some platforms.
    const name = blob.type === 'image/webp' ? 'sticker.webp' : 'sticker.png';
    if (await share(blob, name)) this.note('Shared', name.split('.').pop(), blob.size);
  },

  reset() {
    this.editor.classList.add('hidden');
    this.dropzone.parentElement.classList.remove('hidden');
    if (this.cutoutUrl) { URL.revokeObjectURL(this.cutoutUrl); this.cutoutUrl = null; }
    this.cutout = null;
    this.text.content = '';
    $('#stk-text').value = '';
    this.resetSubject();
  },
};

document.addEventListener('DOMContentLoaded', () => {
  App.init();
});
