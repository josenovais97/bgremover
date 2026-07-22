/**
 * Blur / redact tool — 100% client-side.
 *
 * Drag boxes over faces, plates or sensitive text; each box is blurred,
 * pixelated or blacked out. Everything runs on a canvas in the browser — the
 * photo is never uploaded, which is the whole point for sensitive images.
 *
 * Regions are stored in image-pixel coordinates so the effect exports at full
 * resolution regardless of the on-screen preview size. A region is either a
 * rectangle ({type:'rect', x,y,w,h}) dragged as a box, or a freehand polygon
 * ({type:'path', points:[{x,y}…]}) traced with the lasso. Self-contained.
 */

const { $, $$, Toast, loadImage, download, t } = CBG;

const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));

const App = {
  original: null,
  regions: [],       // committed regions (rect or path), in image-pixel coords
  pending: null,     // region currently being drawn
  drawing: false,    // true while a pointer drag is in progress
  drawStart: null,   // rect-mode: the anchor corner
  shape: 'box',      // 'box' (drag a rectangle) | 'lasso' (trace a freehand shape)
  mode: 'blur',      // 'blur' | 'pixelate' | 'black' (applies to all regions)
  strength: 50,

  init() {
    this.dropzone = $('#rd-dropzone');
    this.input = $('#rd-input');
    this.editor = $('#rd-editor');
    this.canvas = $('#rd-canvas');
    this.hint = $('#rd-hint');

    const open = () => this.input.click();
    $('#rd-browse').addEventListener('click', (e) => { e.stopPropagation(); open(); });
    this.dropzone.addEventListener('click', open);
    this.dropzone.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); } });
    this.input.addEventListener('change', (e) => this.load(e.target.files[0]));

    const icon = $('#rd-icon');
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach((evt) =>
      this.dropzone.addEventListener(evt, (e) => { e.preventDefault(); e.stopPropagation(); }));
    ['dragenter', 'dragover'].forEach((evt) => this.dropzone.addEventListener(evt, () => { this.dropzone.classList.add('border-primary', 'bg-primary/5'); icon.classList.add('scale-110'); }));
    ['dragleave', 'drop'].forEach((evt) => this.dropzone.addEventListener(evt, () => { this.dropzone.classList.remove('border-primary', 'bg-primary/5'); icon.classList.remove('scale-110'); }));
    this.dropzone.addEventListener('drop', (e) => this.load(e.dataTransfer.files[0]));
    document.addEventListener('paste', (e) => {
      const f = [...(e.clipboardData?.items || [])].find((i) => i.kind === 'file');
      if (f) this.load(f.getAsFile());
    });

    $$('.rd-shape').forEach((b) => b.addEventListener('click', () => {
      this.shape = b.dataset.shape;
      $$('.rd-shape').forEach((x) => { const a = x === b; x.classList.toggle('ring-2', a); x.classList.toggle('ring-primary', a); });
      if (this.hint) this.hint.textContent = this.shape === 'lasso'
        ? 'Trace around each area you want to hide'
        : 'Drag over each area you want to hide';
    }));
    $$('.rd-mode').forEach((b) => b.addEventListener('click', () => {
      this.mode = b.dataset.mode;
      $$('.rd-mode').forEach((x) => { const a = x === b; x.classList.toggle('ring-2', a); x.classList.toggle('ring-primary', a); });
      $('#rd-strength-row').style.visibility = this.mode === 'black' ? 'hidden' : 'visible';
      this.render();
    }));
    $('#rd-strength').addEventListener('input', (e) => { this.strength = +e.target.value; this.render(); });
    // Auto-detect faces via the browser's own Shape Detection API. It is not
    // universally implemented, so the button is only revealed where it exists —
    // no model download, no fallback that quietly does nothing.
    const auto = $('#rd-auto');
    if (auto && 'FaceDetector' in window) {
      auto.classList.remove('hidden');
      auto.addEventListener('click', () => this.detectFaces());
    }

    $('#rd-undo').addEventListener('click', () => { this.regions.pop(); this.updateButtons(); this.render(); });
    $('#rd-clear').addEventListener('click', () => { this.regions = []; this.updateButtons(); this.render(); });
    $('#rd-download').addEventListener('click', () => this.export('image/png'));
    $('#rd-download-jpg').addEventListener('click', () => this.export('image/jpeg'));
    $('#rd-new').addEventListener('click', () => this.reset());

    // Draw a region on the canvas: a dragged box, or a traced freehand shape.
    this.canvas.addEventListener('pointerdown', (e) => {
      if (!this.original) return;
      this.canvas.setPointerCapture?.(e.pointerId);
      const p = this.toImage(e);
      this.drawing = true;
      if (this.shape === 'lasso') {
        this.pending = { type: 'path', points: [p] };
      } else {
        this.drawStart = p;
        this.pending = { type: 'rect', x: p.x, y: p.y, w: 0, h: 0 };
      }
    });
    this.canvas.addEventListener('pointermove', (e) => {
      if (!this.drawing) return;
      const p = this.toImage(e);
      if (this.pending.type === 'path') {
        // Skip near-duplicate points so the polygon stays light on long traces.
        const last = this.pending.points[this.pending.points.length - 1];
        if (Math.hypot(p.x - last.x, p.y - last.y) > 2) this.pending.points.push(p);
      } else {
        this.pending = { type: 'rect', ...this.rect(this.drawStart, p) };
      }
      this.render();
    });
    ['pointerup', 'pointercancel'].forEach((ev) => this.canvas.addEventListener(ev, () => {
      if (this.drawing && this.pending) {
        const bb = this.bbox(this.pending);
        const enough = this.pending.type === 'path' ? this.pending.points.length > 2 : true;
        if (enough && bb.w > 4 && bb.h > 4) this.regions.push(this.pending);
      }
      this.drawing = false;
      this.drawStart = null;
      this.pending = null;
      this.updateButtons();
      this.render();
    }));
  },

  // Bounding box (image-pixel coords) of a rect or path region.
  bbox(region) {
    if (region.type === 'path') {
      const xs = region.points.map((p) => p.x), ys = region.points.map((p) => p.y);
      const x = Math.min(...xs), y = Math.min(...ys);
      return { x, y, w: Math.max(...xs) - x, h: Math.max(...ys) - y };
    }
    return { x: region.x, y: region.y, w: region.w, h: region.h };
  },

  // Set the current clip path to a region (rectangle or closed polygon).
  clipTo(ctx, region) {
    ctx.beginPath();
    if (region.type === 'path') {
      const p = region.points;
      ctx.moveTo(p[0].x, p[0].y);
      for (let i = 1; i < p.length; i++) ctx.lineTo(p[i].x, p[i].y);
      ctx.closePath();
    } else {
      ctx.rect(region.x, region.y, region.w, region.h);
    }
    ctx.clip();
  },

  // Trace a region's outline (does not fill); `close` shuts a polygon.
  outline(ctx, region, close) {
    ctx.beginPath();
    if (region.type === 'path') {
      const p = region.points;
      if (!p.length) return;
      ctx.moveTo(p[0].x, p[0].y);
      for (let i = 1; i < p.length; i++) ctx.lineTo(p[i].x, p[i].y);
      if (close) ctx.closePath();
      ctx.stroke();
    } else {
      ctx.strokeRect(region.x, region.y, region.w, region.h);
    }
  },

  // Pointer → image-pixel coordinates (the canvas is the image's native size).
  toImage(e) {
    const r = this.canvas.getBoundingClientRect();
    const x = clamp((e.clientX - r.left) / r.width, 0, 1) * this.canvas.width;
    const y = clamp((e.clientY - r.top) / r.height, 0, 1) * this.canvas.height;
    return { x, y };
  },

  rect(a, b) {
    return { x: Math.min(a.x, b.x), y: Math.min(a.y, b.y), w: Math.abs(a.x - b.x), h: Math.abs(a.y - b.y) };
  },

  /**
   * Add a region over every face the browser can find.
   *
   * Uses the on-device FaceDetector (Shape Detection API) — like everything else
   * here it runs locally, so an image with faces in it is still never uploaded.
   * Boxes are padded outwards because the detector returns a tight crop that
   * leaves hair and chin visible, which is not what "hide this face" means.
   */
  async detectFaces() {
    if (!this.original) return;
    const btn = $('#rd-auto');
    btn.disabled = true;
    try {
      const detector = new window.FaceDetector({ fastMode: false });
      const faces = await detector.detect(this.original);
      if (!faces.length) { Toast.show(t('No faces found — draw over them by hand'), 'error'); return; }
      for (const { boundingBox: b } of faces) {
        const padX = b.width * 0.18;
        const padY = b.height * 0.22;
        this.regions.push({
          type: 'rect',
          x: Math.max(0, b.x - padX),
          y: Math.max(0, b.y - padY),
          w: Math.min(this.original.width, b.width + padX * 2),
          h: Math.min(this.original.height, b.height + padY * 2),
        });
      }
      this.updateButtons();
      this.render();
      Toast.show(CBG.plural(faces.length, '{n} face hidden — adjust or add more by hand', '{n} faces hidden — adjust or add more by hand'));
    } catch {
      Toast.show(t('Face detection is not available in this browser'), 'error');
    } finally {
      btn.disabled = false;
    }
  },

  updateButtons() {
    const has = this.regions.length > 0;
    $('#rd-undo').disabled = !has;
    $('#rd-clear').disabled = !has;
    $('#rd-download').disabled = $('#rd-download-jpg').disabled = !this.original;
  },

  // Apply the current effect inside one region. The effect is painted over the
  // region's bounding box but clipped to its exact shape, so rectangles and
  // freehand polygons are handled the same way.
  applyRegion(ctx, w, h, region) {
    const { x, y, w: bw, h: bh } = this.bbox(region);
    if (bw < 1 || bh < 1) return;
    ctx.save();
    this.clipTo(ctx, region);
    if (this.mode === 'black') {
      ctx.fillStyle = '#000';
      ctx.fillRect(x, y, bw, bh);
    } else if (this.mode === 'pixelate') {
      const block = Math.max(2, Math.round((this.strength / 100) * Math.min(bw, bh) * 0.35));
      const tw = Math.max(1, Math.round(bw / block));
      const th = Math.max(1, Math.round(bh / block));
      const tmp = document.createElement('canvas');
      tmp.width = tw; tmp.height = th;
      tmp.getContext('2d').drawImage(this.original, x, y, bw, bh, 0, 0, tw, th);
      ctx.imageSmoothingEnabled = false;
      ctx.drawImage(tmp, 0, 0, tw, th, x, y, bw, bh);
      ctx.imageSmoothingEnabled = true;
    } else { // blur
      const radius = Math.max(2, (this.strength / 100) * Math.max(w, h) * 0.04);
      ctx.filter = `blur(${radius}px)`;
      ctx.drawImage(this.original, 0, 0, w, h);
    }
    ctx.restore();
  },

  paint(canvas, outlines) {
    const w = this.original.naturalWidth, h = this.original.naturalHeight;
    canvas.width = w; canvas.height = h;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, w, h);
    ctx.drawImage(this.original, 0, 0, w, h);
    for (const box of this.regions) this.applyRegion(ctx, w, h, box);
    if (this.pending) this.applyRegion(ctx, w, h, this.pending);
    if (outlines) {
      const line = Math.max(1, Math.round(Math.max(w, h) * 0.0025));
      ctx.lineWidth = line;
      ctx.strokeStyle = 'rgba(255,255,255,0.9)';
      for (const region of this.regions) this.outline(ctx, region, true);
      if (this.pending) {
        ctx.setLineDash([line * 3, line * 3]);
        ctx.strokeStyle = 'rgba(255,255,255,0.95)';
        // Leave an in-progress lasso open so the trailing edge follows the cursor.
        this.outline(ctx, this.pending, this.pending.type !== 'path');
        ctx.setLineDash([]);
      }
    }
  },

  render() {
    if (!this.original) return;
    this.paint(this.canvas, true);
  },

  async load(file) {
    this.input.value = '';
    if (!file || !/^image\//.test(file.type)) { Toast.show(t('Please choose an image'), 'error'); return; }
    if (this.srcUrl) URL.revokeObjectURL(this.srcUrl);
    this.srcUrl = URL.createObjectURL(file);
    try {
      this.original = await loadImage(this.srcUrl);
    } catch {
      Toast.show(t('Could not read that image'), 'error'); return;
    }
    this.regions = [];
    this.dropzone.parentElement.classList.add('hidden');
    this.editor.classList.remove('hidden');
    this.updateButtons();
    this.render();
  },

  async export(fmt) {
    if (!this.original) return;
    const c = document.createElement('canvas');
    this.paint(c, false); // no outlines in the export
    const ext = fmt === 'image/png' ? 'png' : 'jpg';
    const blob = await new Promise((res) => c.toBlob(res, fmt, 0.95));
    if (!blob) { Toast.show(t('Export failed'), 'error'); return; }
    download(blob, `redacted.${ext}`);
    $('#rd-done').innerHTML = `<i class="fa-solid fa-circle-check text-green-500 mr-1"></i>Saved ${ext.toUpperCase()} · ${this.regions.length} area${this.regions.length === 1 ? '' : 's'} hidden`;
  },

  reset() {
    this.editor.classList.add('hidden');
    this.dropzone.parentElement.classList.remove('hidden');
    if (this.srcUrl) { URL.revokeObjectURL(this.srcUrl); this.srcUrl = null; }
    this.original = null;
    this.regions = [];
    this.pending = null;
    $('#rd-done').textContent = '';
  },
};

document.addEventListener('DOMContentLoaded', () => App.init());
