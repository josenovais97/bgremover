/**
 * Collage / photo grid maker — 100% client-side.
 *
 * Drop several photos and they're laid out in an even grid, each cell cover-fit
 * (cropped to fill, never stretched). Adjustable column count, gap, corner
 * radius, background colour and output aspect ratio; export PNG or JPG. Add more
 * photos at any time and remove any tile. Nothing is uploaded. Shared helpers
 * come from window.CBG.
 */
const { $, $$, Toast, loadImage, dropzone, download, remember, plural, t } = CBG;

const prefs = remember('collage');
const RATIOS = { square: 1, portrait: 4 / 5, landscape: 3 / 2, wide: 16 / 9 };

const App = {
  images: [],        // { img, url }
  cols: 2,
  gap: 12,
  radius: 8,
  bg: '#ffffff',
  ratio: 'square',
  fmt: 'image/png',
  base: 1400,        // longest export edge, px

  init() {
    this.dropzone = $('#cl-dropzone');
    this.hero = this.dropzone.closest('section');
    this.input = $('#cl-input');
    this.editor = $('#cl-editor');
    this.canvas = $('#cl-canvas');
    this.ctx = this.canvas.getContext('2d');

    dropzone(this.dropzone, {
      input: this.input,
      icon: $('#cl-icon'),
      browse: $('#cl-browse'),
      onFiles: (files) => this.add(files),
    });

    $$('.cl-cols').forEach((b) => b.addEventListener('click', () => this.setCols(+b.dataset.cols)));
    $$('.cl-ratio').forEach((b) => b.addEventListener('click', () => this.setRatio(b.dataset.ratio)));
    $('#cl-gap').addEventListener('input', (e) => { this.gap = +e.target.value; this.draw(); });
    $('#cl-radius').addEventListener('input', (e) => { this.radius = +e.target.value; this.draw(); });
    $('#cl-bg').addEventListener('input', (e) => { this.bg = e.target.value; this.draw(); });
    $('#cl-add').addEventListener('click', () => this.input.click());
    $$('.cl-fmt').forEach((b) => b.addEventListener('click', () => this.setFormat(b.dataset.fmt)));
    $('#cl-download').addEventListener('click', () => this.download());
    $('#cl-new').addEventListener('click', () => this.reset());

    const saved = prefs.get();
    if (saved.bg) { this.bg = saved.bg; $('#cl-bg').value = saved.bg; }
  },

  async add(files) {
    for (const file of files) {
      const url = URL.createObjectURL(file);
      try { this.images.push({ img: await loadImage(url), url }); }
      catch { URL.revokeObjectURL(url); }
    }
    if (!this.images.length) { Toast.show(t('Please choose an image'), 'error'); return; }
    this.hero.classList.add('hidden');
    this.editor.classList.remove('hidden');
    this.renderThumbs();
    this.draw();
  },

  setCols(n) {
    this.cols = n;
    $$('.cl-cols').forEach((b) => {
      const a = +b.dataset.cols === n;
      b.classList.toggle('bg-primary', a); b.classList.toggle('text-white', a);
    });
    this.draw();
  },

  setRatio(r) {
    this.ratio = r;
    $$('.cl-ratio').forEach((b) => {
      const a = b.dataset.ratio === r;
      b.classList.toggle('bg-primary', a); b.classList.toggle('text-white', a);
    });
    this.draw();
  },

  setFormat(fmt) {
    this.fmt = fmt;
    $$('.cl-fmt').forEach((b) => {
      const a = b.dataset.fmt === fmt;
      b.classList.toggle('ring-2', a); b.classList.toggle('ring-primary', a);
    });
  },

  renderThumbs() {
    const holder = $('#cl-thumbs');
    holder.innerHTML = '';
    this.images.forEach((it, idx) => {
      const wrap = document.createElement('div');
      wrap.className = 'relative aspect-square rounded-lg overflow-hidden border border-gray-200/70 dark:border-gray-800/70';
      const im = document.createElement('img');
      im.src = it.url; im.className = 'w-full h-full object-cover'; im.alt = '';
      const rm = document.createElement('button');
      rm.type = 'button';
      rm.className = 'absolute top-1 right-1 w-6 h-6 grid place-items-center rounded-full bg-black/60 text-white text-xs hover:bg-black/80 focus:outline-none focus-visible:ring-2 focus-visible:ring-white';
      rm.innerHTML = '<i class="fa-solid fa-xmark" aria-hidden="true"></i>';
      rm.setAttribute('aria-label', t('Remove'));
      rm.addEventListener('click', () => this.remove(idx));
      wrap.append(im, rm);
      holder.appendChild(wrap);
    });
    $('#cl-count').textContent = plural(this.images.length, '{n} photo', '{n} photos');
  },

  remove(idx) {
    const [gone] = this.images.splice(idx, 1);
    if (gone) URL.revokeObjectURL(gone.url);
    if (!this.images.length) { this.reset(); return; }
    this.renderThumbs();
    this.draw();
  },

  /** Grid geometry for the current image count and column choice. */
  layout() {
    const cols = Math.min(this.cols, this.images.length);
    const rows = Math.ceil(this.images.length / cols);
    return { cols, rows };
  },

  draw() {
    if (!this.images.length) return;
    const { cols, rows } = this.layout();
    const ratio = RATIOS[this.ratio];
    // Fit the whole collage inside a `base`-longest-edge box at the chosen ratio.
    let W, H;
    if (ratio >= 1) { W = this.base; H = Math.round(this.base / ratio); }
    else { H = this.base; W = Math.round(this.base * ratio); }
    this.canvas.width = W; this.canvas.height = H;
    const ctx = this.ctx;
    ctx.fillStyle = this.bg;
    ctx.fillRect(0, 0, W, H);

    const gap = this.gap;
    const cellW = (W - gap * (cols + 1)) / cols;
    const cellH = (H - gap * (rows + 1)) / rows;
    const rad = this.radius;

    this.images.forEach((it, i) => {
      const c = i % cols, r = Math.floor(i / cols);
      const x = gap + c * (cellW + gap);
      const y = gap + r * (cellH + gap);
      ctx.save();
      roundRect(ctx, x, y, cellW, cellH, rad);
      ctx.clip();
      // Cover-fit: scale so the image fills the cell, centre-crop the overflow.
      const s = Math.max(cellW / it.img.naturalWidth, cellH / it.img.naturalHeight);
      const dw = it.img.naturalWidth * s, dh = it.img.naturalHeight * s;
      ctx.drawImage(it.img, x + (cellW - dw) / 2, y + (cellH - dh) / 2, dw, dh);
      ctx.restore();
    });
  },

  async download() {
    if (!this.images.length) return;
    prefs.set({ bg: this.bg });
    if (this.fmt === 'image/jpeg') {
      this.canvas.toBlob((b) => this.save(b, 'jpg'), 'image/jpeg', 0.92);
    } else {
      this.canvas.toBlob((b) => this.save(b, 'png'), 'image/png');
    }
  },

  save(blob, ext) {
    if (!blob) { Toast.show(t('Export failed'), 'error'); return; }
    download(blob, `collage.${ext}`);
  },

  reset() {
    this.editor.classList.add('hidden');
    this.hero.classList.remove('hidden');
    this.images.forEach((it) => URL.revokeObjectURL(it.url));
    this.images = [];
  },
};

function roundRect(ctx, x, y, w, h, r) {
  r = Math.min(r, w / 2, h / 2);
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}

document.addEventListener('DOMContentLoaded', () => App.init());
