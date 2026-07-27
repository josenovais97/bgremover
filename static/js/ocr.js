/**
 * Image → text (OCR) — 100% client-side.
 *
 * Tesseract.js runs the classic Tesseract engine as WebAssembly inside a Web
 * Worker, with the language pack fetched (and then cached) on first use. That
 * makes the privacy story real rather than aspirational: screenshots full of
 * conversations, codes and documents are recognised without leaving the device.
 *
 * The library is imported on demand from the CDN; it spawns its worker from a
 * blob: URL itself, which the CSP allows. Shared helpers come from window.CBG.
 */
const { $, Toast, dropzone, download, baseName, t } = CBG;

const App = {
  worker: null,
  workerLang: null,
  file: null,

  init() {
    this.hero = $('#oc-hero');
    this.editor = $('#oc-editor');

    dropzone($('#oc-dropzone'), {
      input: $('#oc-input'),
      icon: $('#oc-icon'),
      browse: $('#oc-browse'),
      multiple: false,
      onFiles: (files) => this.load(files[0]),
    });

    this.pickDefaultLang();
    $('#oc-rerun').addEventListener('click', () => this.recognise());
    $('#oc-lang').addEventListener('change', () => this.recognise());
    $('#oc-copy').addEventListener('click', () => this.copy());
    $('#oc-save').addEventListener('click', () => this.saveTxt());
    $('#oc-new').addEventListener('click', () => this.reset());
  },

  /**
   * Default the OCR language to the visitor's, not always English: the page
   * language first (a /pt/ visitor is reading Portuguese), then the browser's.
   * Only switches if the guess is one of the offered packs — otherwise the
   * English default stands, and the manual picker always wins afterwards.
   */
  pickDefaultLang() {
    const select = $('#oc-lang');
    const map = { en: 'eng', pt: 'por', es: 'spa', fr: 'fra', de: 'deu' };
    const codes = [
      (document.documentElement.lang || '').slice(0, 2).toLowerCase(),
      (navigator.language || '').slice(0, 2).toLowerCase(),
    ];
    for (const c of codes) {
      if (map[c] && [...select.options].some((o) => o.value === map[c])) {
        select.value = map[c];
        return;
      }
    }
  },

  async load(file) {
    this.file = file;
    if (this.url) URL.revokeObjectURL(this.url);
    this.url = URL.createObjectURL(file);
    $('#oc-preview').src = this.url;
    this.hero.classList.add('hidden');
    this.editor.classList.remove('hidden');
    this.recognise();
  },

  async getWorker(lang) {
    if (this.worker && this.workerLang === lang) return this.worker;
    if (this.worker) { await this.worker.terminate(); this.worker = null; }
    const { createWorker } = await import('https://cdn.jsdelivr.net/npm/tesseract.js@5.1.1/+esm');
    this.worker = await createWorker(lang, 1, {
      // Language data from jsDelivr rather than tesseract.js's default host:
      // the service worker already caches cdn.jsdelivr.net into its long-lived
      // cache, so the pack downloads once and OCR keeps working offline. The
      // packages are per-language, so the path is built per worker — fine,
      // since a language change recreates the worker anyway.
      langPath: `https://cdn.jsdelivr.net/npm/@tesseract.js-data/${lang}@1.0.0/4.0.0_best_int`,
      logger: (m) => {
        if (m.status === 'recognizing text') {
          $('#oc-bar').style.width = `${Math.round(m.progress * 100)}%`;
        }
      },
    });
    this.workerLang = lang;
    return this.worker;
  },

  async recognise() {
    if (!this.file) return;
    const box = $('#oc-text');
    box.value = '';
    box.placeholder = t('Reading…');
    $('#oc-bar').style.width = '5%';
    // #oc-words is an aria-live region — mirror the state there too, so a
    // screen reader hears "Reading…" and then the outcome, not just a silent
    // placeholder change on the textarea.
    $('#oc-words').textContent = t('Reading…');
    try {
      const worker = await this.getWorker($('#oc-lang').value);
      const { data } = await worker.recognize(this.file);
      const text = (data.text || '').trim();
      $('#oc-bar').style.width = '100%';
      if (!text) {
        box.placeholder = t('No text found in that image');
        $('#oc-words').textContent = t('No text found in that image');
        Toast.show(t('No text found in that image'), 'info');
        return;
      }
      box.value = text;
      $('#oc-words').textContent = t('{n} words', { n: text.split(/\s+/).length });
      window.__clearbgReport?.(1);
    } catch {
      box.placeholder = t('Could not read the text');
      $('#oc-words').textContent = t('Could not read the text');
      Toast.show(t('Could not read the text'), 'error');
      $('#oc-bar').style.width = '0%';
    }
  },

  async copy() {
    const text = $('#oc-text').value;
    if (!text) return;
    try { await navigator.clipboard.writeText(text); Toast.show(t('Copied to clipboard')); }
    catch { Toast.show(t('Copy failed'), 'error'); }
  },

  saveTxt() {
    const text = $('#oc-text').value;
    if (!text) return;
    download(new Blob([text], { type: 'text/plain' }),
      `${baseName(this.file?.name) || 'text'}.txt`);
  },

  reset() {
    this.editor.classList.add('hidden');
    this.hero.classList.remove('hidden');
    if (this.url) { URL.revokeObjectURL(this.url); this.url = null; }
    this.file = null;
    $('#oc-text').value = '';
    $('#oc-bar').style.width = '0%';
  },
};

document.addEventListener('DOMContentLoaded', () => App.init());
