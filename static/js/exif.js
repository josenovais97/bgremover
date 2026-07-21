/**
 * EXIF / metadata viewer & remover — 100% client-side.
 *
 * Reads the hidden metadata in a photo (GPS location, camera, date, …) with
 * exifr and shows it, then exports a clean copy with the metadata stripped.
 * JPEGs are cleaned losslessly — we drop the APPn/COM marker segments and keep
 * the compressed image data byte-for-byte, so there's zero quality loss.
 * Nothing is uploaded.
 *
 * Batch: stripping metadata needs no per-photo decisions, so extra files are
 * queued and cleaned together into a ZIP. Only the first one is inspected on
 * screen — the rest are cleaned with the same lossless path.
 *
 * Shared helpers come from window.CBG (static/js/kit.js).
 */
import exifr from 'https://cdn.jsdelivr.net/npm/exifr@7.1.3/+esm';

const { $, Toast, loadImage, dropzone, zipDownload, baseName } = window.CBG;

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

// EXIF Orientation says how a viewer must ROTATE the stored pixels, not whether
// the photo is landscape or portrait — the spec's own label for value 1 is
// "Horizontal (normal)", which reads as a shape claim and confuses everyone.
// Keyed by both exifr's translated string and the raw number (if translation is
// ever disabled) so either shape resolves.
const ORIENTATION = {
  1: 'Upright — no rotation', 'Horizontal (normal)': 'Upright — no rotation',
  2: 'Mirrored left–right', 'Mirror horizontal': 'Mirrored left–right',
  3: 'Rotated 180°', 'Rotate 180': 'Rotated 180°',
  4: 'Mirrored top–bottom', 'Mirror vertical': 'Mirrored top–bottom',
  5: 'Mirrored + rotated 270° CW', 'Mirror horizontal and rotate 270 CW': 'Mirrored + rotated 270° CW',
  6: 'Rotated 90° clockwise', 'Rotate 90 CW': 'Rotated 90° clockwise',
  7: 'Mirrored + rotated 90° CW', 'Mirror horizontal and rotate 90 CW': 'Mirrored + rotated 90° CW',
  8: 'Rotated 270° clockwise', 'Rotate 270 CW': 'Rotated 270° clockwise',
};

// Human labels for the fields worth calling out up top.
const NOTABLE = {
  Make: 'Camera make', Model: 'Camera model', LensModel: 'Lens',
  DateTimeOriginal: 'Taken', CreateDate: 'Created', Software: 'Software',
  ISO: 'ISO', FNumber: 'Aperture', ExposureTime: 'Shutter', FocalLength: 'Focal length',
  Orientation: 'Orientation', Artist: 'Author', Copyright: 'Copyright',
};

const { humanSize } = window.CBG;

const App = {
  file: null,
  buffer: null,
  meta: null,
  queue: [],      // extra files cleaned with the same (lossless) path

  init() {
    this.dropzone = $('#ex-dropzone');
    // See watermark.js: closest('section') survives the demo-wrapper grid.
    this.hero = this.dropzone.closest('section');
    this.input = $('#ex-input');
    this.editor = $('#ex-editor');
    this.batch = $('[data-batch]');

    dropzone(this.dropzone, {
      input: this.input,
      icon: $('#ex-icon'),
      browse: $('#ex-browse'),
      onFiles: (files) => this.load(files),
    });

    $('#ex-download').addEventListener('click', () => this.download());
    $('#ex-new').addEventListener('click', () => this.reset());
    $('[data-batch-zip]').addEventListener('click', () => this.downloadAll());

    const sample = $('#ex-sample');
    if (sample) sample.addEventListener('click', (e) => { e.stopPropagation(); this.loadSample(sample.dataset.src); });
  },

  /** Run the tool on the bundled sample photo — same code path as a real drop. */
  async loadSample(src) {
    try {
      const res = await fetch(src);
      const blob = await res.blob();
      await this.load([new File([blob], 'zebra-sample.jpg', { type: 'image/jpeg' })]);
    } catch {
      Toast.show('Could not load the sample', 'error');
    }
  },

  /** Photographers read these as f/1.85 and 1/1433s, not as raw decimals. */
  fmtKeyed(key, v) {
    if (key === 'Orientation') return ORIENTATION[v] || this.fmtValue(v);
    if (typeof v === 'number') {
      if (key === 'FNumber') return `f/${v.toFixed(2).replace(/\.?0+$/, '')}`;
      if (key === 'ExposureTime') return v < 1 ? `1/${Math.round(1 / v)}s` : `${v}s`;
      if (key === 'FocalLength') return `${+v.toFixed(2)} mm`;
    }
    return this.fmtValue(v);
  },

  fmtValue(v) {
    if (v instanceof Date) return v.toLocaleString();
    if (Array.isArray(v)) return v.join(', ');
    if (typeof v === 'number') return Number.isInteger(v) ? String(v) : v.toFixed(4);
    return String(v).slice(0, 120);
  },

  async load(files) {
    const [first, ...rest] = files;
    this.file = first;
    this.queue = rest;
    this.buffer = await first.arrayBuffer();
    if (this.previewUrl) URL.revokeObjectURL(this.previewUrl);
    this.previewUrl = URL.createObjectURL(first);
    $('#ex-preview').src = this.previewUrl;
    try { this.meta = await exifr.parse(first, true); } catch { this.meta = null; }
    this.render();
    this.hero.classList.add('hidden');
    this.editor.classList.remove('hidden');
    this.syncBatch();
  },

  syncBatch() {
    const n = this.queue.length + 1;
    this.batch.classList.toggle('hidden', n < 2);
    this.batch.querySelector('[data-batch-count]').textContent = n;
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
        .map((k) => `<div class="flex justify-between gap-3 py-1 border-b border-gray-200/50 dark:border-gray-800/50 last:border-0"><span class="text-gray-500 dark:text-gray-400">${NOTABLE[k]}</span><span class="font-medium text-right truncate max-w-[60%]">${this.fmtKeyed(k, meta[k])}</span></div>`).join('');
      summary.innerHTML = `<div class="flex items-center gap-2 font-semibold"><i class="fa-solid fa-database text-primaryText"></i> ${count} metadata field${count === 1 ? '' : 's'} found</div>${notable ? `<div class="mt-2">${notable}</div>` : ''}`;
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

  /** Strip metadata from `file` and return {blob, ext} — lossless for JPEG. */
  async cleanBlob(file = this.file, buffer = this.buffer, previewUrl = this.previewUrl) {
    if (!buffer) buffer = await file.arrayBuffer();
    // Lossless path for JPEG; re-encode via canvas otherwise (PNG stays lossless).
    const isJpeg = file.type === 'image/jpeg' || new DataView(buffer).getUint16(0) === 0xFFD8;
    if (isJpeg) {
      const bytes = stripJpeg(buffer);
      if (bytes) return { blob: new Blob([bytes], { type: 'image/jpeg' }), ext: 'jpg' };
    }
    const url = previewUrl || URL.createObjectURL(file);
    try {
      const img = await loadImage(url);
      const c = document.createElement('canvas');
      c.width = img.naturalWidth; c.height = img.naturalHeight;
      c.getContext('2d').drawImage(img, 0, 0);
      const type = file.type === 'image/webp' ? 'image/webp' : 'image/png';
      const ext = type === 'image/webp' ? 'webp' : 'png';
      const blob = await new Promise((res) => c.toBlob(res, type, 0.95));
      return { blob, ext };
    } finally {
      if (url !== previewUrl) URL.revokeObjectURL(url);
    }
  },

  async download() {
    if (!this.file) return;
    const { blob, ext } = await this.cleanBlob();
    if (!blob) { Toast.show('Export failed', 'error'); return; }
    window.CBG.download(blob, `${baseName(this.file.name)}-clean.${ext}`);
    $('#ex-filemeta').innerHTML = `<i class="fa-solid fa-circle-check text-green-500 mr-1"></i>Clean copy saved · ${humanSize(blob.size)} · no metadata`;
  },

  async downloadAll() {
    const btn = $('[data-batch-zip]');
    const label = btn.querySelector('[data-batch-label]');
    const original = label.textContent;
    btn.disabled = true;
    label.textContent = 'Cleaning…';
    try {
      const first = await this.cleanBlob();
      const entries = [{ name: `${baseName(this.file.name)}-clean.${first.ext}`, blob: first.blob }];
      for (const f of this.queue) {
        const { blob, ext } = await this.cleanBlob(f, null, null);
        if (blob) entries.push({ name: `${baseName(f.name)}-clean.${ext}`, blob });
      }
      await zipDownload(entries, 'clearbg-metadata-removed.zip');
    } catch {
      Toast.show('Could not build the ZIP', 'error');
    } finally {
      btn.disabled = false;
      label.textContent = original;
    }
  },

  reset() {
    this.editor.classList.add('hidden');
    this.hero.classList.remove('hidden');
    if (this.previewUrl) { URL.revokeObjectURL(this.previewUrl); this.previewUrl = null; }
    this.file = this.buffer = this.meta = null;
    this.queue = [];
    this.syncBatch();
  },
};

document.addEventListener('DOMContentLoaded', () => App.init());
