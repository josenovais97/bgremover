/**
 * Object remover — 100% client-side.
 *
 * Brush over an object, press Erase, and the brushed region is filled from its
 * surroundings. The fill is a multi-scale diffusion: the image and mask are
 * downscaled, the masked pixels are initialised by onion-peel averaging from
 * the boundary and relaxed with Jacobi iterations, and the result is upscaled
 * and feather-blended back into the full-resolution photo. No model, no
 * dependency, instant — smooth-background scenes (sky, walls, grass) fill
 * convincingly; heavy texture may need a second, smaller pass.
 *
 * Nothing is uploaded. Shared helpers come from window.CBG.
 */
const { $, $$, Toast, loadImage, dropzone, download, baseName, t } = CBG;

// Longest-side cap for the working canvas. Big enough that a phone photo keeps
// its detail, small enough that three undo snapshots don't exhaust memory.
const MAX_DIM = 4096;
// The diffusion runs at this resolution; the result is upscaled into the photo.
const FILL_DIM = 420;
const UNDO_DEPTH = 3;

// The heavy fill loops run off-thread (remove-object-worker.js) so a big brush
// area can't jank the page; the inline fallback below covers no-Worker
// browsers. Resolved relative to this module so the sibling file is found in
// production, where the module itself is served from a hashed URL.
const FILL_WORKER_URL = new URL('./remove-object-worker.js', import.meta.url).href;

const App = {
  brush: 40,
  fmt: 'png',
  drawing: false,
  dirty: false,       // any un-erased strokes on the overlay?
  undoStack: [],

  init() {
    this.hero = $('#ro-hero');
    this.editor = $('#ro-editor');
    this.canvas = $('#ro-canvas');
    this.ctx = this.canvas.getContext('2d');
    this.overlay = $('#ro-overlay');
    this.octx = this.overlay.getContext('2d');
    this.cursor = $('#ro-cursor');
    // Full-resolution stroke mask (white where brushed).
    this.mask = document.createElement('canvas');
    this.mctx = this.mask.getContext('2d');

    dropzone($('#ro-dropzone'), {
      input: $('#ro-input'),
      icon: $('#ro-icon'),
      browse: $('#ro-browse'),
      multiple: false,
      onFiles: (files) => this.load(files[0]),
    });

    const brushInput = $('#ro-brush');
    brushInput.addEventListener('input', () => {
      this.brush = +brushInput.value;
      $('#ro-brush-value').textContent = brushInput.value;
    });

    $$('.ro-fmt').forEach((b) => b.addEventListener('click', () => {
      this.fmt = b.dataset.fmt;
      $$('.ro-fmt').forEach((x) => {
        const a = x === b;
        x.classList.toggle('bg-primary', a); x.classList.toggle('text-white', a);
      });
    }));

    $('#ro-apply').addEventListener('click', () => this.erase());
    $('#ro-undo').addEventListener('click', () => this.undo());
    $('#ro-clear').addEventListener('click', () => this.clearStrokes());
    $('#ro-download').addEventListener('click', () => this.export());
    $('#ro-new').addEventListener('click', () => this.reset());

    this.overlay.addEventListener('pointerdown', (e) => this.start(e));
    this.overlay.addEventListener('pointermove', (e) => this.move(e));
    window.addEventListener('pointerup', () => { this.drawing = false; });
    this.overlay.addEventListener('pointerenter', () => this.cursor.classList.remove('hidden'));
    this.overlay.addEventListener('pointerleave', () => this.cursor.classList.add('hidden'));
  },

  async load(file) {
    const url = URL.createObjectURL(file);
    let img;
    try { img = await loadImage(url); }
    catch { URL.revokeObjectURL(url); Toast.show(t('Could not read that image'), 'error'); return; }
    this.name = baseName(file.name);

    const s = Math.min(1, MAX_DIM / Math.max(img.naturalWidth, img.naturalHeight));
    const w = Math.max(1, Math.round(img.naturalWidth * s));
    const h = Math.max(1, Math.round(img.naturalHeight * s));
    for (const c of [this.canvas, this.overlay, this.mask]) { c.width = w; c.height = h; }
    this.ctx.drawImage(img, 0, 0, w, h);
    URL.revokeObjectURL(url);

    // The overlay sits exactly over the photo whatever size CSS renders it.
    this.overlay.style.width = '100%';
    this.overlay.style.height = '100%';

    this.undoStack = [];
    this.dirty = false;
    $('#ro-undo').disabled = true;
    this.hero.classList.add('hidden');
    this.editor.classList.remove('hidden');
  },

  /** Pointer position in canvas pixels + the display→canvas scale factor. */
  pos(e) {
    const rect = this.overlay.getBoundingClientRect();
    const k = this.canvas.width / rect.width;
    return { x: (e.clientX - rect.left) * k, y: (e.clientY - rect.top) * k, k };
  },

  start(e) {
    e.preventDefault();
    this.drawing = true;
    this.last = null;
    this.move(e);
  },

  move(e) {
    const rect = this.overlay.getBoundingClientRect();
    // Brush cursor ring, in display pixels.
    this.cursor.style.width = `${this.brush}px`;
    this.cursor.style.height = `${this.brush}px`;
    this.cursor.style.left = `${e.clientX - rect.left - this.brush / 2}px`;
    this.cursor.style.top = `${e.clientY - rect.top - this.brush / 2}px`;
    if (!this.drawing) return;

    const { x, y, k } = this.pos(e);
    const r = (this.brush / 2) * k;
    for (const c of [{ ctx: this.octx, style: 'rgba(244,63,94,0.5)' }, { ctx: this.mctx, style: '#fff' }]) {
      c.ctx.strokeStyle = c.style;
      c.ctx.fillStyle = c.style;
      c.ctx.lineWidth = r * 2;
      c.ctx.lineCap = 'round';
      if (this.last) {
        c.ctx.beginPath();
        c.ctx.moveTo(this.last.x, this.last.y);
        c.ctx.lineTo(x, y);
        c.ctx.stroke();
      } else {
        c.ctx.beginPath();
        c.ctx.arc(x, y, r, 0, Math.PI * 2);
        c.ctx.fill();
      }
    }
    this.last = { x, y };
    this.dirty = true;
  },

  clearStrokes() {
    this.octx.clearRect(0, 0, this.overlay.width, this.overlay.height);
    this.mctx.clearRect(0, 0, this.mask.width, this.mask.height);
    this.dirty = false;
  },

  snapshot() {
    const c = document.createElement('canvas');
    c.width = this.canvas.width; c.height = this.canvas.height;
    c.getContext('2d').drawImage(this.canvas, 0, 0);
    this.undoStack.push(c);
    if (this.undoStack.length > UNDO_DEPTH) this.undoStack.shift();
    $('#ro-undo').disabled = false;
  },

  undo() {
    const prev = this.undoStack.pop();
    if (!prev) return;
    this.ctx.drawImage(prev, 0, 0);
    $('#ro-undo').disabled = !this.undoStack.length;
    this.clearStrokes();
  },

  async erase() {
    if (!this.dirty) { Toast.show(t('Brush over the object first'), 'error'); return; }
    $('#ro-busy').classList.remove('hidden');
    // Let the spinner paint before the synchronous fill work starts.
    await new Promise((r) => setTimeout(r, 30));
    try {
      this.snapshot();
      const filled = await this.inpaint();
      // Feathered mask: the fill fades over a few pixels so its edge never
      // prints a hard seam into the photo.
      const W = this.canvas.width, H = this.canvas.height;
      const soft = document.createElement('canvas');
      soft.width = W; soft.height = H;
      const sctx = soft.getContext('2d');
      sctx.filter = `blur(${Math.max(2, W / 800)}px)`;
      sctx.drawImage(this.mask, 0, 0);
      sctx.filter = 'none';
      sctx.globalCompositeOperation = 'source-in';
      sctx.drawImage(filled, 0, 0, W, H);
      this.ctx.drawImage(soft, 0, 0);
      this.clearStrokes();
      window.__clearbgReport?.(1);
      Toast.show(t('Object erased — download or keep brushing'));
    } catch {
      Toast.show(t('Erase failed'), 'error');
    } finally {
      $('#ro-busy').classList.add('hidden');
    }
  },

  /**
   * Diffusion fill at FILL_DIM, returned as an upscalable canvas.
   *
   * Masked pixels are initialised layer by layer from the mask boundary (each
   * layer averages its already-known neighbours), then the whole masked region
   * is relaxed with Jacobi iterations so the fill becomes a smooth membrane
   * stretched across the hole.
   *
   * Canvas work (downscale, upscale) stays here; the per-pixel loops run in
   * remove-object-worker.js so they can't jank the page. If Workers are
   * unavailable the same algorithm runs inline (fillPixels below) — the two
   * must stay in lockstep.
   */
  async inpaint() {
    const scale = Math.min(1, FILL_DIM / Math.max(this.canvas.width, this.canvas.height));
    const w = Math.max(2, Math.round(this.canvas.width * scale));
    const h = Math.max(2, Math.round(this.canvas.height * scale));

    const imgC = document.createElement('canvas');
    imgC.width = w; imgC.height = h;
    const ictx = imgC.getContext('2d', { willReadFrequently: true });
    ictx.drawImage(this.canvas, 0, 0, w, h);
    const img = ictx.getImageData(0, 0, w, h);

    const maskC = document.createElement('canvas');
    maskC.width = w; maskC.height = h;
    const mctx = maskC.getContext('2d', { willReadFrequently: true });
    mctx.drawImage(this.mask, 0, 0, w, h);
    const maskData = mctx.getImageData(0, 0, w, h).data;

    const n = w * h;
    const masked = new Uint8Array(n);        // 1 = needs filling
    for (let i = 0; i < n; i++) {
      if (maskData[i * 4 + 3] > 32) masked[i] = 1;
    }

    let filledPixels;
    if (window.Worker) {
      filledPixels = await new Promise((resolve, reject) => {
        const worker = new Worker(FILL_WORKER_URL);
        worker.onmessage = (e) => { worker.terminate(); resolve(new Uint8ClampedArray(e.data.pixels)); };
        worker.onerror = (e) => { worker.terminate(); reject(e); };
        const pixels = img.data.slice().buffer;
        worker.postMessage({ pixels, mask: masked.buffer.slice(0), w, h }, [pixels]);
      }).catch(() => null);
    }
    if (!filledPixels) {
      // No Worker (or it failed to spawn) — same algorithm, inline.
      filledPixels = img.data;
      this.fillPixels(filledPixels, masked, w, h);
    }
    ictx.putImageData(new ImageData(filledPixels, w, h), 0, 0);

    // Upscale the small fill back to photo resolution.
    const full = document.createElement('canvas');
    full.width = this.canvas.width; full.height = this.canvas.height;
    const fctx = full.getContext('2d');
    fctx.imageSmoothingEnabled = true;
    fctx.imageSmoothingQuality = 'high';
    fctx.drawImage(imgC, 0, 0, full.width, full.height);
    return full;
  },

  /** Inline fallback fill — mirrors diffusionFill in remove-object-worker.js. */
  fillPixels(d, maskArr, w, h) {
    const n = w * h;
    const unknown = new Uint8Array(maskArr);
    const masked = maskArr;
    const idx = (x, y) => y * w + x;

    // Onion peel: fill unknown pixels that touch a known one, layer by layer.
    let remaining = true;
    let guard = 0;
    while (remaining && guard++ < Math.max(w, h)) {
      remaining = false;
      const next = [];
      for (let y = 0; y < h; y++) {
        for (let x = 0; x < w; x++) {
          const i = idx(x, y);
          if (!unknown[i]) continue;
          let r = 0, g = 0, b = 0, c = 0;
          for (let dy = -1; dy <= 1; dy++) {
            for (let dx = -1; dx <= 1; dx++) {
              const nx = x + dx, ny = y + dy;
              if (nx < 0 || ny < 0 || nx >= w || ny >= h) continue;
              const j = idx(nx, ny);
              if (unknown[j]) continue;
              r += d[j * 4]; g += d[j * 4 + 1]; b += d[j * 4 + 2]; c++;
            }
          }
          if (c) {
            d[i * 4] = r / c; d[i * 4 + 1] = g / c; d[i * 4 + 2] = b / c; d[i * 4 + 3] = 255;
            next.push(i);
          } else {
            remaining = true;
          }
        }
      }
      for (const i of next) unknown[i] = 0;
      if (!next.length) break;   // isolated region with no known boundary at all
    }

    // Jacobi relaxation smooths the onion-peel seams into one gradient.
    const src = new Float32Array(n * 3);
    for (let i = 0; i < n; i++) {
      src[i * 3] = d[i * 4]; src[i * 3 + 1] = d[i * 4 + 1]; src[i * 3 + 2] = d[i * 4 + 2];
    }
    const dst = src.slice();
    const iters = 60;
    for (let it = 0; it < iters; it++) {
      const a = it % 2 ? dst : src;
      const b = it % 2 ? src : dst;
      for (let y = 1; y < h - 1; y++) {
        for (let x = 1; x < w - 1; x++) {
          const i = idx(x, y);
          if (!masked[i]) continue;
          for (let ch = 0; ch < 3; ch++) {
            b[i * 3 + ch] = (
              a[(i - 1) * 3 + ch] + a[(i + 1) * 3 + ch] +
              a[(i - w) * 3 + ch] + a[(i + w) * 3 + ch]
            ) / 4;
          }
        }
      }
    }
    const out = iters % 2 ? dst : src;
    for (let i = 0; i < n; i++) {
      if (!masked[i]) continue;
      d[i * 4] = out[i * 3]; d[i * 4 + 1] = out[i * 3 + 1]; d[i * 4 + 2] = out[i * 3 + 2];
      d[i * 4 + 3] = 255;
    }
  },

  export() {
    const mime = this.fmt === 'jpg' ? 'image/jpeg' : 'image/png';
    this.canvas.toBlob((blob) => {
      if (!blob) { Toast.show(t('Export failed'), 'error'); return; }
      window.__clearbgReport?.(1, 'downloaded');
      download(blob, `${this.name || 'photo'}-clean.${this.fmt}`);
    }, mime, 0.92);
  },

  reset() {
    this.editor.classList.add('hidden');
    this.hero.classList.remove('hidden');
    this.undoStack = [];
    this.clearStrokes();
  },
};

document.addEventListener('DOMContentLoaded', () => App.init());
