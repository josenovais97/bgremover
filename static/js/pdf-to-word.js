/**
 * PDF → Word (.docx) — 100% client-side.
 *
 * Read the scope before judging the output: this extracts the **text** of a PDF
 * into an editable Word document. It does not reproduce the layout, and it is
 * presented that way on the page rather than being sold as a conversion it isn't.
 *
 * The asymmetry with word-to-pdf.js is not laziness, it is the file format. A
 * .docx describes intent — "heading", "paragraph", "list item", "table" — so
 * laying it out is a matter of following instructions. A PDF has thrown all of
 * that away: what remains is glyphs at coordinates. There are no paragraphs in a
 * PDF, only runs of characters that happen to share a baseline. Rebuilding a
 * document from that means *inferring* structure, and every inference is a guess
 * that can be wrong. Commercial converters throw machine learning at the problem
 * and still get columns and tables wrong regularly.
 *
 * So this does the part that can be done honestly and well: pdf.js gives glyph
 * runs with positions, and those are grouped into lines by baseline and into
 * paragraphs by vertical gap. What you get is the prose, in order, with the page
 * breaks kept and something reasonable done about headings — editable, which is
 * the actual reason people want Word rather than PDF. What you do not get is the
 * original's columns, tables or exact spacing.
 *
 * Shared helpers come from window.CBG (static/js/kit.js).
 */
const { $, Toast, dropzone, download, baseName, humanSize, plural, t } = CBG;

const PDFJS = 'https://cdn.jsdelivr.net/npm/pdfjs-dist@4.5.136';
const DOCX = 'https://cdn.jsdelivr.net/npm/docx@9.7.1/+esm';

const isPdf = (f) => f.type === 'application/pdf' || /\.pdf$/i.test(f.name);

/**
 * A new paragraph is declared when the vertical gap between two lines exceeds
 * their own line height by this factor. Tuned by eye rather than derived: too low
 * and every wrapped line becomes its own paragraph, too high and separate
 * paragraphs weld together.
 */
const PARA_GAP = 1.6;
/** A line this much larger than the document's body size is treated as a heading. */
const HEADING_RATIO = 1.25;

const App = {
  pages: [],   // [[{ text, size, indent }]] — paragraphs per page
  name: '',

  init() {
    this.dropzoneEl = $('#p2w-dropzone');
    this.input = $('#p2w-input');
    this.hero = this.dropzoneEl.closest('section');
    this.editor = $('#p2w-editor');
    this.preview = $('#p2w-preview');
    this.meta = $('#p2w-meta');
    this.nameEl = $('#p2w-name');
    this.busy = $('#p2w-busy');

    dropzone(this.dropzoneEl, {
      input: this.input,
      icon: $('#p2w-icon'),
      browse: $('#p2w-browse'),
      multiple: false,
      accept: isPdf,
      onFiles: (files) => this.load(files[0]),
    });

    $('#p2w-save').addEventListener('click', () => this.save());
    $('#p2w-new').addEventListener('click', () => this.reset());
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
    this.busy.classList.remove('hidden');
    let doc;
    try {
      const pdfjs = await this.lib();
      doc = await pdfjs.getDocument({ data: await file.arrayBuffer() }).promise;
    } catch {
      this.busy.classList.add('hidden');
      Toast.show(t('Could not read that PDF'), 'error');
      return;
    }

    this.pages = [];
    for (let n = 1; n <= doc.numPages; n++) {
      const page = await doc.getPage(n);
      this.pages.push(this.paragraphs(await page.getTextContent()));
    }
    this.busy.classList.add('hidden');

    const words = this.pages.flat().reduce((n, p) => n + p.text.split(/\s+/).filter(Boolean).length, 0);
    if (!words) {
      // A scan is glyph-free: there is nothing to extract, and saying so is more
      // use than handing over an empty document.
      Toast.show(t('This PDF has no text — it is probably a scan. Try the Image to Text tool.'), 'error');
      return;
    }

    this.name = baseName(file.name);
    this.nameEl.textContent = file.name;
    this.meta.textContent = [
      humanSize(file.size),
      plural(doc.numPages, '{n} page', '{n} pages'),
      plural(words, '{n} word', '{n} words'),
    ].join(' · ');
    this.paintPreview();
    this.hero.classList.add('hidden');
    this.editor.classList.remove('hidden');
    this.editor.scrollIntoView({ behavior: 'smooth', block: 'start' });
  },

  /**
   * Turn pdf.js text items into paragraphs.
   *
   * Items arrive in content-stream order with a transform matrix each. [5] is the
   * y translation and [0] the horizontal scale, which stands in for font size —
   * pdf.js does not report a size directly. Items sharing a y are one line;
   * a y jump larger than PARA_GAP line-heights starts a new paragraph.
   */
  paragraphs(content) {
    const lines = [];
    for (const item of content.items) {
      if (!item.str) continue;
      const y = Math.round(item.transform[5]);
      const size = Math.abs(item.transform[0]) || 10;
      const x = item.transform[4];
      const last = lines[lines.length - 1];
      // Same baseline within a point of rounding: same line.
      if (last && Math.abs(last.y - y) <= 1) {
        last.text += item.str;
        last.size = Math.max(last.size, size);
      } else {
        lines.push({ y, size, x, text: item.str });
      }
    }

    const paras = [];
    let current = null;
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const text = line.text.replace(/\s+/g, ' ').trim();
      if (!text) { current = null; continue; }
      const prev = lines[i - 1];
      const gap = prev ? Math.abs(prev.y - line.y) : Infinity;
      const newPara = !current || gap > line.size * PARA_GAP
        // A size change is a structural boundary too: a heading never continues
        // the body paragraph above it.
        || Math.abs(line.size - current.size) > 0.6;

      if (newPara) {
        current = { text, size: line.size, indent: line.x };
        paras.push(current);
      } else {
        // Rejoin a hyphenated word broken across the line break.
        current.text = current.text.endsWith('-')
          ? current.text.slice(0, -1) + text
          : `${current.text} ${text}`;
      }
    }
    return paras;
  },

  /** The most common line size is the body size; headings are relative to it. */
  bodySize() {
    const tally = new Map();
    for (const p of this.pages.flat()) {
      const k = Math.round(p.size * 2) / 2;
      tally.set(k, (tally.get(k) || 0) + p.text.length);
    }
    return [...tally.entries()].sort((a, b) => b[1] - a[1])[0]?.[0] || 10;
  },

  paintPreview() {
    const body = this.bodySize();
    this.preview.innerHTML = '';
    this.pages.forEach((paras, i) => {
      const sheet = document.createElement('div');
      sheet.className = 'bg-white text-gray-900 rounded-lg shadow p-8 mb-4 text-sm leading-relaxed';
      const tag = document.createElement('p');
      tag.className = 'text-[10px] uppercase tracking-wider text-gray-400 mb-3';
      tag.textContent = `${t('Page')} ${i + 1}`;
      sheet.appendChild(tag);
      paras.forEach((p) => {
        const heading = p.size >= body * HEADING_RATIO;
        const el = document.createElement(heading ? 'h3' : 'p');
        el.className = heading ? 'font-bold text-base mt-4 mb-1' : 'mb-2';
        el.textContent = p.text;   // user content: never innerHTML
        sheet.appendChild(el);
      });
      this.preview.appendChild(sheet);
    });
  },

  async save() {
    const btn = $('#p2w-save');
    btn.disabled = true;
    try {
      const { Document, Packer, Paragraph, TextRun, HeadingLevel, PageBreak } = await import(DOCX);
      const body = this.bodySize();
      const children = [];

      this.pages.forEach((paras, pageIndex) => {
        if (pageIndex > 0) children.push(new Paragraph({ children: [new PageBreak()] }));
        for (const p of paras) {
          const heading = p.size >= body * HEADING_RATIO;
          children.push(new Paragraph({
            heading: heading ? HeadingLevel.HEADING_2 : undefined,
            spacing: { after: heading ? 120 : 160 },
            children: [new TextRun({
              text: p.text,
              // half-points, and clamped: a title set at 60pt in the PDF would
              // otherwise carry into Word at a size nobody wants to edit.
              size: Math.round(Math.min(p.size, body * 2) * 2),
            })],
          }));
        }
      });

      const doc = new Document({ creator: 'ClearBG', sections: [{ children }] });
      const blob = await Packer.toBlob(doc);
      download(blob, `${this.name}.docx`, { chain: false });
      Toast.show(t('Word document ready'), 'success');
    } catch (err) {
      console.error(err);
      Toast.show(t('Conversion failed'), 'error');
    }
    btn.disabled = false;
  },

  reset() {
    this.pages = [];
    this.preview.innerHTML = '';
    this.editor.classList.add('hidden');
    this.hero.classList.remove('hidden');
  },
};

App.init();
