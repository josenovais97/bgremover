/**
 * CSV ⇄ Excel (.xlsx) — 100% client-side.
 *
 * Both directions, because they are the same job seen from two sides and people
 * arrive needing either one.
 *
 * The XLSX → CSV direction is also the honest answer to "convert Excel to Google
 * Sheets". Sheets is a cloud service, so a real conversion would mean uploading
 * the file to Google's servers under OAuth — which this site cannot do and stay
 * what it is. But Sheets imports CSV natively, so handing the user a CSV solves
 * the actual need (getting the data into Sheets) without the file leaving the
 * machine. That is why the CSV download names Sheets in its own copy.
 *
 * Library choice: exceljs, not SheetJS. SheetJS stopped publishing to npm after
 * 0.18.5 in March 2022 and moved to self-hosted distribution under different
 * terms; pinning a four-year-old npm build of a format parser is not a
 * maintenance position worth taking. exceljs is MIT and current.
 *
 * Shared helpers come from window.CBG (static/js/kit.js).
 */
import Papa from 'https://cdn.jsdelivr.net/npm/papaparse@5.5.4/+esm';
import ExcelJS from 'https://cdn.jsdelivr.net/npm/exceljs@4.4.0/+esm';

const { $, $$, Toast, dropzone, download, baseName, remember, plural, t } = CBG;

/** Rows shown in the preview. The grid is a sanity check, not a spreadsheet. */
const PREVIEW_ROWS = 12;
const PREVIEW_COLS = 12;

const prefs = remember('csvx');

const App = {
  mode: 'to-xlsx',   // 'to-xlsx' | 'to-csv'
  sheets: [],        // [{ name, rows }]
  active: 0,
  source: '',

  init() {
    this.dropzoneEl = $('#cx-dropzone');
    this.input = $('#cx-input');
    this.hero = this.dropzoneEl.closest('section');
    this.editor = $('#cx-editor');
    this.grid = $('#cx-grid');
    this.tabs = $('#cx-sheet-tabs');
    this.meta = $('#cx-meta');
    this.name = $('#cx-name');
    this.busy = $('#cx-busy');
    this.saveBtn = $('#cx-save');
    this.hint = $('#cx-hint');

    this.mode = prefs.get().mode || 'to-xlsx';
    this.paintMode();

    $$('.cx-mode').forEach((b) => b.addEventListener('click', () => {
      this.mode = b.dataset.mode;
      prefs.set({ mode: this.mode });
      this.paintMode();
      this.reset();
    }));

    dropzone(this.dropzoneEl, {
      input: this.input,
      icon: $('#cx-icon'),
      browse: $('#cx-browse'),
      multiple: false,
      accept: () => true,
      onFiles: (files) => this.load(files[0]),
    });

    this.saveBtn.addEventListener('click', () => this.save());
    $('#cx-new').addEventListener('click', () => this.reset());
  },

  paintMode() {
    $$('.cx-mode').forEach((b) => {
      const on = b.dataset.mode === this.mode;
      b.classList.toggle('bg-primary', on);
      b.classList.toggle('text-white', on);
      b.setAttribute('aria-selected', on ? 'true' : 'false');
    });
    const toXlsx = this.mode === 'to-xlsx';
    this.input.setAttribute('accept', toXlsx ? '.csv,.tsv,.txt,text/csv' : '.xlsx,.xlsm');
    $('#cx-drop-title').textContent = toXlsx ? t('Drop a CSV file') : t('Drop an Excel file');
    $('#cx-drop-sub').textContent = toXlsx ? t('or click to browse — .csv or .tsv')
                                           : t('or click to browse — .xlsx');
    this.saveBtn.innerHTML = toXlsx
      ? '<i class="fa-solid fa-file-arrow-down mr-1.5" aria-hidden="true"></i>' + t('Download .xlsx')
      : '<i class="fa-solid fa-file-arrow-down mr-1.5" aria-hidden="true"></i>' + t('Download .csv');
  },

  async load(file) {
    this.busy.classList.remove('hidden');
    try {
      if (this.mode === 'to-xlsx') await this.readCsv(file);
      else await this.readXlsx(file);
    } catch (err) {
      console.error(err);
      this.busy.classList.add('hidden');
      Toast.show(this.mode === 'to-xlsx' ? t('Could not read that CSV file')
                                         : t('Could not read that Excel file'), 'error');
      return;
    }
    this.busy.classList.add('hidden');

    if (!this.sheets.length || !this.sheets.some((s) => s.rows.length)) {
      Toast.show(t('That file has no rows'), 'error');
      return;
    }

    this.source = file.name;
    this.name.textContent = file.name;
    this.active = 0;
    this.paintTabs();
    this.paintGrid();
    this.hero.classList.add('hidden');
    this.editor.classList.remove('hidden');
    this.editor.scrollIntoView({ behavior: 'smooth', block: 'start' });
  },

  async readCsv(file) {
    const text = await file.text();
    // Let Papa sniff the delimiter: European exports are frequently
    // semicolon-separated, and guessing comma turns every row into one cell.
    const out = Papa.parse(text, { skipEmptyLines: 'greedy' });
    if (out.errors?.length) console.warn('CSV parse notes', out.errors.slice(0, 3));
    this.sheets = [{ name: baseName(file.name).slice(0, 31) || 'Sheet1', rows: out.data }];
    this.delimiter = out.meta?.delimiter || ',';
  },

  async readXlsx(file) {
    const wb = new ExcelJS.Workbook();
    await wb.xlsx.load(await file.arrayBuffer());
    this.sheets = [];
    wb.eachSheet((ws) => {
      const rows = [];
      ws.eachRow({ includeEmpty: false }, (row) => {
        // row.values is 1-based with a hole at [0]; values may be rich text,
        // formula objects or dates rather than primitives.
        rows.push(row.values.slice(1).map((v) => this.cellText(v)));
      });
      this.sheets.push({ name: ws.name, rows });
    });
  },

  /** Flatten whatever exceljs hands back into a string a CSV can hold. */
  cellText(v) {
    if (v === null || v === undefined) return '';
    if (v instanceof Date) return v.toISOString().slice(0, 10);
    if (typeof v === 'object') {
      // A formula cell carries its last computed result; that is what a CSV
      // wants, since the formula itself would be meaningless out of context.
      if ('result' in v) return this.cellText(v.result);
      if ('text' in v) return String(v.text);
      if (Array.isArray(v.richText)) return v.richText.map((r) => r.text).join('');
      if ('hyperlink' in v) return String(v.text ?? v.hyperlink);
      return '';
    }
    return String(v);
  },

  paintTabs() {
    this.tabs.innerHTML = '';
    this.tabs.classList.toggle('hidden', this.sheets.length < 2);
    this.sheets.forEach((s, i) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'px-3 py-1.5 rounded-lg text-xs font-medium border transition '
        + (i === this.active
          ? 'bg-primary text-white border-primary'
          : 'border-gray-300 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800');
      b.textContent = `${s.name} (${s.rows.length})`;
      b.addEventListener('click', () => { this.active = i; this.paintTabs(); this.paintGrid(); });
      this.tabs.appendChild(b);
    });
  },

  paintGrid() {
    const sheet = this.sheets[this.active];
    const rows = sheet.rows;
    const cols = Math.max(...rows.slice(0, PREVIEW_ROWS).map((r) => r.length), 1);
    const shownCols = Math.min(cols, PREVIEW_COLS);

    const table = document.createElement('table');
    table.className = 'w-full text-xs border-collapse';
    rows.slice(0, PREVIEW_ROWS).forEach((row, r) => {
      const tr = document.createElement('tr');
      if (r === 0) tr.className = 'bg-gray-100 dark:bg-gray-800 font-semibold';
      for (let c = 0; c < shownCols; c++) {
        const cell = document.createElement(r === 0 ? 'th' : 'td');
        cell.className = 'border border-gray-200 dark:border-gray-700 px-2 py-1 text-left '
          + 'max-w-[16rem] truncate';
        // textContent, never innerHTML: these are the user's own cells.
        cell.textContent = row[c] ?? '';
        tr.appendChild(cell);
      }
      table.appendChild(tr);
    });

    this.grid.innerHTML = '';
    this.grid.appendChild(table);

    const extraRows = Math.max(0, rows.length - PREVIEW_ROWS);
    const extraCols = Math.max(0, cols - shownCols);
    this.meta.textContent = [
      plural(rows.length, '{n} row', '{n} rows'),
      plural(cols, '{n} column', '{n} columns'),
    ].join(' · ');
    this.hint.textContent = (extraRows || extraCols)
      ? t('Preview shows the first rows and columns only — the whole file is converted.')
      : '';
  },

  async save() {
    this.saveBtn.disabled = true;
    try {
      if (this.mode === 'to-xlsx') await this.saveXlsx();
      else this.saveCsv();
    } catch (err) {
      console.error(err);
      Toast.show(t('Conversion failed'), 'error');
    }
    this.saveBtn.disabled = false;
  },

  async saveXlsx() {
    const wb = new ExcelJS.Workbook();
    wb.creator = 'ClearBG';
    for (const s of this.sheets) {
      const ws = wb.addWorksheet(s.name);
      s.rows.forEach((r) => ws.addRow(r));
      // Bold the first row and freeze it: a CSV's header line is a header in
      // every use of the file, and it is the one thing Excel cannot infer.
      if (s.rows.length > 1) {
        ws.getRow(1).font = { bold: true };
        ws.views = [{ state: 'frozen', ySplit: 1 }];
      }
      ws.columns.forEach((col, i) => {
        const width = Math.max(...s.rows.slice(0, 200).map((r) => String(r[i] ?? '').length), 8);
        col.width = Math.min(width + 2, 60);
      });
    }
    const buf = await wb.xlsx.writeBuffer();
    // chain:false — the cross-tool bar carries images between image tools; a
    // spreadsheet has nowhere to go from here.
    download(new Blob([buf], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    }), `${baseName(this.source)}.xlsx`, { chain: false });
    Toast.show(t('Excel file ready'), 'success');
  },

  saveCsv() {
    const sheet = this.sheets[this.active];
    // Papa handles the quoting rules: embedded commas, quotes and newlines all
    // have to be escaped or the file is silently corrupt in a way that only
    // shows up rows later.
    const csv = Papa.unparse(sheet.rows, { newline: '\r\n' });
    // The BOM is what makes Excel open a UTF-8 CSV without mangling accented
    // characters — and Sheets ignores it, so it costs nothing on that side.
    download(new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8' }),
      `${baseName(this.source)}${this.sheets.length > 1 ? '-' + sheet.name : ''}.csv`,
      { chain: false });
    Toast.show(t('CSV ready — import it in Google Sheets with File → Import'), 'success');
  },

  reset() {
    this.sheets = [];
    this.grid.innerHTML = '';
    this.tabs.innerHTML = '';
    this.editor.classList.add('hidden');
    this.hero.classList.remove('hidden');
  },
};

App.init();
