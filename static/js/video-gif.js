/**
 * Video → animated GIF — 100% client-side.
 *
 * The browser decodes the video natively (`<video>` handles whatever codecs it
 * supports — H.264 MP4, WebM, most MOV), so there is no ffmpeg and nothing is
 * uploaded. Frames are grabbed by seeking the video to evenly spaced times,
 * painting each onto a fixed-size canvas, then encoding with gifenc — the exact
 * same pipeline the photo GIF maker uses. Extraction and encoding run in one
 * pass so we never hold every frame in memory at once.
 */

const { $, $$, Toast, download, t } = CBG;
import { GIFEncoder, applyPalette, quantize } from 'https://cdn.jsdelivr.net/npm/gifenc@1.0.3/+esm';

const humanSize = (b) => (b < 1024 * 1024 ? `${Math.round(b / 1024)} KB` : `${(b / 1048576).toFixed(1)} MB`);
const fmtTime = (s) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`;

// A GIF this size × this many frames is already a heavy download; cap the frame
// count so a long clip at high fps can't lock the tab up or produce a 50 MB GIF.
const MAX_FRAMES = 300;

const App = {
  video: null,      // the <video> element (also the live preview)
  url: null,        // object URL for the loaded file
  name: '',
  duration: 0,
  start: 0,
  end: 0,
  fps: 10,
  size: 360,
  fit: 'cover',
  loop: true,
  gifUrl: null,
  gifBlob: null,

  init() {
    this.dropzone = $('#vg-dropzone');
    this.input = $('#vg-input');
    this.editor = $('#vg-editor');
    this.video = $('#vg-video');
    this.canvas = $('#vg-canvas');

    const open = () => this.input.click();
    $('#vg-browse').addEventListener('click', (e) => { e.stopPropagation(); open(); });
    this.dropzone.addEventListener('click', open);
    this.dropzone.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); } });
    this.input.addEventListener('change', (e) => this.load(e.target.files));

    const icon = $('#vg-icon');
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach((evt) =>
      this.dropzone.addEventListener(evt, (e) => { e.preventDefault(); e.stopPropagation(); }));
    ['dragenter', 'dragover'].forEach((evt) => this.dropzone.addEventListener(evt, () => { this.dropzone.classList.add('border-primary', 'bg-primary/5'); icon.classList.add('scale-110'); }));
    ['dragleave', 'drop'].forEach((evt) => this.dropzone.addEventListener(evt, () => { this.dropzone.classList.remove('border-primary', 'bg-primary/5'); icon.classList.remove('scale-110'); }));
    this.dropzone.addEventListener('drop', (e) => this.load(e.dataTransfer.files));

    $('#vg-start').addEventListener('input', (e) => this.setTrim(+e.target.value, this.end));
    $('#vg-end').addEventListener('input', (e) => this.setTrim(this.start, +e.target.value));
    $$('.vg-fps').forEach((b) => b.addEventListener('click', () => {
      this.fps = +b.dataset.fps;
      this.segment($$('.vg-fps'), b);
      this.invalidate(); this.updateEstimate();
    }));
    $$('.vg-size').forEach((b) => b.addEventListener('click', () => {
      this.size = +b.dataset.size;
      this.segment($$('.vg-size'), b);
      this.invalidate();
    }));
    $$('.vg-fit').forEach((b) => b.addEventListener('click', () => {
      this.fit = b.dataset.fit;
      this.segment($$('.vg-fit'), b);
      this.invalidate();
    }));
    $('#vg-loop').addEventListener('change', (e) => { this.loop = e.target.checked; this.invalidate(); });
    $('#vg-create').addEventListener('click', () => this.create());
    $('#vg-download').addEventListener('click', () => this.save());
    $('#vg-new').addEventListener('click', () => this.reset());
  },

  segment(group, active) {
    group.forEach((x) => {
      const a = x === active;
      x.classList.toggle('ring-2', a); x.classList.toggle('ring-primary', a);
      x.classList.toggle('hover:bg-gray-100', !a); x.classList.toggle('dark:hover:bg-gray-800', !a);
    });
  },

  async load(fileList) {
    const file = [...(fileList || [])].find((f) => f && /^video\//.test(f.type));
    this.input.value = '';
    if (!file) { Toast.show(t('Please choose a video file'), 'error'); return; }

    if (this.url) URL.revokeObjectURL(this.url);
    this.url = URL.createObjectURL(file);
    this.name = file.name;

    // Wait for the browser to decode enough to know the size, duration and to
    // seek reliably. If the codec isn't supported this rejects — tell the user.
    try {
      await this.ready(this.url);
    } catch {
      URL.revokeObjectURL(this.url); this.url = null;
      Toast.show(t("This video format can't be read in your browser — try an MP4 or WebM."), 'error');
      return;
    }

    this.duration = this.video.duration;
    // Default to the whole clip, but cap the initial window so a long video
    // doesn't start out over the frame limit.
    this.start = 0;
    this.end = Math.min(this.duration, MAX_FRAMES / this.fps);

    const s = $('#vg-start'), e = $('#vg-end');
    s.max = e.max = this.duration.toFixed(2);
    s.value = this.start; e.value = this.end;

    this.dropzone.parentElement.classList.add('hidden');
    this.editor.classList.remove('hidden');
    this.setTrim(this.start, this.end);
    this.invalidate();
  },

  /** Resolve once the video can be seeked and drawn (or reject on decode error). */
  ready(url) {
    return new Promise((resolve, reject) => {
      const v = this.video;
      const done = () => { cleanup(); resolve(); };
      const fail = () => { cleanup(); reject(new Error('decode')); };
      const cleanup = () => {
        v.removeEventListener('loadeddata', done);
        v.removeEventListener('error', fail);
      };
      v.addEventListener('loadeddata', done, { once: true });
      v.addEventListener('error', fail, { once: true });
      v.src = url;
      v.load();
    });
  },

  setTrim(start, end) {
    // Keep start < end and clamp both into the clip.
    start = Math.max(0, Math.min(start, this.duration));
    end = Math.max(0, Math.min(end, this.duration));
    if (end - start < 0.1) {
      // Nudge whichever the user just moved so the window never collapses.
      if (start !== this.start) start = Math.max(0, end - 0.1);
      else end = Math.min(this.duration, start + 0.1);
    }
    this.start = start; this.end = end;
    $('#vg-start').value = start;
    $('#vg-end').value = end;
    $('#vg-start-val').textContent = fmtTime(start);
    $('#vg-end-val').textContent = fmtTime(end);
    // Show the first trimmed frame so the preview reflects the in-point.
    try { this.video.currentTime = start; } catch { /* not seekable yet */ }
    this.invalidate();
    this.updateEstimate();
  },

  frameCount() {
    return Math.min(MAX_FRAMES, Math.max(2, Math.round((this.end - this.start) * this.fps)));
  },

  updateEstimate() {
    const n = this.frameCount();
    const capped = (this.end - this.start) * this.fps > MAX_FRAMES;
    $('#vg-estimate').innerHTML = capped
      ? `~${n} frames · <span class="text-amber-600 dark:text-amber-400">capped — shorten the clip or lower the fps for a smoother result</span>`
      : `${n} frames · ${fmtTime(this.end - this.start)} at ${this.fps} fps`;
  },

  /** GIF has one fixed logical screen — derive it from the video, capped at `size`. */
  dims() {
    const vw = this.video.videoWidth || 2, vh = this.video.videoHeight || 2;
    const ar = vw / vh;
    const [w, h] = ar >= 1 ? [this.size, Math.round(this.size / ar)] : [Math.round(this.size * ar), this.size];
    return [Math.max(2, w), Math.max(2, h)];
  },

  paint(ctx, w, h) {
    ctx.clearRect(0, 0, w, h);
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, w, h);
    const iw = this.video.videoWidth, ih = this.video.videoHeight;
    const scale = this.fit === 'cover' ? Math.max(w / iw, h / ih) : Math.min(w / iw, h / ih);
    const dw = iw * scale, dh = ih * scale;
    ctx.imageSmoothingQuality = 'high';
    ctx.drawImage(this.video, (w - dw) / 2, (h - dh) / 2, dw, dh);
  },

  /** Seek to `time` and resolve once that frame is actually painted-ready. */
  seek(time) {
    return new Promise((resolve) => {
      const v = this.video;
      const onSeeked = () => { v.removeEventListener('seeked', onSeeked); resolve(); };
      v.addEventListener('seeked', onSeeked, { once: true });
      v.currentTime = Math.min(time, Math.max(0, this.duration - 0.001));
    });
  },

  invalidate() {
    $('#vg-download').classList.add('hidden');
    if (this.gifUrl) { URL.revokeObjectURL(this.gifUrl); this.gifUrl = null; }
    this.gifBlob = null;
  },

  save() {
    // Opted out of cross-tool chaining: every destination tool composites through
    // a canvas, so a chained GIF would arrive as one still frame, animation gone.
    if (this.gifBlob) download(this.gifBlob, 'animation.gif', { chain: false });
  },

  async create() {
    if (!this.url) return;
    const btn = $('#vg-create');
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin mr-1.5"></i>Encoding…';
    this.video.pause();

    const [w, h] = this.dims();
    this.canvas.width = w; this.canvas.height = h;
    const ctx = this.canvas.getContext('2d', { willReadFrequently: true });
    const n = this.frameCount();
    const delay = Math.round(1000 / this.fps);
    const step = (this.end - this.start) / n;
    const gif = GIFEncoder();

    try {
      for (let i = 0; i < n; i += 1) {
        await this.seek(this.start + i * step);
        this.paint(ctx, w, h);
        const { data } = ctx.getImageData(0, 0, w, h);
        const palette = quantize(data, 256);
        const index = applyPalette(data, palette);
        // gifenc reads `repeat` from the first frame only: 0 = forever, -1 = once.
        gif.writeFrame(index, w, h, {
          palette,
          delay,
          repeat: this.loop ? 0 : -1,
          first: i === 0,
        });
        $('#vg-status').textContent = `Encoding frame ${i + 1} of ${n}…`;
        await new Promise((r) => setTimeout(r, 0)); // let the status paint
      }
      gif.finish();
      const blob = new Blob([gif.bytes()], { type: 'image/gif' });
      if (this.gifUrl) URL.revokeObjectURL(this.gifUrl);
      this.gifUrl = URL.createObjectURL(blob);
      this.gifBlob = blob;
      const dl = $('#vg-download');
      dl.classList.remove('hidden');
      $('#vg-status').innerHTML = `<i class="fa-solid fa-circle-check text-green-500 mr-1"></i>GIF ready · ${w}×${h} · ${n} frames · ${humanSize(blob.size)}`;
    } catch {
      Toast.show(t('Could not build the GIF'), 'error');
      $('#vg-status').textContent = 'Encoding failed — try a shorter clip or a smaller size.';
    } finally {
      btn.disabled = false;
      btn.innerHTML = '<i class="fa-solid fa-images mr-1.5"></i>Create GIF';
    }
  },

  reset() {
    if (this.url) URL.revokeObjectURL(this.url);
    this.url = null;
    this.video.removeAttribute('src');
    this.video.load();
    this.invalidate();
    this.editor.classList.add('hidden');
    this.dropzone.parentElement.classList.remove('hidden');
    $('#vg-status').textContent = 'Trim, set the speed, then hit Create';
  },
};

document.addEventListener('DOMContentLoaded', () => App.init());
