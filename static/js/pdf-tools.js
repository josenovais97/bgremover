/**
 * Merge and split PDFs — 100% client-side.
 *
 * Both operations are pure page-tree surgery, which is why they belong in one
 * tool and why they are fast: pdf-lib copies page objects between documents
 * without touching their content streams, so nothing is re-encoded, re-compressed
 * or rasterised. A merged PDF's text stays selectable and its images keep the
 * exact bytes they had, because they *are* the bytes they had.
 *
 * This is also the class of file where "nothing is uploaded" stops being a
 * slogan. The reason people merge PDFs is to assemble a submission — a mortgage
 * application, a visa file, a contract with its annexes, a set of payslips — and
 * every mainstream merge site takes the whole bundle onto their servers.
 *
 * Shared helpers come from window.CBG (static/js/kit.js).
 */
import { PDFDocument } from 'https://cdn.jsdelivr.net/npm/pdf-lib@1.17.1/+esm';

const { $, $$, Toast, dropzone, download, humanSize, baseName, zipDownload, plural, t } = CBG;

const isPdf = (f) => f.type === 'application/pdf' || /\.pdf$/i.test(f.name);

const App = {
  mode: 'merge',   // 'merge' | 'split'
  files: [],       // merge: [{ file, pages }]
  split: null,     // split: { file, pages }
  dragIndex: null,

  init() {
    this.dropzoneEl = $('#pt-dropzone');
    this.input = $('#pt-input');
    this.hero = this.dropzoneEl.closest('section');
    this.editor = $('#pt-editor');
    this.list = $('#pt-list');
    this.busy = $('#pt-busy');
    this.mergePane = $('#pt-merge-pane');
    this.splitPane = $('#pt-split-pane');
    this.rangeInput = $('#pt-ranges');

    $$('.pt-mode').forEach((b) => b.addEventListener('click', () => {
      this.mode = b.dataset.mode;
      this.paintMode();
      this.reset();
    }));
    this.paintMode();

    dropzone(this.dropzoneEl, {
      input: this.input,
      icon: $('#pt-icon'),
      browse: $('#pt-browse'),
      multiple: true,
      accept: isPdf,
      onFiles: (files) => this.add(files),
    });

    $('#pt-run').addEventListener('click', () => this.run());
    $('#pt-new').addEventListener('click', () => this.reset());
    this.rangeInput.addEventListener('input', () => this.paintRangeHint());
  },

  paintMode() {
    $$('.pt-mode').forEach((b) => {
      const on = b.dataset.mode === this.mode;
      b.classList.toggle('bg-primary', on);
      b.classList.toggle('text-white', on);
      b.setAttribute('aria-selected', on ? 'true' : 'false');
    });
    const merge = this.mode === 'merge';
    this.input.multiple = merge;
    $('#pt-drop-title').textContent = merge ? t('Drop your PDFs') : t('Drop a PDF to split');
    $('#pt-drop-sub').textContent = merge
      ? t('or click to browse — add as many as you like')
      : t('or click to browse — one file');
    $('#pt-run-label').textContent = merge ? t('Merge into one PDF') : t('Split into separate PDFs');
    this.mergePane.classList.toggle('hidden', !merge);
    this.splitPane.classList.toggle('hidden', merge);
  },

  async add(files) {
    this.busy.classList.remove('hidden');
    const accepted = [];
    for (const file of files) {
      let pages;
      try {
        // Page count comes from a real parse, so a corrupt or password-protected
        // file is rejected here rather than at merge time with half the job done.
        const doc = await PDFDocument.load(await file.arrayBuffer(), { ignoreEncryption: false });
        pages = doc.getPageCount();
      } catch {
        Toast.show(t('Could not read {name} — it may be password-protected').replace('{name}', file.name), 'error');
        continue;
      }
      accepted.push({ file, pages });
    }
    this.busy.classList.add('hidden');
    if (!accepted.length) return;

    if (this.mode === 'merge') {
      this.files.push(...accepted);
    } else {
      this.split = accepted[0];
      this.files = [accepted[0]];
      this.rangeInput.placeholder = `1-${this.split.pages}`;
    }

    this.paintList();
    this.paintRangeHint();
    this.hero.classList.add('hidden');
    this.editor.classList.remove('hidden');
    this.editor.scrollIntoView({ behavior: 'smooth', block: 'start' });
  },

  paintList() {
    this.list.innerHTML = '';
    this.files.forEach((entry, i) => {
      const row = document.createElement('div');
      row.className = 'flex items-center gap-3 p-3 rounded-xl border border-gray-200 '
        + 'dark:border-gray-700 bg-white/60 dark:bg-gray-900/60';
      row.draggable = this.mode === 'merge';

      const grip = document.createElement('span');
      grip.className = 'text-gray-400 text-sm ' + (this.mode === 'merge' ? 'cursor-grab' : 'hidden');
      grip.innerHTML = '<i class="fa-solid fa-arrows-up-down" aria-hidden="true"></i>';

      const label = document.createElement('div');
      label.className = 'min-w-0 flex-1';
      const nm = document.createElement('p');
      nm.className = 'text-sm font-medium truncate';
      nm.textContent = entry.file.name;   // user text: never innerHTML
      const sub = document.createElement('p');
      sub.className = 'text-xs text-gray-500 dark:text-gray-400';
      sub.textContent = `${humanSize(entry.file.size)} · `
        + plural(entry.pages, '{n} page', '{n} pages');
      label.append(nm, sub);

      const del = document.createElement('button');
      del.type = 'button';
      del.className = 'px-2 py-1 text-sm text-gray-400 hover:text-red-500 transition';
      del.setAttribute('aria-label', t('Remove'));
      del.innerHTML = '<i class="fa-solid fa-trash-can" aria-hidden="true"></i>';
      del.addEventListener('click', () => {
        this.files.splice(i, 1);
        if (this.mode === 'split') this.split = null;
        if (!this.files.length) this.reset(); else { this.paintList(); this.paintRangeHint(); }
      });

      row.append(grip, label, del);

      if (this.mode === 'merge') {
        row.addEventListener('dragstart', () => { this.dragIndex = i; row.classList.add('opacity-40'); });
        row.addEventListener('dragend', () => { row.classList.remove('opacity-40'); });
        row.addEventListener('dragover', (e) => e.preventDefault());
        row.addEventListener('drop', (e) => {
          e.preventDefault();
          if (this.dragIndex === null || this.dragIndex === i) return;
          const [moved] = this.files.splice(this.dragIndex, 1);
          this.files.splice(i, 0, moved);
          this.dragIndex = null;
          this.paintList();
        });
      }
      this.list.appendChild(row);
    });

    const total = this.files.reduce((n, f) => n + f.pages, 0);
    const pages = plural(total, '{n} page', '{n} pages');
    $('#pt-total').textContent = this.mode === 'merge'
      ? `${plural(this.files.length, '{n} file', '{n} files')} · ${pages}`
      : pages;
  },

  /**
   * Parse "1-3, 5, 8-" into page-index groups, one output file per group.
   *
   * Returns { groups, bad }. Kept deliberately forgiving about whitespace and an
   * open-ended trailing range, since "8-" for "page 8 to the end" is how people
   * actually write it, but strict about out-of-range numbers — silently clamping
   * them would produce a file that quietly lacks pages the user asked for.
   */
  parseRanges(spec, pageCount) {
    const groups = [];
    const bad = [];
    for (const part of spec.split(',').map((s) => s.trim()).filter(Boolean)) {
      const m = /^(\d+)\s*(-)?\s*(\d+)?$/.exec(part);
      if (!m) { bad.push(part); continue; }
      const from = parseInt(m[1], 10);
      const to = m[2] ? (m[3] ? parseInt(m[3], 10) : pageCount) : from;
      if (from < 1 || to > pageCount || from > to) { bad.push(part); continue; }
      groups.push({ label: from === to ? `${from}` : `${from}-${to}`,
                    indices: Array.from({ length: to - from + 1 }, (_, k) => from - 1 + k) });
    }
    return { groups, bad };
  },

  paintRangeHint() {
    if (this.mode !== 'split' || !this.split) return;
    const spec = this.rangeInput.value.trim();
    const hint = $('#pt-range-hint');
    if (!spec) {
      hint.textContent = t('Leave empty to get every page as its own PDF.');
      hint.className = 'text-xs text-gray-500 dark:text-gray-400';
      return;
    }
    const { groups, bad } = this.parseRanges(spec, this.split.pages);
    if (bad.length) {
      hint.textContent = t('Not a valid range: ') + bad.join(', ');
      hint.className = 'text-xs text-red-600 dark:text-red-400';
    } else {
      hint.textContent = `${plural(groups.length, '{n} file', '{n} files')}: `
        + groups.map((g) => g.label).join(', ');
      hint.className = 'text-xs text-gray-500 dark:text-gray-400';
    }
  },

  async run() {
    const btn = $('#pt-run');
    btn.disabled = true;
    try {
      if (this.mode === 'merge') await this.doMerge();
      else await this.doSplit();
    } catch (err) {
      console.error(err);
      Toast.show(t('Conversion failed'), 'error');
    }
    btn.disabled = false;
  },

  async doMerge() {
    if (this.files.length < 2) { Toast.show(t('Add at least two PDFs to merge'), 'error'); return; }
    const out = await PDFDocument.create();
    for (const { file } of this.files) {
      const src = await PDFDocument.load(await file.arrayBuffer());
      const pages = await out.copyPages(src, src.getPageIndices());
      pages.forEach((p) => out.addPage(p));
    }
    const bytes = await out.save();
    download(new Blob([bytes], { type: 'application/pdf' }), 'merged.pdf', { chain: false });
    Toast.show(t('Merged PDF ready'), 'success');
  },

  async doSplit() {
    const { file, pages: pageCount } = this.split;
    const spec = this.rangeInput.value.trim();
    let groups;
    if (spec) {
      const parsed = this.parseRanges(spec, pageCount);
      if (parsed.bad.length) { Toast.show(t('Not a valid range: ') + parsed.bad.join(', '), 'error'); return; }
      if (!parsed.groups.length) { Toast.show(t('No pages selected'), 'error'); return; }
      groups = parsed.groups;
    } else {
      groups = Array.from({ length: pageCount }, (_, i) => ({ label: `${i + 1}`, indices: [i] }));
    }

    const src = await PDFDocument.load(await file.arrayBuffer());
    const stem = baseName(file.name);
    const entries = [];
    for (const g of groups) {
      const out = await PDFDocument.create();
      const copied = await out.copyPages(src, g.indices);
      copied.forEach((p) => out.addPage(p));
      entries.push({
        name: `${stem}-${g.label}.pdf`,
        blob: new Blob([await out.save()], { type: 'application/pdf' }),
      });
    }

    // A single range is one file; the user asked for that file, not a zip of one.
    if (entries.length === 1) {
      download(entries[0].blob, entries[0].name, { chain: false });
    } else {
      await zipDownload(entries, `${stem}-split.zip`);
    }
    Toast.show(t('Split PDF ready'), 'success');
  },

  reset() {
    this.files = [];
    this.split = null;
    this.list.innerHTML = '';
    this.rangeInput.value = '';
    this.editor.classList.add('hidden');
    this.hero.classList.remove('hidden');
  },
};

App.init();
