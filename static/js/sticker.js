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

const { $, $$, Toast, loadImage, download, share, canShare, t, plural } = CBG;

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

// WhatsApp's own pack rules, enforced in the UI so a user never assembles 2 or 31.
const PACK_MIN = 3;
const PACK_MAX = 30;

const EMOJI = ['😂', '❤️', '🔥', '👍', '😍', '😎', '💀', '✨', '🎉',
               '💯', '👀', '🙏', '🤣', '😭', '🤔', '⭐', '💖', '👑'];

// The platform emoji font, in the order the platforms actually ship them.
const EMOJI_FONT = '"Apple Color Emoji","Segoe UI Emoji","Noto Color Emoji",sans-serif';

const App = {
  cutout: null,
  outline: { on: true, color: '#ffffff', width: 3.5 }, // width = % of the 512 frame
  // Subject transform, applied on top of the automatic fit. dx/dy are fractions
  // of the frame so the whole thing is resolution-independent — the same numbers
  // paint the 512 export, the on-screen preview and the chat chips.
  sub: { scale: 1, dx: 0, dy: 0, rot: 0, flip: false },
  text: { content: '', font: 'Anton', color: '#ffffff', size: 12, x: 0.5, y: 0.84,
          pill: false, pillColor: '#000000' },
  // Emoji stamped on top of the cut-out. Fractions of the frame again, so one
  // list paints the preview and the export identically.
  decos: [],      // {id, char, x, y, size, rot}
  selected: null, // id of the deco being edited, or null
  pack: [],       // {id, blob, url} — assembled stickers, in memory only
  _nextId: 1,
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

    // Decorations: the palette is built from EMOJI rather than written out in the
    // template, so adding one is a single-array edit.
    const palette = $('#stk-emoji');
    EMOJI.forEach((ch) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'py-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition focus:outline-none focus-visible:ring-2 focus-visible:ring-primary';
      b.textContent = ch;
      b.setAttribute('aria-label', `Add ${ch}`);
      b.addEventListener('click', () => this.addDeco(ch));
      palette.appendChild(b);
    });
    $('#stk-deco-size').addEventListener('input', (e) => this.updateDeco('size', +e.target.value));
    $('#stk-deco-rot').addEventListener('input', (e) => this.updateDeco('rot', +e.target.value));
    $('#stk-deco-del').addEventListener('click', () => {
      this.decos = this.decos.filter((d) => d.id !== this.selected);
      this.selectDeco(null);
    });

    // Pack.
    $('#stk-pack-add').addEventListener('click', () => this.addToPack());
    $('#stk-pack-dl').addEventListener('click', () => this.downloadPack());
    this.syncPack();

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
      // Topmost first: a decoration you can see above the caption is the one you
      // meant to grab. Clicking bare canvas deselects and falls through to the
      // subject, so there is no mode to get stuck in.
      const deco = this.hitDeco(e);
      if (deco) {
        if (this.selected !== deco.id) this.selectDeco(deco.id);
        this.drag = { x: e.clientX, y: e.clientY, target: 'deco', id: deco.id };
      } else {
        if (this.selected !== null) this.selectDeco(null);
        this.drag = { x: e.clientX, y: e.clientY, target: this.hitText(e) ? 'text' : 'subject' };
      }
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
    $('#stk-pack-add').disabled = busy || !this.cutout || this.pack.length >= PACK_MAX;
  },

  async load(file) {
    this.input.value = '';
    if (!file || !/^image\//.test(file.type)) { Toast.show(t('Please choose an image'), 'error'); return; }
    this.cutout = null;
    // A new photo gets the automatic framing, not the last photo's zoom, and a
    // clean canvas — but NOT a cleared pack: loading the next photo is exactly
    // how you build one.
    this.decos = [];
    this.selectDeco(null);
    this.resetSubject();
    this.dropzone.parentElement.classList.add('hidden');
    this.editor.classList.remove('hidden');
    this.setBusy(true, t('Removing background…'));
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
      this.syncPack();  // a cut-out exists now, so "Add to pack" comes alive
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
    this.drawDecos(ctx, size);
    this.drawText(ctx, size);
  },

  /** Bounding box of a decoration, in frame pixels. */
  decoBox(d, size) {
    const fs = (d.size / 100) * size;
    return { x: d.x * size - fs / 2, y: d.y * size - fs / 2, w: fs, h: fs, fs };
  },

  drawDecos(ctx, size) {
    for (const d of this.decos) {
      const fs = (d.size / 100) * size;
      ctx.save();
      ctx.translate(d.x * size, d.y * size);
      ctx.rotate((d.rot * Math.PI) / 180);
      ctx.font = `${fs}px ${EMOJI_FONT}`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(d.char, 0, 0);
      ctx.restore();
    }
  },

  /**
   * Paint the selection marquee onto the overlay canvas.
   *
   * Separate from paint() on purpose — see the template comment. The overlay is
   * cleared and redrawn on every render, so a deselect leaves nothing behind.
   */
  drawChrome() {
    const ov = $('#stk-overlay');
    if (!ov) return;
    const ctx = ov.getContext('2d');
    ctx.clearRect(0, 0, ov.width, ov.height);
    const d = this.decos.find((x) => x.id === this.selected);
    if (!d) return;
    const b = this.decoBox(d, ov.width);
    const pad = b.fs * 0.12;
    ctx.save();
    ctx.translate(d.x * ov.width, d.y * ov.width);
    ctx.rotate((d.rot * Math.PI) / 180);
    ctx.strokeStyle = '#6366f1';
    ctx.lineWidth = Math.max(2, ov.width * 0.005);
    ctx.setLineDash([ov.width * 0.02, ov.width * 0.015]);
    ctx.strokeRect(-b.w / 2 - pad, -b.h / 2 - pad, b.w + pad * 2, b.h + pad * 2);
    ctx.restore();
  },

  addDeco(char) {
    if (!this.cutout) return;
    const d = { id: this._nextId++, char, x: 0.5, y: 0.3, size: 18, rot: 0 };
    this.decos.push(d);
    this.selectDeco(d.id);
  },

  selectDeco(id) {
    this.selected = id;
    const d = this.decos.find((x) => x.id === id);
    $('#stk-deco-opts').classList.toggle('hidden', !d);
    $('#stk-deco-del').hidden = !d;
    $('#stk-deco-hint').classList.toggle('hidden', !!d);
    if (d) { $('#stk-deco-size').value = d.size; $('#stk-deco-rot').value = d.rot; }
    this.render();
  },

  updateDeco(key, value) {
    const d = this.decos.find((x) => x.id === this.selected);
    if (!d) return;
    d[key] = value;
    this.render();
  },

  /** Topmost decoration under the pointer, or null. */
  hitDeco(e) {
    const { px, py } = this.pointerPixel(e);
    const size = this.canvas.width;
    // Reverse order: the last drawn is the one on top, so it wins the hit.
    for (let i = this.decos.length - 1; i >= 0; i--) {
      const b = this.decoBox(this.decos[i], size);
      if (px >= b.x && px <= b.x + b.w && py >= b.y && py <= b.y + b.h) return this.decos[i];
    }
    return null;
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
    if (this.drag.target === 'deco') {
      const d = this.decos.find((x) => x.id === this.drag.id);
      if (d) {
        d.x = clamp(d.x + dx / this.canvas.width, 0, 1);
        d.y = clamp(d.y + dy / this.canvas.height, 0, 1);
      }
    } else if (this.drag.target === 'text') {
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
    this.drawChrome();
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

  /* --------------------------------------------------------------- pack */

  /**
   * Freeze the current sticker into the pack.
   *
   * The bytes are encoded once, here — not at download time — so the thumbnail
   * you see in the strip is exactly what ships, and editing on for the next
   * sticker cannot retroactively change one you already added.
   */
  async addToPack() {
    if (!this.cutout || this.pack.length >= PACK_MAX) return;
    const blob = await this.encode('image/webp');
    if (!blob) { Toast.show(t('Export failed'), 'error'); return; }
    this.pack.push({ id: this._nextId++, blob, url: URL.createObjectURL(blob) });
    this.syncPack();
    Toast.show(t('Added to pack'), 'success');
  },

  removeFromPack(id) {
    const i = this.pack.findIndex((s) => s.id === id);
    if (i < 0) return;
    URL.revokeObjectURL(this.pack[i].url);
    this.pack.splice(i, 1);
    this.syncPack();
  },

  /** Repaint the strip, the counter and the enabled/disabled states. */
  syncPack() {
    const n = this.pack.length;
    $('#stk-pack-count').textContent = `${n} / ${PACK_MAX}`;
    $('#stk-pack-add').disabled = !this.cutout || n >= PACK_MAX;
    $('#stk-pack-dl').disabled = n < PACK_MIN;
    // The empty-state line is the same literal the template renders, so the two
    // share one catalogue entry. It spells out PACK_MIN rather than interpolating
    // it because a Django template cannot interpolate — keep them in step.
    $('#stk-pack-hint').textContent = n === 0
      ? t('WhatsApp packs need at least 3 stickers. Import the ZIP with a sticker app like WSTick or Sticker.ly.')
      : n < PACK_MIN
        ? t('{k} more to go — WhatsApp packs need at least {min} stickers.', { k: PACK_MIN - n, min: PACK_MIN })
        : plural(n,
                 '{n} sticker ready. Import the ZIP with a sticker app like WSTick or Sticker.ly.',
                 '{n} stickers ready. Import the ZIP with a sticker app like WSTick or Sticker.ly.');

    const strip = $('#stk-pack-strip');
    strip.textContent = '';
    this.pack.forEach((s, i) => {
      const cell = document.createElement('div');
      cell.className = 'relative group';
      const img = document.createElement('img');
      img.src = s.url;
      img.alt = `Sticker ${i + 1}`;
      img.className = 'w-full aspect-square object-contain rounded-lg checkerboard';
      const del = document.createElement('button');
      del.type = 'button';
      del.className = 'absolute -top-1 -right-1 w-5 h-5 rounded-full bg-gray-900/80 text-white text-[10px] leading-none opacity-0 group-hover:opacity-100 focus:opacity-100 transition focus:outline-none focus-visible:ring-2 focus-visible:ring-primary';
      del.innerHTML = '&times;';
      del.setAttribute('aria-label', `Remove sticker ${i + 1}`);
      del.addEventListener('click', () => this.removeFromPack(s.id));
      cell.append(img, del);
      strip.appendChild(cell);
    });
  },

  /** 96×96 PNG tray icon, which WhatsApp shows in the sticker drawer. */
  async trayIcon() {
    const src = await loadImage(this.pack[0].url);
    const c = document.createElement('canvas');
    c.width = c.height = 96;
    c.getContext('2d').drawImage(src, 0, 0, 96, 96);
    return new Promise((res) => c.toBlob(res, 'image/png'));
  },

  /**
   * Bundle the pack as the ZIP the sticker apps import.
   *
   * WhatsApp itself cannot be handed a pack from a web page — the platform only
   * accepts them from an installed app — so the honest deliverable is the folder
   * layout those apps read, plus a README saying so. contents.json follows the
   * schema from WhatsApp's own sample app.
   */
  async downloadPack() {
    if (this.pack.length < PACK_MIN) return;
    const stamp = Date.now();
    const files = this.pack.map((s, i) => ({ name: `sticker-${i + 1}.webp`, blob: s.blob }));
    const tray = await this.trayIcon();
    if (tray) files.push({ name: 'tray.png', blob: tray });

    const manifest = {
      android_play_store_link: '',
      ios_app_store_link: '',
      sticker_packs: [{
        identifier: `clearbg-${stamp}`,
        name: 'My ClearBG pack',
        publisher: 'ClearBG',
        tray_image_file: 'tray.png',
        image_data_version: '1',
        avoid_cache: false,
        publisher_email: '',
        publisher_website: '',
        privacy_policy_website: '',
        license_agreement_website: '',
        stickers: this.pack.map((s, i) => ({ image_file: `sticker-${i + 1}.webp`, emojis: ['😀'] })),
      }],
    };
    files.push({ name: 'contents.json', blob: new Blob([JSON.stringify(manifest, null, 2)], { type: 'application/json' }) });
    files.push({ name: 'README.txt', blob: new Blob([
      'ClearBG sticker pack\n',
      '====================\n\n',
      `${this.pack.length} stickers, 512x512 transparent WebP, plus a 96x96 tray icon.\n\n`,
      'WhatsApp cannot install a pack straight from a web page — only an app can\n',
      'add one. To use these:\n\n',
      '  1. Copy this folder to your phone.\n',
      '  2. Open a sticker app (WSTick, Sticker.ly, Sticker Maker).\n',
      '  3. Create a new pack and add sticker-1.webp ... in order.\n\n',
      'contents.json follows the manifest format from WhatsApp\'s sample sticker\n',
      'app, so it can also be dropped straight into that project.\n\n',
      'Made at https://clearbg.pt/sticker-maker/ — nothing was uploaded.\n',
    ], { type: 'text/plain' }) });

    await CBG.zipDownload(files, `clearbg-stickers-${stamp}.zip`);
    Toast.show(t('Pack downloaded'), 'success');
  },

  reset() {
    this.editor.classList.add('hidden');
    this.dropzone.parentElement.classList.remove('hidden');
    if (this.cutoutUrl) { URL.revokeObjectURL(this.cutoutUrl); this.cutoutUrl = null; }
    this.cutout = null;
    this.text.content = '';
    $('#stk-text').value = '';
    this.decos = [];
    this.selectDeco(null);
    this.resetSubject();
    this.syncPack();  // the Add button has nothing to add until a photo is loaded
  },
};

document.addEventListener('DOMContentLoaded', () => {
  App.init();
});
