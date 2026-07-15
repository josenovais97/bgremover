/**
 * Blur / redact tool — 100% client-side.
 *
 * Drag boxes over faces, plates or sensitive text; each box is blurred,
 * pixelated or blacked out. Everything runs on a canvas in the browser — the
 * photo is never uploaded, which is the whole point for sensitive images.
 *
 * Regions are stored in image-pixel coordinates so the effect exports at full
 * resolution regardless of the on-screen preview size. Self-contained.
 */
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));

const loadImage = (src) =>
  new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = src;
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
  original: null,
  regions: [],       // committed boxes, in image-pixel coords {x,y,w,h}
  pending: null,     // box currently being dragged
  mode: 'blur',      // 'blur' | 'pixelate' | 'black' (applies to all boxes)
  strength: 50,

  init() {
    this.dropzone = $('#rd-dropzone');
    this.input = $('#rd-input');
    this.editor = $('#rd-editor');
    this.canvas = $('#rd-canvas');

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

    $$('.rd-mode').forEach((b) => b.addEventListener('click', () => {
      this.mode = b.dataset.mode;
      $$('.rd-mode').forEach((x) => { const a = x === b; x.classList.toggle('ring-2', a); x.classList.toggle('ring-primary', a); });
      $('#rd-strength-row').style.visibility = this.mode === 'black' ? 'hidden' : 'visible';
      this.render();
    }));
    $('#rd-strength').addEventListener('input', (e) => { this.strength = +e.target.value; this.render(); });
    $('#rd-undo').addEventListener('click', () => { this.regions.pop(); this.updateButtons(); this.render(); });
    $('#rd-clear').addEventListener('click', () => { this.regions = []; this.updateButtons(); this.render(); });
    $('#rd-download').addEventListener('click', () => this.export('image/png'));
    $('#rd-download-jpg').addEventListener('click', () => this.export('image/jpeg'));
    $('#rd-new').addEventListener('click', () => this.reset());

    // Draw a box by dragging on the canvas.
    this.canvas.addEventListener('pointerdown', (e) => {
      if (!this.original) return;
      this.canvas.setPointerCapture?.(e.pointerId);
      const p = this.toImage(e);
      this.drawStart = p;
      this.pending = { x: p.x, y: p.y, w: 0, h: 0 };
    });
    this.canvas.addEventListener('pointermove', (e) => {
      if (!this.drawStart) return;
      const p = this.toImage(e);
      this.pending = this.rect(this.drawStart, p);
      this.render();
    });
    ['pointerup', 'pointercancel'].forEach((ev) => this.canvas.addEventListener(ev, () => {
      if (this.drawStart && this.pending && this.pending.w > 4 && this.pending.h > 4) {
        this.regions.push(this.pending);
      }
      this.drawStart = null;
      this.pending = null;
      this.updateButtons();
      this.render();
    }));
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

  updateButtons() {
    const has = this.regions.length > 0;
    $('#rd-undo').disabled = !has;
    $('#rd-clear').disabled = !has;
    $('#rd-download').disabled = $('#rd-download-jpg').disabled = !this.original;
  },

  applyRegion(ctx, w, h, box) {
    const { x, y, w: bw, h: bh } = box;
    if (bw < 1 || bh < 1) return;
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
      ctx.save();
      ctx.beginPath(); ctx.rect(x, y, bw, bh); ctx.clip();
      ctx.filter = `blur(${radius}px)`;
      ctx.drawImage(this.original, 0, 0, w, h);
      ctx.restore();
    }
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
      for (const box of this.regions) {
        ctx.strokeStyle = 'rgba(255,255,255,0.9)';
        ctx.strokeRect(box.x, box.y, box.w, box.h);
      }
      if (this.pending) {
        ctx.setLineDash([line * 3, line * 3]);
        ctx.strokeStyle = 'rgba(255,255,255,0.95)';
        ctx.strokeRect(this.pending.x, this.pending.y, this.pending.w, this.pending.h);
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
    if (!file || !/^image\//.test(file.type)) { Toast.show('Please choose an image', 'error'); return; }
    if (this.srcUrl) URL.revokeObjectURL(this.srcUrl);
    this.srcUrl = URL.createObjectURL(file);
    try {
      this.original = await loadImage(this.srcUrl);
    } catch {
      Toast.show('Could not read that image', 'error'); return;
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
    if (!blob) { Toast.show('Export failed', 'error'); return; }
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = `redacted.${ext}`;
    document.body.appendChild(a); a.click(); URL.revokeObjectURL(url); a.remove();
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
