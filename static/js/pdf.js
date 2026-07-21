/**
 * Image → PDF builder — 100% client-side.
 *
 * Embeds each image into a multi-page PDF with pdf-lib. JPEG and PNG bytes are
 * embedded AS-IS (no canvas round-trip), so a scan keeps exactly the quality it
 * had; only formats pdf-lib can't embed natively — WEBP — are re-encoded to JPEG.
 *
 * This is the tool people reach for with their most sensitive images (IDs,
 * contracts, payslips), which is precisely why it runs in the page: the PDF is
 * assembled locally and nothing is uploaded.
 *
 * Shared helpers come from window.CBG (static/js/kit.js).
 */
import { PDFDocument } from 'https://cdn.jsdelivr.net/npm/pdf-lib@1.17.1/+esm';

const { $, $$, Toast, loadImage, dropzone, download, remember } = window.CBG;

// Page sizes in PDF points (1pt = 1/72in).
const PAGE_SIZES = {
  a4: [595.28, 841.89],
  letter: [612, 792],
};

const prefs = remember('pdf');

const App = {
  pages: [],        // { file, url, w, h }
  size: 'a4',
  orient: 'auto',
  margin: 24,
  dragIndex: null,

  init() {
    this.dropzone = $('#pdf-dropzone');
    this.hero = this.dropzone.closest('section');
    this.input = $('#pdf-input');
    this.editor = $('#pdf-editor');
    this.list = $('#pdf-pages');

    dropzone(this.dropzone, {
      input: this.input,
      icon: $('#pdf-icon'),
      browse: $('#pdf-browse'),
      onFiles: (files) => this.add(files),
    });
    $('#pdf-add').addEventListener('click', () => this.input.click());

    $$('.pdf-size-btn').forEach((b) => b.addEventListener('click', () => this.setSize(b.dataset.size)));
    $$('.pdf-orient-btn').forEach((b) => b.addEventListener('click', () => this.setOrient(b.dataset.orient)));
    $('#pdf-margin').addEventListener('input', (e) => {
      this.margin = +e.target.value;
      prefs.set({ margin: this.margin });
    });
    $('#pdf-download').addEventListener('click', () => this.build());
    $('#pdf-new').addEventListener('click', () => this.reset());

    // Page setup is a preference: the same person tends to want the same layout.
    const saved = prefs.get();
    if (saved.size) this.setSize(saved.size);
    if (saved.orient) this.setOrient(saved.orient);
    if (saved.margin != null) { this.margin = saved.margin; $('#pdf-margin').value = saved.margin; }
  },

  setSize(size) {
    this.size = size;
    $$('.pdf-size-btn').forEach((x) => {
      const a = x.dataset.size === size;
      x.classList.toggle('ring-2', a);
      x.classList.toggle('ring-primary', a);
    });
    // Orientation and margin are meaningless when each page IS its image.
    $('#pdf-layout').classList.toggle('hidden', size === 'fit');
    prefs.set({ size });
  },

  setOrient(orient) {
    this.orient = orient;
    $$('.pdf-orient-btn').forEach((x) => {
      const a = x.dataset.orient === orient;
      x.classList.toggle('ring-2', a);
      x.classList.toggle('ring-primary', a);
    });
    prefs.set({ orient });
  },

  async add(files) {
    for (const file of files) {
      const url = URL.createObjectURL(file);
      try {
        const img = await loadImage(url);
        this.pages.push({ file, url, w: img.naturalWidth, h: img.naturalHeight });
      } catch {
        URL.revokeObjectURL(url);
        Toast.show(`Could not read ${file.name}`, 'error');
      }
    }
    if (!this.pages.length) return;
    this.hero.classList.add('hidden');
    this.editor.classList.remove('hidden');
    this.renderPages();
  },

  remove(i) {
    URL.revokeObjectURL(this.pages[i].url);
    this.pages.splice(i, 1);
    if (!this.pages.length) { this.reset(); return; }
    this.renderPages();
  },

  /** Move the dragged page to a new index (drag-to-reorder). */
  move(from, to) {
    if (from === to || from == null) return;
    const [page] = this.pages.splice(from, 1);
    this.pages.splice(to, 0, page);
    this.renderPages();
  },

  renderPages() {
    $('#pdf-count').textContent = this.pages.length;
    this.list.textContent = '';
    this.pages.forEach((page, i) => {
      const li = document.createElement('li');
      li.className = 'relative group rounded-xl overflow-hidden border border-gray-200/70 dark:border-gray-700/70 bg-gray-50 dark:bg-white/5 cursor-move';
      li.draggable = true;
      li.innerHTML = `
        <img src="${page.url}" alt="" class="w-full h-32 object-contain bg-white dark:bg-gray-900">
        <span class="absolute top-1.5 left-1.5 w-5 h-5 grid place-items-center rounded-full bg-primary text-white text-[10px] font-bold">${i + 1}</span>
        <button type="button" class="absolute top-1.5 right-1.5 w-6 h-6 grid place-items-center rounded-full bg-black/60 text-white opacity-0 group-hover:opacity-100 focus:opacity-100 transition" aria-label="Remove page ${i + 1}">
          <i class="fa-solid fa-xmark text-[11px]" aria-hidden="true"></i>
        </button>
        <span class="block px-2 py-1 text-[10px] text-gray-500 dark:text-gray-400 truncate"></span>`;
      li.querySelector('span:last-child').textContent = page.file.name;
      li.querySelector('button').addEventListener('click', () => this.remove(i));
      li.addEventListener('dragstart', () => { this.dragIndex = i; });
      li.addEventListener('dragover', (e) => e.preventDefault());
      li.addEventListener('drop', (e) => { e.preventDefault(); this.move(this.dragIndex, i); this.dragIndex = null; });
      this.list.appendChild(li);
    });
  },

  /**
   * Bytes pdf-lib can embed, plus which embedder to use.
   *
   * JPEG and PNG go in untouched — that's the whole quality story for scans.
   * Anything else (WEBP) is re-encoded to JPEG at high quality, since pdf-lib
   * only speaks those two formats.
   */
  async embeddable(page) {
    if (page.file.type === 'image/jpeg') return { bytes: await page.file.arrayBuffer(), kind: 'jpg' };
    if (page.file.type === 'image/png') return { bytes: await page.file.arrayBuffer(), kind: 'png' };
    const img = await loadImage(page.url);
    const c = document.createElement('canvas');
    c.width = img.naturalWidth;
    c.height = img.naturalHeight;
    const ctx = c.getContext('2d');
    ctx.fillStyle = '#ffffff';                 // WEBP may be transparent; JPEG isn't
    ctx.fillRect(0, 0, c.width, c.height);
    ctx.drawImage(img, 0, 0);
    const blob = await new Promise((res) => c.toBlob(res, 'image/jpeg', 0.92));
    return { bytes: await blob.arrayBuffer(), kind: 'jpg' };
  },

  /** Page box for an image, honouring the size + orientation choice. */
  pageBox(img) {
    if (this.size === 'fit') return [img.width, img.height];
    const [short, long] = PAGE_SIZES[this.size];
    const landscape = this.orient === 'landscape'
      || (this.orient === 'auto' && img.width > img.height);
    return landscape ? [long, short] : [short, long];
  },

  async build() {
    if (!this.pages.length) return;
    const btn = $('#pdf-download');
    const label = $('#pdf-download-label');
    btn.disabled = true;
    label.textContent = 'Building…';
    try {
      const doc = await PDFDocument.create();
      for (const page of this.pages) {
        const { bytes, kind } = await this.embeddable(page);
        const img = kind === 'png' ? await doc.embedPng(bytes) : await doc.embedJpg(bytes);
        const [pw, ph] = this.pageBox(img);
        const sheet = doc.addPage([pw, ph]);
        if (this.size === 'fit') {
          sheet.drawImage(img, { x: 0, y: 0, width: pw, height: ph });
        } else {
          // Contain inside the margin box — never crop, never distort.
          const m = Math.min(this.margin, Math.min(pw, ph) / 2 - 1);
          const boxW = pw - m * 2;
          const boxH = ph - m * 2;
          const s = Math.min(boxW / img.width, boxH / img.height);
          const w = img.width * s;
          const h = img.height * s;
          sheet.drawImage(img, { x: (pw - w) / 2, y: (ph - h) / 2, width: w, height: h });
        }
      }
      const bytes = await doc.save();
      const blob = new Blob([bytes], { type: 'application/pdf' });
      download(blob, 'clearbg.pdf');
      $('#pdf-done').innerHTML = `<i class="fa-solid fa-circle-check text-green-500 mr-1"></i>Saved ${this.pages.length} page${this.pages.length === 1 ? '' : 's'} · ${window.CBG.humanSize(blob.size)}`;
      window.__clearbgReport?.(1, 'downloaded');
    } catch {
      Toast.show('Could not build the PDF', 'error');
    } finally {
      btn.disabled = false;
      label.textContent = 'Download PDF';
    }
  },

  reset() {
    for (const p of this.pages) URL.revokeObjectURL(p.url);
    this.pages = [];
    this.list.textContent = '';
    this.editor.classList.add('hidden');
    this.hero.classList.remove('hidden');
    $('#pdf-done').textContent = '';
  },
};

document.addEventListener('DOMContentLoaded', () => App.init());
