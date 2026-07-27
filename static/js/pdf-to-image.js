/**
 * PDF → images — 100% client-side.
 *
 * pdf.js parses the document and renders each page onto a canvas at the chosen
 * scale, so exports come from the vector source (sharp text) rather than a
 * stretched preview. The library loads on demand from the CDN.
 *
 * The pdf.js worker script is cross-origin on the CDN, and the Worker
 * constructor refuses cross-origin URLs — so the script is fetched and started
 * from a blob: URL instead (allowed by the CSP's `worker-src blob:`).
 *
 * Nothing is uploaded. Shared helpers come from window.CBG.
 */
const { $, $$, Toast, dropzone, download, zipDownload, baseName, plural, t } = CBG;

const PDFJS = 'https://cdn.jsdelivr.net/npm/pdfjs-dist@4.5.136';

const isPdf = (f) => f.type === 'application/pdf' || /\.pdf$/i.test(f.name);

const App = {
  mime: 'image/png',
  ext: 'png',
  scale: 2,
  pages: [],       // {node, canvas, blob}
  doc: null,

  init() {
    this.hero = $('#p2i-hero');
    this.controls = $('#p2i-controls');
    this.grid = $('#p2i-grid');

    dropzone($('#p2i-dropzone'), {
      input: $('#p2i-input'),
      icon: $('#p2i-icon'),
      browse: $('#p2i-browse'),
      multiple: false,
      accept: isPdf,
      onFiles: (files) => this.load(files[0]),
    });

    $$('.p2i-fmt').forEach((b) => b.addEventListener('click', () => {
      this.mime = b.dataset.fmt;
      this.ext = b.dataset.ext;
      $$('.p2i-fmt').forEach((x) => {
        const a = x === b;
        x.classList.toggle('bg-primary', a); x.classList.toggle('text-white', a);
      });
      this.encodeAll();
    }));
    $$('.p2i-scale').forEach((b) => b.addEventListener('click', () => {
      this.scale = +b.dataset.scale;
      $$('.p2i-scale').forEach((x) => {
        const a = x === b;
        x.classList.toggle('bg-primary', a); x.classList.toggle('text-white', a);
      });
      if (this.doc) this.renderAll();
    }));

    $('#p2i-zip').addEventListener('click', () => this.zipAll());
    $('#p2i-clear').addEventListener('click', () => this.clear());
  },

  async lib() {
    if (!this._lib) {
      this._lib = (async () => {
        const pdfjs = await import(`${PDFJS}/+esm`);
        // Same-origin-ify the worker: fetch its source, run it from a blob URL.
        const src = await fetch(`${PDFJS}/build/pdf.worker.min.mjs`).then((r) => r.text());
        pdfjs.GlobalWorkerOptions.workerSrc = URL.createObjectURL(
          new Blob([src], { type: 'text/javascript' }),
        );
        return pdfjs;
      })();
    }
    return this._lib;
  },

  async load(file) {
    if (!isPdf(file)) { Toast.show(t('That is not a PDF file'), 'error'); return; }
    this.name = baseName(file.name);
    Toast.show(t('Reading PDF…'), 'info');
    try {
      const pdfjs = await this.lib();
      const data = await file.arrayBuffer();
      this.doc = await pdfjs.getDocument({ data }).promise;
    } catch {
      Toast.show(t('Could not read that PDF'), 'error');
      return;
    }
    this.hero.classList.add('hidden');
    this.controls.classList.remove('hidden');
    $('#p2i-summary').textContent = plural(this.doc.numPages, '{n} page', '{n} pages');
    await this.renderAll();
  },

  async renderAll() {
    this.grid.innerHTML = '';
    this.pages = [];
    for (let i = 1; i <= this.doc.numPages; i++) {
      const node = $('#p2i-card-template').content.firstElementChild.cloneNode(true);
      node.querySelector('.pagename').textContent = `${t('Page')} ${i}`;
      this.grid.appendChild(node);
      const page = { node, canvas: null, blob: null, num: i };
      node.querySelector('.download-btn').addEventListener('click', () => this.save(page));
      this.pages.push(page);
    }
    // Render sequentially — parallel rendering of a big PDF spikes memory.
    for (const page of this.pages) {
      try {
        const p = await this.doc.getPage(page.num);
        const viewport = p.getViewport({ scale: this.scale });
        const canvas = document.createElement('canvas');
        canvas.width = Math.round(viewport.width);
        canvas.height = Math.round(viewport.height);
        await p.render({ canvasContext: canvas.getContext('2d'), viewport }).promise;
        page.canvas = canvas;
        await this.encode(page);
      } catch {
        page.node.querySelector('.spin').innerHTML = '';
        page.node.querySelector('.pagename').textContent =
          t('Page {n} failed', { n: page.num });
      }
    }
    $('#p2i-zip').classList.toggle('hidden', this.pages.filter((p) => p.blob).length < 2);
  },

  encode(page) {
    if (!page.canvas) return Promise.resolve();
    return new Promise((resolve) => {
      page.canvas.toBlob((blob) => {
        page.blob = blob;
        if (blob) {
          const url = URL.createObjectURL(blob);
          const img = page.node.querySelector('.thumb');
          if (img.src) URL.revokeObjectURL(img.src);
          img.src = url;
          page.node.querySelector('.download-btn').disabled = false;
        }
        page.node.querySelector('.spin').classList.add('hidden');
        resolve();
      }, this.mime, 0.92);
    });
  },

  async encodeAll() {
    for (const page of this.pages) await this.encode(page);
  },

  save(page) {
    if (!page.blob) return;
    download(page.blob, `${this.name || 'page'}-${page.num}.${this.ext}`);
  },

  async zipAll() {
    const done = this.pages.filter((p) => p.blob);
    if (!done.length) return;
    Toast.show(t('Building ZIP…'), 'info');
    try {
      await zipDownload(
        done.map((p) => ({ name: `${this.name || 'page'}-${p.num}.${this.ext}`, blob: p.blob })),
        `${this.name || 'pdf'}-pages.zip`,
      );
    } catch {
      Toast.show(t('Could not build the ZIP'), 'error');
    }
  },

  clear() {
    this.doc = null;
    this.pages = [];
    this.grid.innerHTML = '';
    this.controls.classList.add('hidden');
    this.hero.classList.remove('hidden');
  },
};

document.addEventListener('DOMContentLoaded', () => App.init());
