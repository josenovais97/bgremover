/**
 * Image upscaler — 100% client-side.
 *
 * Enlarges 2× or 4× with pica's Lanczos-class resampler (mks2013) plus its
 * unsharp mask, which is the classic photo-software way to enlarge: clean edge
 * interpolation followed by gentle detail sharpening. Deliberately NOT a neural
 * super-resolution model — the previous AI upscaler froze the tab on large
 * photos, which is worse than honest resampling that finishes in a blink.
 *
 * pica is imported on demand from the CDN (allowed by the CSP, cached by the
 * service worker). Nothing is uploaded. Shared helpers come from window.CBG.
 */
const { $, $$, Toast, loadImage, dropzone, download, zipDownload, baseName, plural, t } = CBG;

// Longest-side output cap so a 4× of a big photo can't exhaust canvas memory.
const MAX_OUT = 8000;

const App = {
  scale: 2,
  fmt: 'png',
  sharpen: 40,
  result: null,
  queue: [],   // extra files upscaled with the same factor + sharpening

  init() {
    this.hero = $('#up-hero');
    this.editor = $('#up-editor');
    this.batch = $('[data-batch]');

    dropzone($('#up-dropzone'), {
      input: $('#up-input'),
      icon: $('#up-icon'),
      browse: $('#up-browse'),
      onFiles: (files) => { this.queue = files.slice(1); this.syncBatch(); this.load(files[0]); },
    });
    $('[data-batch-zip]').addEventListener('click', () => this.downloadAll());

    $$('.up-scale').forEach((b) => b.addEventListener('click', () => {
      this.scale = +b.dataset.scale;
      $$('.up-scale').forEach((x) => {
        const a = x === b;
        x.classList.toggle('bg-primary', a); x.classList.toggle('text-white', a);
      });
      this.updateSize();
    }));
    $$('.up-fmt').forEach((b) => b.addEventListener('click', () => {
      this.fmt = b.dataset.fmt;
      $$('.up-fmt').forEach((x) => {
        const a = x === b;
        x.classList.toggle('bg-primary', a); x.classList.toggle('text-white', a);
      });
    }));

    const sharpenInput = $('#up-sharpen');
    sharpenInput.addEventListener('input', () => {
      this.sharpen = +sharpenInput.value;
      $('#up-sharpen-value').textContent = sharpenInput.value;
    });

    $('#up-run').addEventListener('click', () => this.run());
    $('#up-download').addEventListener('click', () => this.save());
    $('#up-new').addEventListener('click', () => this.reset());
  },

  async load(file) {
    if (this.url) URL.revokeObjectURL(this.url);
    this.url = URL.createObjectURL(file);
    try { this.img = await loadImage(this.url); }
    catch { Toast.show(t('Could not read that image'), 'error'); return; }
    this.name = baseName(file.name);
    this.result = null;
    $('#up-download').disabled = true;
    $('#up-preview').src = this.url;
    this.updateSize();
    this.hero.classList.add('hidden');
    this.editor.classList.remove('hidden');
  },

  outSize() {
    const w = this.img.naturalWidth * this.scale;
    const h = this.img.naturalHeight * this.scale;
    const k = Math.min(1, MAX_OUT / Math.max(w, h));
    return { w: Math.round(w * k), h: Math.round(h * k), capped: k < 1 };
  },

  updateSize() {
    if (!this.img) return;
    const { w, h, capped } = this.outSize();
    $('#up-size').textContent =
      `${this.img.naturalWidth}×${this.img.naturalHeight} → ${w}×${h}` + (capped ? ` (${t('capped')})` : '');
  },

  async pica() {
    if (!this._pica) {
      const { default: Pica } = await import('https://cdn.jsdelivr.net/npm/pica@9.0.1/+esm');
      this._pica = new Pica();
    }
    return this._pica;
  },

  /** Upscale one loaded image with the current settings; returns a blob. */
  async upscaleImage(img) {
    const pica = await this.pica();
    const src = document.createElement('canvas');
    src.width = img.naturalWidth;
    src.height = img.naturalHeight;
    src.getContext('2d').drawImage(img, 0, 0);
    const w0 = img.naturalWidth * this.scale, h0 = img.naturalHeight * this.scale;
    const k = Math.min(1, MAX_OUT / Math.max(w0, h0));
    const dst = document.createElement('canvas');
    dst.width = Math.round(w0 * k); dst.height = Math.round(h0 * k);
    await pica.resize(src, dst, {
      unsharpAmount: this.sharpen * 1.6,   // pica takes 0–500; slider is 0–100
      unsharpRadius: 0.6,
      unsharpThreshold: 2,
    });
    const mime = this.fmt === 'jpg' ? 'image/jpeg' : 'image/png';
    return pica.toBlob(dst, mime, 0.92);
  },

  async run() {
    if (!this.img) return;
    $('#up-busy').classList.remove('hidden');
    try {
      const { w, h } = this.outSize();
      this.result = await this.upscaleImage(this.img);
      $('#up-preview').src = URL.createObjectURL(this.result);
      $('#up-download').disabled = false;
      window.__clearbgReport?.(1);
      Toast.show(t('Upscaled to {w}×{h}', { w, h }));
    } catch {
      Toast.show(t('Could not upscale that image'), 'error');
    } finally {
      $('#up-busy').classList.add('hidden');
    }
  },

  syncBatch() {
    const n = this.queue.length + (this.queue.length ? 1 : 0);
    this.batch.classList.toggle('hidden', n < 2);
    this.batch.querySelector('[data-batch-count]').textContent = n;
  },

  async downloadAll() {
    if (!this.img) return;
    const btn = $('[data-batch-zip]');
    btn.disabled = true;
    $('#up-busy').classList.remove('hidden');
    try {
      const entries = [{
        name: `${this.name || 'image'}-${this.scale}x.${this.fmt}`,
        blob: await this.upscaleImage(this.img),
      }];
      for (const f of this.queue) {
        const url = URL.createObjectURL(f);
        try {
          const img = await loadImage(url);
          entries.push({ name: `${baseName(f.name)}-${this.scale}x.${this.fmt}`, blob: await this.upscaleImage(img) });
        } catch { /* skip an unreadable file rather than sinking the batch */ }
        URL.revokeObjectURL(url);
      }
      await zipDownload(entries.filter((e) => e.blob), 'clearbg-upscaled.zip');
      window.__clearbgReport?.(entries.length, 'downloaded');
      Toast.show(plural(entries.length, 'Exported {n} photo', 'Exported {n} photos'));
    } catch {
      Toast.show(t('Could not build the ZIP'), 'error');
    } finally {
      btn.disabled = false;
      $('#up-busy').classList.add('hidden');
    }
  },

  save() {
    if (!this.result) return;
    window.__clearbgReport?.(1, 'downloaded');
    download(this.result, `${this.name || 'image'}-${this.scale}x.${this.fmt}`);
  },

  reset() {
    this.editor.classList.add('hidden');
    this.hero.classList.remove('hidden');
    if (this.url) { URL.revokeObjectURL(this.url); this.url = null; }
    this.result = null;
    this.queue = [];
    this.syncBatch();
  },
};

document.addEventListener('DOMContentLoaded', () => App.init());
