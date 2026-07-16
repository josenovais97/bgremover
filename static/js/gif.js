/**
 * Animated GIF maker — 100% client-side.
 *
 * Frames are painted onto one fixed-size canvas (GIF has a single logical
 * screen, so mixed dimensions get fitted), then encoded with gifenc. Encoding
 * is deliberately NOT live: quantising every frame is far too slow to run on a
 * slider drag, so the canvas plays a cheap preview loop and the real GIF is
 * only built when the user asks. Nothing is uploaded.
 */
import { GIFEncoder, applyPalette, quantize } from 'https://cdn.jsdelivr.net/npm/gifenc@1.0.3/+esm';

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const humanSize = (b) => (b < 1024 * 1024 ? `${Math.round(b / 1024)} KB` : `${(b / 1048576).toFixed(1)} MB`);

const loadImage = (src) => new Promise((resolve, reject) => {
  const img = new Image(); img.onload = () => resolve(img); img.onerror = reject; img.src = src;
});

const Toast = {
  show(message, type = 'success') {
    const c = $('#toast-container');
    if (!c) return;
    const map = {
      success: ['bg-green-50 dark:bg-green-900/40 text-green-800 dark:text-green-200 border-green-200 dark:border-green-800', 'fa-circle-check text-green-500'],
      error: ['bg-red-50 dark:bg-red-900/40 text-red-800 dark:text-red-200 border-red-200 dark:border-red-800', 'fa-circle-exclamation text-red-500'],
    };
    const [cls, icon] = map[type] || map.success;
    const el = document.createElement('div');
    el.className = `pointer-events-auto flex items-center gap-3 px-5 py-3.5 rounded-xl border shadow-lg transition-all duration-300 translate-y-4 opacity-0 ${cls}`;
    el.setAttribute('role', 'alert');
    el.innerHTML = `<i class="fa-solid ${icon} text-lg"></i><span class="font-medium text-sm">${message}</span>`;
    c.appendChild(el);
    requestAnimationFrame(() => el.classList.remove('translate-y-4', 'opacity-0'));
    setTimeout(() => { el.classList.add('opacity-0', 'translate-y-4'); setTimeout(() => el.remove(), 300); }, 3600);
  },
};

const App = {
  frames: [],       // [{ img, url, name }]
  delay: 400,
  size: 360,
  fit: 'cover',
  loop: true,
  bounce: false,
  playing: null,
  gifUrl: null,

  init() {
    this.dropzone = $('#gf-dropzone');
    this.input = $('#gf-input');
    this.editor = $('#gf-editor');
    this.canvas = $('#gf-canvas');

    const open = () => this.input.click();
    $('#gf-browse').addEventListener('click', (e) => { e.stopPropagation(); open(); });
    $('#gf-add').addEventListener('click', open);
    this.dropzone.addEventListener('click', open);
    this.dropzone.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); } });
    this.input.addEventListener('change', (e) => this.load(e.target.files));

    const icon = $('#gf-icon');
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach((evt) =>
      this.dropzone.addEventListener(evt, (e) => { e.preventDefault(); e.stopPropagation(); }));
    ['dragenter', 'dragover'].forEach((evt) => this.dropzone.addEventListener(evt, () => { this.dropzone.classList.add('border-primary', 'bg-primary/5'); icon.classList.add('scale-110'); }));
    ['dragleave', 'drop'].forEach((evt) => this.dropzone.addEventListener(evt, () => { this.dropzone.classList.remove('border-primary', 'bg-primary/5'); icon.classList.remove('scale-110'); }));
    this.dropzone.addEventListener('drop', (e) => this.load(e.dataTransfer.files));
    document.addEventListener('paste', (e) => {
      const files = [...(e.clipboardData?.items || [])].filter((i) => i.kind === 'file').map((i) => i.getAsFile());
      if (files.length) this.load(files);
    });

    $('#gf-delay').addEventListener('input', (e) => {
      this.delay = +e.target.value;
      $('#gf-delay-val').textContent = `${this.delay}ms`;
      this.invalidate(); this.play();
    });
    $$('.gf-size').forEach((b) => b.addEventListener('click', () => {
      this.size = +b.dataset.size;
      this.segment($$('.gf-size'), b);
      this.resize(); this.invalidate();
    }));
    $$('.gf-fit').forEach((b) => b.addEventListener('click', () => {
      this.fit = b.dataset.fit;
      this.segment($$('.gf-fit'), b);
      this.invalidate();
    }));
    $('#gf-loop').addEventListener('change', (e) => { this.loop = e.target.checked; this.invalidate(); });
    $('#gf-bounce').addEventListener('change', (e) => { this.bounce = e.target.checked; this.invalidate(); this.play(); });
    $('#gf-create').addEventListener('click', () => this.create());
    $('#gf-new').addEventListener('click', () => this.reset());
  },

  segment(group, active) {
    group.forEach((x) => {
      const a = x === active;
      x.classList.toggle('ring-2', a); x.classList.toggle('ring-primary', a);
      x.classList.toggle('hover:bg-gray-100', !a); x.classList.toggle('dark:hover:bg-gray-800', !a);
    });
  },

  async load(fileList) {
    // Snapshot before clearing the input — fileList is the live input.files.
    const files = [...(fileList || [])].filter((f) => f && /^image\//.test(f.type));
    this.input.value = '';
    if (!files.length) { Toast.show('Please choose image files', 'error'); return; }
    for (const f of files) {
      const url = URL.createObjectURL(f);
      try {
        this.frames.push({ img: await loadImage(url), url, name: f.name });
      } catch {
        URL.revokeObjectURL(url);
        Toast.show(`Could not read ${f.name}`, 'error');
      }
    }
    if (!this.frames.length) return;
    this.dropzone.parentElement.classList.add('hidden');
    this.editor.classList.remove('hidden');
    this.resize();
    this.renderFrames();
    this.invalidate();
    this.play();
  },

  /** GIF has one fixed logical screen — derive it from the first frame. */
  resize() {
    const first = this.frames[0];
    if (!first) return;
    const ar = first.img.naturalWidth / first.img.naturalHeight;
    const [w, h] = ar >= 1 ? [this.size, Math.round(this.size / ar)] : [Math.round(this.size * ar), this.size];
    this.canvas.width = Math.max(2, w);
    this.canvas.height = Math.max(2, h);
  },

  paint(ctx, frame) {
    const { width: w, height: h } = this.canvas;
    ctx.clearRect(0, 0, w, h);
    // GIF has no alpha blending here, so letterboxing needs a solid backdrop.
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, w, h);
    const iw = frame.img.naturalWidth, ih = frame.img.naturalHeight;
    const scale = this.fit === 'cover' ? Math.max(w / iw, h / ih) : Math.min(w / iw, h / ih);
    const dw = iw * scale, dh = ih * scale;
    ctx.imageSmoothingQuality = 'high';
    ctx.drawImage(frame.img, (w - dw) / 2, (h - dh) / 2, dw, dh);
  },

  /** Playback order — bounce appends the middle frames in reverse. */
  order() {
    const n = this.frames.length;
    const fwd = this.frames.map((_, i) => i);
    if (!this.bounce || n < 3) return fwd;
    return fwd.concat(fwd.slice(1, -1).reverse());
  },

  play() {
    clearTimeout(this.playing);
    if (!this.frames.length) return;
    const ctx = this.canvas.getContext('2d');
    const seq = this.order();
    let i = 0;
    const tick = () => {
      if (!this.frames.length) return;
      this.paint(ctx, this.frames[seq[i % seq.length]]);
      i += 1;
      this.playing = setTimeout(tick, this.delay);
    };
    tick();
  },

  /** Any setting change makes a previously built GIF stale. */
  invalidate() {
    const dl = $('#gf-download');
    dl.classList.add('hidden');
    if (this.gifUrl) { URL.revokeObjectURL(this.gifUrl); this.gifUrl = null; }
  },

  renderFrames() {
    const list = $('#gf-frames');
    $('#gf-count').textContent = this.frames.length;
    list.innerHTML = '';
    this.frames.forEach((f, i) => {
      const li = document.createElement('li');
      li.className = 'flex items-center gap-2 text-xs';
      li.innerHTML = `
        <img src="${f.url}" alt="" class="w-10 h-10 object-cover rounded border border-gray-200 dark:border-gray-800 shrink-0">
        <span class="truncate flex-1 text-gray-500 dark:text-gray-400">${i + 1}. ${f.name}</span>
        <button type="button" data-act="up" data-i="${i}" class="w-6 h-6 rounded hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-30" aria-label="Move ${f.name} earlier" ${i === 0 ? 'disabled' : ''}><i class="fa-solid fa-arrow-left" aria-hidden="true"></i></button>
        <button type="button" data-act="down" data-i="${i}" class="w-6 h-6 rounded hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-30" aria-label="Move ${f.name} later" ${i === this.frames.length - 1 ? 'disabled' : ''}><i class="fa-solid fa-arrow-left inline-block -scale-x-100" aria-hidden="true"></i></button>
        <button type="button" data-act="del" data-i="${i}" class="w-6 h-6 rounded text-red-500 hover:bg-red-50 dark:hover:bg-red-900/30" aria-label="Remove ${f.name}"><i class="fa-solid fa-trash-can" aria-hidden="true"></i></button>`;
      list.appendChild(li);
    });
    $$('button[data-act]', list).forEach((b) => b.addEventListener('click', () => {
      const i = +b.dataset.i;
      if (b.dataset.act === 'del') {
        URL.revokeObjectURL(this.frames[i].url);
        this.frames.splice(i, 1);
        if (!this.frames.length) { this.reset(); return; }
      } else {
        const j = b.dataset.act === 'up' ? i - 1 : i + 1;
        [this.frames[i], this.frames[j]] = [this.frames[j], this.frames[i]];
      }
      this.resize();
      this.renderFrames();
      this.invalidate();
      this.play();
    }));
  },

  async create() {
    if (this.frames.length < 2) { Toast.show('Add at least 2 photos', 'error'); return; }
    const btn = $('#gf-create');
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin mr-1.5"></i>Encoding…';
    clearTimeout(this.playing);

    const { width: w, height: h } = this.canvas;
    const ctx = this.canvas.getContext('2d', { willReadFrequently: true });
    const seq = this.order();
    const gif = GIFEncoder();

    try {
      for (let n = 0; n < seq.length; n += 1) {
        this.paint(ctx, this.frames[seq[n]]);
        const { data } = ctx.getImageData(0, 0, w, h);
        const palette = quantize(data, 256);
        const index = applyPalette(data, palette);
        // gifenc reads `repeat` from the first frame only: 0 = forever, -1 = once.
        gif.writeFrame(index, w, h, {
          palette,
          delay: this.delay,
          repeat: this.loop ? 0 : -1,
          first: n === 0,
        });
        $('#gf-status').textContent = `Encoding frame ${n + 1} of ${seq.length}…`;
        // Yield so the status text actually paints between frames.
        await new Promise((r) => setTimeout(r, 0));
      }
      gif.finish();
      const blob = new Blob([gif.bytes()], { type: 'image/gif' });
      if (this.gifUrl) URL.revokeObjectURL(this.gifUrl);
      this.gifUrl = URL.createObjectURL(blob);
      const dl = $('#gf-download');
      dl.href = this.gifUrl;
      dl.classList.remove('hidden');
      $('#gf-status').innerHTML = `<i class="fa-solid fa-circle-check text-green-500 mr-1"></i>GIF ready · ${w}×${h} · ${seq.length} frames · ${humanSize(blob.size)}`;
    } catch (err) {
      Toast.show('Could not build the GIF', 'error');
      $('#gf-status').textContent = 'Encoding failed — try fewer or smaller frames.';
    } finally {
      btn.disabled = false;
      btn.innerHTML = '<i class="fa-solid fa-images mr-1.5"></i>Create GIF';
      this.play();
    }
  },

  reset() {
    clearTimeout(this.playing);
    this.frames.forEach((f) => URL.revokeObjectURL(f.url));
    this.frames = [];
    this.invalidate();
    this.editor.classList.add('hidden');
    this.dropzone.parentElement.classList.remove('hidden');
    $('#gf-status').textContent = 'Live preview — the GIF is built when you hit Create';
  },
};

document.addEventListener('DOMContentLoaded', () => App.init());
