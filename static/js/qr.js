/**
 * QR code generator — 100% client-side, with styling.
 *
 * Builds a static QR (data encoded in the code, so it never expires and can't
 * track scans) with qrcode-generator, then renders the module matrix ourselves
 * so we can style it: square / rounded / dot modules, styled corner "eyes",
 * a solid or gradient fill, and an optional centre logo. Exports a crisp PNG
 * (from the canvas) or a matching SVG vector. Nothing is uploaded.
 */

const { $, $$, Toast, download, t } = CBG;
import qrcode from 'https://cdn.jsdelivr.net/npm/qrcode-generator@1.4.4/+esm';

function rafThrottle(fn) {
  let scheduled = false;
  return () => { if (scheduled) return; scheduled = true; requestAnimationFrame(() => { scheduled = false; fn(); }); };
}

const PRESETS = {
  classic: { moduleShape: 'square', eyeShape: 'square', gradient: false },
  rounded: { moduleShape: 'rounded', eyeShape: 'rounded', gradient: false },
  dots: { moduleShape: 'dots', eyeShape: 'circle', gradient: false },
  soft: { moduleShape: 'rounded', eyeShape: 'rounded', gradient: true, fg: '#4f46e5', fg2: '#06b6d4' },
};

// Curated foreground/background pairs. Every one is dark-on-light or light-on-
// dark with a wide margin, because the two reliable ways to make a QR unscannable
// are low contrast and an inverted (light-on-dark) code that some readers reject.
const PALETTES = [
  { name: 'Ink', fg: '#111827', bg: '#ffffff', gradient: false },
  { name: 'Ocean', fg: '#0369a1', bg: '#ffffff', gradient: true, fg2: '#0891b2' },
  { name: 'Grape', fg: '#6d28d9', bg: '#ffffff', gradient: true, fg2: '#c026d3' },
  { name: 'Sunset', fg: '#c2410c', bg: '#ffffff', gradient: true, fg2: '#be123c' },
  { name: 'Forest', fg: '#065f46', bg: '#ffffff', gradient: false },
  { name: 'Midnight', fg: '#e5e7eb', bg: '#0f172a', gradient: false },
];

/* ----------------------------------------------------------------- drawing
 * These are free functions taking an options object rather than methods on App,
 * so the style-preset thumbnails paint through exactly the same code as the
 * 512px export. A thumbnail drawn by a separate simplified routine would
 * eventually stop matching what clicking it actually does.
 */
function roundRectPath(ctx, x, y, w, h, r) {
  ctx.beginPath();
  if (r > 0.01 && ctx.roundRect) ctx.roundRect(x, y, w, h, r);
  else ctx.rect(x, y, w, h);
}

function drawModule(ctx, x, y, cell, shape) {
  // Dots must slightly overlap their neighbours (r ≥ 0.5·cell) or scanners
  // can't fit the module grid; 0.52 keeps a clean dot look with a safety margin.
  if (shape === 'dots') { ctx.beginPath(); ctx.arc(x + cell / 2, y + cell / 2, cell * 0.52, 0, Math.PI * 2); ctx.fill(); }
  else if (shape === 'rounded') { roundRectPath(ctx, x, y, cell, cell, cell * 0.35); ctx.fill(); }
  else ctx.fillRect(x, y, cell, cell);
}

function eyeRadius(n, shape) {
  return shape === 'circle' ? n / 2 : shape === 'rounded' ? n * 0.28 : 0;
}

function drawEye(ctx, ox, oy, cell, fill, o) {
  ctx.fillStyle = fill;
  roundRectPath(ctx, ox, oy, 7 * cell, 7 * cell, eyeRadius(7 * cell, o.eyeShape)); ctx.fill();
  ctx.fillStyle = o.bg;
  roundRectPath(ctx, ox + cell, oy + cell, 5 * cell, 5 * cell, eyeRadius(5 * cell, o.eyeShape)); ctx.fill();
  ctx.fillStyle = fill;
  roundRectPath(ctx, ox + 2 * cell, oy + 2 * cell, 3 * cell, 3 * cell, eyeRadius(3 * cell, o.eyeShape)); ctx.fill();
}

const isEye = (r, c, n) => (r < 7 && c < 7) || (r < 7 && c >= n - 7) || (r >= n - 7 && c < 7);

/** Paint `model` onto `ctx` at `px` pixels square, styled by `o`. */
function paintMatrix(ctx, model, o, px) {
  const count = model.count;
  const m = o.margin ? 4 : 0;
  const total = count + m * 2;
  const cell = px / total;

  ctx.fillStyle = o.bg;
  ctx.fillRect(0, 0, px, px);

  let fill = o.fg;
  if (o.gradient) {
    const rad = (o.gradAngle * Math.PI) / 180;
    const span = count * cell;
    const g = ctx.createLinearGradient(m * cell, m * cell,
      m * cell + Math.cos(rad) * span, m * cell + Math.sin(rad) * span);
    g.addColorStop(0, o.fg); g.addColorStop(1, o.fg2);
    fill = g;
  }

  ctx.fillStyle = fill;
  for (let r = 0; r < count; r++) {
    for (let c = 0; c < count; c++) {
      if (model.isDark(r, c) && !isEye(r, c, count)) {
        drawModule(ctx, (c + m) * cell, (r + m) * cell, cell, o.moduleShape);
      }
    }
  }
  drawEye(ctx, m * cell, m * cell, cell, fill, o);
  drawEye(ctx, (count - 7 + m) * cell, m * cell, cell, fill, o);
  drawEye(ctx, m * cell, (count - 7 + m) * cell, cell, fill, o);
}

/** Relative luminance, for the "these two colours won't scan" warning. */
function luminance(hex) {
  const h = String(hex).replace('#', '');
  const v = [0, 2, 4].map((i) => {
    const n = parseInt(h.slice(i, i + 2), 16) / 255;
    return n <= 0.03928 ? n / 12.92 : ((n + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2];
}

function contrastRatio(a, b) {
  const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return (hi + 0.05) / (lo + 0.05);
}

const App = {
  text: 'https://clearbg.pt',
  fg: '#111827', bg: '#ffffff',
  gradient: false, fg2: '#4f46e5', gradAngle: 45,
  moduleShape: 'square', eyeShape: 'square',
  size: 512, ecc: 'M', margin: true,
  logoImg: null, logoDataUrl: null,
  model: null,

  init() {
    this.canvas = $('#qr-canvas');
    const render = rafThrottle(() => this.render());

    $('#qr-text').addEventListener('input', (e) => { this.text = e.target.value; render(); });
    $('#qr-fg').addEventListener('input', (e) => { this.fg = e.target.value; render(); });
    $('#qr-bg').addEventListener('input', (e) => { this.bg = e.target.value; render(); });
    $('#qr-fg2').addEventListener('input', (e) => { this.fg2 = e.target.value; render(); });
    $('#qr-grad-angle').addEventListener('input', (e) => { this.gradAngle = +e.target.value; render(); });
    $('#qr-gradient').addEventListener('change', (e) => {
      this.gradient = e.target.checked;
      $('#qr-gradient-row').classList.toggle('hidden', !this.gradient);
      $('#qr-gradient-row').classList.toggle('flex', this.gradient);
      render();
    });
    $('#qr-size').addEventListener('input', (e) => { this.size = +e.target.value; $('#qr-size-val').textContent = e.target.value; render(); });
    $('#qr-margin').addEventListener('change', (e) => { this.margin = e.target.checked; render(); });

    $$('.qr-mod').forEach((b) => b.addEventListener('click', () => { this.moduleShape = b.dataset.shape; this.highlight('.qr-mod', b); render(); }));
    $$('.qr-eye').forEach((b) => b.addEventListener('click', () => { this.eyeShape = b.dataset.eye; this.highlight('.qr-eye', b); render(); }));
    $$('.qr-ecc-btn').forEach((b) => b.addEventListener('click', () => { this.ecc = b.dataset.ecc; this.highlight('.qr-ecc-btn', b); render(); }));
    $$('.qr-preset').forEach((b) => b.addEventListener('click', () => { this.applyPreset(b.dataset.preset); this.highlightPreset(b.dataset.preset); render(); }));

    $('#qr-logo').addEventListener('change', (e) => this.setLogo(e.target.files[0]));
    $('#qr-logo-clear').addEventListener('click', () => this.clearLogo());

    $('#qr-download').addEventListener('click', () => this.downloadPng());
    $('#qr-download-svg').addEventListener('click', () => this.downloadSvg());

    this.buildPalettes();
    this.renderThumbs();
    this.render();
  },

  highlight(sel, btn) {
    $$(sel).forEach((x) => { const a = x === btn; x.classList.toggle('ring-2', a); x.classList.toggle('ring-primary', a); });
  },

  /** Selected state for the style tiles, which are cards rather than pills. */
  highlightPreset(name) {
    $$('.qr-preset').forEach((x) => {
      const on = x.dataset.preset === name;
      x.setAttribute('aria-pressed', String(on));
      x.classList.toggle('border-primary', on);
      x.classList.toggle('bg-primary/5', on);
      x.classList.toggle('border-gray-200', !on);
      x.classList.toggle('dark:border-gray-800', !on);
      x.classList.toggle('hover:border-primary/60', !on);
    });
  },

  /** Mirror the current colours back into the pickers and the gradient row. */
  syncColourInputs() {
    $('#qr-fg').value = this.fg;
    $('#qr-bg').value = this.bg;
    $('#qr-fg2').value = this.fg2;
    $('#qr-gradient').checked = this.gradient;
    $('#qr-gradient-row').classList.toggle('hidden', !this.gradient);
    $('#qr-gradient-row').classList.toggle('flex', this.gradient);
  },

  applyPreset(name) {
    const p = PRESETS[name];
    if (!p) return;
    Object.assign(this, p);
    // Reflect the preset in the controls.
    $$('.qr-mod').forEach((x) => { const a = x.dataset.shape === this.moduleShape; x.classList.toggle('ring-2', a); x.classList.toggle('ring-primary', a); });
    $$('.qr-eye').forEach((x) => { const a = x.dataset.eye === this.eyeShape; x.classList.toggle('ring-2', a); x.classList.toggle('ring-primary', a); });
    this.syncColourInputs();
  },

  /** Build the one-tap colour pairs, each previewing its own fill. */
  buildPalettes() {
    const holder = $('#qr-palettes');
    PALETTES.forEach((p) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.className =
        'qr-palette w-8 h-8 rounded-lg border border-gray-300 dark:border-gray-700 shadow-sm transition hover:scale-110 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary';
      b.title = p.name;
      b.setAttribute('aria-label', `${p.name} colours`);
      // The swatch shows the fill over the background it is meant to sit on, so
      // a light-on-dark pair reads as such before you apply it.
      b.style.background = p.gradient
        ? `linear-gradient(135deg, ${p.fg}, ${p.fg2})`
        : `linear-gradient(135deg, ${p.fg} 0 50%, ${p.bg} 50% 100%)`;
      b.addEventListener('click', () => {
        Object.assign(this, { fg: p.fg, bg: p.bg, gradient: p.gradient, fg2: p.fg2 || this.fg2 });
        this.syncColourInputs();
        this.render();
      });
      holder.appendChild(b);
    });
  },

  async setLogo(file) {
    if (!file || !/^image\//.test(file.type)) return;
    const dataUrl = await new Promise((res) => { const fr = new FileReader(); fr.onload = () => res(fr.result); fr.readAsDataURL(file); });
    const img = new Image();
    img.onload = () => {
      this.logoImg = img; this.logoDataUrl = dataUrl;
      $('#qr-logo-clear').classList.remove('hidden');
      // A logo covers centre modules — force high error correction so it scans.
      this.ecc = 'H';
      this.highlight('.qr-ecc-btn', $('.qr-ecc-btn[data-ecc="H"]'));
      this.render();
    };
    img.src = dataUrl;
  },

  clearLogo() {
    this.logoImg = null; this.logoDataUrl = null;
    $('#qr-logo').value = '';
    $('#qr-logo-clear').classList.add('hidden');
    this.render();
  },

  build() {
    const qr = qrcode(0, this.logoImg ? 'H' : this.ecc);
    qr.addData(this.text || ' ');
    try { qr.make(); } catch { return false; }
    this.model = { count: qr.getModuleCount(), isDark: (r, c) => qr.isDark(r, c) };
    return true;
  },

  drawLogo(ctx, px) {
    const box = px * 0.22, x = (px - box) / 2, y = (px - box) / 2, pad = box * 0.14;
    ctx.fillStyle = this.bg;
    roundRectPath(ctx, x - pad, y - pad, box + 2 * pad, box + 2 * pad, box * 0.2); ctx.fill();
    const img = this.logoImg;
    const s = Math.min(box / img.naturalWidth, box / img.naturalHeight);
    const dw = img.naturalWidth * s, dh = img.naturalHeight * s;
    ctx.drawImage(img, x + (box - dw) / 2, y + (box - dh) / 2, dw, dh);
  },

  /** The style fields paintMatrix needs, snapshotted from current state. */
  style(overrides) {
    return {
      moduleShape: this.moduleShape, eyeShape: this.eyeShape,
      fg: this.fg, fg2: this.fg2, bg: this.bg,
      gradient: this.gradient, gradAngle: this.gradAngle,
      margin: this.margin,
      ...overrides,
    };
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

    const total = this.model.count + (this.margin ? 8 : 0);
    const px = Math.max(total, this.size);
    const c = this.canvas;
    c.width = px; c.height = px;
    const ctx = c.getContext('2d');
    paintMatrix(ctx, this.model, this.style(), px);
    if (this.logoImg) this.drawLogo(ctx, px);
    this.updateSpecs();
  },

  /** Live export summary under the preview, and the contrast warning. */
  updateSpecs() {
    const ECC_LABEL = { L: 'Low recovery', M: 'Medium recovery', Q: 'High recovery', H: 'Max recovery' };
    const px = this.canvas.width;
    $('#qr-spec-size').textContent = `${px} × ${px}`;
    $('#qr-spec-ecc').textContent = ECC_LABEL[this.logoImg ? 'H' : this.ecc];
    // Compare the lighter gradient stop too — a gradient is only as scannable
    // as its weakest end against the background.
    const worst = this.gradient
      ? Math.min(contrastRatio(this.fg, this.bg), contrastRatio(this.fg2, this.bg))
      : contrastRatio(this.fg, this.bg);
    $('#qr-contrast').classList.toggle('hidden', worst >= 4);
  },

  /** Paint each style tile with a miniature of the code it would produce. */
  renderThumbs() {
    const qr = qrcode(0, 'M');
    qr.addData('https://clearbg.pt');
    try { qr.make(); } catch { return; }
    const model = { count: qr.getModuleCount(), isDark: (r, c) => qr.isDark(r, c) };

    $$('.qr-preset').forEach((btn) => {
      const canvas = btn.querySelector('canvas');
      if (!canvas) return;
      const p = PRESETS[btn.dataset.preset];
      const ctx = canvas.getContext('2d');
      paintMatrix(ctx, model, {
        moduleShape: p.moduleShape, eyeShape: p.eyeShape,
        fg: p.fg || '#111827', fg2: p.fg2 || '#4f46e5', bg: '#ffffff',
        gradient: !!p.gradient, gradAngle: 45, margin: true,
      }, canvas.width);
    });
  },

  // --- SVG (vector) mirror of the canvas render ---
  svgString() {
    const { count } = this.model;
    const m = this.margin ? 4 : 0;
    const total = count + m * 2;
    const f = (n) => +n.toFixed(3);
    const fillRef = this.gradient ? 'url(#g)' : this.fg;
    let defs = '';
    if (this.gradient) {
      const rad = (this.gradAngle * Math.PI) / 180;
      defs = `<defs><linearGradient id="g" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="${f(Math.cos(rad) * total)}" y2="${f(Math.sin(rad) * total)}"><stop offset="0" stop-color="${this.fg}"/><stop offset="1" stop-color="${this.fg2}"/></linearGradient></defs>`;
    }
    let body = '';
    for (let r = 0; r < count; r++) {
      for (let col = 0; col < count; col++) {
        if (!this.model.isDark(r, col) || isEye(r, col, count)) continue;
        const x = col + m, y = r + m;
        if (this.moduleShape === 'dots') body += `<circle cx="${f(x + 0.5)}" cy="${f(y + 0.5)}" r="0.52"/>`;
        else if (this.moduleShape === 'rounded') body += `<rect x="${x}" y="${y}" width="1" height="1" rx="0.35"/>`;
        else body += `<rect x="${x}" y="${y}" width="1" height="1"/>`;
      }
    }
    const eye = (ox, oy) => {
      const rr = (n) => f(eyeRadius(n, this.eyeShape));
      return `<rect x="${ox}" y="${oy}" width="7" height="7" rx="${rr(7)}" fill="${fillRef}"/>` +
        `<rect x="${ox + 1}" y="${oy + 1}" width="5" height="5" rx="${rr(5)}" fill="${this.bg}"/>` +
        `<rect x="${ox + 2}" y="${oy + 2}" width="3" height="3" rx="${rr(3)}" fill="${fillRef}"/>`;
    };
    const eyes = eye(m, m) + eye(count - 7 + m, m) + eye(m, count - 7 + m);
    let logo = '';
    if (this.logoDataUrl) {
      const box = total * 0.22, x = (total - box) / 2, y = (total - box) / 2, pad = box * 0.14;
      logo = `<rect x="${f(x - pad)}" y="${f(y - pad)}" width="${f(box + 2 * pad)}" height="${f(box + 2 * pad)}" rx="${f(box * 0.2)}" fill="${this.bg}"/>` +
        `<image href="${this.logoDataUrl}" x="${f(x)}" y="${f(y)}" width="${f(box)}" height="${f(box)}" preserveAspectRatio="xMidYMid meet"/>`;
    }
    return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${total} ${total}" width="${this.size}" height="${this.size}" shape-rendering="geometricPrecision">${defs}` +
      `<rect width="${total}" height="${total}" fill="${this.bg}"/><g fill="${fillRef}">${body}</g>${eyes}${logo}</svg>`;
  },

  save(blob, name) {
    download(blob, name);
  },

  async downloadPng() {
    if (!this.model) return;
    const blob = await new Promise((res) => this.canvas.toBlob(res, 'image/png'));
    if (!blob) { Toast.show(t('Export failed'), 'error'); return; }
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
