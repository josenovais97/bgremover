/**
 * QR code generator — 100% client-side.
 *
 * Builds a static QR code (data encoded directly in the code, so it never
 * expires and can't track scans) with qrcode-generator, then renders the
 * module matrix to a canvas ourselves for full control over size and colour,
 * plus a matching SVG for a crisp vector download. Nothing is uploaded.
 */
import qrcode from 'https://cdn.jsdelivr.net/npm/qrcode-generator@1.4.4/+esm';

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];

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

function rafThrottle(fn) {
  let scheduled = false;
  return () => { if (scheduled) return; scheduled = true; requestAnimationFrame(() => { scheduled = false; fn(); }); };
}

const App = {
  text: 'https://clearbg.pt',
  fg: '#000000',
  bg: '#ffffff',
  size: 512,
  ecc: 'M',
  margin: true,
  model: null, // { count, isDark(r,c) }

  init() {
    this.canvas = $('#qr-canvas');
    const render = rafThrottle(() => this.render());

    $('#qr-text').addEventListener('input', (e) => { this.text = e.target.value; render(); });
    $('#qr-fg').addEventListener('input', (e) => { this.fg = e.target.value; render(); });
    $('#qr-bg').addEventListener('input', (e) => { this.bg = e.target.value; render(); });
    $('#qr-size').addEventListener('input', (e) => { this.size = +e.target.value; $('#qr-size-val').textContent = e.target.value; render(); });
    $('#qr-margin').addEventListener('change', (e) => { this.margin = e.target.checked; render(); });
    $$('.qr-ecc-btn').forEach((b) => b.addEventListener('click', () => {
      this.ecc = b.dataset.ecc;
      $$('.qr-ecc-btn').forEach((x) => { const a = x === b; x.classList.toggle('ring-2', a); x.classList.toggle('ring-primary', a); });
      this.render();
    }));

    $('#qr-download').addEventListener('click', () => this.downloadPng());
    $('#qr-download-svg').addEventListener('click', () => this.downloadSvg());

    this.render();
  },

  // Build the QR matrix; returns false (and toasts) if the data is too long.
  build() {
    const qr = qrcode(0, this.ecc); // type 0 = auto-fit the smallest version
    qr.addData(this.text || ' ');
    try {
      qr.make();
    } catch {
      return false; // data overflowed even the largest version at this ECC
    }
    this.model = { count: qr.getModuleCount(), isDark: (r, c) => qr.isDark(r, c) };
    return true;
  },

  render() {
    const ok = this.build();
    const dl = $('#qr-download'), dls = $('#qr-download-svg');
    if (!ok) {
      dl.disabled = dls.disabled = true;
      $('#qr-done').innerHTML = '<span class="text-red-500">Too much data — shorten the text or lower the error correction.</span>';
      return;
    }
    dl.disabled = dls.disabled = false;
    $('#qr-done').textContent = 'Scan it to test before you download.';

    const { count } = this.model;
    const m = this.margin ? 4 : 0;
    const total = count + m * 2;
    const px = Math.max(total, this.size); // preview draws at export size for crispness
    const cell = px / total;
    const c = this.canvas;
    c.width = px; c.height = px;
    const ctx = c.getContext('2d');
    ctx.fillStyle = this.bg;
    ctx.fillRect(0, 0, px, px);
    ctx.fillStyle = this.fg;
    for (let r = 0; r < count; r++) {
      for (let col = 0; col < count; col++) {
        if (this.model.isDark(r, col)) {
          // Round outward so adjacent modules meet with no seams.
          const x = Math.floor((col + m) * cell);
          const y = Math.floor((r + m) * cell);
          const x2 = Math.ceil((col + m + 1) * cell);
          const y2 = Math.ceil((r + m + 1) * cell);
          ctx.fillRect(x, y, x2 - x, y2 - y);
        }
      }
    }
  },

  svgString() {
    const { count } = this.model;
    const m = this.margin ? 4 : 0;
    const total = count + m * 2;
    let rects = '';
    for (let r = 0; r < count; r++) {
      for (let col = 0; col < count; col++) {
        if (this.model.isDark(r, col)) rects += `<rect x="${col + m}" y="${r + m}" width="1" height="1"/>`;
      }
    }
    return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${total} ${total}" width="${this.size}" height="${this.size}" shape-rendering="crispEdges">` +
      `<rect width="${total}" height="${total}" fill="${this.bg}"/><g fill="${this.fg}">${rects}</g></svg>`;
  },

  save(blob, name) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = name;
    document.body.appendChild(a); a.click(); URL.revokeObjectURL(url); a.remove();
  },

  async downloadPng() {
    if (!this.model) return;
    const blob = await new Promise((res) => this.canvas.toBlob(res, 'image/png'));
    if (!blob) { Toast.show('Export failed', 'error'); return; }
    this.save(blob, 'qr-code.png');
    $('#qr-done').innerHTML = `<i class="fa-solid fa-circle-check text-green-500 mr-1"></i>PNG saved · ${this.canvas.width}×${this.canvas.height}px`;
  },

  downloadSvg() {
    if (!this.model) return;
    this.save(new Blob([this.svgString()], { type: 'image/svg+xml' }), 'qr-code.svg');
    $('#qr-done').innerHTML = '<i class="fa-solid fa-circle-check text-green-500 mr-1"></i>SVG saved · scalable vector';
  },
};

document.addEventListener('DOMContentLoaded', () => App.init());
