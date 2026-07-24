/**
 * Video converter — trim, change speed, mute and re-encode, 100% client-side.
 *
 * The browser decodes the source natively, we play it (at the chosen speed) onto
 * a canvas, and MediaRecorder captures that canvas — plus the audio, routed
 * through a WebAudio graph so it can be recorded without blasting the speakers.
 * Nothing is uploaded. Because MediaRecorder records what it's fed in real time,
 * a clip takes about (duration ÷ speed) to process — the trade for needing no
 * ffmpeg and no server. Output is MP4 where the browser can record it, else WebM.
 */

const { $, $$, Toast, download, t } = CBG;

const humanSize = (b) => (b < 1024 * 1024 ? `${Math.round(b / 1024)} KB` : `${(b / 1048576).toFixed(1)} MB`);
const fmtTime = (s) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`;
const evenify = (n) => Math.max(2, Math.round(n / 2) * 2); // H.264 needs even dimensions

// Preferred container/codec order. MP4 first (what people actually want from a
// converter), WebM as the universal fallback.
const MP4_MIMES = ['video/mp4;codecs=avc1.42E01E,mp4a.40.2', 'video/mp4;codecs=avc1', 'video/mp4'];
const WEBM_MIMES = ['video/webm;codecs=vp9,opus', 'video/webm;codecs=vp8,opus', 'video/webm'];

const App = {
  url: null,
  duration: 0,
  start: 0,
  end: 0,
  speed: 1,
  size: 'original',   // 'original' | 720 | 480 (max dimension)
  format: 'mp4',      // 'mp4' | 'webm'
  mute: false,
  busy: false,
  audioCtx: null,
  audioTrack: null,
  resultUrl: null,
  resultBlob: null,

  init() {
    this.dropzone = $('#vc-dropzone');
    this.input = $('#vc-input');
    this.editor = $('#vc-editor');
    this.video = $('#vc-video');
    this.canvas = $('#vc-canvas');

    if (!window.MediaRecorder || !this.canvas.captureStream) {
      this.dropzone.classList.add('opacity-60', 'pointer-events-none');
      $('#vc-unsupported')?.classList.remove('hidden');
    } else {
      this.detectFormats();
    }

    const open = () => this.input.click();
    $('#vc-browse').addEventListener('click', (e) => { e.stopPropagation(); open(); });
    this.dropzone.addEventListener('click', open);
    this.dropzone.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); } });
    this.input.addEventListener('change', (e) => this.load(e.target.files));

    const icon = $('#vc-icon');
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach((evt) =>
      this.dropzone.addEventListener(evt, (e) => { e.preventDefault(); e.stopPropagation(); }));
    ['dragenter', 'dragover'].forEach((evt) => this.dropzone.addEventListener(evt, () => { this.dropzone.classList.add('border-primary', 'bg-primary/5'); icon.classList.add('scale-110'); }));
    ['dragleave', 'drop'].forEach((evt) => this.dropzone.addEventListener(evt, () => { this.dropzone.classList.remove('border-primary', 'bg-primary/5'); icon.classList.remove('scale-110'); }));
    this.dropzone.addEventListener('drop', (e) => this.load(e.dataTransfer.files));

    $('#vc-start').addEventListener('input', (e) => this.setTrim(+e.target.value, this.end));
    $('#vc-end').addEventListener('input', (e) => this.setTrim(this.start, +e.target.value));
    $$('.vc-speed').forEach((b) => b.addEventListener('click', () => {
      this.speed = +b.dataset.speed;
      this.segment($$('.vc-speed'), b);
      this.video.playbackRate = this.speed;
      this.updateEstimate();
    }));
    $$('.vc-size').forEach((b) => b.addEventListener('click', () => {
      this.size = b.dataset.size === 'original' ? 'original' : +b.dataset.size;
      this.segment($$('.vc-size'), b);
    }));
    $$('.vc-format').forEach((b) => b.addEventListener('click', () => {
      if (b.disabled) return;
      this.format = b.dataset.format;
      this.segment($$('.vc-format'), b);
    }));
    $('#vc-mute').addEventListener('change', (e) => { this.mute = e.target.checked; });
    $('#vc-convert').addEventListener('click', () => this.convert());
    $('#vc-download').addEventListener('click', () => this.save());
    $('#vc-new').addEventListener('click', () => this.reset());
  },

  /** Grey out formats the browser can't record; default to the best it can. */
  detectFormats() {
    const mp4 = this.pickMime('mp4');
    const webm = this.pickMime('webm');
    const setBtn = (fmt, ok) => {
      const b = $(`.vc-format[data-format="${fmt}"]`);
      if (!b) return;
      b.disabled = !ok;
      b.classList.toggle('opacity-40', !ok);
      b.classList.toggle('cursor-not-allowed', !ok);
      if (!ok) b.title = 'Your browser can’t record this format';
    };
    setBtn('mp4', !!mp4);
    setBtn('webm', !!webm);
    this.format = mp4 ? 'mp4' : 'webm';
    this.segment($$('.vc-format'), $(`.vc-format[data-format="${this.format}"]`));
  },

  pickMime(fmt) {
    const cands = fmt === 'mp4' ? MP4_MIMES : WEBM_MIMES;
    return cands.find((c) => MediaRecorder.isTypeSupported(c)) || '';
  },

  segment(group, active) {
    group.forEach((x) => {
      const a = x === active;
      x.classList.toggle('ring-2', a); x.classList.toggle('ring-primary', a);
      x.classList.toggle('hover:bg-gray-100', !a && !x.disabled); x.classList.toggle('dark:hover:bg-gray-800', !a && !x.disabled);
    });
  },

  async load(fileList) {
    const file = [...(fileList || [])].find((f) => f && /^video\//.test(f.type));
    this.input.value = '';
    if (!file) { Toast.show(t('Please choose a video file'), 'error'); return; }

    if (this.url) URL.revokeObjectURL(this.url);
    this.url = URL.createObjectURL(file);
    try {
      await this.ready(this.url);
    } catch {
      URL.revokeObjectURL(this.url); this.url = null;
      Toast.show(t("This video format can't be read in your browser — try an MP4 or WebM."), 'error');
      return;
    }

    this.duration = this.video.duration;
    this.start = 0;
    this.end = this.duration;
    const s = $('#vc-start'), e = $('#vc-end');
    s.max = e.max = this.duration.toFixed(2);
    s.value = 0; e.value = this.end;

    this.dropzone.parentElement.classList.add('hidden');
    this.editor.classList.remove('hidden');
    this.clearResult();
    this.setTrim(this.start, this.end);
  },

  ready(url) {
    return new Promise((resolve, reject) => {
      const v = this.video;
      const done = () => { cleanup(); resolve(); };
      const fail = () => { cleanup(); reject(new Error('decode')); };
      const cleanup = () => { v.removeEventListener('loadeddata', done); v.removeEventListener('error', fail); };
      v.addEventListener('loadeddata', done, { once: true });
      v.addEventListener('error', fail, { once: true });
      v.src = url;
      v.load();
    });
  },

  setTrim(start, end) {
    start = Math.max(0, Math.min(start, this.duration));
    end = Math.max(0, Math.min(end, this.duration));
    if (end - start < 0.1) {
      if (start !== this.start) start = Math.max(0, end - 0.1);
      else end = Math.min(this.duration, start + 0.1);
    }
    this.start = start; this.end = end;
    $('#vc-start').value = start;
    $('#vc-end').value = end;
    $('#vc-start-val').textContent = fmtTime(start);
    $('#vc-end-val').textContent = fmtTime(end);
    try { this.video.currentTime = start; } catch { /* not seekable yet */ }
    this.updateEstimate();
  },

  updateEstimate() {
    const out = (this.end - this.start) / this.speed;
    $('#vc-estimate').textContent =
      `output ~${fmtTime(out)}${this.speed !== 1 ? ` · ${this.speed}×` : ''} · processes in real time`;
  },

  /** Target dimensions: keep aspect ratio, cap the longest side at `size`. */
  dims() {
    const vw = this.video.videoWidth || 2, vh = this.video.videoHeight || 2;
    if (this.size === 'original') return [evenify(vw), evenify(vh)];
    const scale = Math.min(1, this.size / Math.max(vw, vh));
    return [evenify(vw * scale), evenify(vh * scale)];
  },

  seek(time) {
    return new Promise((resolve) => {
      const v = this.video;
      const onSeeked = () => { v.removeEventListener('seeked', onSeeked); resolve(); };
      v.addEventListener('seeked', onSeeked, { once: true });
      v.currentTime = Math.min(time, Math.max(0, this.duration - 0.001));
    });
  },

  /**
   * Audio track for the recording, captured silently via WebAudio so it isn't
   * played aloud while converting. Created once — createMediaElementSource can
   * only be called on an element a single time — and reused for every run.
   */
  ensureAudio() {
    if (this.audioTrack) return this.audioTrack;
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return null;
    this.audioCtx = new AC();
    const src = this.audioCtx.createMediaElementSource(this.video);
    const dest = this.audioCtx.createMediaStreamDestination();
    src.connect(dest); // to the recording only — not to ctx.destination (stays silent)
    this.audioTrack = dest.stream.getAudioTracks()[0] || null;
    return this.audioTrack;
  },

  setProgress(p) {
    const pct = Math.max(0, Math.min(100, Math.round(p * 100)));
    $('#vc-bar').style.width = `${pct}%`;
    $('#vc-status').textContent = `Converting… ${pct}%`;
  },

  async convert() {
    if (!this.url || this.busy) return;
    this.busy = true;
    this.clearResult();
    const btn = $('#vc-convert');
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin mr-1.5"></i>Converting…';
    $('#vc-progress').classList.remove('hidden');

    const [w, h] = this.dims();
    this.canvas.width = w; this.canvas.height = h;
    const ctx = this.canvas.getContext('2d');

    const mime = this.pickMime(this.format) || this.pickMime('webm');
    const stream = this.canvas.captureStream(30);
    let audioTrack = null;
    if (!this.mute) {
      audioTrack = this.ensureAudio();
      if (audioTrack) stream.addTrack(audioTrack);
    }

    const chunks = [];
    let rec;
    try {
      rec = new MediaRecorder(stream, {
        mimeType: mime,
        videoBitsPerSecond: Math.min(8_000_000, Math.round(w * h * 30 * 0.1)),
      });
    } catch {
      this.fail(t('Could not convert the video'));
      stream.getVideoTracks().forEach((tr) => tr.stop());
      return;
    }
    rec.ondataavailable = (e) => { if (e.data && e.data.size) chunks.push(e.data); };

    const finish = () => {
      if (this._stopped) return;
      this._stopped = true;
      this.video.pause();
      if (rec.state !== 'inactive') rec.stop();
    };

    rec.onstop = () => {
      stream.getVideoTracks().forEach((tr) => tr.stop()); // keep the shared audio track alive
      const blob = new Blob(chunks, { type: mime.split(';')[0] });
      this.showResult(blob, w, h);
      this.busy = false;
      btn.disabled = false;
      btn.innerHTML = '<i class="fa-solid fa-arrow-right-arrow-left mr-1.5"></i>Convert video';
    };

    this._stopped = false;
    // requestVideoFrameCallback stops firing once playback ends, so when the
    // trim reaches the end of the clip the frame loop never sees it — the
    // `ended` event is the reliable backstop that flushes the recording.
    this.video.addEventListener('ended', finish, { once: true });
    this.video.playbackRate = this.speed;
    this.video.muted = true; // don't play the source aloud while capturing
    await this.seek(this.start);
    if (this.audioCtx) { try { await this.audioCtx.resume(); } catch { /* ignore */ } }

    const drawWith = (schedule) => {
      const step = () => {
        if (this._stopped) return;
        if (this.video.currentTime >= this.end - 0.001 || this.video.ended) { finish(); return; }
        ctx.drawImage(this.video, 0, 0, w, h);
        this.setProgress((this.video.currentTime - this.start) / (this.end - this.start));
        schedule(step);
      };
      schedule(step);
    };

    rec.start();
    try {
      await this.video.play();
    } catch {
      this.fail(t('Could not convert the video'));
      return;
    }
    // Prefer per-decoded-frame callbacks; fall back to rAF where unavailable.
    if (this.video.requestVideoFrameCallback) {
      drawWith((fn) => this.video.requestVideoFrameCallback(fn));
    } else {
      drawWith((fn) => requestAnimationFrame(fn));
    }
  },

  fail(msg) {
    Toast.show(msg, 'error');
    this._stopped = true;
    this.busy = false;
    $('#vc-progress').classList.add('hidden');
    const btn = $('#vc-convert');
    btn.disabled = false;
    btn.innerHTML = '<i class="fa-solid fa-arrow-right-arrow-left mr-1.5"></i>Convert video';
  },

  showResult(blob, w, h) {
    $('#vc-progress').classList.add('hidden');
    if (!blob.size) { Toast.show(t('Could not convert the video'), 'error'); return; }
    this.resultBlob = blob;
    if (this.resultUrl) URL.revokeObjectURL(this.resultUrl);
    this.resultUrl = URL.createObjectURL(blob);
    const r = $('#vc-result');
    r.src = this.resultUrl;
    $('#vc-result-wrap').classList.remove('hidden');
    $('#vc-download').classList.remove('hidden');
    const ext = blob.type.includes('mp4') ? 'MP4' : 'WebM';
    $('#vc-status').innerHTML = `<i class="fa-solid fa-circle-check text-green-500 mr-1"></i>Done · ${ext} · ${w}×${h} · ${humanSize(blob.size)}`;
  },

  save() {
    if (this.resultBlob) {
      const ext = this.resultBlob.type.includes('mp4') ? 'mp4' : 'webm';
      download(this.resultBlob, `video.${ext}`, { chain: false });
    }
  },

  clearResult() {
    if (this.resultUrl) { URL.revokeObjectURL(this.resultUrl); this.resultUrl = null; }
    this.resultBlob = null;
    $('#vc-result-wrap').classList.add('hidden');
    $('#vc-download').classList.add('hidden');
    $('#vc-progress').classList.add('hidden');
    $('#vc-bar').style.width = '0%';
  },

  reset() {
    this._stopped = true;
    if (this.url) URL.revokeObjectURL(this.url);
    this.url = null;
    this.busy = false;
    this.speed = 1; this.size = 'original'; this.mute = false;
    this.video.playbackRate = 1;
    this.video.removeAttribute('src');
    this.video.load();
    this.segment($$('.vc-speed'), $('.vc-speed[data-speed="1"]'));
    this.segment($$('.vc-size'), $('.vc-size[data-size="original"]'));
    $('#vc-mute').checked = false;
    this.clearResult();
    this.editor.classList.add('hidden');
    this.dropzone.parentElement.classList.remove('hidden');
    $('#vc-status').textContent = 'Trim, set the speed, then convert';
  },
};

document.addEventListener('DOMContentLoaded', () => App.init());
