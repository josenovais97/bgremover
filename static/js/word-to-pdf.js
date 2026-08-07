/**
 * Word (.docx) → PDF — 100% client-side.
 *
 * Two halves. `docx-preview` parses the OOXML and lays the document out as real
 * DOM, one `section.docx` per page, at the page size and margins the document
 * itself declares. Then the browser's own print engine turns that DOM into the
 * PDF.
 *
 * Why the print engine and not a PDF library: the alternative is rasterising the
 * preview (html2canvas, jsPDF.html) and embedding pictures of the pages. That
 * gives a PDF with no selectable text, no accessibility, a huge file and visible
 * softness on paper — for contracts and CVs, which is what people convert, that
 * is the wrong output. Printing produces real text runs and real pagination at a
 * fraction of the size. The cost is that the user passes through the print
 * dialog and picks "Save as PDF" rather than getting a direct download, which no
 * amount of code can remove: a page cannot write to the filesystem unasked.
 *
 * Fidelity is deliberately advertised as close, not identical, because it cannot
 * be identical. A .docx names its fonts (Calibri, Cambria) without embedding
 * them; when the machine doesn't have them the browser substitutes, text remeasures,
 * and line and page breaks drift from what Word would show. That is why the
 * preview is not a nicety — it is the tool showing you its actual output before
 * you commit, so a reflow is something you see rather than discover later.
 *
 * Shared helpers come from window.CBG (static/js/kit.js).
 */
import { renderAsync } from 'https://cdn.jsdelivr.net/npm/docx-preview@0.4.0/+esm';

const { $, Toast, dropzone, humanSize, plural, t } = CBG;

/** .docx is a zip ("PK"); the old binary .doc is an OLE container. */
const OLE_MAGIC = [0xd0, 0xcf, 0x11, 0xe0];

const App = {
  file: null,

  init() {
    this.dropzoneEl = $('#w2p-dropzone');
    this.input = $('#w2p-input');
    this.hero = this.dropzoneEl.closest('section');
    this.editor = $('#w2p-editor');
    this.preview = $('#w2p-preview');
    this.meta = $('#w2p-meta');
    this.name = $('#w2p-name');
    this.busy = $('#w2p-busy');

    dropzone(this.dropzoneEl, {
      input: this.input,
      icon: $('#w2p-icon'),
      browse: $('#w2p-browse'),
      multiple: false,
      // Accept anything and diagnose it ourselves: a wrong file deserves a
      // specific reason, not the generic "please choose an image".
      accept: () => true,
      onFiles: (files) => this.load(files[0]),
    });

    $('#w2p-print').addEventListener('click', () => this.toPdf());
    $('#w2p-new').addEventListener('click', () => this.reset());

    // Put the document back in the page once the dialog closes, whether the user
    // saved or cancelled — afterprint fires either way.
    window.addEventListener('afterprint', () => this.unstage());
  },

  async load(file) {
    const why = await this.reject(file);
    if (why) { Toast.show(why, 'error'); return; }

    this.file = file;
    this.busy.classList.remove('hidden');
    this.preview.innerHTML = '';

    try {
      await renderAsync(file, this.preview, null, {
        className: 'docx',
        inWrapper: true,
        ignoreWidth: false,
        ignoreHeight: false,
        breakPages: true,
        renderHeaders: true,
        renderFooters: true,
        renderFootnotes: true,
        useBase64URL: true,
      });
    } catch (err) {
      console.error(err);
      this.busy.classList.add('hidden');
      Toast.show(t('That file could not be read as a Word document'), 'error');
      return;
    }

    this.busy.classList.add('hidden');
    const pages = this.preview.querySelectorAll('section.docx').length;
    this.name.textContent = file.name;
    this.meta.textContent = `${humanSize(file.size)} · ${plural(pages, '{n} page', '{n} pages')}`;
    this.hero.classList.add('hidden');
    this.editor.classList.remove('hidden');
    this.editor.scrollIntoView({ behavior: 'smooth', block: 'start' });
  },

  /** Return a reason to refuse the file, or null to accept it. */
  async reject(file) {
    if (!file) return t('No file chosen');
    const head = new Uint8Array(await file.slice(0, 4).arrayBuffer());
    if (OLE_MAGIC.every((b, i) => head[i] === b)) {
      // Worth its own message: "word to pdf" searches bring plenty of .doc, and
      // "unsupported file" would read as a bug rather than a format limit.
      return t('This is an old .doc file. Open it in Word and save as .docx first.');
    }
    if (!(head[0] === 0x50 && head[1] === 0x4b)) return t('That is not a .docx file');
    return null;
  },

  /**
   * Hand the rendered pages to the print engine.
   *
   * The document is moved to be a direct child of <body> for the duration. The
   * print stylesheet hides body's other children, and hiding *siblings* only
   * works if there are no ancestors in between — with the preview left nested in
   * the page, either its wrappers keep their padding and shift every page, or
   * `visibility: hidden` on ancestors keeps their boxes and emits blank pages.
   */
  toPdf() {
    const doc = this.preview.querySelector('.docx-wrapper');
    if (!doc) return;
    this.matchPageSize();
    this.slot = document.createElement('span');
    this.preview.appendChild(this.slot);
    $('#w2p-print-root').appendChild(doc);
    document.documentElement.classList.add('w2p-printing');
    window.print();
  },

  /**
   * Point @page at the document's own page size.
   *
   * Without this the sheet stays whatever the browser defaults to — Letter, in
   * most locales — and an A4 document is 1.8cm taller than that, so every single
   * page spills a sliver onto a second sheet and the PDF comes out at double
   * length with a blank between each page. docx-preview has already resolved the
   * real size onto section.docx from the document's sectPr, so read it back off
   * the element rather than guessing or offering a picker.
   */
  matchPageSize() {
    const page = this.preview.querySelector('section.docx');
    if (!page) return;
    let el = $('#w2p-page-size');
    if (!el) {
      el = document.createElement('style');
      el.id = 'w2p-page-size';
      document.head.appendChild(el);
    }
    // CSS px is 1/96in by definition, so this converts exactly.
    const w = page.offsetWidth / 96, h = page.offsetHeight / 96;
    el.textContent = `@media print { @page { size: ${w}in ${h}in; margin: 0; } }`;
  },

  unstage() {
    const doc = $('#w2p-print-root').querySelector('.docx-wrapper');
    if (doc && this.slot) this.slot.replaceWith(doc);
    this.slot = null;
    document.documentElement.classList.remove('w2p-printing');
  },

  reset() {
    this.file = null;
    this.preview.innerHTML = '';
    this.editor.classList.add('hidden');
    this.hero.classList.remove('hidden');
    this.hero.scrollIntoView({ behavior: 'smooth', block: 'start' });
  },
};

App.init();
