/**
 * BG Remover — client-side application.
 *
 * All background removal runs in the browser via @imgly/background-removal
 * (ISNet / U²-Net). Nothing is uploaded to the server. The library and the
 * model assets are loaded from a CDN and cached by the browser after first use.
 *
 * To swap the model later, replace the `removeBackground` import and the call
 * inside `Card.process()` — the rest of the UI is model-agnostic.
 */
import { removeBackground, preload } from 'https://cdn.jsdelivr.net/npm/@imgly/background-removal@1.6.0/+esm';
import JSZip from 'https://cdn.jsdelivr.net/npm/jszip@3.10.1/+esm';

/* ------------------------------------------------------------------ config */
const CONFIG = {
  maxFileSize: 25 * 1024 * 1024, // 25 MB
  acceptedTypes: ['image/jpeg', 'image/png', 'image/webp'],
  maxHistory: 12,
  encodeQuality: 0.92, // for JPG/WEBP output
  removalOptions: {
    output: { format: 'image/png', quality: 1 }, // lossless cut-out, full resolution
    // `model` defaults to 'isnet' (best quality). Use 'isnet_quint8' for speed.
  },
};

const EXT = { 'image/png': 'png', 'image/jpeg': 'jpg', 'image/webp': 'webp' };
const LABEL = { 'image/png': 'PNG', 'image/jpeg': 'JPG', 'image/webp': 'WEBP' };

// Crop presets. `aspect` is width/height; `shape` controls the mask applied to
// the output ('rect' = plain crop, 'circle'/'rounded' = masked with transparency).
const CROPS = {
  circle:  { label: 'Circle',  aspect: 1,      shape: 'circle' },
  square:  { label: 'Square',  aspect: 1,      shape: 'rect' },
  rounded: { label: 'Rounded', aspect: 1,      shape: 'rounded' },
  '4:5':   { label: '4:5',     aspect: 4 / 5,  shape: 'rect' },
  '16:9':  { label: '16:9',    aspect: 16 / 9, shape: 'rect' },
  '9:16':  { label: '9:16',    aspect: 9 / 16, shape: 'rect' },
};

/* --------------------------------------------------------------- utilities */
const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

const clamp = (v, min, max) => Math.min(max, Math.max(min, v));

/** Trace a rounded-rectangle path (radius clamped to half the shorter side). */
function roundRectPath(ctx, x, y, w, h, r) {
  r = Math.min(r, w / 2, h / 2);
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}

/**
 * Given a source image and a crop preset + zoom/center, compute the source
 * sampling rectangle and the output canvas dimensions. Shared by the live
 * cropper preview and the final compose() so the two always match exactly.
 */
function cropGeometry(iw, ih, crop) {
  const baseW = Math.min(iw, ih * crop.aspect);
  const baseH = baseW / crop.aspect;
  const z = Math.max(1, crop.z || 1);
  const sw = baseW / z;
  const sh = baseH / z;
  const halfU = sw / 2 / iw;
  const halfV = sh / 2 / ih;
  const u = clamp(crop.u ?? 0.5, halfU, 1 - halfU);
  const v = clamp(crop.v ?? 0.5, halfV, 1 - halfV);
  const sx = clamp(u * iw - sw / 2, 0, iw - sw);
  const sy = clamp(v * ih - sh / 2, 0, ih - sh);
  return { sx, sy, sw, sh, outW: Math.round(baseW), outH: Math.round(baseH) };
}

const humanSize = (bytes) => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
};

const sanitizeName = (name) =>
  name.replace(/\.[^.]+$/, '').replace(/[^\w\-]+/g, '_').slice(0, 60) || 'image';

const loadImage = (src) =>
  new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = src;
  });

/* ------------------------------------------------------------- preferences */
// Remembers the last-used background/format so batch users don't re-pick them
// for every image. Wrapped in try/catch because localStorage can be disabled
// (private mode, blocked cookies) — in that case it silently no-ops.
const Prefs = {
  get(key) {
    try {
      return localStorage.getItem(`bgr:${key}`);
    } catch {
      return null;
    }
  },
  set(key, value) {
    try {
      localStorage.setItem(`bgr:${key}`, value);
    } catch {
      /* storage unavailable — preference just isn't remembered */
    }
  },
};

/* -------------------------------------------------------------- toast queue */
const Toast = {
  show(message, type = 'success') {
    const container = $('#toast-container');
    const styles = {
      success: ['bg-green-50 dark:bg-green-900/40', 'text-green-800 dark:text-green-200', 'border-green-200 dark:border-green-800', 'fa-circle-check text-green-500'],
      error: ['bg-red-50 dark:bg-red-900/40', 'text-red-800 dark:text-red-200', 'border-red-200 dark:border-red-800', 'fa-circle-exclamation text-red-500'],
      info: ['bg-blue-50 dark:bg-blue-900/40', 'text-blue-800 dark:text-blue-200', 'border-blue-200 dark:border-blue-800', 'fa-circle-info text-blue-500'],
    }[type] || [];
    const [bg, text, border, icon] = styles;

    const el = document.createElement('div');
    el.className = `pointer-events-auto flex items-center gap-3 px-5 py-3.5 rounded-xl border shadow-lg transition-all duration-300 translate-y-4 opacity-0 ${bg} ${text} ${border}`;
    el.setAttribute('role', 'alert');
    el.innerHTML = `<i class="fa-solid ${icon} text-lg"></i><span class="font-medium text-sm">${message}</span>`;
    container.appendChild(el);

    requestAnimationFrame(() => el.classList.remove('translate-y-4', 'opacity-0'));
    setTimeout(() => {
      el.classList.add('opacity-0', 'translate-y-4');
      setTimeout(() => el.remove(), 300);
    }, 3800);
  },
};

/* --------------------------------------------------------- model warm-up */
const ModelStatus = {
  started: false,
  init() {
    this.el = $('#model-status');
  },
  render(html, cls) {
    this.el.className = `inline-flex items-center gap-2 mt-1 px-3 py-1 rounded-full text-xs font-medium ${cls}`;
    this.el.innerHTML = html;
    this.el.classList.remove('hidden');
  },
  async warm() {
    if (this.started) return;
    this.started = true;
    this.render('<i class="fa-solid fa-circle-notch fa-spin"></i> Preparing AI model…', 'bg-primary/10 text-primary');
    try {
      if (typeof preload === 'function') await preload(CONFIG.removalOptions);
      this.render('<i class="fa-solid fa-circle-check text-green-500"></i> AI model ready', 'bg-green-500/10 text-green-600 dark:text-green-400');
    } catch {
      // Warm-up is best-effort; real processing will still download on demand.
      this.started = false;
      this.el.classList.add('hidden');
    }
  },
};

/* --------------------------------------------------------------- statistics */
const Stats = {
  sessionCount: 0,
  sessionTotalMs: 0,
  record(durationMs) {
    this.sessionCount += 1;
    this.sessionTotalMs += durationMs;
    const total = Number(localStorage.getItem('bgr_total') || 0) + 1;
    localStorage.setItem('bgr_total', String(total));
    this.render();
  },
  render() {
    $('#stat-count').textContent = this.sessionCount;
    $('#stat-avg').textContent = this.sessionCount
      ? (this.sessionTotalMs / this.sessionCount / 1000).toFixed(1)
      : '0.0';
    $('#stat-saved').textContent = localStorage.getItem('bgr_total') || '0';
  },
};

/* ------------------------------------------------------------------ history */
const History = {
  key: 'bgr_history',
  load() {
    try {
      return JSON.parse(sessionStorage.getItem(this.key) || '[]');
    } catch {
      return [];
    }
  },
  add(thumbDataUrl, name) {
    const items = this.load();
    items.unshift({ thumb: thumbDataUrl, name, at: Date.now() });
    sessionStorage.setItem(this.key, JSON.stringify(items.slice(0, CONFIG.maxHistory)));
    this.render();
  },
  clear() {
    sessionStorage.removeItem(this.key);
    this.render();
  },
  render() {
    const items = this.load();
    const section = $('#history-section');
    const strip = $('#history-strip');
    strip.innerHTML = '';
    if (!items.length) {
      section.classList.add('hidden');
      return;
    }
    section.classList.remove('hidden');
    for (const item of items) {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'shrink-0 w-24 h-24 rounded-xl overflow-hidden checkerboard border border-gray-200 dark:border-gray-800 hover:ring-2 hover:ring-primary transition focus:outline-none focus-visible:ring-2 focus-visible:ring-primary';
      btn.title = item.name;
      btn.innerHTML = `<img src="${item.thumb}" alt="${item.name}" class="w-full h-full object-contain">`;
      btn.addEventListener('click', () => Zoom.open(item.thumb));
      strip.appendChild(btn);
    }
  },
};

/* --------------------------------------------------------------------- zoom */
const Zoom = {
  scale: 1,
  init() {
    this.modal = $('#zoom-modal');
    this.img = $('#zoom-img');
    $('#zoom-close').addEventListener('click', () => this.close());
    this.modal.addEventListener('click', (e) => { if (e.target === this.modal) this.close(); });
    $('#zoom-in').addEventListener('click', () => this.zoom(0.25));
    $('#zoom-out').addEventListener('click', () => this.zoom(-0.25));
  },
  open(src) {
    this.scale = 1;
    this.img.src = src;
    this.apply();
    this.modal.classList.remove('hidden');
    this.modal.classList.add('flex');
  },
  close() {
    this.modal.classList.add('hidden');
    this.modal.classList.remove('flex');
    this.img.src = '';
  },
  zoom(delta) {
    this.scale = Math.min(4, Math.max(0.25, this.scale + delta));
    this.apply();
  },
  apply() {
    this.img.style.width = `${this.scale * 100}%`;
    $('#zoom-level').textContent = `${Math.round(this.scale * 100)}%`;
  },
  get isOpen() {
    return !this.modal.classList.contains('hidden');
  },
};

/* ---------------------------------------------------- refine brush editor */
/**
 * Lets the user fix the AI's mistakes with two soft brushes:
 *   - "restore" paints the original image back (adds alpha)
 *   - "erase"   wipes leftover background away (removes alpha)
 * Everything runs on an off-screen alpha mask at the image's native
 * resolution, so applying the edit keeps full quality.
 */
const Editor = {
  tool: 'restore',
  brush: 45, // brush diameter in on-screen pixels
  feather: 0, // edge-smoothing blur radius (native px)
  painting: false,
  panning: false,
  pinching: false,
  spaceHeld: false,
  zoom: 1,
  panX: 0,
  panY: 0,
  pointers: new Map(),
  undoStack: [],

  init() {
    this.modal = $('#editor-modal');
    this.stage = $('#editor-stage');
    this.viewport = $('#editor-viewport');
    this.canvas = $('#editor-canvas');
    this.ctx = this.canvas.getContext('2d');
    this.cursor = $('#brush-cursor');
    this.orig = document.createElement('canvas'); // original image
    this.mask = document.createElement('canvas'); // working alpha mask
    this.initial = document.createElement('canvas'); // AI result (for reset)

    $('#editor-cancel').addEventListener('click', () => this.close());
    $('#editor-apply').addEventListener('click', () => this.apply());
    $('#editor-undo').addEventListener('click', () => this.undo());
    $('#editor-reset').addEventListener('click', () => this.reset());
    $('#editor-zoom-in').addEventListener('click', () => this.zoomButton(1.25));
    $('#editor-zoom-out').addEventListener('click', () => this.zoomButton(1 / 1.25));
    $('#editor-zoom-fit').addEventListener('click', () => this.fit());
    $('#brush-size').addEventListener('input', (e) => this.setBrush(+e.target.value));
    $('#editor-smooth').addEventListener('input', (e) => { this.feather = +e.target.value; this.render(); });
    $$('.tool-btn', this.modal).forEach((b) => b.addEventListener('click', () => this.setTool(b.dataset.tool)));

    this.canvas.addEventListener('pointerdown', (e) => this.onDown(e));
    this.canvas.addEventListener('pointermove', (e) => this.onMove(e));
    this.canvas.addEventListener('pointerup', (e) => this.onUp(e));
    this.canvas.addEventListener('pointercancel', (e) => this.onUp(e));
    this.canvas.addEventListener('pointerleave', () => { if (!this.painting) this.cursor.classList.add('hidden'); });

    // Wheel to zoom toward the cursor.
    this.stage.addEventListener('wheel', (e) => {
      if (!this.isOpen) return;
      e.preventDefault();
      this.zoomAt(e.clientX, e.clientY, e.deltaY < 0 ? 1.15 : 1 / 1.15);
    }, { passive: false });

    // Hold Space to pan; single-key tool + brush shortcuts.
    document.addEventListener('keydown', (e) => {
      if (!this.isOpen) return;
      if (e.code === 'Space') { e.preventDefault(); if (!this.spaceHeld) { this.spaceHeld = true; this.updateCursor(); } return; }
      if (e.target.tagName === 'INPUT') return;
      const k = e.key.toLowerCase();
      if ((e.ctrlKey || e.metaKey) && k === 'z') { e.preventDefault(); this.undo(); }
      else if (k === 'r') this.setTool('restore');
      else if (k === 'e') this.setTool('erase');
      else if (k === 'm' || k === 'h') this.setTool('move');
      else if (k === ']' || k === '+' || k === '=') this.setBrush(this.brush + 6);
      else if (k === '[' || k === '-' || k === '_') this.setBrush(this.brush - 6);
    });
    document.addEventListener('keyup', (e) => {
      if (e.code === 'Space') { this.spaceHeld = false; this.updateCursor(); }
    });
  },

  async open(card) {
    if (!card.done || !card.processedUrl) return;
    this.card = card;
    const [orig, proc] = await Promise.all([loadImage(card.originalUrl), loadImage(card.processedUrl)]);
    const w = proc.naturalWidth;
    const h = proc.naturalHeight;
    for (const c of [this.orig, this.mask, this.initial, this.canvas]) {
      c.width = w;
      c.height = h;
    }
    this.orig.getContext('2d').drawImage(orig, 0, 0, w, h);
    this.mask.getContext('2d').drawImage(proc, 0, 0); // proc's alpha is the subject mask
    this.initial.getContext('2d').drawImage(proc, 0, 0);
    this.undoStack = [];
    this.spaceHeld = false;
    this.pinching = false;
    this.pointers.clear();
    this.feather = 0;
    $('#editor-smooth').value = 0;
    this.setTool('restore');
    this.render();

    this.modal.classList.remove('hidden');
    this.modal.classList.add('flex');
    document.body.style.overflow = 'hidden';

    // Size the viewport to fit the stage, then reset zoom/pan (needs layout).
    requestAnimationFrame(() => {
      this.fitToStage();
      this.fit();
      this.updateCursor();
    });
  },

  /** Scale the viewport so the whole image fits the stage. */
  fitToStage() {
    const rect = this.stage.getBoundingClientRect();
    const pad = 32;
    const s = Math.min((rect.width - pad) / this.canvas.width, (rect.height - pad) / this.canvas.height);
    this.viewport.style.width = `${this.canvas.width * s}px`;
    this.viewport.style.height = `${this.canvas.height * s}px`;
  },

  applyTransform() {
    this.viewport.style.transform =
      `translate(-50%, -50%) translate(${this.panX}px, ${this.panY}px) scale(${this.zoom})`;
    $('#editor-zoom-level').textContent = `${Math.round(this.zoom * 100)}%`;
  },

  /** Zoom keeping the point under (sx, sy) fixed on screen. */
  zoomAt(sx, sy, factor) {
    const r0 = this.viewport.getBoundingClientRect();
    const fx = (sx - r0.left) / r0.width;
    const fy = (sy - r0.top) / r0.height;
    this.zoom = Math.min(8, Math.max(1, this.zoom * factor));
    this.applyTransform();
    const r1 = this.viewport.getBoundingClientRect();
    this.panX += sx - (r1.left + fx * r1.width);
    this.panY += sy - (r1.top + fy * r1.height);
    this.applyTransform();
  },

  zoomButton(factor) {
    const r = this.stage.getBoundingClientRect();
    this.zoomAt(r.left + r.width / 2, r.top + r.height / 2, factor);
  },

  fit() {
    this.zoom = 1;
    this.panX = 0;
    this.panY = 0;
    this.applyTransform();
  },

  setBrush(v) {
    this.brush = Math.min(200, Math.max(10, v));
    $('#brush-size').value = this.brush;
    this.sizeCursor();
  },

  isPanMode(e) {
    return this.tool === 'move' || this.spaceHeld || (e && e.button === 1);
  },

  updateCursor() {
    const pan = this.isPanMode();
    this.canvas.style.cursor = pan ? (this.panning ? 'grabbing' : 'grab') : 'none';
    if (pan) this.cursor.classList.add('hidden');
  },

  close() {
    this.modal.classList.add('hidden');
    this.modal.classList.remove('flex');
    this.cursor.classList.add('hidden');
    document.body.style.overflow = '';
  },

  setTool(tool) {
    this.tool = tool;
    $$('.tool-btn', this.modal).forEach((b) => {
      const active = b.dataset.tool === tool;
      b.classList.toggle('bg-primary', active);
      b.classList.toggle('text-white', active);
    });
    this.updateCursor();
  },

  /** The mask with optional edge smoothing (blur) applied to its alpha. */
  featheredMask() {
    if (!this.feather) return this.mask;
    const c = this._feather || (this._feather = document.createElement('canvas'));
    c.width = this.mask.width;
    c.height = this.mask.height;
    const fx = c.getContext('2d');
    fx.clearRect(0, 0, c.width, c.height);
    fx.filter = `blur(${this.feather}px)`;
    fx.drawImage(this.mask, 0, 0);
    fx.filter = 'none';
    return c;
  },

  /** Composite original × mask onto the visible canvas. */
  render() {
    const { ctx, canvas } = this;
    ctx.globalCompositeOperation = 'source-over';
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(this.orig, 0, 0);
    ctx.globalCompositeOperation = 'destination-in';
    ctx.drawImage(this.featheredMask(), 0, 0);
    ctx.globalCompositeOperation = 'source-over';
  },

  /** Map a pointer event to canvas-space coords + brush radius. */
  locate(e) {
    const rect = this.canvas.getBoundingClientRect();
    const scale = this.canvas.width / rect.width;
    return {
      x: (e.clientX - rect.left) * scale,
      y: (e.clientY - rect.top) * scale,
      r: (this.brush / 2) * scale,
    };
  },

  pushUndo() {
    const snap = document.createElement('canvas');
    snap.width = this.mask.width;
    snap.height = this.mask.height;
    snap.getContext('2d').drawImage(this.mask, 0, 0);
    this.undoStack.push(snap);
    if (this.undoStack.length > 12) this.undoStack.shift();
  },

  restoreSnap(snap) {
    const m = this.mask.getContext('2d');
    m.globalCompositeOperation = 'source-over';
    m.clearRect(0, 0, this.mask.width, this.mask.height);
    m.drawImage(snap, 0, 0);
    this.render();
  },

  undo() {
    const snap = this.undoStack.pop();
    if (snap) this.restoreSnap(snap);
  },

  reset() {
    this.pushUndo();
    this.restoreSnap(this.initial);
  },

  /* ---- pointer routing (supports two-finger pinch zoom/pan) ---- */
  onDown(e) {
    this.canvas.setPointerCapture(e.pointerId);
    this.pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (this.pointers.size === 2) { this.startPinch(); return; }
    if (this.pointers.size > 2) return;
    this.start(e);
  },

  onMove(e) {
    if (this.pointers.has(e.pointerId)) this.pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (this.pinching) { if (this.pointers.size >= 2) this.doPinch(); return; }
    this.move(e);
  },

  onUp(e) {
    this.pointers.delete(e.pointerId);
    if (this.pointers.size < 2) this.pinching = false;
    if (this.pointers.size === 0) { this.painting = false; this.panning = false; this.updateCursor(); }
  },

  pinchGeometry() {
    const [a, b] = [...this.pointers.values()];
    return { dist: Math.hypot(a.x - b.x, a.y - b.y), midX: (a.x + b.x) / 2, midY: (a.y + b.y) / 2 };
  },

  startPinch() {
    this.pinching = true;
    this.painting = false;
    this.panning = false;
    this.cursor.classList.add('hidden');
    this.pinchPrev = this.pinchGeometry();
  },

  doPinch() {
    const cur = this.pinchGeometry();
    if (this.pinchPrev.dist > 0) {
      this.zoomAt(cur.midX, cur.midY, cur.dist / this.pinchPrev.dist);
      this.panX += cur.midX - this.pinchPrev.midX;
      this.panY += cur.midY - this.pinchPrev.midY;
      this.applyTransform();
    }
    this.pinchPrev = cur;
  },

  start(e) {
    if (this.isPanMode(e)) {
      this.panning = true;
      this.panLast = { x: e.clientX, y: e.clientY };
      this.updateCursor();
      return;
    }
    this.painting = true;
    this.pushUndo();
    this.last = this.locate(e);
    this.stamp(this.last.x, this.last.y, this.last.r);
    this.render();
    this.moveCursor(e);
  },

  move(e) {
    if (this.panning) {
      this.panX += e.clientX - this.panLast.x;
      this.panY += e.clientY - this.panLast.y;
      this.panLast = { x: e.clientX, y: e.clientY };
      this.applyTransform();
      return;
    }
    this.moveCursor(e);
    if (!this.painting) return;
    const p = this.locate(e);
    const dx = p.x - this.last.x;
    const dy = p.y - this.last.y;
    const dist = Math.hypot(dx, dy);
    const steps = Math.max(1, Math.ceil(dist / Math.max(1, p.r / 4)));
    for (let i = 1; i <= steps; i++) {
      this.stamp(this.last.x + (dx * i) / steps, this.last.y + (dy * i) / steps, p.r);
    }
    this.last = p;
    this.render();
  },

  /** Paint one soft, feathered dab onto the mask. */
  stamp(x, y, r) {
    const m = this.mask.getContext('2d');
    const grad = m.createRadialGradient(x, y, 0, x, y, r);
    if (this.tool === 'erase') {
      m.globalCompositeOperation = 'destination-out';
      grad.addColorStop(0, 'rgba(0,0,0,1)');
      grad.addColorStop(1, 'rgba(0,0,0,0)');
    } else {
      m.globalCompositeOperation = 'source-over';
      grad.addColorStop(0, 'rgba(255,255,255,1)');
      grad.addColorStop(1, 'rgba(255,255,255,0)');
    }
    m.fillStyle = grad;
    m.beginPath();
    m.arc(x, y, r, 0, Math.PI * 2);
    m.fill();
    m.globalCompositeOperation = 'source-over';
  },

  moveCursor(e) {
    if (this.isPanMode()) { this.cursor.classList.add('hidden'); return; }
    this.cursor.classList.remove('hidden');
    this.cursor.style.left = `${e.clientX}px`;
    this.cursor.style.top = `${e.clientY}px`;
    this.sizeCursor();
  },

  sizeCursor() {
    // `brush` is an on-screen diameter, so the ring maps 1:1 to screen pixels.
    this.cursor.style.width = `${this.brush}px`;
    this.cursor.style.height = `${this.brush}px`;
  },

  apply() {
    const out = document.createElement('canvas');
    out.width = this.mask.width;
    out.height = this.mask.height;
    const o = out.getContext('2d');
    o.drawImage(this.orig, 0, 0);
    o.globalCompositeOperation = 'destination-in';
    o.drawImage(this.featheredMask(), 0, 0);
    out.toBlob((blob) => {
      if (blob) this.card.applyEdited(blob);
      this.close();
    }, 'image/png');
  },

  get isOpen() {
    return !this.modal.classList.contains('hidden');
  },
};

/* -------------------------------------------------------------------- cropper */
// Interactive crop dialog: pick a shape/aspect, then zoom and drag the image to
// position it inside the frame. The preview canvas is redrawn with the exact
// same geometry helper compose() uses, so what you see is what you export.
const Cropper = {
  card: null,
  img: null,
  source: 'cutout', // 'cutout' = transparent bg-removed result, 'original' = uploaded image
  key: 'square',
  z: 1,
  u: 0.5,
  v: 0.5,
  dragging: false,
  last: null,

  init() {
    this.modal = $('#crop-modal');
    if (!this.modal) return;
    this.canvas = $('#crop-canvas');
    this.ctx = this.canvas.getContext('2d');
    this.slider = $('#crop-zoom');

    $('#crop-cancel').addEventListener('click', () => this.close());
    $('#crop-apply').addEventListener('click', () => this.apply());
    $('#crop-remove').addEventListener('click', () => {
      if (this.card) this.card.setCropState(null);
      this.close();
    });
    $$('.crop-shape', this.modal).forEach((btn) =>
      btn.addEventListener('click', () => this.setShape(btn.dataset.crop)),
    );
    $$('.crop-source', this.modal).forEach((btn) =>
      btn.addEventListener('click', () => this.setSource(btn.dataset.source)),
    );

    this.slider.addEventListener('input', () => this.setZoom(parseFloat(this.slider.value)));
    this.canvas.addEventListener('pointerdown', (e) => this.onDown(e));
    this.canvas.addEventListener('pointermove', (e) => this.onMove(e));
    ['pointerup', 'pointercancel', 'pointerleave'].forEach((ev) =>
      this.canvas.addEventListener(ev, () => this.onUp()),
    );
    this.canvas.addEventListener('wheel', (e) => {
      e.preventDefault();
      this.setZoom(this.z * (e.deltaY < 0 ? 1.1 : 1 / 1.1));
    }, { passive: false });

    document.addEventListener('keydown', (e) => {
      if (this.isOpen && e.key === 'Escape') this.close();
    });
  },

  async open(card) {
    this.card = card;

    const s = card.cropState;
    // Default to the transparent cut-out once it exists, otherwise the original
    // image — so Crop is usable immediately, before (or without) bg removal.
    this.source = s ? s.source : card.done ? 'cutout' : 'original';
    if (this.source === 'cutout' && !card.done) this.source = 'original';
    await this.loadSourceImage();

    this.key = (s && s.key) || 'square';
    this.z = (s && s.z) || 1;
    this.u = s ? s.u : 0.5;
    this.v = s ? s.v : 0.5;

    this.updateSourceButtons();
    this.highlightShape();
    this.sizeCanvas();
    this.slider.value = this.z;
    this.redraw();

    this.modal.classList.remove('hidden');
    this.modal.classList.add('flex');
  },

  /** Load the image for the active source into this.img. */
  loadSourceImage() {
    const url = this.source === 'original' ? this.card.originalUrl : this.card.processedUrl;
    return loadImage(url).then((img) => { this.img = img; });
  },

  setSource(src) {
    if (src === this.source) return;
    if (src === 'cutout' && !this.card.done) return; // cut-out not ready yet
    this.source = src;
    this.loadSourceImage().then(() => {
      this.updateSourceButtons();
      this.redraw();
    });
  },

  /** Highlight the active source and disable Cut-out until bg removal is done. */
  updateSourceButtons() {
    $$('.crop-source', this.modal).forEach((b) => {
      const active = b.dataset.source === this.source;
      b.classList.toggle('bg-primary', active);
      b.classList.toggle('text-white', active);
      const disabled = b.dataset.source === 'cutout' && !this.card.done;
      b.disabled = disabled;
      b.classList.toggle('opacity-40', disabled);
      b.classList.toggle('cursor-not-allowed', disabled);
      b.title = disabled ? 'Available once background removal finishes' : '';
    });
  },

  close() {
    this.modal.classList.add('hidden');
    this.modal.classList.remove('flex');
    this.dragging = false;
  },

  get isOpen() {
    return this.modal && !this.modal.classList.contains('hidden');
  },

  /** Size the preview canvas to the chosen aspect within a fixed box. */
  sizeCanvas() {
    const aspect = CROPS[this.key].aspect;
    const box = 360;
    const w = aspect >= 1 ? box : Math.round(box * aspect);
    const h = aspect >= 1 ? Math.round(box / aspect) : box;
    this.canvas.width = w;
    this.canvas.height = h;
  },

  setShape(key) {
    this.key = key;
    this.highlightShape();
    this.sizeCanvas();
    this.redraw();
  },

  highlightShape() {
    $$('.crop-shape', this.modal).forEach((b) => {
      const active = b.dataset.crop === this.key;
      b.classList.toggle('bg-primary', active);
      b.classList.toggle('text-white', active);
    });
  },

  setZoom(z) {
    this.z = clamp(z, 1, 5);
    this.slider.value = this.z;
    this.redraw();
  },

  onDown(e) {
    this.dragging = true;
    this.last = { x: e.clientX, y: e.clientY };
    this.canvas.setPointerCapture?.(e.pointerId);
  },

  onMove(e) {
    if (!this.dragging) return;
    const iw = this.img.naturalWidth;
    const ih = this.img.naturalHeight;
    const geo = cropGeometry(iw, ih, { aspect: CROPS[this.key].aspect, z: this.z, u: this.u, v: this.v });
    // Convert on-screen drag into a shift of the sampled region (drag the image,
    // so the view moves the opposite way).
    const rect = this.canvas.getBoundingClientRect();
    const dx = (e.clientX - this.last.x) * (this.canvas.width / rect.width);
    const dy = (e.clientY - this.last.y) * (this.canvas.height / rect.height);
    this.u -= (dx * geo.sw / this.canvas.width) / iw;
    this.v -= (dy * geo.sh / this.canvas.height) / ih;
    this.last = { x: e.clientX, y: e.clientY };
    this.redraw();
  },

  onUp() {
    this.dragging = false;
  },

  redraw() {
    const def = CROPS[this.key];
    const iw = this.img.naturalWidth;
    const ih = this.img.naturalHeight;
    const geo = cropGeometry(iw, ih, { aspect: def.aspect, z: this.z, u: this.u, v: this.v });
    // Keep normalized centre in sync with the clamped geometry so dragging stops
    // cleanly at the edges instead of drifting.
    this.u = (geo.sx + geo.sw / 2) / iw;
    this.v = (geo.sy + geo.sh / 2) / ih;

    const c = this.canvas;
    const ctx = this.ctx;
    ctx.clearRect(0, 0, c.width, c.height);
    ctx.save();
    if (def.shape === 'circle') {
      ctx.beginPath();
      ctx.ellipse(c.width / 2, c.height / 2, c.width / 2, c.height / 2, 0, 0, Math.PI * 2);
      ctx.clip();
    } else if (def.shape === 'rounded') {
      roundRectPath(ctx, 0, 0, c.width, c.height, Math.min(c.width, c.height) * 0.18);
      ctx.clip();
    }
    this.drawCheckerboard(ctx, c.width, c.height);
    ctx.drawImage(this.img, geo.sx, geo.sy, geo.sw, geo.sh, 0, 0, c.width, c.height);
    ctx.restore();
  },

  drawCheckerboard(ctx, w, h) {
    const s = 12;
    for (let y = 0; y < h; y += s) {
      for (let x = 0; x < w; x += s) {
        ctx.fillStyle = ((x / s + y / s) & 1) ? '#e5e7eb' : '#ffffff';
        ctx.fillRect(x, y, s, s);
      }
    }
  },

  apply() {
    const def = CROPS[this.key];
    this.card.setCropState({ key: this.key, aspect: def.aspect, shape: def.shape, z: this.z, u: this.u, v: this.v, source: this.source });
    this.close();
    Toast.show('Crop applied', 'success');
  },
};

/* ---------------------------------------------------------------- card view */
let cardSeq = 0;

class Card {
  constructor(file) {
    this.file = file;
    this.id = `card-${++cardSeq}`;
    this.originalUrl = URL.createObjectURL(file);
    this.processedUrl = null;
    this.processedBlob = null; // transparent PNG cut-out (source of truth)
    this.done = false;
    this.bg = null; // null = transparent
    this.format = 'image/png';
    this.cropState = null; // null = no crop; else { key, aspect, shape, z, u, v }
    this.previewUrl = null; // object URL for the composed (cropped) preview, if any
    this.build();
  }

  build() {
    const tpl = $('#card-template').content.cloneNode(true);
    this.el = tpl.querySelector('.card');
    this.el.id = this.id;

    this.el.querySelector('.original-img').src = this.originalUrl;
    this.el.querySelector('.original-img-split').src = this.originalUrl;
    const nameEl = this.el.querySelector('.filename');
    nameEl.textContent = this.file.name;
    nameEl.title = this.file.name;

    // Compare slider
    const range = this.el.querySelector('.compare-range');
    const line = this.el.querySelector('.slider-line');
    const orig = this.el.querySelector('.original-img');
    range.addEventListener('input', () => {
      orig.style.clipPath = `inset(0 ${100 - range.value}% 0 0)`;
      line.style.left = `${range.value}%`;
    });

    // Actions
    this.el.querySelector('.download-btn').addEventListener('click', () => this.download());
    this.el.querySelector('.copy-btn').addEventListener('click', () => this.copy());
    this.el.querySelector('.remove-btn').addEventListener('click', () => this.destroy());
    this.el.querySelector('.retry-btn').addEventListener('click', () => this.process());
    this.el.querySelector('.toggle-view-btn').addEventListener('click', () => this.toggleView());
    this.el.querySelector('.edit-btn').addEventListener('click', () => Editor.open(this));
    this.el.querySelector('.crop-btn').addEventListener('click', () => Cropper.open(this));
    this.el.querySelector('.options-btn').addEventListener('click', () =>
      this.el.querySelector('.options-panel').classList.toggle('hidden'),
    );
    $$('.zoomable', this.el).forEach((img) =>
      img.addEventListener('click', () => this.done && Zoom.open(this.processedUrl)),
    );

    // Background swatches — remember the choice across the session.
    $$('.swatch', this.el).forEach((sw) =>
      sw.addEventListener('click', () => {
        this.setBackground(sw.dataset.bg, sw);
        Prefs.set('bg', sw.dataset.bg);
      }),
    );
    const custom = this.el.querySelector('.custom-color');
    custom.addEventListener('input', () => this.setBackground(custom.value, custom.parentElement));

    // Output format — likewise remembered.
    $$('.format-btn', this.el).forEach((btn) =>
      btn.addEventListener('click', () => {
        this.setFormat(btn.dataset.format);
        Prefs.set('format', btn.dataset.format);
      }),
    );

    this.applyRememberedOptions();
    $('#results-grid').appendChild(this.el);
  }

  /** Pre-select the background/format the user last chose this session. */
  applyRememberedOptions() {
    const bg = Prefs.get('bg');
    if (bg) {
      const swatch = this.el.querySelector(`.swatch[data-bg="${bg}"]`);
      if (swatch) this.setBackground(bg, swatch);
    }
    const format = Prefs.get('format');
    if (format && EXT[format]) {
      const btn = this.el.querySelector(`.format-btn[data-format="${format}"]`);
      if (btn) this.setFormat(format);
    }
  }

  async process() {
    this.setState('processing');
    const bar = this.el.querySelector('.progress-bar');
    const label = this.el.querySelector('.progress-label');
    const started = performance.now();

    try {
      // Pass the File/Blob directly (more robust than a blob: URL fetch).
      const blob = await removeBackground(this.file, {
        ...CONFIG.removalOptions,
        progress: (key, current, total) => {
          const pct = total ? Math.round((current / total) * 100) : 0;
          bar.style.width = `${pct}%`;
          label.textContent = key.startsWith('fetch')
            ? `Downloading AI model… ${pct}%`
            : 'Removing background…';
        },
      });

      this.processedBlob = blob;
      this.processedUrl = URL.createObjectURL(blob);
      this.el.querySelector('.processed-img').src = this.processedUrl;
      this.el.querySelector('.processed-img-split').src = this.processedUrl;
      this.el.querySelector('.meta').textContent = `${humanSize(this.file.size)} → ${humanSize(blob.size)}`;

      this.done = true;
      this.setState('done');
      this.refreshPreview(); // apply any remembered background now the image exists
      Stats.record(performance.now() - started);
      ModelStatus.render('<i class="fa-solid fa-circle-check text-green-500"></i> AI model ready', 'bg-green-500/10 text-green-600 dark:text-green-400');
      this.saveToHistory();
      App.refreshToolbar();
    } catch (err) {
      console.error('[bg-remover] processing failed:', err);
      const detail = (err && (err.message || err.name)) || 'Unknown error';
      this.el.querySelector('.error-msg').textContent = detail.slice(0, 180);
      this.setState('error');
      Toast.show(`Failed: ${detail}`.slice(0, 140), 'error');
    }
  }

  setState(state) {
    this.el.dataset.state = state;
    this.el.querySelector('.processing-overlay').classList.toggle('hidden', state !== 'processing');
    this.el.querySelector('.error-overlay').classList.toggle('hidden', state !== 'error');
  }

  toggleView() {
    const compare = this.el.querySelector('.view-compare');
    const split = this.el.querySelector('.view-split');
    const showSplit = compare.classList.toggle('hidden');
    split.classList.toggle('hidden', !showSplit);
    this.el.querySelector('.toggle-view-btn i').className = showSplit ? 'fa-solid fa-sliders' : 'fa-solid fa-table-columns';
    this.el.querySelector('.view-label').textContent = showSplit ? 'Slider' : 'Side-by-side';
  }

  setBackground(value, swatchEl) {
    this.bg = value === 'transparent' ? null : value;

    // Highlight the active swatch.
    $$('.swatch', this.el).forEach((s) => s.classList.remove('ring-2', 'ring-primary', 'ring-offset-1'));
    this.el.querySelector('.custom-color').parentElement.classList.remove('ring-2', 'ring-primary');
    if (swatchEl) swatchEl.classList.add('ring-2', 'ring-primary', 'ring-offset-1');

    this.refreshPreview();
  }

  /** Apply (or clear) a crop and refresh the on-card preview. */
  setCropState(state) {
    this.cropState = state;
    this.refreshPreview();
    const meta = this.el.querySelector('.meta');
    if (state) meta.textContent = `${humanSize(this.file.size)} · cropped (${CROPS[state.key].label})`;
  }

  /**
   * Update the card's preview surfaces to reflect the current background/crop.
   * Without a crop, the transparent cut-out is shown with the background painted
   * on the surface behind it. With a crop, the exact composed PNG is shown on a
   * checkerboard so masked (transparent) corners read correctly.
   */
  async refreshPreview() {
    const surfaces = [this.el.querySelector('.preview'), this.el.querySelector('.split-bg')];
    const processed = this.el.querySelector('.processed-img');
    const processedSplit = this.el.querySelector('.processed-img-split');

    // A crop of the original image can be previewed even before bg removal
    // finishes, since it doesn't depend on the cut-out existing.
    const cropOnOriginal = this.cropState && this.cropState.source === 'original';

    // Called during build (for remembered options) before any image exists —
    // set the background surface but leave the image alone until it's ready.
    if (!this.processedUrl && !cropOnOriginal) {
      for (const surface of surfaces) {
        if (this.bg) {
          surface.classList.remove('checkerboard');
          surface.style.backgroundColor = this.bg;
        } else {
          surface.classList.add('checkerboard');
          surface.style.backgroundColor = '';
        }
      }
      return;
    }

    if (this.previewUrl) {
      URL.revokeObjectURL(this.previewUrl);
      this.previewUrl = null;
    }

    if (!this.cropState) {
      processed.src = this.processedUrl;
      processedSplit.src = this.processedUrl;
      for (const surface of surfaces) {
        if (this.bg) {
          surface.classList.remove('checkerboard');
          surface.style.backgroundColor = this.bg;
        } else {
          surface.classList.add('checkerboard');
          surface.style.backgroundColor = '';
        }
      }
      return;
    }

    const blob = await this.compose('image/png', this.bg, this.cropState);
    this.previewUrl = URL.createObjectURL(blob);
    processed.src = this.previewUrl;
    processedSplit.src = this.previewUrl;
    for (const surface of surfaces) {
      surface.classList.add('checkerboard');
      surface.style.backgroundColor = '';
    }
  }

  setFormat(format) {
    this.format = format;
    $$('.format-btn', this.el).forEach((b) => {
      const active = b.dataset.format === format;
      b.classList.toggle('bg-primary', active);
      b.classList.toggle('text-white', active);
    });
    this.el.querySelector('.download-label').textContent = LABEL[format];
  }

  /** Composite the transparent cut-out onto the chosen background, crop & format. */
  async compose(format = this.format, bg = this.bg, crop = this.cropState) {
    // Fast path: unmodified, uncropped transparent PNG keeps the original bytes.
    if (!bg && format === 'image/png' && !crop) return this.processedBlob;

    // A crop can target the original image (background intact) or the cut-out.
    const srcUrl = crop && crop.source === 'original' ? this.originalUrl : this.processedUrl;
    const img = await loadImage(srcUrl);
    const iw = img.naturalWidth;
    const ih = img.naturalHeight;

    // Source sampling rect + output size — full image unless a crop is set.
    const geo = crop
      ? cropGeometry(iw, ih, crop)
      : { sx: 0, sy: 0, sw: iw, sh: ih, outW: iw, outH: ih };
    const shape = crop ? crop.shape : 'rect';

    const canvas = document.createElement('canvas');
    canvas.width = geo.outW;
    canvas.height = geo.outH;
    const ctx = canvas.getContext('2d');

    // JPG has no alpha; fall back to white so transparency doesn't become black.
    const fill = bg || (format === 'image/jpeg' ? '#ffffff' : null);

    // Paint the whole canvas first for opaque output so any area outside a
    // shape mask is the fallback colour rather than transparent-turned-black.
    if (format === 'image/jpeg') {
      ctx.fillStyle = fill;
      ctx.fillRect(0, 0, geo.outW, geo.outH);
    }

    ctx.save();
    if (shape === 'circle') {
      ctx.beginPath();
      ctx.ellipse(geo.outW / 2, geo.outH / 2, geo.outW / 2, geo.outH / 2, 0, 0, Math.PI * 2);
      ctx.clip();
    } else if (shape === 'rounded') {
      roundRectPath(ctx, 0, 0, geo.outW, geo.outH, Math.min(geo.outW, geo.outH) * 0.18);
      ctx.clip();
    }
    if (fill) {
      ctx.fillStyle = fill;
      ctx.fillRect(0, 0, geo.outW, geo.outH);
    }
    ctx.drawImage(img, geo.sx, geo.sy, geo.sw, geo.sh, 0, 0, geo.outW, geo.outH);
    ctx.restore();

    const quality = format === 'image/png' ? undefined : CONFIG.encodeQuality;
    return new Promise((resolve) => canvas.toBlob(resolve, format, quality));
  }

  async download() {
    // Allow download once there's a cut-out, or a crop of the original.
    if (!this.processedBlob && !this.cropState) return;
    const blob = await this.compose();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    const suffix = this.cropState && this.cropState.source === 'original' ? 'crop' : 'no-bg';
    a.download = `${sanitizeName(this.file.name)}-${suffix}.${EXT[this.format]}`;
    document.body.appendChild(a);
    a.click();
    URL.revokeObjectURL(url);
    a.remove();
  }

  async copy() {
    if (!this.processedBlob) return;
    try {
      const blob = await this.compose('image/png', this.bg);
      await navigator.clipboard.write([new ClipboardItem({ 'image/png': blob })]);
      Toast.show('Copied to clipboard', 'success');
    } catch {
      Toast.show('Clipboard not supported in this browser', 'error');
    }
  }

  /** Replace the cut-out with a hand-refined version from the editor. */
  applyEdited(blob) {
    if (this.processedUrl) URL.revokeObjectURL(this.processedUrl);
    this.processedBlob = blob;
    this.processedUrl = URL.createObjectURL(blob);
    this.el.querySelector('.meta').textContent = `${humanSize(this.file.size)} → ${humanSize(blob.size)} · edited`;
    this.refreshPreview(); // re-applies any active crop over the new cut-out
    this.saveToHistory();
    Toast.show('Edits applied', 'success');
  }

  async saveToHistory() {
    try {
      History.add(await makeThumbnail(this.processedUrl), this.file.name);
    } catch {
      /* thumbnails are best-effort */
    }
  }

  destroy() {
    URL.revokeObjectURL(this.originalUrl);
    if (this.processedUrl) URL.revokeObjectURL(this.processedUrl);
    if (this.previewUrl) URL.revokeObjectURL(this.previewUrl);
    this.el.remove();
    App.cards = App.cards.filter((c) => c !== this);
    App.refreshToolbar();
    if (!App.cards.length) App.showLanding();
  }
}

/* -------------------------------------------------------------- thumbnails */
function makeThumbnail(url, size = 160) {
  return loadImage(url).then((img) => {
    const scale = Math.min(size / img.width, size / img.height, 1);
    const canvas = document.createElement('canvas');
    canvas.width = Math.max(1, Math.round(img.width * scale));
    canvas.height = Math.max(1, Math.round(img.height * scale));
    canvas.getContext('2d').drawImage(img, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL('image/png');
  });
}

/* --------------------------------------------------------------------- app */
const App = {
  cards: [],

  init() {
    this.dropzone = $('#dropzone');
    this.fileInput = $('#file-input');
    this.workspace = $('#workspace');
    this.landing = $('#landing');

    // Surface uncaught errors so failures are never silent.
    window.addEventListener('error', (e) => {
      console.error('[bg-remover] error:', e.error || e.message);
      Toast.show(`Error: ${e.message}`.slice(0, 140), 'error');
    });
    window.addEventListener('unhandledrejection', (e) => {
      const reason = e.reason?.message || e.reason || 'Unknown error';
      console.error('[bg-remover] unhandled rejection:', e.reason);
      Toast.show(`Error: ${reason}`.slice(0, 140), 'error');
    });

    ModelStatus.init();
    this.bindUpload();
    this.bindToolbar();
    this.bindShortcuts();
    Zoom.init();
    Editor.init();
    Cropper.init();
    Stats.render();
    History.render();
  },

  bindUpload() {
    const open = () => this.fileInput.click();
    $('#browse-btn').addEventListener('click', (e) => { e.stopPropagation(); open(); });
    this.dropzone.addEventListener('click', open);
    this.dropzone.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); }
    });
    this.fileInput.addEventListener('change', (e) => this.handleFiles(e.target.files));

    // Warm up the model as soon as the user shows intent (once).
    ['pointerenter', 'focusin', 'touchstart'].forEach((evt) =>
      this.dropzone.addEventListener(evt, () => ModelStatus.warm(), { once: true, passive: true }),
    );

    const icon = $('#upload-icon');
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach((evt) =>
      this.dropzone.addEventListener(evt, (e) => { e.preventDefault(); e.stopPropagation(); }),
    );
    ['dragenter', 'dragover'].forEach((evt) =>
      this.dropzone.addEventListener(evt, () => {
        this.dropzone.classList.add('border-primary', 'bg-primary/5');
        icon.classList.add('scale-110');
      }),
    );
    ['dragleave', 'drop'].forEach((evt) =>
      this.dropzone.addEventListener(evt, () => {
        this.dropzone.classList.remove('border-primary', 'bg-primary/5');
        icon.classList.remove('scale-110');
      }),
    );
    this.dropzone.addEventListener('drop', (e) => this.handleFiles(e.dataTransfer.files));

    document.addEventListener('paste', (e) => {
      const files = [...(e.clipboardData?.items || [])]
        .filter((i) => i.kind === 'file')
        .map((i) => i.getAsFile())
        .filter(Boolean);
      if (files.length) this.handleFiles(files);
    });
  },

  handleFiles(fileList) {
    const files = [...fileList];
    this.fileInput.value = '';
    if (!files.length) return;

    const valid = [];
    for (const file of files) {
      if (!CONFIG.acceptedTypes.includes(file.type)) {
        Toast.show(`${file.name}: unsupported format (use JPG, PNG or WEBP)`, 'error');
        continue;
      }
      if (file.size > CONFIG.maxFileSize) {
        Toast.show(`${file.name}: too large (max ${humanSize(CONFIG.maxFileSize)})`, 'error');
        continue;
      }
      valid.push(file);
    }
    if (!valid.length) return;

    this.showWorkspace();
    for (const file of valid) {
      const card = new Card(file);
      this.cards.push(card);
      card.process();
    }
    this.refreshToolbar();
  },

  bindToolbar() {
    $('#add-more-btn').addEventListener('click', () => this.fileInput.click());
    $('#clear-all-btn').addEventListener('click', () => this.clearAll());
    $('#download-all-btn').addEventListener('click', () => this.downloadAll());
    $('#clear-history-btn').addEventListener('click', () => {
      History.clear();
      Toast.show('History cleared', 'info');
    });
  },

  showWorkspace() {
    this.landing.classList.add('hidden');
    this.workspace.classList.remove('hidden');
  },

  showLanding() {
    this.workspace.classList.add('hidden');
    this.landing.classList.remove('hidden');
  },

  clearAll() {
    [...this.cards].forEach((c) => c.destroy());
    this.showLanding();
    Toast.show('Cleared all images', 'info');
  },

  refreshToolbar() {
    const doneCount = this.cards.filter((c) => c.done).length;
    $('#download-all-btn').classList.toggle('hidden', doneCount < 2);
  },

  async downloadAll() {
    const ready = this.cards.filter((c) => c.done && c.processedBlob);
    if (!ready.length) return;
    Toast.show('Building ZIP…', 'info');
    const zip = new JSZip();
    const used = {};
    for (const card of ready) {
      const base = sanitizeName(card.file.name);
      let name = `${base}-no-bg.${EXT[card.format]}`;
      if (used[name]) name = `${base}-${used[name]++}-no-bg.${EXT[card.format]}`;
      else used[name] = 1;
      zip.file(name, await card.compose());
    }
    const blob = await zip.generateAsync({ type: 'blob' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'bg-remover-results.zip';
    document.body.appendChild(a);
    a.click();
    URL.revokeObjectURL(url);
    a.remove();
  },

  bindShortcuts() {
    const modal = $('#shortcuts-modal');
    const openModal = () => { modal.classList.remove('hidden'); modal.classList.add('flex'); };
    const closeModal = () => { modal.classList.add('hidden'); modal.classList.remove('flex'); };
    $('#shortcuts-btn').addEventListener('click', openModal);
    $('#shortcuts-close').addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => { if (e.target === modal) closeModal(); });

    document.addEventListener('keydown', (e) => {
      // The editor is a focused mode: only Escape (to close) is handled there.
      if (Editor.isOpen) {
        if (e.key === 'Escape') Editor.close();
        return;
      }
      if (e.key === 'Escape') {
        closeModal();
        if (Zoom.isOpen) Zoom.close();
        return;
      }
      if (['INPUT', 'TEXTAREA'].includes(e.target.tagName)) return; // don't hijack typing

      if (e.ctrlKey && e.key.toLowerCase() === 's') {
        e.preventDefault();
        this.downloadAll();
      } else if (!e.ctrlKey && !e.metaKey) {
        if (e.key.toLowerCase() === 'o') { e.preventDefault(); this.fileInput.click(); }
        if (e.key.toLowerCase() === 'd') window.toggleTheme();
        if (e.key === '?') openModal();
      }
    });
  },
};

document.addEventListener('DOMContentLoaded', () => App.init());
