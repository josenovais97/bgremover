/**
 * Base64 / data-URI converter — 100% client-side.
 *
 * Two directions, one page:
 *   • Encode  an image file → a `data:` URI (copy, or download as .txt)
 *   • Decode  a `data:` URI or raw Base64 → a real image (preview, download,
 *             and chain onward like any other tool result)
 *
 * There is no upload and no server round-trip: FileReader does the encode and a
 * plain <img>/canvas does the decode. Shared helpers come from window.CBG.
 */
const { $, $$, Toast, download, dropzone, baseName, t } = CBG;

const App = {
  mode: 'encode',

  init() {
    this.dropzone = $('#b64-dropzone');
    this.input = $('#b64-input');
    this.editor = $('#b64-editor');

    dropzone(this.dropzone, {
      input: this.input,
      icon: $('#b64-icon'),
      browse: $('#b64-browse'),
      multiple: false,
      onFiles: (files) => this.encode(files[0]),
    });

    $$('.b64-mode').forEach((b) => b.addEventListener('click', () => this.setMode(b.dataset.mode)));
    $('#b64-decode-input').addEventListener('input', () => this.decode());
    $('#b64-copy').addEventListener('click', () => this.copy());
    $('#b64-copy-html').addEventListener('click', () => this.copyHtml());
    $('#b64-txt').addEventListener('click', () => this.downloadText());
    $('#b64-save-img').addEventListener('click', () => this.saveImage());
    $('#b64-new').addEventListener('click', () => this.reset());
  },

  setMode(mode) {
    this.mode = mode;
    $$('.b64-mode').forEach((b) => {
      const a = b.dataset.mode === mode;
      b.classList.toggle('bg-primary', a);
      b.classList.toggle('text-white', a);
      b.setAttribute('aria-selected', a);
    });
    $('#b64-encode-pane').classList.toggle('hidden', mode !== 'encode');
    $('#b64-decode-pane').classList.toggle('hidden', mode !== 'decode');
    // The encode result only belongs under the encode tab.
    if (mode !== 'encode') this.editor.classList.add('hidden');
  },

  /* --------------------------------------------------------------- encode */
  encode(file) {
    if (!file) return;
    this.encodeName = baseName(file.name);
    const reader = new FileReader();
    reader.onerror = () => Toast.show(t('Could not read that image'), 'error');
    reader.onload = () => {
      const uri = reader.result;
      $('#b64-out').value = uri;
      $('#b64-out-meta').textContent = this.meta(file.type, uri.length);
      $('#b64-out-preview').src = uri;
      this.setMode('encode');
      this.editor.classList.remove('hidden');
      this.editor.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    };
    reader.readAsDataURL(file);
  },

  meta(type, chars) {
    const kb = (chars / 1024).toFixed(1);
    // Base64 inflates bytes ~33%; the string length is what actually gets pasted.
    return `${(type || 'image').replace('image/', '').toUpperCase()} · ${kb} KB of text`;
  },

  async copy() {
    const text = $('#b64-out').value;
    if (!text) return;
    try { await navigator.clipboard.writeText(text); Toast.show(t('Copied to clipboard')); }
    catch { Toast.show(t('Copy failed'), 'error'); }
  },

  async copyHtml() {
    const uri = $('#b64-out').value;
    if (!uri) return;
    try {
      await navigator.clipboard.writeText(`<img src="${uri}" alt="">`);
      Toast.show(t('HTML copied to clipboard'));
    } catch { Toast.show(t('Copy failed'), 'error'); }
  },

  downloadText() {
    const text = $('#b64-out').value;
    if (!text) return;
    // A .txt blob, not an image — pass chain:false so the "keep editing" bar
    // doesn't offer a text file to the image tools.
    download(new Blob([text], { type: 'text/plain' }), `${this.encodeName || 'image'}-base64.txt`, { chain: false });
  },

  /* --------------------------------------------------------------- decode */
  decode() {
    const raw = $('#b64-decode-input').value.trim();
    const preview = $('#b64-decode-preview');
    const meta = $('#b64-decode-meta');
    this.decodedUri = '';
    if (!raw) { preview.classList.add('hidden'); meta.textContent = ''; $('#b64-save-img').disabled = true; return; }

    // Accept a full data: URI or bare Base64 (assume PNG if the header is absent).
    const uri = /^data:image\//i.test(raw) ? raw : `data:image/png;base64,${raw.replace(/\s+/g, '')}`;
    const probe = new Image();
    probe.onload = () => {
      this.decodedUri = uri;
      this.decodedDims = `${probe.naturalWidth} × ${probe.naturalHeight}`;
      preview.src = uri;
      preview.classList.remove('hidden');
      meta.textContent = `${this.decodedDims} px`;
      $('#b64-save-img').disabled = false;
    };
    probe.onerror = () => {
      preview.classList.add('hidden');
      meta.textContent = t('That is not a valid image data URI');
      $('#b64-save-img').disabled = true;
    };
    probe.src = uri;
  },

  async saveImage() {
    if (!this.decodedUri) return;
    try {
      const blob = await (await fetch(this.decodedUri)).blob();
      const ext = (blob.type.split('/')[1] || 'png').replace('jpeg', 'jpg');
      download(blob, `decoded.${ext}`);
    } catch { Toast.show(t('Export failed'), 'error'); }
  },

  reset() {
    this.editor.classList.add('hidden');
    $('#b64-out').value = '';
    $('#b64-decode-input').value = '';
    this.decode();
  },
};

document.addEventListener('DOMContentLoaded', () => App.init());
