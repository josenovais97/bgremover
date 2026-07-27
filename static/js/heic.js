/**
 * HEIC → JPG/PNG/WEBP converter — 100% client-side.
 *
 * iPhones shoot HEIC by default; Windows, Android and most of the web can't
 * open it. The decoder (heic2any, which bundles libheif) is imported on demand
 * from the CDN on the first conversion, cached by the browser and the service
 * worker afterwards — so photos never leave the device, which is the point:
 * nobody's camera roll should transit a stranger's server to change format.
 *
 * Shared helpers come from window.CBG.
 */
const { $, $$, Toast, dropzone, download, zipDownload, humanSize, baseName, plural, t } = CBG;

const isHeic = (f) =>
  /\.heic$|\.heif$/i.test(f.name) || /heic|heif/i.test(f.type || '');

const App = {
  mime: 'image/jpeg',
  ext: 'jpg',
  cards: [],
  _decoder: null,

  init() {
    this.hero = $('#hc-hero');
    this.controls = $('#hc-controls');
    this.grid = $('#hc-grid');
    this.input = $('#hc-input');

    dropzone($('#hc-dropzone'), {
      input: this.input,
      icon: $('#hc-icon'),
      browse: $('#hc-browse'),
      accept: isHeic,
      onFiles: (files) => this.add(files),
    });

    $$('.hc-fmt').forEach((b) => b.addEventListener('click', () => {
      this.mime = b.dataset.fmt;
      this.ext = b.dataset.ext;
      $$('.hc-fmt').forEach((x) => {
        const a = x === b;
        x.classList.toggle('bg-primary', a); x.classList.toggle('text-white', a);
      });
      // Re-encode everything in the new format from the decoded originals.
      this.cards.forEach((card) => this.convert(card));
    }));

    $('#hc-add').addEventListener('click', () => this.input.click());
    $('#hc-clear').addEventListener('click', () => this.clear());
    $('#hc-zip').addEventListener('click', () => this.zipAll());
  },

  decoder() {
    // One import promise shared by every card, so a 10-photo drop doesn't
    // fetch the library ten times.
    if (!this._decoder) {
      this._decoder = import('https://cdn.jsdelivr.net/npm/heic2any@0.0.4/+esm')
        .then((m) => m.default);
    }
    return this._decoder;
  },

  add(files) {
    const heics = files.filter(isHeic);
    if (!heics.length) { Toast.show(t('Those are not HEIC files — drop .heic photos'), 'error'); return; }
    this.hero.classList.add('hidden');
    this.controls.classList.remove('hidden');
    for (const file of heics) {
      const node = $('#hc-card-template').content.firstElementChild.cloneNode(true);
      const card = { file, node, blob: null, url: null };
      node.querySelector('.filename').textContent = file.name;
      node.querySelector('.remove-btn').addEventListener('click', () => this.remove(card));
      node.querySelector('.download-btn').addEventListener('click', () => this.save(card));
      this.grid.appendChild(node);
      this.cards.push(card);
      this.convert(card);
    }
  },

  async convert(card) {
    const meta = card.node.querySelector('.meta');
    const spin = card.node.querySelector('.spin');
    spin.classList.remove('hidden');
    meta.textContent = t('Converting…');
    card.node.querySelector('.download-btn').disabled = true;
    try {
      const heic2any = await this.decoder();
      const out = await heic2any({ blob: card.file, toType: this.mime, quality: 0.92 });
      card.blob = Array.isArray(out) ? out[0] : out;
      if (card.url) URL.revokeObjectURL(card.url);
      card.url = URL.createObjectURL(card.blob);
      card.node.querySelector('.thumb').src = card.url;
      meta.textContent = `${humanSize(card.file.size)} → ${humanSize(card.blob.size)} · ${this.ext.toUpperCase()}`;
      card.node.querySelector('.download-btn').disabled = false;
      this.refreshZip();
    } catch {
      meta.textContent = t('Could not convert {name}', { name: card.file.name });
    } finally {
      spin.classList.add('hidden');
    }
  },

  save(card) {
    if (!card.blob) return;
    download(card.blob, `${baseName(card.file.name)}.${this.ext}`);
  },

  refreshZip() {
    const done = this.cards.filter((c) => c.blob);
    $('#hc-zip').classList.toggle('hidden', done.length < 2);
  },

  async zipAll() {
    const done = this.cards.filter((c) => c.blob);
    if (!done.length) return;
    Toast.show(t('Building ZIP…'), 'info');
    try {
      await zipDownload(
        done.map((c) => ({ name: `${baseName(c.file.name)}.${this.ext}`, blob: c.blob })),
        'clearbg-heic.zip',
      );
      Toast.show(plural(done.length, 'Converted {n} photo', 'Converted {n} photos'));
    } catch {
      Toast.show(t('Could not build the ZIP'), 'error');
    }
  },

  remove(card) {
    if (card.url) URL.revokeObjectURL(card.url);
    card.node.remove();
    this.cards = this.cards.filter((c) => c !== card);
    this.refreshZip();
    if (!this.cards.length) this.clear();
  },

  clear() {
    this.cards.forEach((c) => c.url && URL.revokeObjectURL(c.url));
    this.cards = [];
    this.grid.innerHTML = '';
    this.controls.classList.add('hidden');
    this.hero.classList.remove('hidden');
  },
};

document.addEventListener('DOMContentLoaded', () => App.init());
