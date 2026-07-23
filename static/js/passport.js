/**
 * Passport / ID photo maker — 100% client-side.
 *
 * Removes the background from a portrait (lazy-loaded @imgly model), drops the
 * subject onto a plain compliant background, and lets you position the head
 * inside biometric guides for a specific country's size. Exports the exact pixel
 * dimensions that photo booths / official portals expect (at 300 DPI), plus an
 * optional 6×4" print sheet tiled with copies. Nothing is uploaded.
 *
 * Helpers ($, Toast, loadImage, t, …) come from window.CBG (static/js/kit.js),
 * a classic script — a local ES import would break, since Django's hashed-manifest
 * static storage does not rewrite ES-module import paths.
 */

const { $, $$, Toast, loadImage, download, t } = CBG;
import { removeBackground } from 'https://cdn.jsdelivr.net/npm/@imgly/background-removal@1.6.0/+esm';

/* --------------------------------------------------------------- helpers */
const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));

function rafThrottle(fn) {
  let scheduled = false;
  return () => { if (scheduled) return; scheduled = true; requestAnimationFrame(() => { scheduled = false; fn(); }); };
}

const DPI = 300;
const MM = DPI / 25.4;                       // px per millimetre at 300 DPI
const mm = (v) => Math.round(v * MM);
const inch = (v) => Math.round(v * DPI);

/**
 * Country / document presets. `w`/`h` are the exact export pixels at 300 DPI.
 * `crown`/`chin` are the target head band (top of hair → bottom of chin) as a
 * fraction of frame height — rendered as guide lines to position the face.
 */
const PRESETS = {
  us:        { label: 'US 2×2 in — Passport · Visa · Green Card', size: '2×2 in', w: inch(2),  h: inch(2),  crown: 0.12, chin: 0.80 },
  schengen:  { label: 'EU · Schengen · UK · India · AU — 35×45 mm', size: '35×45 mm', w: mm(35), h: mm(45), crown: 0.06, chin: 0.82 },
  canada:    { label: 'Canada — 50×70 mm', size: '50×70 mm', w: mm(50), h: mm(70), crown: 0.10, chin: 0.56 },
  china:     { label: 'China Visa — 33×48 mm', size: '33×48 mm', w: mm(33), h: mm(48), crown: 0.10, chin: 0.80 },
  custom:    { label: 'Custom size…', size: '', w: mm(35), h: mm(45), crown: 0.07, chin: 0.82, custom: true },
};

// Common compliant background colours (white is the safe default nearly
// everywhere; light grey/blue are accepted by some countries).
const BACKGROUNDS = [
  { label: 'White', value: '#ffffff' },
  { label: 'Off-white', value: '#f3f4f6' },
  { label: 'Light grey', value: '#d1d5db' },
  { label: 'Light blue', value: '#dbeafe' },
];

/* --------------------------------------------------------------------- app */
const App = {
  cutout: null,       // HTMLImageElement of the transparent cut-out
  bbox: null,         // subject bounding box in cut-out source px
  presetKey: 'us',
  custom: { w: 35, h: 45 },   // mm
  bg: '#ffffff',
  place: { s: 1, dx: 0, dy: 0 }, // scale + top-left offset of cut-out in frame px
  showGuides: true,

  init() {
    this.dropzone = $('#pp-dropzone');
    this.input = $('#pp-input');
    this.editor = $('#pp-editor');
    this.canvas = $('#pp-canvas');
    this.overlay = $('#pp-overlay');

    const open = () => this.input.click();
    $('#pp-browse').addEventListener('click', (e) => { e.stopPropagation(); open(); });
    this.dropzone.addEventListener('click', open);
    this.dropzone.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); } });
    this.input.addEventListener('change', (e) => this.load(e.target.files[0]));

    const icon = $('#pp-icon');
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach((evt) =>
      this.dropzone.addEventListener(evt, (e) => { e.preventDefault(); e.stopPropagation(); }));
    ['dragenter', 'dragover'].forEach((evt) => this.dropzone.addEventListener(evt, () => { this.dropzone.classList.add('border-primary', 'bg-primary/5'); icon.classList.add('scale-110'); }));
    ['dragleave', 'drop'].forEach((evt) => this.dropzone.addEventListener(evt, () => { this.dropzone.classList.remove('border-primary', 'bg-primary/5'); icon.classList.remove('scale-110'); }));
    this.dropzone.addEventListener('drop', (e) => this.load(e.dataTransfer.files[0]));
    document.addEventListener('paste', (e) => {
      const f = [...(e.clipboardData?.items || [])].find((i) => i.kind === 'file');
      if (f) this.load(f.getAsFile());
    });

    // Preset buttons.
    const presetWrap = $('#pp-presets');
    presetWrap.innerHTML = Object.entries(PRESETS).map(([k, p]) =>
      `<button type="button" data-preset="${k}" class="pp-preset text-left px-3 py-2 rounded-lg border text-xs transition ${k === this.presetKey ? 'border-primary bg-primary/5 text-primaryText' : 'border-gray-300 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800'}">
        <span class="block font-semibold leading-tight">${p.label.split(' — ')[0]}</span>
        <span class="block text-gray-400">${p.size || 'set below'}</span>
      </button>`).join('');
    presetWrap.addEventListener('click', (e) => {
      const b = e.target.closest('.pp-preset');
      if (!b) return;
      this.setPreset(b.dataset.preset);
    });

    // Background swatches.
    const bgWrap = $('#pp-bg');
    bgWrap.innerHTML = BACKGROUNDS.map((c) =>
      `<button type="button" data-bg="${c.value}" title="${c.label}" class="pp-bg w-8 h-8 rounded-full border-2 ${c.value === this.bg ? 'border-primary ring-2 ring-primary/40' : 'border-gray-300 dark:border-gray-600'}" style="background:${c.value}"></button>`).join('');
    bgWrap.addEventListener('click', (e) => {
      const b = e.target.closest('.pp-bg');
      if (!b) return;
      this.bg = b.dataset.bg;
      $$('.pp-bg').forEach((x) => { const a = x.dataset.bg === this.bg; x.classList.toggle('border-primary', a); x.classList.toggle('ring-2', a); x.classList.toggle('ring-primary/40', a); x.classList.toggle('border-gray-300', !a); x.classList.toggle('dark:border-gray-600', !a); });
      this.render();
    });

    // Custom size inputs.
    $('#pp-cw').addEventListener('input', (e) => { this.custom.w = clamp(+e.target.value || 0, 10, 200); if (this.presetKey === 'custom') this.applyPreset(); });
    $('#pp-ch').addEventListener('input', (e) => { this.custom.h = clamp(+e.target.value || 0, 10, 200); if (this.presetKey === 'custom') this.applyPreset(); });

    // Zoom + reposition.
    const render = rafThrottle(() => this.render());
    $('#pp-zoom').addEventListener('input', (e) => { this.zoomTo(+e.target.value / 100); render(); });
    $('#pp-guides').addEventListener('change', (e) => { this.showGuides = e.target.checked; this.render(); });
    $('#pp-autofit').addEventListener('click', () => { this.autoFit(); this.render(); });

    this.overlay.addEventListener('pointerdown', (e) => {
      this.overlay.setPointerCapture?.(e.pointerId);
      this.drag = { x: e.clientX, y: e.clientY };
      this.overlay.style.cursor = 'grabbing';
    });
    this.overlay.addEventListener('pointermove', (e) => this.onDrag(e));
    ['pointerup', 'pointercancel', 'pointerleave'].forEach((ev) => this.overlay.addEventListener(ev, () => { this.drag = null; this.overlay.style.cursor = 'grab'; }));
    this.overlay.addEventListener('wheel', (e) => {
      e.preventDefault();
      this.zoomTo(this.place.s / this.baseScale * (e.deltaY < 0 ? 1.06 : 0.94));
      $('#pp-zoom').value = Math.round(this.place.s / this.baseScale * 100);
      render();
    }, { passive: false });

    $('#pp-download').addEventListener('click', () => this.export('image/jpeg'));
    $('#pp-download-png').addEventListener('click', () => this.export('image/png'));
    $$('.pp-sheet').forEach((b) => b.addEventListener('click', () => this.exportSheet(b.dataset.sheet)));
    $('#pp-new').addEventListener('click', () => this.reset());

    // Deep link from a country landing page: /passport-photo/?w=35&h=45&country=UK
    // pre-selects that exact size as a custom preset.
    const params = new URLSearchParams(location.search);
    const uw = parseInt(params.get('w'), 10);
    const uh = parseInt(params.get('h'), 10);
    if (uw >= 10 && uw <= 200 && uh >= 10 && uh <= 200) {
      this.custom = { w: uw, h: uh };
      $('#pp-cw').value = uw;
      $('#pp-ch').value = uh;
      const country = params.get('country');
      if (country) {
        const label = $('#pp-preset-note');
        if (label) label.textContent = `${country} · ${uw}×${uh} mm`;
      }
      this.setPreset('custom');
    } else {
      this.applyPreset();
    }
  },

  frame() {
    const p = PRESETS[this.presetKey];
    if (p.custom) return { w: mm(this.custom.w), h: mm(this.custom.h), crown: p.crown, chin: p.chin };
    return { w: p.w, h: p.h, crown: p.crown, chin: p.chin };
  },

  setPreset(key) {
    this.presetKey = key;
    $$('.pp-preset').forEach((b) => {
      const a = b.dataset.preset === key;
      b.classList.toggle('border-primary', a); b.classList.toggle('bg-primary/5', a); b.classList.toggle('text-primaryText', a);
      b.classList.toggle('border-gray-300', !a); b.classList.toggle('dark:border-gray-700', !a);
    });
    $('#pp-custom-row').classList.toggle('hidden', key !== 'custom');
    this.applyPreset();
  },

  applyPreset() {
    const f = this.frame();
    // Canvas intrinsic size = exact export pixels; CSS scales it to fit.
    this.canvas.width = f.w; this.canvas.height = f.h;
    this.overlay.width = f.w; this.overlay.height = f.h;
    $('#pp-size-note').textContent = `${f.w}×${f.h} px · 300 DPI`;
    if (this.cutout) { this.autoFit(); this.render(); }
  },

  setBusy(busy, text) {
    $('#pp-status').classList.toggle('hidden', !busy);
    if (text) $('#pp-status-text').textContent = text;
    [$('#pp-download'), $('#pp-download-png'), ...$$('.pp-sheet')].forEach((el) => { el.disabled = busy || !this.cutout; });
  },

  async load(file) {
    this.input.value = '';
    if (!file || !/^image\//.test(file.type)) { Toast.show(t('Please choose an image'), 'error'); return; }
    this.cutout = null;
    this.dropzone.parentElement.classList.add('hidden');
    this.editor.classList.remove('hidden');
    this.setBusy(true, 'Removing background…');
    try {
      // Full 'isnet' when cross-origin isolated (threaded WASM); quantized
      // fallback otherwise. See config/middleware.py ISOLATED_VIEWS.
      const blob = await removeBackground(file, { model: self.crossOriginIsolated ? 'isnet' : 'isnet_quint8' });
      if (this.cutoutUrl) URL.revokeObjectURL(this.cutoutUrl);
      this.cutoutUrl = URL.createObjectURL(blob);
      this.cutout = await loadImage(this.cutoutUrl);
      this.bbox = this.alphaBBox(this.cutout);
      this.setBusy(false);
      this.autoFit();
      this.render();
      window.__clearbgReport?.(1);
      Toast.show(t('Background removed — position the head inside the guides'), 'success');
    } catch (err) {
      console.error('[passport] bg removal failed:', err);
      Toast.show(t('Background removal failed'), 'error');
      this.setBusy(false);
    }
  },

  /** Tight bounding box of non-transparent pixels, in source px. */
  alphaBBox(img) {
    const w = img.naturalWidth, h = img.naturalHeight;
    const c = document.createElement('canvas');
    c.width = w; c.height = h;
    const ctx = c.getContext('2d');
    ctx.drawImage(img, 0, 0);
    const data = ctx.getImageData(0, 0, w, h).data;
    let minX = w, minY = h, maxX = 0, maxY = 0, found = false;
    for (let y = 0; y < h; y++) {
      for (let x = 0; x < w; x++) {
        if (data[(y * w + x) * 4 + 3] > 12) {
          found = true;
          if (x < minX) minX = x; if (x > maxX) maxX = x;
          if (y < minY) minY = y; if (y > maxY) maxY = y;
        }
      }
    }
    if (!found) return { x: 0, y: 0, w, h };
    return { x: minX, y: minY, w: maxX - minX + 1, h: maxY - minY + 1 };
  },

  /**
   * Auto-place the subject: scale so the head (estimated as the top ~55% of the
   * subject box — head+neck) spans the guide band, then align its top near the
   * crown line and centre it horizontally.
   */
  autoFit() {
    if (!this.cutout || !this.bbox) return;
    const f = this.frame();
    const bandTop = f.crown * f.h;
    const bandBottom = f.chin * f.h;
    const targetHeadPx = bandBottom - bandTop;
    // Head portion of the cut-out box (crown → chin ≈ top 55% of a head+shoulders shot).
    const headSrc = this.bbox.h * 0.55;
    this.baseScale = targetHeadPx / headSrc;
    this.place.s = this.baseScale;
    const bboxCx = this.bbox.x + this.bbox.w / 2;
    this.place.dx = f.w / 2 - bboxCx * this.place.s;
    this.place.dy = bandTop - this.bbox.y * this.place.s;
    $('#pp-zoom').value = 100;
  },

  zoomTo(mult) {
    const f = this.frame();
    const newS = clamp(this.baseScale * mult, this.baseScale * 0.4, this.baseScale * 3);
    // Zoom around the frame centre so the head stays roughly put.
    const cx = f.w / 2, cy = f.h / 2;
    const k = newS / this.place.s;
    this.place.dx = cx - (cx - this.place.dx) * k;
    this.place.dy = cy - (cy - this.place.dy) * k;
    this.place.s = newS;
  },

  onDrag(e) {
    if (!this.drag) return;
    const r = this.overlay.getBoundingClientRect();
    const sx = this.overlay.width / r.width, sy = this.overlay.height / r.height;
    this.place.dx += (e.clientX - this.drag.x) * sx;
    this.place.dy += (e.clientY - this.drag.y) * sy;
    this.drag = { x: e.clientX, y: e.clientY };
    this.render();
  },

  /** Paint the passport photo (background + cut-out) into `canvas` at frame size. */
  paint(canvas, f) {
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, f.w, f.h);
    ctx.fillStyle = this.bg;
    ctx.fillRect(0, 0, f.w, f.h);
    if (!this.cutout) return;
    const dw = this.cutout.naturalWidth * this.place.s;
    const dh = this.cutout.naturalHeight * this.place.s;
    ctx.imageSmoothingQuality = 'high';
    ctx.drawImage(this.cutout, this.place.dx, this.place.dy, dw, dh);
  },

  render() {
    const f = this.frame();
    this.paint(this.canvas, f);
    this.drawGuides(f);
  },

  drawGuides(f) {
    const ctx = this.overlay.getContext('2d');
    ctx.clearRect(0, 0, f.w, f.h);
    if (!this.showGuides) return;
    const crownY = f.crown * f.h, chinY = f.chin * f.h;
    ctx.save();
    ctx.strokeStyle = 'rgba(79,70,229,0.9)';
    ctx.setLineDash([f.w * 0.02, f.w * 0.02]);
    ctx.lineWidth = Math.max(2, f.w * 0.006);
    // Crown + chin band.
    [crownY, chinY].forEach((y) => { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(f.w, y); ctx.stroke(); });
    // Vertical centre.
    ctx.beginPath(); ctx.moveTo(f.w / 2, 0); ctx.lineTo(f.w / 2, f.h); ctx.stroke();
    // Head oval guide.
    const cy = (crownY + chinY) / 2, rh = (chinY - crownY) / 2, rw = rh * 0.72;
    ctx.setLineDash([]);
    ctx.strokeStyle = 'rgba(79,70,229,0.55)';
    ctx.beginPath(); ctx.ellipse(f.w / 2, cy, rw, rh, 0, 0, Math.PI * 2); ctx.stroke();
    ctx.restore();
  },

  /* ------------------------------------------------------------- export */
  filename(ext) {
    const p = PRESETS[this.presetKey];
    const tag = p.custom ? `${this.custom.w}x${this.custom.h}mm` : p.size.replace(/[^\dx]/gi, '') || 'photo';
    return `passport-photo-${tag}.${ext}`;
  },

  async export(fmt) {
    if (!this.cutout) return;
    const f = this.frame();
    const c = document.createElement('canvas');
    c.width = f.w; c.height = f.h;
    this.paint(c, f);
    const ext = fmt === 'image/png' ? 'png' : 'jpg';
    const blob = await new Promise((res) => c.toBlob(res, fmt, 0.95));
    if (!blob) { Toast.show(t('Export failed'), 'error'); return; }
    this.download(blob, this.filename(ext));
    const kb = Math.round(blob.size / 1024);
    $('#pp-done').innerHTML = `<i class="fa-solid fa-circle-check text-green-500 mr-1"></i>Saved ${ext.toUpperCase()} · ${f.w}×${f.h}px · ${kb} KB`;
  },

  /**
   * Tile the photo onto a print sheet with thin cut guides, at 300 DPI:
   *   '6x4'    6×4 in  (1800×1200) — pharmacy / kiosk photo print
   *   'a4'     A4      (210×297 mm) — home printer, most of the world
   *   'letter' Letter  (8.5×11 in) — home printer, US / Canada
   * Portrait orientation for the paper sizes fits more rows of a tall photo.
   */
  async exportSheet(kind = '6x4') {
    if (!this.cutout) return;
    const f = this.frame();
    const SHEETS = {
      '6x4': { w: inch(6), h: inch(4), label: '6×4"' },
      a4: { w: mm(210), h: mm(297), label: 'A4' },
      letter: { w: inch(8.5), h: inch(11), label: 'Letter' },
    };
    const paper = SHEETS[kind] || SHEETS['6x4'];
    const SW = paper.w, SH = paper.h, gap = mm(3), margin = mm(4);
    // One rendered photo to stamp repeatedly.
    const photo = document.createElement('canvas');
    photo.width = f.w; photo.height = f.h;
    this.paint(photo, f);

    const sheet = document.createElement('canvas');
    sheet.width = SW; sheet.height = SH;
    const ctx = sheet.getContext('2d');
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, SW, SH);
    const cols = Math.max(1, Math.floor((SW - 2 * margin + gap) / (f.w + gap)));
    const rows = Math.max(1, Math.floor((SH - 2 * margin + gap) / (f.h + gap)));
    if (cols * rows === 0) { Toast.show(t('Photo is larger than a 6×4 print'), 'error'); return; }
    const totalW = cols * f.w + (cols - 1) * gap;
    const totalH = rows * f.h + (rows - 1) * gap;
    const ox = (SW - totalW) / 2, oy = (SH - totalH) / 2;
    for (let r = 0; r < rows; r++) {
      for (let cN = 0; cN < cols; cN++) {
        const x = ox + cN * (f.w + gap), y = oy + r * (f.h + gap);
        ctx.drawImage(photo, x, y);
        ctx.strokeStyle = 'rgba(0,0,0,0.25)';
        ctx.lineWidth = 1;
        ctx.strokeRect(x + 0.5, y + 0.5, f.w - 1, f.h - 1);
      }
    }
    const blob = await new Promise((res) => sheet.toBlob(res, 'image/jpeg', 0.95));
    if (!blob) { Toast.show(t('Export failed'), 'error'); return; }
    this.download(blob, this.filename(`sheet-${kind}.jpg`));
    $('#pp-done').innerHTML = `<i class="fa-solid fa-circle-check text-green-500 mr-1"></i>Print sheet saved · ${cols * rows} copies on ${paper.label}`;
  },

  download(blob, name) {
    download(blob, name);
  },

  reset() {
    this.editor.classList.add('hidden');
    this.dropzone.parentElement.classList.remove('hidden');
    if (this.cutoutUrl) { URL.revokeObjectURL(this.cutoutUrl); this.cutoutUrl = null; }
    this.cutout = null; this.bbox = null;
    $('#pp-done').textContent = '';
  },
};

document.addEventListener('DOMContentLoaded', () => App.init());
