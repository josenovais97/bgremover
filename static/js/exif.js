/**
 * EXIF / metadata viewer & remover — 100% client-side.
 *
 * Reads the hidden metadata in a photo (GPS location, camera, date, …) with
 * exifr and shows it, then exports a clean copy with the metadata stripped.
 * JPEGs are cleaned losslessly — we drop the APPn/COM marker segments and keep
 * the compressed image data byte-for-byte, so there's zero quality loss.
 * Nothing is uploaded.
 */
import exifr from 'https://cdn.jsdelivr.net/npm/exifr@7.1.3/+esm';

const $ = (s, r = document) => r.querySelector(s);

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

const humanSize = (b) => (b < 1024 ? `${b} B` : b < 1048576 ? `${(b / 1024).toFixed(0)} KB` : `${(b / 1048576).toFixed(1)} MB`);

// Losslessly strip a JPEG's metadata: keep every marker segment except the
// APPn (0xE0–0xEF, where EXIF/JFIF/XMP live) and COM (0xFE) blocks, and copy
// the entropy-coded scan (from SOS) verbatim. Returns a Uint8Array or null.
function stripJpeg(buffer) {
  const v = new DataView(buffer);
  if (v.getUint16(0) !== 0xFFD8) return null;
  const src = new Uint8Array(buffer);
  const keep = [[0, 2]]; // SOI
  let o = 2;
  const n = v.byteLength;
  while (o < n) {
    if (v.getUint8(o) !== 0xFF) break;
    const marker = v.getUint8(o + 1);
    if (marker === 0xDA) { keep.push([o, n]); break; }          // SOS → rest is scan
    if (marker === 0xD9) { keep.push([o, o + 2]); break; }       // EOI
    if (marker >= 0xD0 && marker <= 0xD8) { o += 2; continue; }  // standalone markers
    const len = v.getUint16(o + 2);
    const drop = (marker >= 0xE0 && marker <= 0xEF) || marker === 0xFE;
    if (!drop) keep.push([o, o + 2 + len]);
    o += 2 + len;
  }
  const total = keep.reduce((s, [a, b]) => s + (b - a), 0);
  const out = new Uint8Array(total);
  let p = 0;
  for (const [a, b] of keep) { out.set(src.subarray(a, b), p); p += b - a; }
  return out;
}

const loadImage = (src) => new Promise((resolve, reject) => {
  const img = new Image(); img.onload = () => resolve(img); img.onerror = reject; img.src = src;
});

// Human labels for the fields worth calling out up top.
const NOTABLE = {
  Make: 'Camera make', Model: 'Camera model', LensModel: 'Lens',
  DateTimeOriginal: 'Taken', CreateDate: 'Created', Software: 'Software',
  ISO: 'ISO', FNumber: 'Aperture', ExposureTime: 'Shutter', FocalLength: 'Focal length',
  Orientation: 'Orientation', Artist: 'Author', Copyright: 'Copyright',
};

const App = {
  file: null,
  buffer: null,
  meta: null,

  init() {
    this.dropzone = $('#ex-dropzone');
    this.input = $('#ex-input');
    this.editor = $('#ex-editor');

    const open = () => this.input.click();
    $('#ex-browse').addEventListener('click', (e) => { e.stopPropagation(); open(); });
    this.dropzone.addEventListener('click', open);
    this.dropzone.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); } });
    this.input.addEventListener('change', (e) => this.load(e.target.files[0]));

    const icon = $('#ex-icon');
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach((evt) =>
      this.dropzone.addEventListener(evt, (e) => { e.preventDefault(); e.stopPropagation(); }));
    ['dragenter', 'dragover'].forEach((evt) => this.dropzone.addEventListener(evt, () => { this.dropzone.classList.add('border-primary', 'bg-primary/5'); icon.classList.add('scale-110'); }));
    ['dragleave', 'drop'].forEach((evt) => this.dropzone.addEventListener(evt, () => { this.dropzone.classList.remove('border-primary', 'bg-primary/5'); icon.classList.remove('scale-110'); }));
    this.dropzone.addEventListener('drop', (e) => this.load(e.dataTransfer.files[0]));
    document.addEventListener('paste', (e) => {
      const f = [...(e.clipboardData?.items || [])].find((i) => i.kind === 'file');
      if (f) this.load(f.getAsFile());
    });

    $('#ex-download').addEventListener('click', () => this.download());
    $('#ex-new').addEventListener('click', () => this.reset());
  },

  fmtValue(v) {
    if (v instanceof Date) return v.toLocaleString();
    if (Array.isArray(v)) return v.join(', ');
    if (typeof v === 'number') return Number.isInteger(v) ? String(v) : v.toFixed(4);
    return String(v).slice(0, 120);
  },

  async load(file) {
    this.input.value = '';
    if (!file || !/^image\//.test(file.type)) { Toast.show('Please choose an image', 'error'); return; }
    this.file = file;
    this.buffer = await file.arrayBuffer();
    if (this.previewUrl) URL.revokeObjectURL(this.previewUrl);
    this.previewUrl = URL.createObjectURL(file);
    $('#ex-preview').src = this.previewUrl;
    try { this.meta = await exifr.parse(file, true); } catch { this.meta = null; }
    this.render();
    this.dropzone.parentElement.classList.add('hidden');
    this.editor.classList.remove('hidden');
  },

  render() {
    const meta = this.meta || {};
    const keys = Object.keys(meta).filter((k) => meta[k] != null && meta[k] !== '');
    const count = keys.length;
    $('#ex-filemeta').textContent = `${this.file.name} · ${humanSize(this.file.size)}`;

    // Summary
    const summary = $('#ex-summary');
    if (!count) {
      summary.innerHTML = '<div class="flex items-center gap-2 text-green-600 dark:text-green-400 font-semibold"><i class="fa-solid fa-circle-check"></i> No metadata found</div><p class="text-xs text-gray-500 dark:text-gray-400 mt-1">This photo is already clean — you can still re-save a copy below.</p>';
    } else {
      const notable = Object.keys(NOTABLE).filter((k) => meta[k] != null && meta[k] !== '')
        .map((k) => `<div class="flex justify-between gap-3 py-1 border-b border-gray-200/50 dark:border-gray-800/50 last:border-0"><span class="text-gray-500 dark:text-gray-400">${NOTABLE[k]}</span><span class="font-medium text-right truncate max-w-[60%]">${this.fmtValue(meta[k])}</span></div>`).join('');
      summary.innerHTML = `<div class="flex items-center gap-2 font-semibold"><i class="fa-solid fa-database text-primary"></i> ${count} metadata field${count === 1 ? '' : 's'} found</div>${notable ? `<div class="mt-2">${notable}</div>` : ''}`;
    }

    // GPS
    const gps = $('#ex-gps');
    if (meta.latitude != null && meta.longitude != null) {
      gps.classList.remove('hidden');
      $('#ex-gps-detail').textContent = `${meta.latitude.toFixed(5)}, ${meta.longitude.toFixed(5)} — this reveals exactly where the photo was taken. It will be removed from the clean copy.`;
    } else {
      gps.classList.add('hidden');
    }

    // Full list
    const details = $('#ex-details'), list = $('#ex-list');
    if (count) {
      details.classList.remove('hidden');
      list.innerHTML = keys.map((k) => `<div class="flex justify-between gap-3"><span class="text-gray-500 dark:text-gray-400 shrink-0">${k}</span><span class="text-right break-all">${this.fmtValue(meta[k])}</span></div>`).join('');
    } else {
      details.classList.add('hidden');
    }
  },

  async cleanBlob() {
    // Lossless path for JPEG; re-encode via canvas otherwise (PNG stays lossless).
    const isJpeg = this.file.type === 'image/jpeg' || new DataView(this.buffer).getUint16(0) === 0xFFD8;
    if (isJpeg) {
      const bytes = stripJpeg(this.buffer);
      if (bytes) return { blob: new Blob([bytes], { type: 'image/jpeg' }), ext: 'jpg' };
    }
    const img = await loadImage(this.previewUrl);
    const c = document.createElement('canvas');
    c.width = img.naturalWidth; c.height = img.naturalHeight;
    c.getContext('2d').drawImage(img, 0, 0);
    const type = this.file.type === 'image/webp' ? 'image/webp' : 'image/png';
    const ext = type === 'image/webp' ? 'webp' : 'png';
    const blob = await new Promise((res) => c.toBlob(res, type, 0.95));
    return { blob, ext };
  },

  async download() {
    if (!this.file) return;
    const { blob, ext } = await this.cleanBlob();
    if (!blob) { Toast.show('Export failed', 'error'); return; }
    const base = this.file.name.replace(/\.[^.]+$/, '');
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = `${base}-clean.${ext}`;
    document.body.appendChild(a); a.click(); URL.revokeObjectURL(url); a.remove();
    $('#ex-filemeta').innerHTML = `<i class="fa-solid fa-circle-check text-green-500 mr-1"></i>Clean copy saved · ${humanSize(blob.size)} · no metadata`;
  },

  reset() {
    this.editor.classList.add('hidden');
    this.dropzone.parentElement.classList.remove('hidden');
    if (this.previewUrl) { URL.revokeObjectURL(this.previewUrl); this.previewUrl = null; }
    this.file = this.buffer = this.meta = null;
  },
};

document.addEventListener('DOMContentLoaded', () => App.init());
